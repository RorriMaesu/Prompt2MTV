import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import copy
import json
import urllib.request
import urllib.error
import urllib.parse
import time
import random
import threading
import os
import subprocess
import shutil
from datetime import datetime
from PIL import Image, ImageTk
import ttkbootstrap as tb

# Try to get ffmpeg from imageio_ffmpeg, fallback to 'ffmpeg'
try:
    imageio_ffmpeg = __import__('imageio_ffmpeg')
    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FFMPEG_PATH = shutil.which('ffmpeg') or 'ffmpeg'

DEFAULT_VIDEO_PROFILE = "ltx_2_3_t2v"
DEFAULT_MODEL_SEARCH_ROOTS = [
    r"D:\ComfyUI\ComfyUI\models",
    r"D:\ComfyUI\models"
]
MODEL_SUBDIRECTORIES = {
    "checkpoint_name": "checkpoints",
    "text_encoder_name": "text_encoders",
    "lora_name": "loras",
    "upscaler_name": "latent_upscale_models"
}
THEME_NAME = "superhero"
UI_COLORS = {
    "bg": "#08111f",
    "surface": "#101a2d",
    "surface_alt": "#16233b",
    "surface_soft": "#1b2b46",
    "card": "#122036",
    "border": "#223657",
    "text": "#edf4ff",
    "text_muted": "#99a8c7",
    "accent": "#42d6d0",
    "accent_hover": "#64e4df",
    "primary": "#2e6cff",
    "primary_hover": "#4c83ff",
    "success": "#2fb67a",
    "success_hover": "#43c88d",
    "danger": "#d86b79",
    "danger_hover": "#e4818d",
    "warning": "#d8a85f",
    "input_bg": "#0d1628",
    "input_border": "#294166",
    "black": "#04070d"
}
UI_FONTS = {
    "title": ("Segoe UI Semibold", 16),
    "section": ("Segoe UI Semibold", 11),
    "body": ("Segoe UI", 10),
    "body_strong": ("Segoe UI Semibold", 10),
    "small": ("Segoe UI", 9),
    "micro": ("Segoe UI", 8)
}
VIDEO_WORKFLOW_PROFILES = {
    "ltx_2_3_t2v": {
        "label": "LTX 2.3 Text to Video",
        "workflow_path": "video_ltx2_3_t2v.json",
        "roles": {
            "prompt": {"node_id": "267:240", "input": "text"},
            "negative_prompt": {"node_id": "267:247", "input": "text"},
            "width": {"node_id": "267:257", "input": "value"},
            "height": {"node_id": "267:258", "input": "value"},
            "fps": {"node_id": "267:260", "input": "value"},
            "length": {"node_id": "267:225", "input": "value"},
            "t2v_enabled": {"node_id": "267:201", "input": "value"},
            "filename_prefix": {"node_id": "75", "input": "filename_prefix"},
            "noise_seed": [
                {"node_id": "267:216", "input": "noise_seed"},
                {"node_id": "267:237", "input": "noise_seed"}
            ],
            "checkpoint_name": [
                {"node_id": "267:221", "input": "ckpt_name"},
                {"node_id": "267:243", "input": "ckpt_name"},
                {"node_id": "267:236", "input": "ckpt_name"}
            ],
            "text_encoder_name": {"node_id": "267:243", "input": "text_encoder"},
            "lora_name": {"node_id": "267:232", "input": "lora_name"},
            "upscaler_name": {"node_id": "267:233", "input": "model_name"}
        }
    }
}

class LTXQueueManager:
    def __init__(self, root):
        self.root = root
        self.root.title("LTX-2.3 Video Queue Manager")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        default_width = min(1320, max(1080, int(screen_width * 0.9)))
        default_height = min(920, max(760, int(screen_height * 0.86)))
        self.root.geometry(f"{default_width}x{default_height}")
        self.root.minsize(980, 720)
        self.root.after(0, self._maximize_window)
        self.colors = dict(UI_COLORS)
        self.fonts = dict(UI_FONTS)
        self._configure_theme_system()
        
        self.api_json_path = VIDEO_WORKFLOW_PROFILES[DEFAULT_VIDEO_PROFILE]["workflow_path"]
        self.music_json_path = "ACE_Step_AI_Music_Generator_Workflow.json"
        self.workflow = None
        self.music_workflow = None
        self.prompts = []
        self.comfyui_process = None
        self.global_settings_file = "app_settings.json"
        self.selected_videos = set()
        self.video_checkbox_vars = []
        self.selected_video_for_music = None
        self.current_generated_audio = None
        self.current_project_dir = None
        self.debug_lock = threading.Lock()
        self.debug_log_file = None
        self.model_search_roots = list(DEFAULT_MODEL_SEARCH_ROOTS)
        self.video_model_choices = {field_name: [] for field_name in MODEL_SUBDIRECTORIES}
        self.collapsible_sections = {}
        self.collapsible_section_groups = {}
        self.responsive_layout_mode = None
        
        # Setup base output directory
        self.base_output_dir = "outputs"
        os.makedirs(self.base_output_dir, exist_ok=True)
        
        self.thumbnail_images = []
        
        self.setup_ui()
        self.load_global_settings() # Load global settings first to get the last project
        self.load_default_json()
        self.launch_comfyui()

    def _configure_theme_system(self):
        self.style = tb.Style(theme=THEME_NAME)
        self.root.configure(bg=self.colors["bg"])
        self.root.option_add("*Font", self.fonts["body"])
        self.root.option_add("*Menu.font", self.fonts["body"])
        self.root.option_add("*TCombobox*Listbox.font", self.fonts["body"])
        self._configure_ttk_styles()

    def _configure_ttk_styles(self):
        self.style.configure(
            "App.TNotebook",
            background=self.colors["bg"],
            borderwidth=0,
            tabmargins=(0, 0, 0, 0)
        )
        self.style.configure(
            "App.TNotebook.Tab",
            background=self.colors["surface_alt"],
            foreground=self.colors["text_muted"],
            padding=(18, 10),
            font=self.fonts["body_strong"]
        )
        self.style.map(
            "App.TNotebook.Tab",
            background=[("selected", self.colors["surface"]), ("active", self.colors["surface_soft"])],
            foreground=[("selected", self.colors["text"]), ("active", self.colors["text"])]
        )
        self.style.configure(
            "TCombobox",
            fieldbackground=self.colors["input_bg"],
            background=self.colors["input_bg"],
            foreground=self.colors["text"],
            bordercolor=self.colors["input_border"],
            arrowcolor=self.colors["text_muted"],
            insertcolor=self.colors["text"],
            padding=6
        )

    def _bind_button_hover(self, button, base_bg, hover_bg):
        button.bind("<Enter>", lambda _event, widget=button, color=hover_bg: widget.configure(bg=color))
        button.bind("<Leave>", lambda _event, widget=button, color=base_bg: widget.configure(bg=color))

    def _style_button(self, button, variant="secondary", compact=False):
        palette = {
            "primary": (self.colors["primary"], self.colors["primary_hover"], self.colors["text"]),
            "accent": (self.colors["accent"], self.colors["accent_hover"], self.colors["black"]),
            "success": (self.colors["success"], self.colors["success_hover"], self.colors["text"]),
            "danger": (self.colors["danger"], self.colors["danger_hover"], self.colors["text"]),
            "secondary": (self.colors["surface_soft"], self.colors["border"], self.colors["text"]),
            "ghost": (self.colors["surface"], self.colors["surface_soft"], self.colors["text_muted"])
        }
        bg_color, hover_color, fg_color = palette.get(variant, palette["secondary"])
        button.configure(
            bg=bg_color,
            fg=fg_color,
            activebackground=hover_color,
            activeforeground=fg_color,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            font=self.fonts["body_strong" if not compact else "small"],
            padx=12 if not compact else 10,
            pady=8 if not compact else 6
        )
        self._bind_button_hover(button, bg_color, hover_color)

    def _style_text_input(self, widget, multiline=False):
        try:
            widget.configure(
                bg=self.colors["input_bg"],
                fg=self.colors["text"],
                insertbackground=self.colors["text"],
                relief=tk.FLAT,
                bd=0,
                highlightthickness=1,
                highlightbackground=self.colors["input_border"],
                highlightcolor=self.colors["accent"],
                selectbackground=self.colors["primary"],
                selectforeground=self.colors["text"],
                font=self.fonts["body"]
            )
            if multiline:
                widget.configure(padx=10, pady=8)
        except tk.TclError:
            try:
                widget.configure(font=self.fonts["body"])
            except tk.TclError:
                pass

    def _style_panel(self, widget, background=None, border=False):
        bg_color = background or self.colors["surface"]
        widget.configure(bg=bg_color)
        if border:
            widget.configure(highlightbackground=self.colors["border"], highlightthickness=1, bd=0)

    def _style_labelframe(self, widget):
        widget.configure(
            bg=self.colors["surface"],
            fg=self.colors["text"],
            bd=0,
            relief=tk.FLAT,
            font=self.fonts["section"],
            highlightbackground=self.colors["border"],
            highlightthickness=1,
            labelanchor="nw"
        )

    def _style_label(self, widget, tone="body", background=None):
        font_map = {
            "title": self.fonts["title"],
            "section": self.fonts["section"],
            "muted": self.fonts["small"],
            "body": self.fonts["body"],
            "body_strong": self.fonts["body_strong"]
        }
        fg_map = {
            "title": self.colors["text"],
            "section": self.colors["text"],
            "muted": self.colors["text_muted"],
            "body": self.colors["text"],
            "body_strong": self.colors["text"]
        }
        widget.configure(
            bg=background or widget.master.cget("bg"),
            fg=fg_map.get(tone, self.colors["text"]),
            font=font_map.get(tone, self.fonts["body"])
        )

    def _style_checkbutton(self, widget, background=None):
        widget.configure(
            bg=background or widget.master.cget("bg"),
            fg=self.colors["text_muted"],
            activebackground=background or widget.master.cget("bg"),
            activeforeground=self.colors["text"],
            selectcolor=self.colors["surface_soft"],
            font=self.fonts["small"],
            bd=0,
            highlightthickness=0,
            cursor="hand2"
        )

    def _create_metric_chip(self, parent, label_text, value_text="0", align="left"):
        anchor_map = {"left": "w", "center": "center", "right": "e"}
        anchor = anchor_map.get(align, align)
        chip = tk.Frame(parent, padx=12, pady=10)
        self._style_panel(chip, self.colors["surface_soft"], border=True)

        label = tk.Label(chip, text=label_text.upper(), anchor=anchor)
        label.pack(fill=tk.X)
        self._style_label(label, "muted", self.colors["surface_soft"])
        label.configure(font=self.fonts["micro"])

        value = tk.Label(chip, text=value_text, anchor=anchor)
        value.pack(fill=tk.X, pady=(4, 0))
        self._style_label(value, "section", self.colors["surface_soft"])
        return chip, value

    def _create_section_intro(self, parent, eyebrow_text, title_text, description_text):
        eyebrow = tk.Label(parent, text=eyebrow_text.upper(), anchor="w")
        eyebrow.pack(anchor="w")
        self._style_label(eyebrow, "muted", parent.cget("bg"))
        eyebrow.configure(font=self.fonts["micro"])

        title = tk.Label(parent, text=title_text, anchor="w", justify=tk.LEFT)
        title.pack(anchor="w", pady=(4, 0))
        self._style_label(title, "title", parent.cget("bg"))

        description = tk.Label(parent, text=description_text, anchor="w", justify=tk.LEFT, wraplength=700)
        description.pack(anchor="w", pady=(6, 0), fill=tk.X)
        self._style_label(description, "muted", parent.cget("bg"))
        return eyebrow, title, description

    def _create_collapsible_section(self, parent, key, title, meta_text="", is_open=True, body_expand=False, body_background=None, group=None):
        section_frame = tk.Frame(parent)
        header_frame = tk.Frame(section_frame, padx=12, pady=10)
        header_frame.pack(fill=tk.X)
        header_frame.grid_columnconfigure(1, weight=1)

        toggle_button = tk.Button(
            header_frame,
            text="▼" if is_open else "▶",
            width=2,
            command=lambda section_key=key: self._toggle_collapsible_section(section_key)
        )
        toggle_button.grid(row=0, column=0, sticky="w")

        title_label = tk.Label(header_frame, text=title, anchor="w")
        title_label.grid(row=0, column=1, sticky="w", padx=(8, 0))

        meta_label = tk.Label(header_frame, text=meta_text, anchor="e")
        meta_label.grid(row=0, column=2, sticky="e", padx=(10, 0))

        body_frame = tk.Frame(section_frame)

        section = {
            "container": section_frame,
            "header": header_frame,
            "toggle": toggle_button,
            "title": title_label,
            "meta": meta_label,
            "body": body_frame,
            "open": False,
            "body_expand": body_expand,
            "body_background": body_background or self.colors["surface"],
            "group": group
        }
        self.collapsible_sections[key] = section
        if group:
            self.collapsible_section_groups.setdefault(group, []).append(key)
        self._set_collapsible_section_open(key, is_open)
        return section

    def _set_collapsible_section_open(self, key, is_open, via_group=False):
        section = self.collapsible_sections.get(key)
        if not section:
            return

        try:
            if int(section["container"].winfo_exists()) != 1:
                return
        except tk.TclError:
            return

        if is_open and section.get("group") and not via_group:
            for sibling_key in self.collapsible_section_groups.get(section["group"], []):
                if sibling_key != key:
                    self._set_collapsible_section_open(sibling_key, False, via_group=True)

        section["open"] = bool(is_open)
        try:
            section["toggle"].config(text="▼" if section["open"] else "▶")
            section["body"].pack_forget()
            if section["open"]:
                section["body"].pack(fill=tk.BOTH if section["body_expand"] else tk.X, expand=section["body_expand"])
        except tk.TclError:
            return

    def _toggle_collapsible_section(self, key):
        section = self.collapsible_sections.get(key)
        if not section:
            return
        self._set_collapsible_section_open(key, not section["open"])
        self._update_video_workspace_balance()
        self._refresh_responsive_copy()

    def _update_collapsible_section_meta(self, key, meta_text):
        section = self.collapsible_sections.get(key)
        if not section:
            return
        section["meta"].config(text=meta_text)

    def _apply_header_density_mode(self, is_compact):
        self.video_header_eyebrow_label.config(text="" if is_compact else "VIDEO STUDIO")
        self.video_header_copy_label.config(
            text="Workflow, prompts, and output review." if is_compact else "Keep workflow control, prompting, and output review in one screen."
        )
        self.prompt_section_eyebrow_label.config(text="" if is_compact else "PROMPT QUEUE")
        self.prompt_section_copy_label.config(
            text="Shot cards for the active render queue." if is_compact else "Each card is an individual shot. Keep fast one-off renders here, then promote the best clips to the stitch and music pipeline from the gallery."
        )
        self.gallery_eyebrow_label.config(text="" if is_compact else "MEDIA BROWSER")
        self.gallery_copy_label.config(
            text="Scenes, stitched renders, and finals." if is_compact else "Review generated scenes, stitched renders, and finished music videos without leaving the queue manager."
        )
        self.music_header_eyebrow_label.config(text="" if is_compact else "MUSIC STUDIO")
        self.music_header_copy_label.config(
            text="Score the selected cut." if is_compact else "Use tags for direction, lyrics for narrative, and then lock timing with duration, BPM, and key before generating audio and approving the final merge."
        )
        self.music_sidebar_eyebrow_label.config(text="" if is_compact else "LINKED MEDIA")
        self.music_sidebar_copy_label.config(
            text="Clip, audio, and final state." if is_compact else "This panel tracks the source clip, generated audio, and final export state for the current music pass."
        )
        self.music_tags_hint_label.config(
            text="Genre, texture, emotion, instrumentation." if is_compact else "Describe genre, texture, emotion, and instrumentation."
        )
        self.music_lyrics_hint_label.config(
            text="Optional vocal or narrative notes." if is_compact else "Optional. Use this for hooks, spoken phrasing, or narrative structure."
        )

    def _apply_responsive_section_defaults(self):
        width = self._safe_widget_width(self.root) or 0
        if width <= 0:
            return

        new_mode = "compact" if width < 1500 else "wide"
        if new_mode == self.responsive_layout_mode:
            return

        self.responsive_layout_mode = new_mode
        is_compact = new_mode == "compact"
        self._apply_header_density_mode(is_compact)

        target_states = {
            "video_prompt_queue": True,
            "video_settings": False,
            "video_preflight": False,
            "video_debug": False,
            "gallery_browser": not is_compact,
            "music_lyrics": False,
            "music_preview": not is_compact
        }
        for key, is_open in target_states.items():
            self._set_collapsible_section_open(key, is_open)
        self._update_video_workspace_balance()

    def _protect_primary_workspaces(self):
        prompt_canvas_height = self._safe_widget_height(getattr(self, "canvas", None)) or 0
        if prompt_canvas_height and prompt_canvas_height < 110:
            for key in ["gallery_browser"]:
                self._set_collapsible_section_open(key, False)

        music_main_height = self._safe_widget_height(getattr(self, "music_main_frame", None)) or 0
        if music_main_height and music_main_height < 420:
            for key in ["music_preview", "music_lyrics"]:
                self._set_collapsible_section_open(key, False)

    def _update_video_workspace_balance(self):
        if not hasattr(self, "video_config_row"):
            return

        try:
            if int(self.video_config_row.winfo_exists()) != 1:
                return
        except tk.TclError:
            return

        accordion_order = ["video_prompt_queue", "video_settings", "video_preflight", "video_debug"]
        active_support = next(
            (
                key for key in accordion_order
                if self.collapsible_sections.get(key) and self.collapsible_sections[key].get("open")
            ),
            None
        )

        try:
            for index, key in enumerate(accordion_order):
                section = self.collapsible_sections.get(key)
                if not section or int(section["container"].winfo_exists()) != 1:
                    continue

                section["container"].pack_forget()
                section["container"].pack(
                    fill=tk.BOTH if key == active_support else tk.X,
                    expand=key == active_support,
                    pady=(0, 10) if index < len(accordion_order) - 1 else 0
                )

            if hasattr(self, "settings_canvas") and int(self.settings_canvas.winfo_exists()) == 1:
                self.settings_canvas.configure(height=320 if active_support == "video_settings" else 240)
        except tk.TclError:
            return

    def _maximize_window(self):
        try:
            self.root.state("zoomed")
        except tk.TclError:
            try:
                self.root.attributes("-zoomed", True)
            except tk.TclError:
                pass

    def _set_wraplength(self, widget, width, padding=0, minimum=140):
        if widget is None:
            return
        try:
            if int(widget.winfo_exists()) != 1:
                return
            wraplength = max(minimum, width - padding)
            widget.config(wraplength=wraplength)
        except tk.TclError:
            pass

    def _safe_widget_width(self, widget):
        if widget is None:
            return None
        try:
            if int(widget.winfo_exists()) != 1:
                return None
            return widget.winfo_width()
        except tk.TclError:
            return None

    def _safe_widget_height(self, widget):
        if widget is None:
            return None
        try:
            if int(widget.winfo_exists()) != 1:
                return None
            return widget.winfo_height()
        except tk.TclError:
            return None

    def _refresh_responsive_copy(self):
        video_header_width = self._safe_widget_width(getattr(self, "video_header_text_frame", None))
        if video_header_width:
            self._set_wraplength(self.video_header_copy_label, video_header_width, padding=24, minimum=320)

        prompt_header_width = self._safe_widget_width(getattr(self, "prompt_header_frame", None))
        if prompt_header_width:
            self._set_wraplength(self.prompt_section_copy_label, prompt_header_width, padding=20, minimum=320)

        gallery_header_width = self._safe_widget_width(getattr(self, "gallery_header_frame", None))
        if gallery_header_width:
            self._set_wraplength(self.gallery_copy_label, gallery_header_width, padding=20, minimum=220)

        music_header_width = self._safe_widget_width(getattr(self, "music_header_frame", None))
        if music_header_width:
            self._set_wraplength(self.music_header_copy_label, music_header_width, padding=20, minimum=320)

        music_prompt_width = self._safe_widget_width(getattr(self, "music_prompt_card", None))
        if music_prompt_width:
            self._set_wraplength(self.music_tags_hint_label, music_prompt_width, padding=40, minimum=260)

        music_lyrics_width = self._safe_widget_width(getattr(self, "music_lyrics_card", None))
        if music_lyrics_width:
            self._set_wraplength(self.music_lyrics_hint_label, music_lyrics_width, padding=40, minimum=260)

        music_sidebar_width = self._safe_widget_width(getattr(self, "music_right_frame", None))
        if music_sidebar_width:
            self._set_wraplength(self.music_sidebar_copy_label, music_sidebar_width, padding=28, minimum=220)
            self._set_wraplength(self.selected_video_lbl, music_sidebar_width, padding=68, minimum=220)
            self._set_wraplength(self.selected_video_meta_label, music_sidebar_width, padding=68, minimum=220)

    def _reflow_video_left_panel(self):
        layout_sequence = [
            (self.video_header_frame, {"side": tk.TOP, "fill": tk.X}),
            (self.workflow_toolbar_card, {"side": tk.TOP, "fill": tk.X, "padx": 18, "pady": (0, 10)}),
            (self.post_process_frame, {"side": tk.BOTTOM, "fill": tk.X, "padx": 18, "pady": (0, 8)}),
            (self.separator, {"side": tk.BOTTOM, "fill": tk.X, "padx": 18, "pady": 2}),
            (self.bottom_frame, {"side": tk.BOTTOM, "fill": tk.X, "padx": 18, "pady": (0, 8)}),
            (self.video_config_row, {"side": tk.TOP, "fill": tk.BOTH, "expand": True, "padx": 18, "pady": (0, 12)})
        ]

        for widget, pack_options in layout_sequence:
            widget.pack_forget()
            widget.pack(**pack_options)

    def _on_window_resize(self, _event=None):
        self._apply_responsive_section_defaults()
        self._protect_primary_workspaces()
        self._update_video_workspace_balance()
        self._refresh_responsive_copy()

    def _update_prompt_collection_summary(self):
        if hasattr(self, "prompt_count_value_label"):
            prompt_count = len(self.scrollable_frame.winfo_children()) if hasattr(self, "scrollable_frame") else 0
            self.prompt_count_value_label.config(text=f"{prompt_count} prompt{'s' if prompt_count != 1 else ''}")
            self._update_collapsible_section_meta("video_prompt_queue", f"{prompt_count} queued")

    def _update_video_selection_summary(self):
        if hasattr(self, "selection_count_value_label"):
            selection_count = len(self.selected_videos)
            self.selection_count_value_label.config(text=f"{selection_count} selected")

    def _update_gallery_overview(self, final_count=0, stitched_count=0, scenes_count=0):
        if hasattr(self, "gallery_final_count_label"):
            self.gallery_final_count_label.config(text=str(final_count))
        if hasattr(self, "gallery_stitched_count_label"):
            self.gallery_stitched_count_label.config(text=str(stitched_count))
        if hasattr(self, "gallery_scene_count_label"):
            self.gallery_scene_count_label.config(text=str(scenes_count))
        self._update_collapsible_section_meta("gallery_browser", f"{scenes_count} scenes • {stitched_count} stitched • {final_count} finals")

    def _update_music_config_summary(self, *_args):
        if hasattr(self, "music_duration_value_label"):
            self.music_duration_value_label.config(text=f"{self.music_duration_var.get()}s")
        if hasattr(self, "music_bpm_value_label"):
            self.music_bpm_value_label.config(text=str(self.music_bpm_var.get()))
        if hasattr(self, "music_key_value_label"):
            self.music_key_value_label.config(text=self.music_key_var.get().strip() or "Unset")
        self._update_collapsible_section_meta("music_lyrics", "Optional" if not getattr(self, "music_lyrics_text", None) or not self.music_lyrics_text.get("1.0", tk.END).strip() else "Has content")

    def _refresh_music_sidebar_state(self):
        if hasattr(self, "music_selected_clip_value_label"):
            selected_name = os.path.basename(self.selected_video_for_music) if self.selected_video_for_music else "No clip linked"
            self.music_selected_clip_value_label.config(text=selected_name)
        if hasattr(self, "music_audio_state_value_label"):
            audio_state = os.path.basename(self.current_generated_audio) if self.current_generated_audio and os.path.exists(self.current_generated_audio) else "No audio generated"
            self.music_audio_state_value_label.config(text=audio_state)
        if hasattr(self, "music_final_state_value_label"):
            final_state = os.path.basename(self.current_final_video) if getattr(self, "current_final_video", None) and os.path.exists(self.current_final_video) else "No final render"
            self.music_final_state_value_label.config(text=final_state)
        preview_meta = os.path.basename(self.selected_video_for_music) if self.selected_video_for_music else "Reference clip"
        self._update_collapsible_section_meta("music_preview", preview_meta)

    def _reset_selected_video_preview(self):
        self.selected_video_lbl.config(text="No video selected.\nGo to Video Generation tab\nand click 'Add Music'.")
        self.selected_video_thumb.config(image="")
        self.selected_video_thumb.image = None
        if hasattr(self, "selected_video_meta_label"):
            self.selected_video_meta_label.config(text="Select a stitched render from the gallery to lock music direction to a specific cut.")
        self._refresh_music_sidebar_state()

    def _set_selected_video_preview(self, video_path, thumb_path=None):
        self.selected_video_lbl.config(text=os.path.basename(video_path))
        if hasattr(self, "selected_video_meta_label"):
            modified_text = datetime.fromtimestamp(os.path.getmtime(video_path)).strftime("Updated %b %d, %Y %I:%M %p")
            self.selected_video_meta_label.config(text=modified_text)

        self.selected_video_thumb.config(image="")
        self.selected_video_thumb.image = None
        try:
            if thumb_path and os.path.exists(thumb_path):
                img = Image.open(thumb_path)
                img.thumbnail((260, 146))
                photo = ImageTk.PhotoImage(img)
                self.selected_video_thumb.config(image=photo)
                self.selected_video_thumb.image = photo
        except Exception as e:
            print(f"Error loading thumbnail for music tab: {e}")

        self._refresh_music_sidebar_state()

    def _apply_static_theme(self):
        self.root.configure(bg=self.colors["bg"])
        self.menubar.configure(bg=self.colors["surface"], fg=self.colors["text"], activebackground=self.colors["surface_soft"], activeforeground=self.colors["text"], bd=0)
        self.project_menu.configure(bg=self.colors["surface"], fg=self.colors["text"], activebackground=self.colors["surface_soft"], activeforeground=self.colors["text"], bd=0)

        for widget in [
            self.status_frame,
            self.video_tab,
            self.music_tab,
            self.left_frame,
            self.right_frame,
            self.video_header_frame,
            self.workflow_toolbar_card,
            self.video_config_row,
            self.video_prompt_queue_section["container"],
            self.video_prompt_queue_section["header"],
            self.video_settings_section["container"],
            self.video_settings_section["header"],
            self.settings_scroll_shell,
            self.settings_frame,
            self.video_preflight_section["container"],
            self.video_preflight_section["header"],
            self.preflight_frame,
            self.prompt_section_frame,
            self.prompt_header_frame,
            self.video_debug_section["container"],
            self.video_debug_section["header"],
            self.bottom_frame,
            self.post_process_frame,
            self.gallery_header_frame,
            self.gallery_section["container"],
            self.gallery_section["header"],
            self.gallery_shell_frame,
            self.gallery_inner_frame,
            self.music_left_frame,
            self.music_main_frame,
            self.music_header_frame,
            self.music_prompt_card,
            self.music_lyrics_section["container"],
            self.music_lyrics_section["header"],
            self.music_lyrics_card,
            self.music_controls_card,
            self.music_action_frame,
            self.music_preview_section["container"],
            self.music_preview_section["header"],
            self.music_sidebar_card,
            self.music_sidebar_summary_frame,
            self.music_preview_card,
            self.music_preview_media_frame,
            self.music_preview_actions_frame,
            self.music_preview_status_frame
        ]:
            self._style_panel(widget, self.colors["bg"] if widget in [self.video_tab, self.music_tab] else self.colors["surface"])

        self._style_panel(self.right_frame, self.colors["surface_alt"])
        self._style_panel(self.main_paned, self.colors["bg"])
        self._style_panel(self.settings_canvas, self.colors["surface"])
        self._style_panel(self.gallery_canvas, self.colors["surface_alt"])
        self._style_panel(self.gallery_inner_frame, self.colors["surface_alt"])
        self._style_panel(self.music_right_frame, self.colors["surface_alt"], border=True)
        self._style_panel(self.music_sidebar_card, self.colors["surface_alt"], border=True)
        self._style_panel(self.music_preview_card, self.colors["surface"], border=True)
        self._style_panel(self.settings_frame, self.colors["surface"])
        self._style_panel(self.preflight_frame, self.colors["surface"])
        self._style_panel(self.workflow_toolbar_card, self.colors["surface_alt"], border=True)
        self._style_panel(self.prompt_section_frame, self.colors["surface"])
        self._style_panel(self.gallery_shell_frame, self.colors["surface_alt"], border=True)

        for key in ["video_prompt_queue", "video_settings", "video_preflight", "video_debug", "gallery_browser", "music_lyrics", "music_preview"]:
            section = self.collapsible_sections[key]
            section_bg = self.colors["surface_alt"] if key in ["gallery_browser", "music_preview"] else self.colors["surface"]
            self._style_panel(section["container"], section_bg, border=True)
            self._style_panel(section["header"], section_bg)
            self._style_panel(section["body"], section_bg)
            self._style_label(section["title"], "section", section_bg)
            self._style_label(section["meta"], "muted", section_bg)
            self._style_button(section["toggle"], "ghost", compact=True)
            section["toggle"].configure(padx=6, pady=4)

        self.project_label.configure(bg=self.colors["surface_alt"], fg=self.colors["text"], font=self.fonts["body_strong"])
        self.status_frame.configure(bg=self.colors["surface_alt"], highlightbackground=self.colors["border"], highlightthickness=1)
        self.separator.configure(bg=self.colors["border"], height=1, bd=0, relief=tk.FLAT)

        self.notebook.configure(style="App.TNotebook")
        for child in self.notebook.winfo_children():
            child.configure(bg=self.colors["bg"])
        self.style.configure("App.TNotebook", background=self.colors["bg"])
        self.style.layout("App.TNotebook", self.style.layout("TNotebook"))
        self.style.layout("App.TNotebook.Tab", self.style.layout("TNotebook.Tab"))
        self.notebook.configure(style="App.TNotebook")
        self.style.configure("App.TNotebook.Tab")
        self.notebook.enable_traversal()
        self.notebook.tab(0)

        self._style_label(self.json_label, "muted", self.top_frame.cget("bg"))
        self._style_label(self.video_header_eyebrow_label, "muted", self.video_header_frame.cget("bg"))
        self.video_header_eyebrow_label.configure(font=self.fonts["micro"])
        self._style_label(self.video_header_title_label, "title", self.video_header_frame.cget("bg"))
        self._style_label(self.video_header_copy_label, "muted", self.video_header_frame.cget("bg"))
        self._style_label(self.prompt_section_eyebrow_label, "muted", self.prompt_header_frame.cget("bg"))
        self.prompt_section_eyebrow_label.configure(font=self.fonts["micro"])
        self._style_label(self.prompt_section_title_label, "section", self.prompt_header_frame.cget("bg"))
        self._style_label(self.prompt_section_copy_label, "muted", self.prompt_header_frame.cget("bg"))
        self._style_label(self.debug_prompt_label, "muted", self.video_debug_section["body"].cget("bg"))
        self._style_label(self.status_label, "muted", self.bottom_frame.cget("bg"))
        self._style_label(self.music_header_eyebrow_label, "muted", self.music_header_frame.cget("bg"))
        self.music_header_eyebrow_label.configure(font=self.fonts["micro"])
        self._style_label(self.music_header_title_label, "title", self.music_header_frame.cget("bg"))
        self._style_label(self.music_header_copy_label, "muted", self.music_header_frame.cget("bg"))
        self._style_label(self.music_tags_label, "section", self.music_prompt_card.cget("bg"))
        self._style_label(self.music_tags_hint_label, "muted", self.music_prompt_card.cget("bg"))
        self._style_label(self.music_lyrics_label, "section", self.music_lyrics_card.cget("bg"))
        self._style_label(self.music_lyrics_hint_label, "muted", self.music_lyrics_card.cget("bg"))
        self._style_label(self.music_controls_eyebrow_label, "muted", self.music_controls_card.cget("bg"))
        self.music_controls_eyebrow_label.configure(font=self.fonts["micro"])
        self._style_label(self.music_controls_title_label, "section", self.music_controls_card.cget("bg"))
        self._style_label(self.music_status_label, "muted", self.music_left_frame.cget("bg"))
        self._style_label(self.music_sidebar_eyebrow_label, "muted", self.music_right_frame.cget("bg"))
        self.music_sidebar_eyebrow_label.configure(font=self.fonts["micro"])
        self._style_label(self.music_sidebar_title_label, "title", self.music_right_frame.cget("bg"))
        self._style_label(self.music_sidebar_copy_label, "muted", self.music_right_frame.cget("bg"))
        self._style_label(self.gallery_title_label, "title", self.right_frame.cget("bg"))
        self._style_label(self.gallery_eyebrow_label, "muted", self.gallery_header_frame.cget("bg"))
        self.gallery_eyebrow_label.configure(font=self.fonts["micro"])
        self._style_label(self.gallery_copy_label, "muted", self.gallery_header_frame.cget("bg"))
        self._style_label(self.selected_video_header_label, "section", self.music_right_frame.cget("bg"))
        self._style_label(self.selected_video_lbl, "muted", self.music_right_frame.cget("bg"))
        self._style_label(self.selected_video_meta_label, "muted", self.music_right_frame.cget("bg"))

        for button, variant in [
            (self.load_btn, "secondary"),
            (self.open_debug_btn, "ghost"),
            (self.reset_video_profile_btn, "ghost"),
            (self.validate_video_btn, "primary"),
            (self.refresh_model_lists_btn, "secondary"),
            (self.add_prompt_btn, "secondary"),
            (self.run_queue_btn, "accent"),
            (self.stitch_btn, "primary"),
            (self.clear_sel_btn, "ghost"),
            (self.select_all_btn, "secondary"),
            (self.gen_music_btn, "accent"),
            (self.preview_music_btn, "secondary"),
            (self.preview_final_btn, "secondary"),
            (self.merge_music_btn, "primary")
        ]:
            self._style_button(button, variant)

        for compact_button, variant in [
            (self.load_btn, "secondary"),
            (self.open_debug_btn, "ghost"),
            (self.reset_video_profile_btn, "ghost"),
            (self.validate_video_btn, "primary"),
            (self.refresh_model_lists_btn, "secondary"),
            (self.add_prompt_btn, "secondary"),
            (self.run_queue_btn, "accent"),
            (self.stitch_btn, "primary"),
            (self.clear_sel_btn, "ghost"),
            (self.select_all_btn, "secondary")
        ]:
            self._style_button(compact_button, variant, compact=True)

        for checkbutton in [self.strip_audio_cb, self.video_output_include_project_cb]:
            self._style_checkbutton(checkbutton)

        for entry_widget in [
            self.music_tags_text,
            self.music_lyrics_text,
            self.video_preflight_text
        ]:
            self._style_text_input(entry_widget, multiline=True)

        for combobox in [self.video_profile_combo, self.video_checkpoint_combo, self.video_text_encoder_combo, self.video_lora_combo, self.video_upscaler_combo]:
            combobox.configure(style="TCombobox")

        self._theme_existing_entries(self.left_frame)
        self._theme_existing_entries(self.music_left_frame)
        self._update_prompt_collection_summary()
        self._update_video_selection_summary()
        self._update_music_config_summary()
        self._refresh_music_sidebar_state()

    def _theme_existing_entries(self, parent):
        for child in parent.winfo_children():
            if isinstance(child, tk.Entry):
                self._style_text_input(child)
            elif isinstance(child, tk.Text):
                self._style_text_input(child, multiline=True)
            elif isinstance(child, tk.LabelFrame):
                self._style_labelframe(child)
            elif isinstance(child, tk.Label):
                self._style_label(child)
            elif isinstance(child, tk.Checkbutton):
                self._style_checkbutton(child)
            elif isinstance(child, tk.Frame):
                if child not in [self.status_frame, self.right_frame, self.gallery_inner_frame, self.music_right_frame]:
                    self._style_panel(child, child.master.cget("bg") if hasattr(child.master, "cget") else self.colors["surface"])
            if child.winfo_children():
                self._theme_existing_entries(child)

    def set_project(self, project_dir):
        # Save current project state before switching
        if self.current_project_dir:
            self.save_project_state()
            
        self.current_project_dir = project_dir
        
        # Setup project subdirectories
        self.scenes_dir = os.path.join(self.current_project_dir, "generated_scenes")
        self.stitched_dir = os.path.join(self.current_project_dir, "stitched_videos")
        self.thumbs_dir = os.path.join(self.current_project_dir, "thumbnails")
        self.audio_dir = os.path.join(self.current_project_dir, "generated_audio")
        self.final_mv_dir = os.path.join(self.current_project_dir, "final_music_videos")
        self.debug_dir = os.path.join(self.current_project_dir, "debug")
        
        for d in [self.scenes_dir, self.stitched_dir, self.thumbs_dir, self.audio_dir, self.final_mv_dir, self.debug_dir]:
            os.makedirs(d, exist_ok=True)

        self.debug_log_file = os.path.join(self.debug_dir, "wrapper_debug.log")
        self.log_debug("PROJECT_SET", project_dir=self.current_project_dir)
            
        self.project_label.config(text=f"Current Project: {os.path.basename(self.current_project_dir)}")
        self.load_project_state()
        self.refresh_gallery()

    def create_new_project(self):
        project_name = simpledialog.askstring("New Project", "Enter project name:", parent=self.root)
        if project_name:
            # Sanitize folder name
            safe_name = "".join([c for c in project_name if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).rstrip()
            if not safe_name:
                safe_name = f"Project_{int(time.time())}"
                
            new_dir = os.path.join(self.base_output_dir, safe_name)
            if os.path.exists(new_dir):
                messagebox.showwarning("Warning", "A project with this name already exists.")
                return
                
            self.set_project(new_dir)
            
            # Clear prompts and music settings for new project
            self.clear_ui_fields()
            
            self.save_global_settings()
            self.save_project_state()

    def open_project(self):
        project_dir = filedialog.askdirectory(
            initialdir=os.path.abspath(self.base_output_dir),
            title="Select Project Folder"
        )
        if project_dir:
            # Verify it's a valid project folder (or at least inside outputs)
            if os.path.commonpath([os.path.abspath(project_dir), os.path.abspath(self.base_output_dir)]) == os.path.abspath(self.base_output_dir):
                self.set_project(project_dir)
                self.save_global_settings()
            else:
                messagebox.showerror("Error", "Please select a folder inside the 'outputs' directory.")

    def rename_current_project(self):
        if not self.current_project_dir:
            return
            
        current_name = os.path.basename(self.current_project_dir)
        new_name = simpledialog.askstring("Rename Project", "Enter new project name:", initialvalue=current_name, parent=self.root)
        
        if new_name and new_name != current_name:
            # Sanitize folder name
            safe_name = "".join([c for c in new_name if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).rstrip()
            if not safe_name:
                messagebox.showwarning("Warning", "Invalid project name.")
                return
                
            new_dir = os.path.join(self.base_output_dir, safe_name)
            if os.path.exists(new_dir):
                messagebox.showwarning("Warning", "A project with this name already exists.")
                return
                
            try:
                os.rename(self.current_project_dir, new_dir)
                self.current_project_dir = new_dir # Update path without triggering save of old path
                self.set_project(new_dir)
                self.save_global_settings()
                messagebox.showinfo("Success", f"Project renamed to '{safe_name}'.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to rename project:\n{e}")

    def launch_comfyui(self):
        # Ping port 8188 first
        try:
            req = urllib.request.Request("http://127.0.0.1:8188/system_stats")
            urllib.request.urlopen(req, timeout=1)
            self.update_status("ComfyUI already running on port 8188.", "blue")
            return  # Skip launch
        except:
            pass  # Server not found, proceed to launch

        bat_path = r"D:\ComfyUI\run_ltx2_queue_manager.bat"
        if os.path.exists(bat_path):
            self.update_status("Launching ComfyUI...", "blue")
            try:
                # Launch in a new console window so it doesn't block our UI
                self.comfyui_process = subprocess.Popen(
                    bat_path, 
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    cwd=os.path.dirname(bat_path)
                )
                # Give it some time to start up
                self.root.after(5000, lambda: self.update_status("ComfyUI Launched. Waiting for connection...", "blue"))
            except Exception as e:
                self.update_status(f"Error launching ComfyUI: {e}", "red")
        else:
            self.update_status("ComfyUI bat file not found.", "red")

    def setup_ui(self):
        # Top Menu Bar
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        self.project_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Project", menu=self.project_menu)
        self.project_menu.add_command(label="New Project", command=self.create_new_project)
        self.project_menu.add_command(label="Open Project", command=self.open_project)
        self.project_menu.add_command(label="Rename Current Project", command=self.rename_current_project)
        self.project_menu.add_separator()
        self.project_menu.add_command(label="Exit", command=self.on_closing)
        
        # Project Status Bar
        self.status_frame = tk.Frame(self.root, pady=8)
        self.status_frame.pack(fill=tk.X)
        self.status_frame.grid_columnconfigure(0, weight=1)
        self.project_label = tk.Label(self.status_frame, text="Current Project: None")
        self.project_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # Create Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Video Generation
        self.video_tab = tk.Frame(self.notebook)
        self.notebook.add(self.video_tab, text="Video Generation")
        
        # Tab 2: Music Studio
        self.music_tab = tk.Frame(self.notebook)
        self.notebook.add(self.music_tab, text="Music Studio")
        
        # --- Video Tab Content ---
        # Main container
        self.main_paned = tk.PanedWindow(self.video_tab, orient=tk.HORIZONTAL, sashwidth=10, bd=0, relief=tk.FLAT)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=14, pady=(6, 14))
        
        # Left Frame (Prompts & Controls)
        self.left_frame = tk.Frame(self.main_paned, padx=0, pady=0)
        self.main_paned.add(self.left_frame, minsize=560)
        
        # Right Frame (Gallery)
        self.right_frame = tk.Frame(self.main_paned, padx=0, pady=0)
        self.main_paned.add(self.right_frame, minsize=320)
        
        # --- Left Frame Content ---
        self.video_header_frame = tk.Frame(self.left_frame, padx=18, pady=10)
        self.video_header_frame.pack(side=tk.TOP, fill=tk.X)

        self.video_header_text_frame = tk.Frame(self.video_header_frame)
        self.video_header_text_frame.pack(side=tk.TOP, fill=tk.X, expand=True)
        header_intro = self._create_section_intro(
            self.video_header_text_frame,
            "Video Studio",
            "Build scenes, queue renders, and manage delivery",
            "Keep workflow control, prompting, and output review in one screen."
        )
        self.video_header_eyebrow_label, self.video_header_title_label, self.video_header_copy_label = header_intro

        self.video_header_stats_frame = tk.Frame(self.video_header_frame)
        self.video_header_stats_frame.pack(side=tk.TOP, fill=tk.X, pady=(12, 0))
        _, self.prompt_count_value_label = self._create_metric_chip(self.video_header_stats_frame, "Queue", "0 prompts")
        self.prompt_count_value_label.master.pack(side=tk.LEFT, fill=tk.X, expand=True)
        _, self.selection_count_value_label = self._create_metric_chip(self.video_header_stats_frame, "Stitch", "0 selected")
        self.selection_count_value_label.master.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        # Top Bar
        self.workflow_toolbar_card = tk.Frame(self.left_frame, padx=18, pady=10)
        self.workflow_toolbar_card.pack(side=tk.TOP, fill=tk.X, padx=18, pady=(0, 10))

        self.top_frame = tk.Frame(self.workflow_toolbar_card)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)
        self.top_frame.grid_columnconfigure(2, weight=1)
        
        self.load_btn = tk.Button(self.top_frame, text="Load Workflow JSON", command=self.load_json_dialog)
        self.load_btn.grid(row=0, column=0, sticky="w")

        self.open_debug_btn = tk.Button(self.top_frame, text="Open Debug Log", command=self.open_debug_log)
        self.open_debug_btn.grid(row=0, column=1, sticky="w", padx=(8, 0))
        
        self.json_label = tk.Label(self.workflow_toolbar_card, text="No JSON loaded", anchor="w", justify=tk.LEFT)
        self.json_label.pack(side=tk.TOP, fill=tk.X, expand=True, pady=(6, 0))

        self.video_config_row = tk.Frame(self.left_frame)
        self.video_config_row.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=18, pady=(0, 12))

        self.video_prompt_queue_section = self._create_collapsible_section(
            self.video_config_row,
            "video_prompt_queue",
            "Prompt Queue",
            meta_text="0 queued",
            is_open=True,
            body_expand=True,
            group="video_left_support"
        )
        self.video_prompt_queue_section["container"].pack(fill=tk.BOTH, expand=True)

        self.video_settings_section = self._create_collapsible_section(
            self.video_config_row,
            "video_settings",
            "Workflow Settings",
            meta_text="Profile, models, output",
            is_open=False,
            body_expand=True,
            group="video_left_support"
        )
        self.video_settings_section["container"].pack(fill=tk.X)

        self.settings_scroll_shell = tk.Frame(self.video_settings_section["body"])
        self.settings_scroll_shell.pack(fill=tk.BOTH, expand=True)

        self.settings_canvas = tk.Canvas(self.settings_scroll_shell, bd=0, highlightthickness=0, height=300)
        self.settings_scrollbar = tk.Scrollbar(self.settings_scroll_shell, orient="vertical", command=self.settings_canvas.yview)
        self.settings_frame = tk.Frame(self.settings_canvas, padx=6, pady=6)
        self.settings_window_id = self.settings_canvas.create_window((0, 0), window=self.settings_frame, anchor="nw")
        self.settings_canvas.configure(yscrollcommand=self.settings_scrollbar.set)

        self.settings_frame.bind(
            "<Configure>",
            lambda _event: self.settings_canvas.configure(scrollregion=self.settings_canvas.bbox("all"))
        )
        self.settings_canvas.bind(
            "<Configure>",
            lambda event: self.settings_canvas.itemconfig(self.settings_window_id, width=event.width)
        )

        self.settings_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.settings_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.video_profile_key_to_label = {
            key: profile["label"] for key, profile in VIDEO_WORKFLOW_PROFILES.items()
        }
        self.video_profile_label_to_key = {
            label: key for key, label in self.video_profile_key_to_label.items()
        }
        self.video_profile_var = tk.StringVar(value=self.video_profile_key_to_label[DEFAULT_VIDEO_PROFILE])
        self.video_negative_prompt_var = tk.StringVar()
        self.video_width_var = tk.StringVar()
        self.video_height_var = tk.StringVar()
        self.video_fps_var = tk.StringVar()
        self.video_length_var = tk.StringVar()
        self.video_checkpoint_var = tk.StringVar()
        self.video_text_encoder_var = tk.StringVar()
        self.video_lora_var = tk.StringVar()
        self.video_upscaler_var = tk.StringVar()
        self.video_output_subfolder_var = tk.StringVar(value="video")
        self.video_output_base_name_var = tk.StringVar(value="LTX2_3_Scene")
        self.video_output_include_project_var = tk.BooleanVar(value=False)

        settings_header_frame = tk.Frame(self.settings_frame)
        settings_header_frame.pack(fill=tk.X, pady=(0, 4))
        settings_header_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        workflow_group = tk.Frame(settings_header_frame)
        workflow_group.grid(row=0, column=0, columnspan=2, sticky="ew", padx=(0, 8))

        self.workflow_label = tk.Label(workflow_group, text="Workflow")
        self.workflow_label.pack(anchor="w")
        self.video_profile_combo = ttk.Combobox(
            workflow_group,
            textvariable=self.video_profile_var,
            values=list(self.video_profile_key_to_label.values()),
            state="readonly",
            width=24
        )
        self.video_profile_combo.pack(fill=tk.X, pady=(2, 0))
        self.video_profile_combo.bind("<<ComboboxSelected>>", self.on_video_profile_changed)

        negative_prompt_frame = tk.Frame(settings_header_frame)
        negative_prompt_frame.grid(row=0, column=2, columnspan=2, sticky="ew")
        negative_prompt_frame.grid_columnconfigure(0, weight=1)
        self.negative_prompt_label = tk.Label(negative_prompt_frame, text="Negative Prompt")
        self.negative_prompt_label.grid(row=0, column=0, sticky="w")
        self.video_negative_prompt_entry = tk.Entry(negative_prompt_frame, textvariable=self.video_negative_prompt_var)
        self.video_negative_prompt_entry.grid(row=1, column=0, sticky="ew", pady=(2, 0))

        numeric_settings_frame = tk.Frame(self.settings_frame)
        numeric_settings_frame.pack(fill=tk.X, pady=(0, 4))
        numeric_settings_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        for index, (label_text, variable) in enumerate([
            ("Width", self.video_width_var),
            ("Height", self.video_height_var),
            ("FPS", self.video_fps_var),
            ("Length", self.video_length_var)
        ]):
            field_frame = tk.Frame(numeric_settings_frame)
            field_frame.grid(row=0, column=index, sticky="ew", padx=(0 if index == 0 else 8, 0))
            tk.Label(field_frame, text=label_text).pack(anchor="w")
            tk.Entry(field_frame, textvariable=variable, width=10).pack(fill=tk.X, pady=(2, 0))

        model_rows_frame = tk.Frame(self.settings_frame)
        model_rows_frame.pack(fill=tk.X, pady=(0, 4))
        model_rows_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        tk.Label(model_rows_frame, text="Checkpoint").grid(row=0, column=0, sticky="w")
        tk.Label(model_rows_frame, text="Text Encoder").grid(row=0, column=1, sticky="w", padx=(8, 0))
        tk.Label(model_rows_frame, text="LoRA").grid(row=0, column=2, sticky="w", padx=(8, 0))
        tk.Label(model_rows_frame, text="Upscaler").grid(row=0, column=3, sticky="w", padx=(8, 0))

        self.video_checkpoint_combo = ttk.Combobox(model_rows_frame, textvariable=self.video_checkpoint_var)
        self.video_checkpoint_combo.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        self.video_text_encoder_combo = ttk.Combobox(model_rows_frame, textvariable=self.video_text_encoder_var)
        self.video_text_encoder_combo.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(2, 0))
        self.video_lora_combo = ttk.Combobox(model_rows_frame, textvariable=self.video_lora_var)
        self.video_lora_combo.grid(row=1, column=2, sticky="ew", padx=(8, 0), pady=(2, 0))
        self.video_upscaler_combo = ttk.Combobox(model_rows_frame, textvariable=self.video_upscaler_var)
        self.video_upscaler_combo.grid(row=1, column=3, sticky="ew", padx=(8, 0), pady=(2, 0))

        output_frame = tk.Frame(self.settings_frame)
        output_frame.pack(fill=tk.X, pady=(0, 4))
        output_frame.grid_columnconfigure((0, 1, 2), weight=1)

        tk.Label(output_frame, text="Output Folder").grid(row=0, column=0, sticky="w")
        tk.Label(output_frame, text="Base Name").grid(row=0, column=1, sticky="w", padx=(8, 0))
        tk.Label(output_frame, text="Prefix").grid(row=0, column=2, sticky="w", padx=(8, 0))

        output_folder_frame = tk.Frame(output_frame)
        output_folder_frame.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        tk.Entry(output_folder_frame, textvariable=self.video_output_subfolder_var).pack(fill=tk.X)

        output_base_frame = tk.Frame(output_frame)
        output_base_frame.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(2, 0))
        tk.Entry(output_base_frame, textvariable=self.video_output_base_name_var).pack(fill=tk.X)

        output_toggle_frame = tk.Frame(output_frame)
        output_toggle_frame.grid(row=1, column=2, sticky="ew", padx=(8, 0), pady=(2, 0))
        self.video_output_include_project_cb = tk.Checkbutton(
            output_toggle_frame,
            text="Prefix Project Name",
            variable=self.video_output_include_project_var
        )
        self.video_output_include_project_cb.pack(anchor="w")

        settings_actions_frame = tk.Frame(self.settings_frame)
        settings_actions_frame.pack(fill=tk.X)
        settings_actions_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.reset_video_profile_btn = tk.Button(
            settings_actions_frame,
            text="Reset Defaults",
            command=self.reset_video_profile_defaults
        )
        self.reset_video_profile_btn.grid(row=0, column=0, sticky="ew")

        self.validate_video_btn = tk.Button(
            settings_actions_frame,
            text="Validate",
            command=self.validate_video_setup
        )
        self.validate_video_btn.grid(row=0, column=1, sticky="ew", padx=6)

        self.refresh_model_lists_btn = tk.Button(
            settings_actions_frame,
            text="Refresh Models",
            command=self.refresh_video_model_choices
        )
        self.refresh_model_lists_btn.grid(row=0, column=2, sticky="ew")

        self.refresh_video_model_choices(initial_load=True)

        self.video_preflight_section = self._create_collapsible_section(
            self.video_config_row,
            "video_preflight",
            "Preflight",
            meta_text="Not validated",
            is_open=False,
            body_expand=True,
            group="video_left_support"
        )
        self.video_preflight_section["container"].pack(fill=tk.X, pady=(10, 0))

        self.preflight_frame = tk.Frame(self.video_preflight_section["body"], padx=8, pady=5)
        self.preflight_frame.pack(fill=tk.BOTH, expand=True)

        self.video_preflight_status_label = tk.Label(self.preflight_frame, text="Status: Not validated", fg="gray", anchor="w")
        self.video_preflight_status_label.pack(fill=tk.X, pady=(0, 4))

        self.video_preflight_text = tk.Text(self.preflight_frame, height=3, wrap="word")
        self.video_preflight_text.pack(fill=tk.BOTH, expand=True)
        self.video_preflight_text.configure(state=tk.DISABLED)
        self._set_video_preflight_summary("Validation not run for current settings.", "Not validated", "gray")
        
        self.prompt_section_frame = tk.Frame(self.video_prompt_queue_section["body"], padx=18, pady=16)
        self.prompt_section_frame.pack(fill=tk.BOTH, expand=True)

        self.prompt_header_frame = tk.Frame(self.prompt_section_frame)
        self.prompt_header_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        prompt_intro = self._create_section_intro(
            self.prompt_header_frame,
            "Prompt Queue",
            "Draft shots and send them in sequence",
            "Each card is an individual shot. Keep fast one-off renders here, then promote the best clips to the stitch and music pipeline from the gallery."
        )
        self.prompt_section_eyebrow_label, self.prompt_section_title_label, self.prompt_section_copy_label = prompt_intro

        self.canvas_shell = tk.Frame(self.prompt_section_frame)
        self.canvas_shell.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self._style_panel(self.canvas_shell, self.colors["surface"], border=False)

        # Scrollable Frame for Prompts
        self.canvas = tk.Canvas(self.canvas_shell, bd=0, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.canvas_shell, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.canvas_window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        def configure_scrollable_frame(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
        self.scrollable_frame.bind("<Configure>", configure_scrollable_frame)
        
        def configure_canvas(event):
            self.canvas.itemconfig(self.canvas_window_id, width=event.width)
            
        self.canvas.bind("<Configure>", configure_canvas)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(0, 8))
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.video_debug_section = self._create_collapsible_section(
            self.video_config_row,
            "video_debug",
            "Diagnostics",
            meta_text="Queued prompt preview",
            is_open=False,
            body_expand=True,
            group="video_left_support"
        )
        self.video_debug_section["container"].pack(fill=tk.X)

        self.debug_prompt_label = tk.Label(
            self.video_debug_section["body"],
            text="Debug: Queued Prompt: (none)",
            fg="gray",
            anchor="w",
            justify=tk.LEFT,
            wraplength=520,
            font=self.fonts["small"]
        )
        self.debug_prompt_label.pack(side=tk.TOP, fill=tk.X)

        self._update_video_workspace_balance()

        self.left_frame.bind("<Configure>", self._on_left_panel_resize)
        
        # Bottom Bar
        self.bottom_frame = tk.Frame(self.left_frame, padx=18, pady=10)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=18, pady=(0, 12))
        self.bottom_frame.grid_columnconfigure(1, weight=1)
        self.bottom_actions_frame = tk.Frame(self.bottom_frame)
        self.bottom_actions_frame.grid(row=0, column=0, sticky="w")
        
        self.add_prompt_btn = tk.Button(self.bottom_actions_frame, text="Add Prompt", command=self.add_prompt_entry)
        self.add_prompt_btn.pack(side=tk.LEFT)
        
        self.run_queue_btn = tk.Button(self.bottom_actions_frame, text="Run Queue", command=self.start_queue)
        self.run_queue_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        self.status_label = tk.Label(self.bottom_frame, text="Status: Idle", fg="blue")
        self.status_label.grid(row=0, column=1, sticky="e", padx=(12, 0))
        
        # Separator
        self.separator = tk.Frame(self.left_frame, height=2, bd=1, relief=tk.SUNKEN)
        self.separator.pack(side=tk.BOTTOM, fill=tk.X, padx=18, pady=4)
        
        # Post Process Frame
        self.post_process_frame = tk.Frame(self.left_frame, padx=18, pady=10)
        self.post_process_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=18, pady=(0, 10))
        self.post_process_frame.grid_columnconfigure(1, weight=1)
        
        self.strip_audio_var = tk.BooleanVar(value=True)
        self.strip_audio_cb = tk.Checkbutton(self.post_process_frame, text="Strip Audio (Mute Final Video)", variable=self.strip_audio_var)
        self.strip_audio_cb.grid(row=0, column=0, sticky="w")

        self.post_process_actions_frame = tk.Frame(self.post_process_frame)
        self.post_process_actions_frame.grid(row=0, column=1, sticky="e")
        
        self.stitch_btn = tk.Button(self.post_process_actions_frame, text="Stitch Selected Videos", command=self.stitch_selected_videos)
        self.stitch_btn.pack(side=tk.RIGHT)
        
        self.clear_sel_btn = tk.Button(self.post_process_actions_frame, text="Clear Selection", command=self.clear_selection)
        self.clear_sel_btn.pack(side=tk.RIGHT, padx=5)
        
        self.select_all_btn = tk.Button(self.post_process_actions_frame, text="Select All", command=self.select_all_videos)
        self.select_all_btn.pack(side=tk.RIGHT, padx=5)
        
        # --- Right Frame Content (Gallery) ---
        self.gallery_header_frame = tk.Frame(self.right_frame, padx=18, pady=14)
        self.gallery_header_frame.pack(side=tk.TOP, fill=tk.X)

        self.gallery_eyebrow_label = tk.Label(self.gallery_header_frame, text="Media Browser")
        self.gallery_eyebrow_label.pack(anchor="w")
        self.gallery_title_label = tk.Label(self.right_frame, text="Video Gallery")
        self.gallery_title_label.pack(in_=self.gallery_header_frame, anchor="w", pady=(4, 0))
        self.gallery_copy_label = tk.Label(
            self.gallery_header_frame,
            text="Review generated scenes, stitched renders, and finished music videos without leaving the queue manager.",
            anchor="w",
            justify=tk.LEFT,
            wraplength=340
        )
        self.gallery_copy_label.pack(anchor="w", pady=(6, 14), fill=tk.X)

        self.gallery_stats_frame = tk.Frame(self.gallery_header_frame)
        self.gallery_stats_frame.pack(fill=tk.X)
        _, self.gallery_scene_count_label = self._create_metric_chip(self.gallery_stats_frame, "Scenes", "0")
        self.gallery_scene_count_label.master.pack(side=tk.LEFT, fill=tk.X, expand=True)
        _, self.gallery_stitched_count_label = self._create_metric_chip(self.gallery_stats_frame, "Stitched", "0")
        self.gallery_stitched_count_label.master.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        _, self.gallery_final_count_label = self._create_metric_chip(self.gallery_stats_frame, "Finals", "0")
        self.gallery_final_count_label.master.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.gallery_section = self._create_collapsible_section(
            self.right_frame,
            "gallery_browser",
            "Gallery Browser",
            meta_text="Collapsed",
            is_open=False,
            body_expand=True,
            body_background=self.colors["surface_alt"]
        )
        self.gallery_section["container"].pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=18, pady=(0, 18))

        self.gallery_shell_frame = tk.Frame(self.gallery_section["body"], padx=0, pady=0)
        self.gallery_shell_frame.pack(fill=tk.BOTH, expand=True)

        self.gallery_canvas = tk.Canvas(self.gallery_shell_frame, bd=0, highlightthickness=0)
        self.gallery_scrollbar = tk.Scrollbar(self.gallery_shell_frame, orient="vertical", command=self.gallery_canvas.yview)
        self.gallery_inner_frame = tk.Frame(self.gallery_canvas)
        
        self.gallery_window_id = self.gallery_canvas.create_window((0, 0), window=self.gallery_inner_frame, anchor="nw")
        self.gallery_canvas.configure(yscrollcommand=self.gallery_scrollbar.set)
        
        def configure_gallery_inner_frame(event):
            self.gallery_canvas.configure(scrollregion=self.gallery_canvas.bbox("all"))
            
        self.gallery_inner_frame.bind("<Configure>", configure_gallery_inner_frame)
        
        def configure_gallery_canvas(event):
            self.gallery_canvas.itemconfig(self.gallery_window_id, width=event.width)
            
        self.gallery_canvas.bind("<Configure>", configure_gallery_canvas)
        
        self.gallery_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.gallery_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Global mousewheel scrolling
        def _on_mousewheel(event):
            widget = event.widget.winfo_containing(event.x_root, event.y_root)
            if widget:
                # Go up the hierarchy to find a canvas
                while widget:
                    if isinstance(widget, tk.Canvas):
                        # Only scroll if the canvas has a scrollbar attached and is scrollable
                        if widget.yview() != (0.0, 1.0):
                            widget.yview_scroll(int(-1*(event.delta/120)), "units")
                        break
                    if widget == self.root:
                        break
                    widget = widget.master
                    
        self.root.bind_all("<MouseWheel>", _on_mousewheel)
        self.root.bind("<Configure>", self._on_window_resize)
        self.root.after(0, self._finalize_initial_layout)

        # --- Music Tab Content ---
        self.setup_music_tab()
        self._reflow_video_left_panel()
        self._apply_static_theme()

    def _finalize_initial_layout(self):
        try:
            total_width = self.main_paned.winfo_width()
            if total_width > 0:
                self.main_paned.sash_place(0, int(total_width * 0.6), 0)
        except Exception:
            pass
        self._apply_responsive_section_defaults()
        self._protect_primary_workspaces()
        self._refresh_responsive_copy()

    def _on_left_panel_resize(self, event):
        available_width = max(320, event.width - 40)
        self.debug_prompt_label.config(wraplength=available_width)

    def setup_music_tab(self):
        # Left side: Controls
        self.music_left_frame = tk.Frame(self.music_tab, padx=0, pady=0)
        self.music_left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(18, 10), pady=18)
        
        # Right side: Selected Video Preview
        self.music_right_frame = tk.Frame(self.music_tab, padx=0, pady=0, width=360)
        self.music_right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 18), pady=18)
        self.music_right_frame.pack_propagate(False)

        self.music_main_frame = tk.Frame(self.music_left_frame, padx=18, pady=14)
        self.music_main_frame.pack(fill=tk.BOTH, expand=True)

        self.music_header_frame = tk.Frame(self.music_main_frame)
        self.music_header_frame.pack(fill=tk.X)
        music_intro = self._create_section_intro(
            self.music_header_frame,
            "Music Studio",
            "Shape a score around the selected cut",
            "Use tags for direction, lyrics for narrative, and then lock timing with duration, BPM, and key before generating audio and approving the final merge."
        )
        self.music_header_eyebrow_label, self.music_header_title_label, self.music_header_copy_label = music_intro

        self.music_header_stats_frame = tk.Frame(self.music_header_frame)
        self.music_header_stats_frame.pack(fill=tk.X, pady=(14, 0))
        self.music_header_stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        _, self.music_duration_value_label = self._create_metric_chip(self.music_header_stats_frame, "Duration", "120s")
        self.music_duration_value_label.master.pack(side=tk.LEFT, fill=tk.X, expand=True)
        _, self.music_bpm_value_label = self._create_metric_chip(self.music_header_stats_frame, "BPM", "120")
        self.music_bpm_value_label.master.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        _, self.music_key_value_label = self._create_metric_chip(self.music_header_stats_frame, "Key", "C major")
        self.music_key_value_label.master.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.music_prompt_card = tk.Frame(self.music_main_frame, padx=16, pady=16)
        self.music_prompt_card.pack(fill=tk.X, pady=(18, 12))

        self.music_tags_label = tk.Label(self.music_prompt_card, text="Style Direction")
        self.music_tags_label.pack(anchor="w")
        self.music_tags_hint_label = tk.Label(self.music_prompt_card, text="Describe genre, texture, emotion, and instrumentation.", anchor="w", justify=tk.LEFT)
        self.music_tags_hint_label.pack(anchor="w", pady=(4, 10), fill=tk.X)
        self.music_tags_text = tk.Text(self.music_prompt_card, height=5, width=60)
        self.music_tags_text.pack(fill=tk.X)
        
        self.music_lyrics_section = self._create_collapsible_section(
            self.music_main_frame,
            "music_lyrics",
            "Lyrics / Vocal Direction",
            meta_text="Optional",
            is_open=False,
            body_expand=True
        )
        self.music_lyrics_section["container"].pack(fill=tk.X, pady=(0, 12))

        self.music_lyrics_card = tk.Frame(self.music_lyrics_section["body"], padx=16, pady=16)
        self.music_lyrics_card.pack(fill=tk.BOTH, expand=True)
        
        self.music_lyrics_label = tk.Label(self.music_lyrics_card, text="Lyrics / Vocal Direction")
        self.music_lyrics_label.pack(anchor="w")
        self.music_lyrics_hint_label = tk.Label(self.music_lyrics_card, text="Optional. Use this for hooks, spoken phrasing, or narrative structure.", anchor="w", justify=tk.LEFT)
        self.music_lyrics_hint_label.pack(anchor="w", pady=(4, 10), fill=tk.X)
        self.music_lyrics_text = tk.Text(self.music_lyrics_card, height=12, width=60)
        self.music_lyrics_text.pack(fill=tk.BOTH, expand=True)
        self.music_lyrics_text.bind("<KeyRelease>", lambda _event: self._update_collapsible_section_meta("music_lyrics", "Has content" if self.music_lyrics_text.get("1.0", tk.END).strip() else "Optional"))
        
        self.music_controls_card = tk.Frame(self.music_main_frame, padx=16, pady=16)
        self.music_controls_card.pack(fill=tk.X)
        self.music_controls_eyebrow_label = tk.Label(self.music_controls_card, text="Playback Parameters")
        self.music_controls_eyebrow_label.pack(anchor="w")
        self.music_controls_title_label = tk.Label(self.music_controls_card, text="Time, pulse, and delivery")
        self.music_controls_title_label.pack(anchor="w", pady=(4, 14))
        
        # Settings Frame
        self.music_settings_frame = tk.Frame(self.music_controls_card)
        self.music_settings_frame.pack(fill=tk.X)
        self.music_settings_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        duration_frame = tk.Frame(self.music_settings_frame)
        duration_frame.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        duration_label = tk.Label(duration_frame, text="Duration (s)")
        duration_label.pack(anchor="w")
        self.music_duration_var = tk.IntVar(value=120)
        self.music_duration_var.trace_add("write", self._update_music_config_summary)
        self.music_duration_entry = tk.Entry(duration_frame, textvariable=self.music_duration_var, width=8)
        self.music_duration_entry.pack(fill=tk.X, pady=(6, 0))
        
        bpm_frame = tk.Frame(self.music_settings_frame)
        bpm_frame.grid(row=0, column=1, sticky="ew", padx=8)
        bpm_label = tk.Label(bpm_frame, text="BPM")
        bpm_label.pack(anchor="w")
        self.music_bpm_var = tk.IntVar(value=120)
        self.music_bpm_var.trace_add("write", self._update_music_config_summary)
        self.music_bpm_entry = tk.Entry(bpm_frame, textvariable=self.music_bpm_var, width=8)
        self.music_bpm_entry.pack(fill=tk.X, pady=(6, 0))
        
        key_frame = tk.Frame(self.music_settings_frame)
        key_frame.grid(row=0, column=2, sticky="ew", padx=(8, 0))
        key_label = tk.Label(key_frame, text="Key / Scale")
        key_label.pack(anchor="w")
        self.music_key_var = tk.StringVar(value="C major")
        self.music_key_var.trace_add("write", self._update_music_config_summary)
        self.music_key_entry = tk.Entry(key_frame, textvariable=self.music_key_var, width=15)
        self.music_key_entry.pack(fill=tk.X, pady=(6, 0))
        
        # Action Buttons
        self.music_action_frame = tk.Frame(self.music_controls_card)
        self.music_action_frame.pack(fill=tk.X, pady=(16, 0))
        self.music_action_frame.grid_columnconfigure((0, 1), weight=1)
        self.music_primary_actions_frame = tk.Frame(self.music_action_frame)
        self.music_primary_actions_frame.grid(row=0, column=0, sticky="w")
        self.music_secondary_actions_frame = tk.Frame(self.music_action_frame)
        self.music_secondary_actions_frame.grid(row=0, column=1, sticky="e")
        
        self.gen_music_btn = tk.Button(self.music_primary_actions_frame, text="Generate Music", command=self.generate_music)
        self.gen_music_btn.pack(side=tk.LEFT)
        
        self.preview_music_btn = tk.Button(self.music_primary_actions_frame, text="Preview Audio", command=self.preview_audio, state=tk.DISABLED)
        self.preview_music_btn.pack(side=tk.LEFT, padx=(8, 0))
        
        self.preview_final_btn = tk.Button(self.music_secondary_actions_frame, text="Preview Final Video", command=self.preview_final_video, state=tk.DISABLED)
        self.preview_final_btn.pack(side=tk.RIGHT)
        
        self.merge_music_btn = tk.Button(self.music_secondary_actions_frame, text="Approve & Merge with Video", command=self.merge_audio_video, state=tk.DISABLED)
        self.merge_music_btn.pack(side=tk.RIGHT, padx=(0, 8))
        
        self.music_status_label = tk.Label(self.music_controls_card, text="Status: Idle", fg="blue")
        self.music_status_label.pack(anchor="w", pady=(14, 0))
        
        # --- Selected Video Info ---
        self.music_sidebar_eyebrow_label = tk.Label(self.music_right_frame, text="Linked Media")
        self.music_sidebar_eyebrow_label.pack(anchor="w")
        self.music_sidebar_title_label = tk.Label(self.music_right_frame, text="Selected Video")
        self.music_sidebar_title_label.pack(anchor="w", pady=(4, 0))
        self.music_sidebar_copy_label = tk.Label(
            self.music_right_frame,
            text="This panel tracks the source clip, generated audio, and final export state for the current music pass.",
            anchor="w",
            justify=tk.LEFT,
            wraplength=320
        )
        self.music_sidebar_copy_label.pack(anchor="w", pady=(6, 14), fill=tk.X)

        self.music_sidebar_summary_frame = tk.Frame(self.music_right_frame)
        self.music_sidebar_summary_frame.pack(fill=tk.X)
        _, self.music_selected_clip_value_label = self._create_metric_chip(self.music_sidebar_summary_frame, "Clip", "No clip linked")
        self.music_selected_clip_value_label.master.pack(fill=tk.X)
        _, self.music_audio_state_value_label = self._create_metric_chip(self.music_sidebar_summary_frame, "Audio", "No audio generated")
        self.music_audio_state_value_label.master.pack(fill=tk.X, pady=(8, 0))
        _, self.music_final_state_value_label = self._create_metric_chip(self.music_sidebar_summary_frame, "Final", "No final render")
        self.music_final_state_value_label.master.pack(fill=tk.X, pady=(8, 0))

        self.music_preview_section = self._create_collapsible_section(
            self.music_right_frame,
            "music_preview",
            "Preview",
            meta_text="Reference clip",
            is_open=False,
            body_expand=True,
            body_background=self.colors["surface_alt"]
        )
        self.music_preview_section["container"].pack(fill=tk.BOTH, expand=True, pady=(16, 0))

        self.music_sidebar_card = tk.Frame(self.music_preview_section["body"], padx=16, pady=16)
        self.music_sidebar_card.pack(fill=tk.BOTH, expand=True)

        self.music_preview_card = tk.Frame(self.music_sidebar_card, padx=14, pady=14)
        self.music_preview_card.pack(fill=tk.BOTH, expand=True)

        self.selected_video_header_label = tk.Label(self.music_preview_card, text="Preview")
        self.selected_video_header_label.pack(anchor="w")
        self.selected_video_lbl = tk.Label(self.music_preview_card, text="No video selected.\nGo to Video Generation tab\nand click 'Add Music'.", wraplength=280, justify=tk.LEFT, anchor="w")
        self.selected_video_lbl.pack(anchor="w", pady=(10, 6), fill=tk.X)
        self.selected_video_meta_label = tk.Label(
            self.music_preview_card,
            text="Select a stitched render from the gallery to lock music direction to a specific cut.",
            wraplength=280,
            justify=tk.LEFT,
            anchor="w"
        )
        self.selected_video_meta_label.pack(anchor="w", fill=tk.X)

        self.music_preview_media_frame = tk.Frame(self.music_preview_card, padx=8, pady=8)
        self.music_preview_media_frame.pack(fill=tk.X, pady=(14, 0))
        self.selected_video_thumb = tk.Label(self.music_preview_media_frame)
        self.selected_video_thumb.pack(anchor="center")

        self.music_preview_actions_frame = tk.Frame(self.music_preview_card)
        self.music_preview_actions_frame.pack(fill=tk.X, pady=(14, 0))

        self.music_preview_status_frame = tk.Frame(self.music_preview_card)
        self.music_preview_status_frame.pack(fill=tk.X, pady=(10, 0))

        self._update_music_config_summary()
        self._refresh_music_sidebar_state()

    def _get_selected_video_profile_key(self):
        selected_label = self.video_profile_var.get()
        return self.video_profile_label_to_key.get(selected_label, DEFAULT_VIDEO_PROFILE)

    def _set_selected_video_profile_key(self, profile_key):
        profile_label = self.video_profile_key_to_label.get(profile_key, self.video_profile_key_to_label[DEFAULT_VIDEO_PROFILE])
        self.video_profile_var.set(profile_label)

    def _get_video_profile(self, profile_key=None):
        resolved_key = profile_key or self._get_selected_video_profile_key()
        return VIDEO_WORKFLOW_PROFILES.get(resolved_key, VIDEO_WORKFLOW_PROFILES[DEFAULT_VIDEO_PROFILE])

    def _make_workflow_path_absolute(self, workflow_path):
        if not workflow_path:
            return workflow_path
        if os.path.isabs(workflow_path):
            return workflow_path
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), workflow_path)

    def _resolve_video_workflow_path(self, preferred_path=None, profile_key=None):
        if preferred_path:
            preferred_abs = self._make_workflow_path_absolute(preferred_path)
            if os.path.exists(preferred_abs):
                return preferred_abs

        profile = self._get_video_profile(profile_key)
        return self._make_workflow_path_absolute(profile["workflow_path"])

    def _update_video_workflow_label(self):
        profile_label = self.video_profile_key_to_label.get(self._get_selected_video_profile_key(), "Unknown Profile")
        if self.workflow and self.api_json_path:
            self.json_label.config(text=f"Loaded: {os.path.basename(self.api_json_path)} ({profile_label})")
        elif self.api_json_path:
            self.json_label.config(text=f"Workflow: {os.path.basename(self.api_json_path)} ({profile_label})")
        else:
            self.json_label.config(text=f"No JSON loaded ({profile_label})")

    def _iter_role_refs(self, role_ref):
        if isinstance(role_ref, list):
            return role_ref
        return [role_ref]

    def _get_profile_role_refs(self, role_name, profile_key=None):
        profile = self._get_video_profile(profile_key)
        role_ref = profile["roles"].get(role_name)
        if not role_ref:
            return []
        return self._iter_role_refs(role_ref)

    def _get_workflow_role_value(self, workflow, role_name, default="", profile_key=None):
        for role_ref in self._get_profile_role_refs(role_name, profile_key):
            node_id = str(role_ref["node_id"])
            node_data = workflow.get(node_id, {})
            inputs = node_data.get("inputs", {})
            input_name = role_ref["input"]
            if input_name in inputs:
                value = inputs[input_name]
                if isinstance(value, list):
                    return default
                return value
        return default

    def _set_workflow_role_value(self, workflow, role_name, value, profile_key=None):
        updated_count = 0
        for role_ref in self._get_profile_role_refs(role_name, profile_key):
            node_id = str(role_ref["node_id"])
            node_data = workflow.get(node_id)
            if not node_data:
                continue
            node_inputs = node_data.setdefault("inputs", {})
            node_inputs[role_ref["input"]] = value
            updated_count += 1
        return updated_count

    def _sync_video_settings_from_workflow(self, force=False):
        if not self.workflow:
            return

        field_mapping = [
            (self.video_negative_prompt_var, "negative_prompt"),
            (self.video_width_var, "width"),
            (self.video_height_var, "height"),
            (self.video_fps_var, "fps"),
            (self.video_length_var, "length"),
            (self.video_checkpoint_var, "checkpoint_name"),
            (self.video_text_encoder_var, "text_encoder_name"),
            (self.video_lora_var, "lora_name"),
            (self.video_upscaler_var, "upscaler_name")
        ]

        for tk_var, role_name in field_mapping:
            current_value = tk_var.get().strip() if isinstance(tk_var.get(), str) else tk_var.get()
            if current_value and not force:
                continue
            role_value = self._get_workflow_role_value(self.workflow, role_name, default="")
            tk_var.set("" if role_value is None else str(role_value))

    def _reset_video_settings_to_loaded_workflow(self):
        for tk_var in [
            self.video_negative_prompt_var,
            self.video_width_var,
            self.video_height_var,
            self.video_fps_var,
            self.video_length_var,
            self.video_checkpoint_var,
            self.video_text_encoder_var,
            self.video_lora_var,
            self.video_upscaler_var
        ]:
            tk_var.set("")
        self.video_output_subfolder_var.set("video")
        self.video_output_base_name_var.set("LTX2_3_Scene")
        self.video_output_include_project_var.set(False)
        self._sync_video_settings_from_workflow(force=True)

    def _get_video_settings_snapshot(self):
        return {
            "negative_prompt": self.video_negative_prompt_var.get().strip(),
            "width": self.video_width_var.get().strip(),
            "height": self.video_height_var.get().strip(),
            "fps": self.video_fps_var.get().strip(),
            "length": self.video_length_var.get().strip(),
            "checkpoint_name": self.video_checkpoint_var.get().strip(),
            "text_encoder_name": self.video_text_encoder_var.get().strip(),
            "lora_name": self.video_lora_var.get().strip(),
            "upscaler_name": self.video_upscaler_var.get().strip(),
            "output_subfolder": self.video_output_subfolder_var.get().strip(),
            "output_base_name": self.video_output_base_name_var.get().strip(),
            "output_include_project_name": bool(self.video_output_include_project_var.get())
        }

    def _apply_saved_video_settings(self, saved_settings):
        if not saved_settings:
            return

        self.video_negative_prompt_var.set(saved_settings.get("negative_prompt", self.video_negative_prompt_var.get()).strip())
        self.video_width_var.set(str(saved_settings.get("width", self.video_width_var.get())).strip())
        self.video_height_var.set(str(saved_settings.get("height", self.video_height_var.get())).strip())
        self.video_fps_var.set(str(saved_settings.get("fps", self.video_fps_var.get())).strip())
        self.video_length_var.set(str(saved_settings.get("length", self.video_length_var.get())).strip())
        self.video_checkpoint_var.set(saved_settings.get("checkpoint_name", self.video_checkpoint_var.get()).strip())
        self.video_text_encoder_var.set(saved_settings.get("text_encoder_name", self.video_text_encoder_var.get()).strip())
        self.video_lora_var.set(saved_settings.get("lora_name", self.video_lora_var.get()).strip())
        self.video_upscaler_var.set(saved_settings.get("upscaler_name", self.video_upscaler_var.get()).strip())
        self.video_output_subfolder_var.set(str(saved_settings.get("output_subfolder", self.video_output_subfolder_var.get())).strip() or "video")
        self.video_output_base_name_var.set(str(saved_settings.get("output_base_name", self.video_output_base_name_var.get())).strip() or "LTX2_3_Scene")
        self.video_output_include_project_var.set(bool(saved_settings.get("output_include_project_name", self.video_output_include_project_var.get())))

    def _sanitize_output_token(self, value, fallback="output"):
        sanitized = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in str(value).strip())
        sanitized = sanitized.strip("_")
        return sanitized or fallback

    def _validate_video_workflow_template(self, workflow=None, profile_key=None):
        workflow_to_validate = workflow if workflow is not None else self.workflow
        if not workflow_to_validate:
            return False, "No video workflow is loaded."

        required_roles = [
            "prompt",
            "negative_prompt",
            "width",
            "height",
            "fps",
            "length",
            "filename_prefix",
            "noise_seed",
            "checkpoint_name",
            "text_encoder_name",
            "lora_name",
            "upscaler_name"
        ]

        for role_name in required_roles:
            role_refs = self._get_profile_role_refs(role_name, profile_key)
            if not role_refs:
                return False, f"Workflow profile is missing the '{role_name}' mapping."
            for role_ref in role_refs:
                node_id = str(role_ref["node_id"])
                node_data = workflow_to_validate.get(node_id)
                if not node_data:
                    return False, f"Workflow is missing node {node_id} for role '{role_name}'."
                if role_ref["input"] not in node_data.get("inputs", {}):
                    return False, f"Workflow node {node_id} is missing input '{role_ref['input']}' for role '{role_name}'."

        return True, None

    def _collect_validated_video_settings(self):
        is_valid, validation_error = self._validate_video_workflow_template()
        if not is_valid:
            return None, validation_error

        parsed_settings = {
            "negative_prompt": self.video_negative_prompt_var.get().strip(),
            "checkpoint_name": self.video_checkpoint_var.get().strip(),
            "text_encoder_name": self.video_text_encoder_var.get().strip(),
            "lora_name": self.video_lora_var.get().strip(),
            "upscaler_name": self.video_upscaler_var.get().strip(),
            "output_subfolder": self.video_output_subfolder_var.get().strip(),
            "output_base_name": self.video_output_base_name_var.get().strip(),
            "output_include_project_name": bool(self.video_output_include_project_var.get()),
            "t2v_enabled": True
        }

        numeric_fields = [
            ("width", self.video_width_var.get().strip()),
            ("height", self.video_height_var.get().strip()),
            ("fps", self.video_fps_var.get().strip()),
            ("length", self.video_length_var.get().strip())
        ]
        for field_name, raw_value in numeric_fields:
            if not raw_value:
                return None, f"{field_name.replace('_', ' ').title()} is required."
            try:
                parsed_value = int(raw_value)
            except ValueError:
                return None, f"{field_name.replace('_', ' ').title()} must be an integer."
            if parsed_value <= 0:
                return None, f"{field_name.replace('_', ' ').title()} must be greater than zero."
            parsed_settings[field_name] = parsed_value

        for field_name in ["checkpoint_name", "text_encoder_name", "lora_name", "upscaler_name"]:
            if not parsed_settings[field_name]:
                return None, f"{field_name.replace('_', ' ').title()} is required."

        if not parsed_settings["output_subfolder"]:
            parsed_settings["output_subfolder"] = "video"
        if not parsed_settings["output_base_name"]:
            parsed_settings["output_base_name"] = "LTX2_3_Scene"

        return parsed_settings, None

    def _build_video_filename_prefix(self, video_settings, mode, index=None):
        subfolder = self._sanitize_output_token(video_settings.get("output_subfolder", "video"), fallback="video")
        base_name = self._sanitize_output_token(video_settings.get("output_base_name", "LTX2_3_Scene"), fallback="LTX2_3_Scene")
        parts = []

        if video_settings.get("output_include_project_name") and self.current_project_dir:
            parts.append(self._sanitize_output_token(os.path.basename(self.current_project_dir), fallback="project"))

        parts.append(base_name)

        if mode == "single":
            parts.append("Single")
            parts.append(str(int(time.time())))
        elif index is not None:
            parts.append(f"{index:02d}")
        else:
            parts.append(str(int(time.time())))

        return f"{subfolder}/{'_'.join(parts)}"

    def _get_available_model_search_roots(self):
        return [root for root in self.model_search_roots if os.path.exists(root)]

    def _set_video_preflight_summary(self, summary_text, status_text, color):
        self.video_preflight_status_label.config(text=f"Status: {status_text}", fg=color)
        self.video_preflight_text.configure(state=tk.NORMAL)
        self.video_preflight_text.delete("1.0", tk.END)
        self.video_preflight_text.insert("1.0", summary_text)
        self.video_preflight_text.configure(state=tk.DISABLED)
        self._update_collapsible_section_meta("video_preflight", status_text)

    def _mark_video_preflight_stale(self, reason="Validation not run for current settings."):
        self._set_video_preflight_summary(reason, "Not validated", "gray")

    def _scan_model_choices_for_field(self, field_name):
        subdirectory = MODEL_SUBDIRECTORIES.get(field_name)
        if not subdirectory:
            return []

        discovered_names = set()
        for root in self._get_available_model_search_roots():
            candidate_dir = os.path.join(root, subdirectory)
            if not os.path.exists(candidate_dir):
                continue
            for entry in os.scandir(candidate_dir):
                if entry.is_file() and entry.name.lower().endswith('.safetensors'):
                    discovered_names.add(entry.name)

        return sorted(discovered_names, key=str.lower)

    def refresh_video_model_choices(self, initial_load=False):
        combo_mapping = {
            "checkpoint_name": self.video_checkpoint_combo,
            "text_encoder_name": self.video_text_encoder_combo,
            "lora_name": self.video_lora_combo,
            "upscaler_name": self.video_upscaler_combo
        }
        variable_mapping = {
            "checkpoint_name": self.video_checkpoint_var,
            "text_encoder_name": self.video_text_encoder_var,
            "lora_name": self.video_lora_var,
            "upscaler_name": self.video_upscaler_var
        }

        for field_name, combo in combo_mapping.items():
            current_value = variable_mapping[field_name].get().strip()
            discovered_choices = self._scan_model_choices_for_field(field_name)
            self.video_model_choices[field_name] = discovered_choices
            combo["values"] = discovered_choices
            if initial_load:
                continue
            if current_value and current_value not in discovered_choices:
                combo.set(current_value)

        if not initial_load:
            total_choices = sum(len(choices) for choices in self.video_model_choices.values())
            self.update_status(f"Refreshed model lists ({total_choices} choices found).", "blue")
            self.log_debug("VIDEO_MODEL_LISTS_REFRESHED", counts={k: len(v) for k, v in self.video_model_choices.items()})
            self._mark_video_preflight_stale("Model lists refreshed. Re-run validation for current settings.")

    def _find_model_file(self, filename):
        if not filename:
            return None

        if os.path.isabs(filename) and os.path.exists(filename):
            return filename

        for root in self._get_available_model_search_roots():
            for current_root, _, files in os.walk(root):
                if filename in files:
                    return os.path.join(current_root, filename)
        return None

    def _validate_video_model_files(self, video_settings):
        model_field_labels = {
            "checkpoint_name": "Checkpoint",
            "text_encoder_name": "Text Encoder",
            "lora_name": "LoRA",
            "upscaler_name": "Upscaler"
        }

        found_models = {}
        missing_models = []

        for field_name, label in model_field_labels.items():
            resolved_path = self._find_model_file(video_settings.get(field_name, ""))
            if resolved_path:
                found_models[label] = resolved_path
            else:
                missing_models.append(f"{label}: {video_settings.get(field_name, '')}")

        return found_models, missing_models

    def validate_video_setup(self):
        video_settings, validation_error = self._collect_validated_video_settings()
        if validation_error:
            self.update_status(validation_error, "red")
            self._set_video_preflight_summary(validation_error, "Validation failed", "red")
            messagebox.showerror("Video Setup Validation", validation_error)
            self.log_debug("VIDEO_SETUP_VALIDATION_FAILED", reason=validation_error)
            return

        model_roots = self._get_available_model_search_roots()
        found_models, missing_models = self._validate_video_model_files(video_settings)

        details = [
            f"Workflow: {self.video_profile_var.get()}",
            f"Workflow JSON: {self.api_json_path}",
            f"Dimensions: {video_settings['width']}x{video_settings['height']}",
            f"FPS: {video_settings['fps']}",
            f"Length: {video_settings['length']}",
            f"Output Prefix: {self._build_video_filename_prefix(video_settings, 'preview', 1)}"
        ]

        if model_roots:
            details.append("Model roots:")
            details.extend(model_roots)
        else:
            details.append("Model roots: none found; model file checks may fail")

        if found_models:
            details.append("Resolved model files:")
            for label, path in found_models.items():
                details.append(f"{label}: {path}")

        if missing_models:
            details.append("Missing model files:")
            details.extend(missing_models)
            self._set_video_preflight_summary("\n".join(details), "Warnings", "orange")
            messagebox.showwarning("Video Setup Validation", "\n".join(details))
            self.update_status("Video setup validation found missing model files.", "orange")
            self.log_debug(
                "VIDEO_SETUP_VALIDATION_WARNING",
                missing_models=missing_models,
                model_roots=model_roots,
                resolved_models=found_models
            )
            return

        self._set_video_preflight_summary("\n".join(details), "Validation passed", "green")
        messagebox.showinfo("Video Setup Validation", "\n".join(details))
        self.update_status("Video setup validation passed.", "green")
        self.log_debug(
            "VIDEO_SETUP_VALIDATION_PASSED",
            model_roots=model_roots,
            resolved_models=found_models,
            width=video_settings["width"],
            height=video_settings["height"],
            fps=video_settings["fps"],
            length=video_settings["length"]
        )

    def _build_video_workflow_for_prompt(self, prompt_text, filename_prefix, video_settings):
        workflow_to_submit = copy.deepcopy(self.workflow)

        self._set_workflow_role_value(workflow_to_submit, "prompt", prompt_text)
        self._set_workflow_role_value(workflow_to_submit, "negative_prompt", video_settings["negative_prompt"])
        self._set_workflow_role_value(workflow_to_submit, "width", video_settings["width"])
        self._set_workflow_role_value(workflow_to_submit, "height", video_settings["height"])
        self._set_workflow_role_value(workflow_to_submit, "fps", video_settings["fps"])
        self._set_workflow_role_value(workflow_to_submit, "length", video_settings["length"])
        self._set_workflow_role_value(workflow_to_submit, "t2v_enabled", video_settings["t2v_enabled"])
        self._set_workflow_role_value(workflow_to_submit, "filename_prefix", filename_prefix)
        self._set_workflow_role_value(workflow_to_submit, "checkpoint_name", video_settings["checkpoint_name"])
        self._set_workflow_role_value(workflow_to_submit, "text_encoder_name", video_settings["text_encoder_name"])
        self._set_workflow_role_value(workflow_to_submit, "lora_name", video_settings["lora_name"])
        self._set_workflow_role_value(workflow_to_submit, "upscaler_name", video_settings["upscaler_name"])

        for role_ref in self._get_profile_role_refs("noise_seed"):
            node_id = str(role_ref["node_id"])
            workflow_to_submit[node_id]["inputs"][role_ref["input"]] = random.randint(1, 999999999999999)

        self.log_debug(
            "WORKFLOW_PREPARED",
            prompt_preview=self._truncate_text(prompt_text, 120),
            filename_prefix=filename_prefix,
            width=video_settings["width"],
            height=video_settings["height"],
            fps=video_settings["fps"],
            length=video_settings["length"],
            checkpoint=video_settings["checkpoint_name"],
            text_encoder=video_settings["text_encoder_name"],
            lora=video_settings["lora_name"],
            upscaler=video_settings["upscaler_name"]
        )
        return workflow_to_submit

    def _load_video_workflow_template(self, force_video_settings=False):
        self.api_json_path = self._resolve_video_workflow_path(self.api_json_path, self._get_selected_video_profile_key())

        if os.path.exists(self.api_json_path):
            try:
                with open(self.api_json_path, 'r', encoding='utf-8') as f:
                    self.workflow = json.load(f)
                self._sync_video_settings_from_workflow(force=force_video_settings)
            except Exception:
                self.workflow = None
                self.json_label.config(text="Error loading video workflow JSON")
                return
        else:
            self.workflow = None
            self.json_label.config(text="Default JSON not found")
            return

        self._update_video_workflow_label()

    def _load_video_profile_state(self, profile_key, workflow_path=None, saved_settings=None):
        self._set_selected_video_profile_key(profile_key)
        self.api_json_path = self._resolve_video_workflow_path(workflow_path, profile_key)
        self._load_video_workflow_template(force_video_settings=True)
        if saved_settings:
            self._apply_saved_video_settings(saved_settings)

    def on_video_profile_changed(self, event=None):
        selected_profile = self._get_selected_video_profile_key()
        self.api_json_path = self._resolve_video_workflow_path(None, selected_profile)
        self._load_video_workflow_template(force_video_settings=True)
        self._mark_video_preflight_stale("Workflow profile changed. Re-run validation for current settings.")
        self.save_global_settings()

    def reset_video_profile_defaults(self):
        selected_profile = self._get_selected_video_profile_key()
        self._load_video_profile_state(selected_profile)
        self._mark_video_preflight_stale("Video settings reset to workflow defaults. Re-run validation.")
        self.save_global_settings()
        self.save_project_state()
        self.update_status("Video settings reset to workflow defaults.", "blue")
        self.log_debug("VIDEO_SETTINGS_RESET", profile=selected_profile, workflow_path=self.api_json_path)

    def load_default_json(self):
        self._load_video_workflow_template(force_video_settings=False)
            
        if os.path.exists(self.music_json_path):
            try:
                with open(self.music_json_path, 'r', encoding='utf-8') as f:
                    self.music_workflow = json.load(f)
            except Exception as e:
                print(f"Error loading music JSON: {e}")

    def load_json_dialog(self):
        filepath = filedialog.askopenfilename(
            title="Select API JSON",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.workflow = json.load(f)
                self.api_json_path = filepath
                self._sync_video_settings_from_workflow(force=True)
                self._update_video_workflow_label()
                self._mark_video_preflight_stale("Workflow JSON changed. Re-run validation for current settings.")
                self.log_debug("WORKFLOW_LOADED", path=filepath)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load JSON:\n{e}")

    def _truncate_text(self, text, max_len=240):
        if text is None:
            return ""
        text = str(text).replace("\n", "\\n")
        if len(text) <= max_len:
            return text
        return text[:max_len] + "..."

    def log_debug(self, event, **kwargs):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        details = " | ".join([f"{k}={self._truncate_text(v)}" for k, v in kwargs.items()])
        line = f"[{timestamp}] {event}"
        if details:
            line += f" | {details}"

        print(line)

        if not self.debug_log_file:
            return

        try:
            with self.debug_lock:
                with open(self.debug_log_file, 'a', encoding='utf-8') as f:
                    f.write(line + "\n")
        except Exception:
            pass

    def open_debug_log(self):
        if not self.debug_log_file:
            messagebox.showwarning("Debug Log", "Debug log path is not ready yet.")
            return

        if not os.path.exists(self.debug_log_file):
            try:
                os.makedirs(os.path.dirname(self.debug_log_file), exist_ok=True)
                with open(self.debug_log_file, 'a', encoding='utf-8'):
                    pass
            except Exception as e:
                messagebox.showerror("Error", f"Could not create debug log:\n{e}")
                return

        try:
            os.startfile(self.debug_log_file)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open debug log:\n{e}")

    def update_scroll_region(self):
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def add_prompt_entry(self):
        frame = tk.Frame(self.scrollable_frame, pady=6)
        frame.pack(fill=tk.X, expand=True)
        self._style_panel(frame, self.colors["card"], border=True)
        
        text_widget = tk.Text(frame, height=4, width=50)
        text_widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._style_text_input(text_widget, multiline=True)
        frame.prompt_text_widget = text_widget
        
        btn_frame = tk.Frame(frame)
        btn_frame.pack(side=tk.RIGHT, padx=5)
        self._style_panel(btn_frame, self.colors["card"])
        
        generate_btn = tk.Button(btn_frame, text="Generate", command=lambda t=text_widget: self.generate_single_prompt(t))
        generate_btn.pack(side=tk.TOP, fill=tk.X, pady=(0, 2))
        self._style_button(generate_btn, "accent", compact=True)
        
        remove_btn = tk.Button(btn_frame, text="Remove", command=lambda f=frame, t=text_widget: self.remove_prompt_entry(f, t))
        remove_btn.pack(side=tk.TOP, fill=tk.X)
        self._style_button(remove_btn, "ghost", compact=True)
        
        self.prompts.append(text_widget)
        self.log_debug("PROMPT_ADDED", widget_id=id(text_widget), total_widgets=len(self.prompts))
        self.update_scroll_region()
        self._update_prompt_collection_summary()

    def _clear_all_prompt_entries(self):
        cleared_count = len(self.scrollable_frame.winfo_children())
        for frame in list(self.scrollable_frame.winfo_children()):
            frame.destroy()
        self.prompts.clear()
        self.log_debug("PROMPTS_CLEARED", cleared_count=cleared_count)
        self.update_scroll_region()
        self._update_prompt_collection_summary()

    def _collect_prompt_widgets(self):
        widgets = []
        for frame in self.scrollable_frame.winfo_children():
            text_widget = getattr(frame, "prompt_text_widget", None)
            if text_widget is None:
                continue
            try:
                if int(text_widget.winfo_exists()) == 1:
                    widgets.append(text_widget)
            except tk.TclError:
                continue
        self.prompts = widgets
        return widgets

    def _collect_prompt_texts(self):
        prompts_text = [w.get("1.0", tk.END).strip() for w in self._collect_prompt_widgets() if w.get("1.0", tk.END).strip()]
        previews = [self._truncate_text(p, 120) for p in prompts_text]
        self.log_debug("PROMPTS_COLLECTED", count=len(prompts_text), previews=previews)
        return prompts_text

    def remove_prompt_entry(self, frame, text_widget):
        try:
            removed_text = text_widget.get("1.0", tk.END).strip()
        except Exception:
            removed_text = ""

        frame.destroy()
        if text_widget in self.prompts:
            self.prompts.remove(text_widget)

        if not self.scrollable_frame.winfo_children():
            self.add_prompt_entry()
        else:
            self._collect_prompt_widgets()

        self.log_debug(
            "PROMPT_REMOVED",
            widget_id=id(text_widget),
            removed_preview=self._truncate_text(removed_text, 120),
            remaining_widgets=len(self.scrollable_frame.winfo_children())
        )

        self.update_scroll_region()
        self._update_prompt_collection_summary()

    def clear_ui_fields(self):
        # Clear Video Prompts
        self._clear_all_prompt_entries()
        self.add_prompt_entry()
        self.update_debug_prompt_status("(none)")
        self._reset_video_settings_to_loaded_workflow()
        self.selected_videos.clear()
        self._update_video_selection_summary()
        
        # Clear Music Settings
        self.music_tags_text.delete("1.0", tk.END)
        self.music_lyrics_text.delete("1.0", tk.END)
        self.music_duration_var.set(120)
        self.music_bpm_var.set(120)
        self.music_key_var.set("C major")
        self.strip_audio_var.set(True)
        
        self.current_generated_audio = None
        self.selected_video_for_music = None
        self.current_final_video = None
        self._reset_selected_video_preview()
        
        self.preview_music_btn.config(state=tk.DISABLED)
        self.merge_music_btn.config(state=tk.DISABLED)
        if hasattr(self, 'preview_final_btn'):
            self.preview_final_btn.config(state=tk.DISABLED)
        self._refresh_music_sidebar_state()

    def save_global_settings(self):
        settings = {
            "api_json_path": self.api_json_path,
            "video_profile": self._get_selected_video_profile_key(),
            "video_settings": self._get_video_settings_snapshot(),
            "last_project_dir": self.current_project_dir
        }
        try:
            with open(self.global_settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"Error saving global settings: {e}")

    def load_global_settings(self):
        if os.path.exists(self.global_settings_file):
            try:
                with open(self.global_settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                self._load_video_profile_state(
                    settings.get("video_profile", DEFAULT_VIDEO_PROFILE),
                    settings.get("api_json_path"),
                    settings.get("video_settings", {})
                )
                
                last_project = settings.get("last_project_dir")
                if last_project and os.path.exists(last_project):
                    self.set_project(last_project)
                else:
                    # Create a default project if none exists
                    default_project = os.path.join(self.base_output_dir, f"Project_{int(time.time())}")
                    self.set_project(default_project)
            except Exception as e:
                print(f"Error loading global settings: {e}")
                default_project = os.path.join(self.base_output_dir, f"Project_{int(time.time())}")
                self.set_project(default_project)
        else:
            default_project = os.path.join(self.base_output_dir, f"Project_{int(time.time())}")
            self.set_project(default_project)

    def save_project_state(self):
        if not self.current_project_dir:
            return
            
        project_data_file = os.path.join(self.current_project_dir, "project_data.json")
        state = {
            "prompts": self._collect_prompt_texts(),
            "video_profile": self._get_selected_video_profile_key(),
            "api_json_path": self.api_json_path,
            "video_settings": self._get_video_settings_snapshot(),
            "music_tags": self.music_tags_text.get("1.0", tk.END).strip(),
            "music_lyrics": self.music_lyrics_text.get("1.0", tk.END).strip(),
            "music_duration": self.music_duration_var.get(),
            "music_bpm": self.music_bpm_var.get(),
            "music_key": self.music_key_var.get(),
            "strip_audio": self.strip_audio_var.get(),
            "current_generated_audio": self.current_generated_audio,
            "selected_video_for_music": self.selected_video_for_music,
            "current_final_video": getattr(self, 'current_final_video', None)
        }
        try:
            with open(project_data_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=4)
        except Exception as e:
            print(f"Error saving project state: {e}")

    def load_project_state(self):
        if not self.current_project_dir:
            return
            
        project_data_file = os.path.join(self.current_project_dir, "project_data.json")
        
        # Clear existing UI fields first
        self.clear_ui_fields()
        
        if os.path.exists(project_data_file):
            try:
                with open(project_data_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)

                saved_profile = state.get("video_profile", self._get_selected_video_profile_key())
                self._load_video_profile_state(
                    saved_profile,
                    state.get("api_json_path"),
                    state.get("video_settings", {})
                )
                
                # Load Video Prompts
                saved_prompts = state.get("prompts", [])
                if saved_prompts:
                    # Remove the default empty prompt added by clear_ui_fields
                    self._clear_all_prompt_entries()
                        
                    for prompt_text in saved_prompts:
                        self.add_prompt_entry()
                        self.prompts[-1].insert(tk.END, prompt_text)
                self._update_prompt_collection_summary()
                
                # Load Music Settings
                self.music_tags_text.insert(tk.END, state.get("music_tags", ""))
                self.music_lyrics_text.insert(tk.END, state.get("music_lyrics", ""))
                self.music_duration_var.set(state.get("music_duration", 120))
                self.music_bpm_var.set(state.get("music_bpm", 120))
                self.music_key_var.set(state.get("music_key", "C major"))
                self.strip_audio_var.set(state.get("strip_audio", True))
                
                # Load Music State
                self.current_generated_audio = state.get("current_generated_audio")
                self.selected_video_for_music = state.get("selected_video_for_music")
                self.current_final_video = state.get("current_final_video")
                
                # Update UI for loaded music state
                if self.selected_video_for_music and os.path.exists(self.selected_video_for_music):
                    thumb_path = os.path.join(self.thumbs_dir, f"{os.path.basename(self.selected_video_for_music)}.jpg")
                    self._set_selected_video_preview(self.selected_video_for_music, thumb_path)
                else:
                    self.selected_video_for_music = None
                    self._reset_selected_video_preview()
                    
                if self.current_generated_audio and os.path.exists(self.current_generated_audio):
                    self.preview_music_btn.config(state=tk.NORMAL)
                    if self.selected_video_for_music:
                        self.merge_music_btn.config(state=tk.NORMAL)
                else:
                    self.current_generated_audio = None
                    self.preview_music_btn.config(state=tk.DISABLED)
                    self.merge_music_btn.config(state=tk.DISABLED)
                    
                if self.current_final_video and os.path.exists(self.current_final_video):
                    if hasattr(self, 'preview_final_btn'):
                        self.preview_final_btn.config(state=tk.NORMAL)
                else:
                    self.current_final_video = None
                    if hasattr(self, 'preview_final_btn'):
                        self.preview_final_btn.config(state=tk.DISABLED)
                self._refresh_music_sidebar_state()

            except Exception as e:
                print(f"Error loading project state: {e}")

    def refresh_gallery(self):
        # Clear existing
        for widget in self.gallery_inner_frame.winfo_children():
            widget.destroy()
        self.thumbnail_images.clear()
        self.video_checkbox_vars.clear()
        final_files = self._get_gallery_video_files(self.final_mv_dir)
        stitched_files = self._get_gallery_video_files(self.stitched_dir)
        scene_files = self._get_gallery_video_files(self.scenes_dir)
        current_project_videos = {
            os.path.join(self.final_mv_dir, filename) for filename in final_files
        } | {
            os.path.join(self.stitched_dir, filename) for filename in stitched_files
        } | {
            os.path.join(self.scenes_dir, filename) for filename in scene_files
        }
        self.selected_videos = {path for path in self.selected_videos if path in current_project_videos}

        self._update_gallery_overview(len(final_files), len(stitched_files), len(scene_files))

        self._populate_gallery_section(
            "Final Music Videos",
            "Finished exports ready for review or delivery.",
            self.final_mv_dir,
            final_files,
            show_add_music=False
        )
        self._populate_gallery_section(
            "Stitched Renders",
            "Long-form comps assembled from selected scenes.",
            self.stitched_dir,
            stitched_files,
            show_add_music=True
        )
        self._populate_gallery_section(
            "Generated Scenes",
            "Newest individual scene renders from the active queue.",
            self.scenes_dir,
            scene_files,
            show_add_music=False
        )
        self._update_video_selection_summary()

    def _get_gallery_video_files(self, folder_path):
        if not os.path.exists(folder_path):
            return []
        return sorted(
            [f for f in os.listdir(folder_path) if f.endswith('.mp4')],
            key=lambda x: os.path.getmtime(os.path.join(folder_path, x)),
            reverse=True
        )

    def _populate_gallery_section(self, title, description, folder_path, files, show_add_music=False):
        section_frame = tk.Frame(self.gallery_inner_frame, padx=14, pady=14)
        section_frame.pack(fill=tk.X, padx=4, pady=(0, 12))
        self._style_panel(section_frame, self.colors["surface"], border=True)

        header_row = tk.Frame(section_frame)
        header_row.pack(fill=tk.X)
        self._style_panel(header_row, self.colors["surface"])

        text_frame = tk.Frame(header_row)
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._style_panel(text_frame, self.colors["surface"])

        title_label = tk.Label(text_frame, text=title, anchor="w")
        title_label.pack(anchor="w")
        self._style_label(title_label, "section", self.colors["surface"])

        description_label = tk.Label(text_frame, text=description, anchor="w", justify=tk.LEFT, wraplength=320)
        description_label.pack(anchor="w", pady=(4, 0), fill=tk.X)
        self._style_label(description_label, "muted", self.colors["surface"])

        _, count_label = self._create_metric_chip(header_row, "Items", str(len(files)))
        count_label.master.pack(side=tk.RIGHT, padx=(12, 0))

        if not files:
            empty_label = tk.Label(section_frame, text="No renders in this section yet.", anchor="w")
            empty_label.pack(fill=tk.X, pady=(14, 0))
            self._style_label(empty_label, "muted", self.colors["surface"])
            return

        for filename in files:
            video_path = os.path.join(folder_path, filename)
            thumb_path = os.path.join(self.thumbs_dir, f"{filename}.jpg")

            if not os.path.exists(thumb_path):
                self.generate_thumbnail(video_path, thumb_path)

            self.add_gallery_item(section_frame, video_path, thumb_path, filename, show_add_music)

    def generate_thumbnail(self, video_path, thumb_path):
        try:
            # Extract frame at 00:00:00
            cmd = [FFMPEG_PATH, '-y', '-i', video_path, '-ss', '00:00:00.000', '-vframes', '1', thumb_path]
            subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW, capture_output=True, check=True)
        except FileNotFoundError:
            self.log_debug("THUMBNAIL_SKIPPED", video_path=video_path, reason="ffmpeg_not_found", ffmpeg_path=FFMPEG_PATH)
        except Exception as e:
            print(f"Error generating thumbnail for {video_path}: {e}")

    def add_gallery_item(self, parent, video_path, thumb_path, title, show_add_music=False):
        frame = tk.Frame(parent, bd=0, relief=tk.FLAT)
        frame.pack(fill=tk.X, pady=(12, 0))
        self._style_panel(frame, self.colors["card"], border=True)

        thumb_shell = tk.Frame(frame, padx=8, pady=8)
        thumb_shell.pack(side=tk.LEFT, padx=(0, 6), pady=0)
        self._style_panel(thumb_shell, self.colors["surface_soft"])
        
        try:
            if os.path.exists(thumb_path):
                img = Image.open(thumb_path)
                img.thumbnail((160, 90)) # 16:9 aspect ratio
                photo = ImageTk.PhotoImage(img)
                self.thumbnail_images.append(photo)

                btn = tk.Button(thumb_shell, image=photo, command=lambda p=video_path: self.play_video(p), bg=self.colors["black"], cursor="hand2")
                btn.pack(side=tk.LEFT)
            else:
                btn = tk.Button(thumb_shell, text="Play", width=15, height=5, command=lambda p=video_path: self.play_video(p), bg=self.colors["black"], fg=self.colors["text"], cursor="hand2")
                btn.pack(side=tk.LEFT)
            btn.configure(relief=tk.FLAT, bd=0, highlightthickness=0, activebackground=self.colors["black"], activeforeground=self.colors["text"])
        except Exception as e:
            print(f"Error loading thumbnail: {e}")
            
        info_frame = tk.Frame(frame)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=10)
        self._style_panel(info_frame, self.colors["card"])
        
        lbl = tk.Label(info_frame, text=title, wraplength=260, justify=tk.LEFT)
        lbl.pack(anchor="nw")
        self._style_label(lbl, "body_strong", self.colors["card"])

        modified_text = datetime.fromtimestamp(os.path.getmtime(video_path)).strftime("%b %d, %Y %I:%M %p")
        meta_label = tk.Label(info_frame, text=f"Updated {modified_text}", anchor="w")
        meta_label.pack(anchor="w", pady=(4, 6))
        self._style_label(meta_label, "muted", self.colors["card"])
        
        # Add a checkbox for selection
        var = tk.BooleanVar(value=(video_path in self.selected_videos))
        chk = tk.Checkbutton(info_frame, text="Select for Stitching", variable=var,
                             command=lambda p=video_path, v=var: self.toggle_video_selection(p, v))
        chk.pack(anchor="sw", pady=(2, 0))
        self._style_checkbutton(chk, self.colors["card"])
        self.video_checkbox_vars.append((var, video_path))
        
        btn_frame = tk.Frame(info_frame)
        btn_frame.pack(fill=tk.X, pady=(8, 0))
        self._style_panel(btn_frame, self.colors["card"])
        btn_frame.grid_columnconfigure((0, 1), weight=1)
        
        open_folder_btn = tk.Button(btn_frame, text="Open Folder", command=lambda p=video_path: self.open_folder(p))
        open_folder_btn.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self._style_button(open_folder_btn, "secondary", compact=True)
        
        delete_btn = tk.Button(btn_frame, text="Delete", fg="red", command=lambda p=video_path, t=thumb_path: self.delete_video(p, t))
        delete_btn.grid(row=0, column=1, sticky="ew", padx=(4, 0))
        self._style_button(delete_btn, "danger", compact=True)
        
        if show_add_music:
            add_music_btn = tk.Button(btn_frame, text="Add Music", command=lambda p=video_path, t=thumb_path: self.select_video_for_music(p, t))
            add_music_btn.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
            self._style_button(add_music_btn, "accent", compact=True)

    def delete_video(self, video_path, thumb_path):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {os.path.basename(video_path)}?"):
            try:
                if os.path.exists(video_path):
                    os.remove(video_path)
                if os.path.exists(thumb_path):
                    os.remove(thumb_path)
                    
                if video_path in self.selected_videos:
                    self.selected_videos.remove(video_path)
                    
                if self.selected_video_for_music == video_path:
                    self.selected_video_for_music = None
                    self._reset_selected_video_preview()
                    self.merge_music_btn.config(state=tk.DISABLED)
                    
                self.refresh_gallery()
                self._update_video_selection_summary()
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete video:\n{e}")

    def select_video_for_music(self, video_path, thumb_path):
        self.selected_video_for_music = video_path
        self._set_selected_video_preview(video_path, thumb_path)
            
        self.notebook.select(self.music_tab)
        self.update_music_status("Video selected. Ready to generate music.", "blue")

    def toggle_video_selection(self, video_path, var):
        if var.get():
            self.selected_videos.add(video_path)
        else:
            self.selected_videos.discard(video_path)
        self._update_video_selection_summary()

    def select_all_videos(self):
        for var, path in self.video_checkbox_vars:
            # Only select generated scenes for stitching to avoid nesting final videos
            if os.path.dirname(path) == self.scenes_dir:
                var.set(True)
                self.selected_videos.add(path)
        self._update_video_selection_summary()

    def clear_selection(self):
        for var, path in self.video_checkbox_vars:
            var.set(False)
            self.selected_videos.discard(path)
        self._update_video_selection_summary()

    def play_video(self, path):
        try:
            os.startfile(path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not play video:\n{e}")
            
    def open_folder(self, path):
        try:
            os.startfile(os.path.dirname(path))
        except Exception as e:
            pass

    def update_status(self, message, color="black"):
        self.root.after(0, lambda: self.status_label.config(text=f"Status: {message}", fg=color))

    def update_music_status(self, message, color="black"):
        self.root.after(0, lambda: self.music_status_label.config(text=f"Status: {message}", fg=color))

    def update_debug_prompt_status(self, prompt_text, current=None, total=None):
        if current is not None and total is not None:
            message = f"Debug: Queued Prompt ({current}/{total}): {prompt_text}"
        else:
            message = f"Debug: Queued Prompt: {prompt_text}"
        self.root.after(0, lambda: self.debug_prompt_label.config(text=message))

    def stitch_selected_videos(self):
        if not self.selected_videos:
            messagebox.showwarning("Warning", "No videos selected for stitching.")
            return
            
        # Sort the selected videos by creation time (oldest first)
        filepaths = sorted(list(self.selected_videos), key=lambda x: os.path.getmtime(x))
        
        self.stitch_btn.config(state=tk.DISABLED)
        strip_audio = self.strip_audio_var.get()
        thread = threading.Thread(target=self.process_stitching, args=(filepaths, strip_audio))
        thread.daemon = True
        thread.start()

    def process_stitching(self, filepaths, strip_audio):
        self.update_status("Stitching videos...", "blue")
        timestamp = int(time.time())
        list_file = f"concat_{timestamp}.txt"
        
        try:
            with open(list_file, 'w', encoding='utf-8') as f:
                for path in filepaths:
                    # FFmpeg requires forward slashes
                    formatted_path = path.replace('\\', '/')
                    f.write(f"file '{formatted_path}'\n")
            
            output_file = os.path.join(self.stitched_dir, f"final_master_render_{timestamp}.mp4")
            
            cmd = [FFMPEG_PATH, '-y', '-f', 'concat', '-safe', '0', '-i', list_file, '-c:v', 'copy']
            
            if strip_audio:
                cmd.append('-an')
            else:
                cmd.extend(['-c:a', 'copy'])
                
            cmd.append(output_file)
            
            subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW, capture_output=True, text=True, check=True)
            
            self.update_status(f"Stitching Complete! Saved as {os.path.basename(output_file)}", "green")
            
            # Clear selection after successful stitch
            self.selected_videos.clear()
            
            self.root.after(0, self.refresh_gallery)
            
        except FileNotFoundError:
            self.update_status("Error: FFmpeg not found. Please install FFmpeg or imageio-ffmpeg.", "red")
        except subprocess.CalledProcessError as e:
            self.update_status(f"FFmpeg Error: {e.stderr}", "red")
        except Exception as e:
            self.update_status(f"Stitching Error: {str(e)}", "red")
        finally:
            if os.path.exists(list_file):
                try:
                    os.remove(list_file)
                except:
                    pass
            self.root.after(0, lambda: self.stitch_btn.config(state=tk.NORMAL))

    def generate_single_prompt(self, text_widget):
        self.save_project_state()
        if not self.workflow:
            messagebox.showwarning("Warning", "Please load an API JSON file first.")
            return
            
        prompt_text = text_widget.get("1.0", tk.END).strip()
        if not prompt_text:
            messagebox.showwarning("Warning", "Prompt is empty.")
            return

        video_settings, validation_error = self._collect_validated_video_settings()
        if validation_error:
            messagebox.showerror("Workflow Settings Error", validation_error)
            self.update_status(validation_error, "red")
            return

        self.log_debug("SINGLE_PROMPT_REQUESTED", prompt_preview=self._truncate_text(prompt_text, 140))
            
        self.run_queue_btn.config(state=tk.DISABLED)
        self.add_prompt_btn.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self.run_single_prompt_thread, args=(prompt_text, video_settings))
        thread.daemon = True
        thread.start()

    def run_single_prompt_thread(self, prompt_text, video_settings):
        self.update_status("Generating single clip...", "blue")
        self.update_debug_prompt_status(prompt_text)
        self.log_debug("SINGLE_PROMPT_THREAD_START", prompt_preview=self._truncate_text(prompt_text, 140))

        filename_prefix = self._build_video_filename_prefix(video_settings, "single")

        workflow_to_submit = self._build_video_workflow_for_prompt(
            prompt_text,
            filename_prefix,
            video_settings
        )
            
        prompt_id = self.queue_prompt(workflow_to_submit)
        if prompt_id:
            self.log_debug("SINGLE_PROMPT_QUEUED", prompt_id=prompt_id)
            success = self.wait_for_completion(prompt_id)
            if success:
                self.update_status("Single clip generated successfully!", "green")
                self.log_debug("SINGLE_PROMPT_COMPLETE", prompt_id=prompt_id, success=True)
            else:
                self.update_status("Failed to generate single clip.", "red")
                self.log_debug("SINGLE_PROMPT_COMPLETE", prompt_id=prompt_id, success=False)
                
        self.root.after(0, lambda: self.run_queue_btn.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.add_prompt_btn.config(state=tk.NORMAL))

    def start_queue(self):
        self.save_project_state()
        if not self.workflow:
            messagebox.showwarning("Warning", "Please load an API JSON file first.")
            return
            
        prompts_text = self._collect_prompt_texts()
        if not prompts_text:
            messagebox.showwarning("Warning", "Please add at least one prompt.")
            return

        video_settings, validation_error = self._collect_validated_video_settings()
        if validation_error:
            messagebox.showerror("Workflow Settings Error", validation_error)
            self.update_status(validation_error, "red")
            return

        self.log_debug("QUEUE_START", prompt_count=len(prompts_text), previews=[self._truncate_text(p, 120) for p in prompts_text])
            
        self.run_queue_btn.config(state=tk.DISABLED)
        self.add_prompt_btn.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self.run_queue, args=(prompts_text, video_settings))
        thread.daemon = True
        thread.start()

    def run_queue(self, prompts_text, video_settings):
        total = len(prompts_text)
        
        for i, prompt_text in enumerate(prompts_text, start=1):
            self.update_status(f"Generating {i} of {total}...", "blue")
            self.update_debug_prompt_status(prompt_text, current=i, total=total)
            self.log_debug("QUEUE_ITEM_START", index=i, total=total, prompt_preview=self._truncate_text(prompt_text, 140))

            filename_prefix = self._build_video_filename_prefix(video_settings, "queue", i)

            workflow_to_submit = self._build_video_workflow_for_prompt(
                prompt_text,
                filename_prefix,
                video_settings
            )
                
            # Send POST request
            prompt_id = self.queue_prompt(workflow_to_submit)
            if not prompt_id:
                self.log_debug("QUEUE_ITEM_ABORTED", index=i, reason="queue_prompt_failed")
                break
            self.log_debug("QUEUE_ITEM_QUEUED", index=i, prompt_id=prompt_id)
                
            # Polling Loop
            success = self.wait_for_completion(prompt_id)
            if not success:
                self.log_debug("QUEUE_ITEM_FAILED", index=i, prompt_id=prompt_id)
                break
            self.log_debug("QUEUE_ITEM_COMPLETE", index=i, prompt_id=prompt_id)
                
        else:
            self.update_status("Finished all prompts!", "green")
            self.log_debug("QUEUE_COMPLETE", total=total)
            
        self.root.after(0, lambda: self.run_queue_btn.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.add_prompt_btn.config(state=tk.NORMAL))

    def queue_prompt(self, workflow):
        prompt_preview = self._get_workflow_role_value(workflow, "prompt", default="")

        self.log_debug(
            "QUEUE_PROMPT_POST",
            prompt_preview=self._truncate_text(prompt_preview, 160)
        )

        p = {"prompt": workflow}
        data = json.dumps(p).encode('utf-8')
        req = urllib.request.Request("http://127.0.0.1:8188/prompt", data=data)
        req.add_header('Content-Type', 'application/json')
        
        max_retries = 6
        for attempt in range(max_retries):
            try:
                with urllib.request.urlopen(req, timeout=15) as response:
                    try:
                        response_data = json.loads(response.read())
                    except json.JSONDecodeError:
                        self.update_status("Error: Invalid JSON response from ComfyUI", "red")
                        self.log_debug("QUEUE_PROMPT_ERROR", reason="invalid_json_response")
                        return None
                    self.log_debug("QUEUE_PROMPT_ACCEPTED", prompt_id=response_data.get("prompt_id"))
                    return response_data.get("prompt_id")
            except urllib.error.HTTPError as e:
                if e.code == 400:
                    self.update_status("Error: 400 Bad Request (Invalid JSON workflow).", "red")
                    self.log_debug("QUEUE_PROMPT_ERROR", reason="http_400", details=str(e))
                    return None
                if attempt < max_retries - 1:
                    self.update_status(f"Server booting, retrying ({attempt+1}/{max_retries})...", "orange")
                    self.log_debug("QUEUE_PROMPT_RETRY", attempt=attempt + 1, max_retries=max_retries, reason=f"HTTPError:{e.code}")
                    time.sleep(5)
                else:
                    self.update_status("Error: Cannot connect to ComfyUI after retries", "red")
                    self.log_debug("QUEUE_PROMPT_ERROR", reason="http_error_retries_exhausted", code=e.code)
                    return None
            except urllib.error.URLError as e:
                if attempt < max_retries - 1:
                    self.update_status(f"Server booting, retrying ({attempt+1}/{max_retries})...", "orange")
                    self.log_debug("QUEUE_PROMPT_RETRY", attempt=attempt + 1, max_retries=max_retries, reason=f"URLError:{getattr(e, 'reason', str(e))}")
                    time.sleep(5)
                else:
                    self.update_status("Error: Cannot connect to ComfyUI after retries", "red")
                    self.log_debug("QUEUE_PROMPT_ERROR", reason="url_error_retries_exhausted", details=str(getattr(e, 'reason', str(e))))
                    return None
            except Exception as e:
                self.update_status(f"Error: {str(e)}", "red")
                self.log_debug("QUEUE_PROMPT_ERROR", reason="unexpected_exception", details=str(e))
                return None

    def download_comfyui_video(self, filename, subfolder, folder_type, dest_path):
        try:
            url = f"http://127.0.0.1:8188/view?filename={urllib.parse.quote(filename)}&subfolder={urllib.parse.quote(subfolder)}&type={urllib.parse.quote(folder_type)}"
            urllib.request.urlretrieve(url, dest_path)
            return True
        except Exception as e:
            print(f"Error downloading file: {e}")
            return False

    def wait_for_completion(self, prompt_id, is_music=False):
        error_count = 0
        while True:
            try:
                # Check history
                req_history = urllib.request.Request(f"http://127.0.0.1:8188/history/{prompt_id}")
                with urllib.request.urlopen(req_history, timeout=5) as response:
                    try:
                        history = json.loads(response.read())
                        error_count = 0
                    except json.JSONDecodeError:
                        time.sleep(3)
                        continue
                    if prompt_id in history:
                        self.log_debug("PROMPT_HISTORY_FOUND", prompt_id=prompt_id, is_music=is_music)
                        # Extract output filename and download
                        try:
                            outputs = history[prompt_id].get('outputs', {})
                            for node_id, node_output in outputs.items():
                                media_list = node_output.get('gifs', []) + node_output.get('images', []) + node_output.get('audio', [])
                                for media in media_list:
                                    filename = media.get('filename', '')
                                    if filename.endswith('.mp4') and not is_music:
                                        subfolder = media.get('subfolder', '')
                                        folder_type = media.get('type', 'output')
                                        
                                        dest_path = os.path.join(self.scenes_dir, filename)
                                        if self.download_comfyui_video(filename, subfolder, folder_type, dest_path):
                                            self.root.after(0, self.refresh_gallery)
                                            self.log_debug("PROMPT_OUTPUT_DOWNLOADED", prompt_id=prompt_id, media_type="video", filename=filename, dest_path=dest_path)
                                        break
                                    elif filename.endswith('.mp3') and is_music:
                                        subfolder = media.get('subfolder', '')
                                        folder_type = media.get('type', 'output')
                                        
                                        dest_path = os.path.join(self.audio_dir, filename)
                                        if self.download_comfyui_video(filename, subfolder, folder_type, dest_path):
                                            self.current_generated_audio = dest_path
                                            self.log_debug("PROMPT_OUTPUT_DOWNLOADED", prompt_id=prompt_id, media_type="audio", filename=filename, dest_path=dest_path)
                                        break
                        except Exception as e:
                            print(f"Error parsing history for output: {e}")
                            self.log_debug("PROMPT_HISTORY_PARSE_ERROR", prompt_id=prompt_id, details=str(e))
                        return True
                
                # Check queue
                req_queue = urllib.request.Request("http://127.0.0.1:8188/queue")
                with urllib.request.urlopen(req_queue, timeout=5) as response:
                    try:
                        queue_data = json.loads(response.read())
                        error_count = 0
                    except json.JSONDecodeError:
                        time.sleep(3)
                        continue
                    
                    # queue_data has "queue_running" and "queue_pending"
                    # Each is a list of items, where item[1] is the prompt_id
                    in_queue = False
                    for q_list in [queue_data.get("queue_running", []), queue_data.get("queue_pending", [])]:
                        for item in q_list:
                            if item[1] == prompt_id:
                                in_queue = True
                                break
                        if in_queue:
                            break
                            
                    if not in_queue:
                        # Final race-condition check
                        req_history_check = urllib.request.Request(f"http://127.0.0.1:8188/history/{prompt_id}")
                        with urllib.request.urlopen(req_history_check, timeout=5) as response:
                            try:
                                history_check = json.loads(response.read())
                                if prompt_id in history_check:
                                    self.log_debug("PROMPT_HISTORY_FOUND_FINAL_CHECK", prompt_id=prompt_id)
                                    return True
                            except json.JSONDecodeError:
                                pass
                        
                        self.update_status(f"Error: Prompt {prompt_id} failed or was cancelled in ComfyUI", "red")
                        self.update_music_status(f"Error: Prompt {prompt_id} failed or was cancelled in ComfyUI", "red")
                        self.log_debug("PROMPT_FAILED_OR_CANCELLED", prompt_id=prompt_id)
                        return False

            except urllib.error.URLError as e:
                error_count += 1
                if error_count >= 10:
                    self.update_status("Fatal Error: Server unresponsive. Aborting.", "red")
                    self.update_music_status("Fatal Error: Server unresponsive. Aborting.", "red")
                    return False
                # Don't abort on timeouts or temporary connection refusals under heavy GPU load
                error_reason = getattr(e, 'reason', str(e))
                self.update_status(f"Server busy or timeout ({error_reason}). Waiting...", "orange")
                self.update_music_status(f"Server busy or timeout ({error_reason}). Waiting...", "orange")
                self.log_debug("PROMPT_POLL_RETRY", prompt_id=prompt_id, error=str(error_reason), error_count=error_count)
                pass # Let it fall through to time.sleep(3) and try again
            except Exception as e:
                error_count += 1
                if error_count >= 10:
                    self.update_status("Fatal Error: Server unresponsive. Aborting.", "red")
                    self.update_music_status("Fatal Error: Server unresponsive. Aborting.", "red")
                    return False
                self.update_status(f"Polling error: {str(e)}. Retrying...", "orange")
                self.update_music_status(f"Polling error: {str(e)}. Retrying...", "orange")
                self.log_debug("PROMPT_POLL_EXCEPTION", prompt_id=prompt_id, error=str(e), error_count=error_count)
                pass # Let it fall through to time.sleep(3) and try again
                
            time.sleep(3)

    def generate_music(self):
        self.save_project_state()
        if not self.music_workflow:
            messagebox.showwarning("Warning", "Music workflow JSON not loaded.")
            return
            
        if not self.selected_video_for_music:
            messagebox.showwarning("Warning", "Please select a video from the Video Generation tab first.")
            return
            
        tags = self.music_tags_text.get("1.0", tk.END).strip()
        lyrics = self.music_lyrics_text.get("1.0", tk.END).strip()
        
        if not tags and not lyrics:
            messagebox.showwarning("Warning", "Please enter some tags or lyrics.")
            return
            
        self.gen_music_btn.config(state=tk.DISABLED)
        self.preview_music_btn.config(state=tk.DISABLED)
        self.merge_music_btn.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self.run_music_generation, args=(tags, lyrics))
        thread.daemon = True
        thread.start()

    def run_music_generation(self, tags, lyrics):
        self.update_music_status("Generating Music...", "blue")
        
        try:
            # Update workflow
            self.music_workflow["94"]["inputs"]["tags"] = tags
            self.music_workflow["94"]["inputs"]["lyrics"] = lyrics
            self.music_workflow["94"]["inputs"]["duration"] = self.music_duration_var.get()
            self.music_workflow["94"]["inputs"]["bpm"] = self.music_bpm_var.get()
            self.music_workflow["94"]["inputs"]["keyscale"] = self.music_key_var.get()
            self.music_workflow["94"]["inputs"]["seed"] = random.randint(1, 999999999)
            self.music_workflow["3"]["inputs"]["seed"] = random.randint(1, 999999999)
            self.music_workflow["98"]["inputs"]["seconds"] = self.music_duration_var.get()
            self.music_workflow["107"]["inputs"]["filename_prefix"] = f"ACE_Music_{int(time.time())}"
        except KeyError as e:
            self.update_music_status(f"Error: Missing node in JSON ({e})", "red")
            self.root.after(0, lambda: self.gen_music_btn.config(state=tk.NORMAL))
            return
            
        prompt_id = self.queue_prompt(self.music_workflow)
        if not prompt_id:
            self.root.after(0, lambda: self.gen_music_btn.config(state=tk.NORMAL))
            return
            
        success = self.wait_for_completion(prompt_id, is_music=True)
        
        if success and self.current_generated_audio:
            self.update_music_status("Music Generation Complete! Ready to preview or merge.", "green")
            self.root.after(0, lambda: self.preview_music_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.merge_music_btn.config(state=tk.NORMAL))
            self.root.after(0, self._refresh_music_sidebar_state)
        else:
            self.update_music_status("Music Generation Failed.", "red")
            self.root.after(0, self._refresh_music_sidebar_state)
            
        self.root.after(0, lambda: self.gen_music_btn.config(state=tk.NORMAL))

    def preview_audio(self):
        if self.current_generated_audio and os.path.exists(self.current_generated_audio):
            try:
                os.startfile(self.current_generated_audio)
            except Exception as e:
                messagebox.showerror("Error", f"Could not play audio:\n{e}")

    def preview_final_video(self):
        if hasattr(self, 'current_final_video') and self.current_final_video and os.path.exists(self.current_final_video):
            try:
                os.startfile(self.current_final_video)
            except Exception as e:
                messagebox.showerror("Error", f"Could not play video:\n{e}")

    def merge_audio_video(self):
        if not self.selected_video_for_music or not self.current_generated_audio:
            return
            
        self.merge_music_btn.config(state=tk.DISABLED)
        self.gen_music_btn.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self.process_merge)
        thread.daemon = True
        thread.start()

    def process_merge(self):
        self.update_music_status("Merging Audio and Video...", "blue")
        timestamp = int(time.time())
        output_file = os.path.join(self.final_mv_dir, f"Final_Music_Video_{timestamp}.mp4")
        
        try:
            # -map 0:v:0 (take video from first input)
            # -map 1:a:0 (take audio from second input)
            # -c:v copy (copy video stream without re-encoding)
            # -c:a aac (encode audio to aac for mp4 compatibility)
            # -shortest (finish encoding when the shortest input stream ends)
            cmd = [
                FFMPEG_PATH, '-y', 
                '-i', self.selected_video_for_music, 
                '-i', self.current_generated_audio, 
                '-map', '0:v:0', '-map', '1:a:0', 
                '-c:v', 'copy', '-c:a', 'aac', 
                '-shortest', output_file
            ]
            
            subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW, capture_output=True, text=True, check=True)
            
            self.current_final_video = output_file
            self.update_music_status(f"Merge Complete! Saved as {os.path.basename(output_file)}", "green")
            self.root.after(0, self.refresh_gallery)
            self.root.after(0, lambda: self.preview_final_btn.config(state=tk.NORMAL))
            self.root.after(0, self._refresh_music_sidebar_state)
            
        except FileNotFoundError:
            self.update_music_status("Error: FFmpeg not found.", "red")
        except subprocess.CalledProcessError as e:
            self.update_music_status(f"FFmpeg Error: {e.stderr}", "red")
        except Exception as e:
            self.update_music_status(f"Merge Error: {str(e)}", "red")
        finally:
            self.root.after(0, lambda: self.merge_music_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.gen_music_btn.config(state=tk.NORMAL))
            self.root.after(0, self._refresh_music_sidebar_state)

    def on_closing(self):
        self.save_global_settings()
        self.save_project_state()
        if self.comfyui_process:
            try:
                subprocess.run(['TASKKILL', '/F', '/T', '/PID', str(self.comfyui_process.pid)], creationflags=subprocess.CREATE_NO_WINDOW)
            except Exception:
                pass
        self.root.destroy()

if __name__ == "__main__":
    root = tb.Window(themename=THEME_NAME)
    app = LTXQueueManager(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
