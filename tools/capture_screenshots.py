#!/usr/bin/env python3
"""
Automated screenshot capture for Prompt2MTV README.

Mirrors the tutorial flow from tools/tutorial_runner.py, capturing 13
screenshots — one per significant phase — with real AI-generated output
and a neon-glow highlight on the key widget per shot.

Prerequisites:
    - ComfyUI must be running (or will be launched by the app)
    - Required models must be installed (LTX-Video, ACE-Step music, z-image)
    - A chatbot backend (Ollama / managed) must be reachable

Usage:
    python tools/capture_screenshots.py
"""

import ctypes
import glob
import os
import sys
import time
import tkinter as tk
from contextlib import suppress
from tkinter import messagebox as _original_messagebox
import urllib.request
import urllib.error

# ── DPI awareness (must be set before any Tk import) ────────────────────────
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

# ── Redirect modal messageboxes to stdout (prevents script from blocking) ───
_real_showerror = _original_messagebox.showerror
_real_showwarning = _original_messagebox.showwarning
_real_showinfo = _original_messagebox.showinfo


def _intercept_showerror(title="", message="", **kw):
    print(f"  [messagebox.showerror] {title}: {message}")


def _intercept_showwarning(title="", message="", **kw):
    print(f"  [messagebox.showwarning] {title}: {message}")


def _intercept_showinfo(title="", message="", **kw):
    print(f"  [messagebox.showinfo] {title}: {message}")


_original_messagebox.showerror = _intercept_showerror
_original_messagebox.showwarning = _intercept_showwarning
_original_messagebox.showinfo = _intercept_showinfo

# ── Ensure project root is on sys.path ──────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from PIL import ImageGrab  # noqa: E402

SCREENSHOT_DIR = os.path.join(PROJECT_ROOT, "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

TARGET_WIDTH = 1280

# ── Tutorial-matching constants ─────────────────────────────────────────────
TUTORIAL_WIDTH = 320
TUTORIAL_HEIGHT = 192
TUTORIAL_FPS = 8
TUTORIAL_LENGTH_FRAMES = 41
TUTORIAL_IMAGE_WIDTH = 512
TUTORIAL_IMAGE_HEIGHT = 512
TUTORIAL_IMAGE_STEPS = 12
TUTORIAL_IMAGE_CFG = 3.0
TUTORIAL_IMAGE_DENOISE = 1.0
TUTORIAL_DURATION_SECONDS = 5

CHATBOT_BRIEF = (
    "Plan exactly one beginner-friendly scene for a 5-second tutorial demo "
    "clip featuring a futuristic neon cube reveal. Return exactly one usable "
    "scene prompt."
)
MUSIC_TAGS = (
    "fast synthwave arpeggio, cyber pulse, warm bass, futuristic tension, "
    "clean electronic beat"
)

# ── Fallback chatbot conversation if backend is unavailable ─────────────────
CHATBOT_FALLBACK_TURNS = [
    ("user", CHATBOT_BRIEF),
    (
        "assistant",
        "Here is a single scene plan for a 5-second tutorial demo:\n\n"
        "**Scene 1 — Neon Cube Reveal**\n"
        "A glowing futuristic neon cube spins slowly against pure black space. "
        "Crisp teal edge-light rims every face. The camera drifts inward as the "
        "cube rotates, catching sharp reflections. Cinematic, high-contrast, clean.\n\n"
        "Prompt: A glowing futuristic neon cube spinning in empty space, cinematic "
        "lighting, clean background, high contrast, polished reflections",
    ),
]


# ═════════════════════════════════════════════════════════════════════════════
# Event-loop helpers (proven stable across 4 iterations)
# ═════════════════════════════════════════════════════════════════════════════

def _pump(root, seconds):
    """Run root.mainloop() for *seconds*, then return."""
    root.after(max(1, int(seconds * 1000)), root.quit)
    root.mainloop()


def _settle(root, delay=0.5):
    _pump(root, delay)


def _wait_for(root, condition_fn, timeout=300, interval=0.5, label="condition"):
    start = time.time()
    while time.time() - start < timeout:
        _pump(root, interval)
        if condition_fn():
            elapsed = time.time() - start
            print(f"    OK {label} after {elapsed:.1f}s")
            return True
    elapsed = time.time() - start
    print(f"    TIMEOUT {label} after {elapsed:.1f}s")
    return False


def _comfyui_reachable():
    try:
        req = urllib.request.Request("http://127.0.0.1:8188/system_stats")
        with urllib.request.urlopen(req, timeout=5):
            return True
    except Exception:
        return False


# ═════════════════════════════════════════════════════════════════════════════
# Highlight system (ported from tutorial_runner.py)
# ═════════════════════════════════════════════════════════════════════════════

_highlight_window = None
_highlight_canvas = None
_highlight_job = None
_highlight_pulse_job = None
_highlight_outline_ids = []


def _remove_highlight(root):
    global _highlight_window, _highlight_canvas, _highlight_job, _highlight_pulse_job, _highlight_outline_ids
    if _highlight_pulse_job is not None:
        with suppress(tk.TclError):
            root.after_cancel(_highlight_pulse_job)
    _highlight_pulse_job = None
    if _highlight_job is not None:
        with suppress(tk.TclError):
            root.after_cancel(_highlight_job)
    _highlight_job = None
    _highlight_outline_ids = []
    _highlight_canvas = None
    if _highlight_window:
        with suppress(tk.TclError):
            _highlight_window.destroy()
    _highlight_window = None


def _show_highlight(root, x, y, width, height, duration_ms=3000, color="#00ffcc"):
    """Neon-glow highlight overlay (transparent Toplevel with pulse)."""
    global _highlight_window, _highlight_canvas, _highlight_job, _highlight_pulse_job, _highlight_outline_ids
    _remove_highlight(root)
    if width <= 0 or height <= 0:
        return

    transparent = "#010203"
    _highlight_window = tk.Toplevel(root)
    _highlight_window.overrideredirect(True)
    _highlight_window.attributes("-topmost", True)
    with suppress(tk.TclError):
        _highlight_window.attributes("-transparentcolor", transparent)
    _highlight_window.configure(bg=transparent)
    _highlight_window.geometry(f"{int(width)}x{int(height)}+{int(x)}+{int(y)}")
    _highlight_window.lift()

    _highlight_canvas = tk.Canvas(
        _highlight_window,
        width=int(width), height=int(height),
        bg=transparent, highlightthickness=0, bd=0,
    )
    _highlight_canvas.pack(fill=tk.BOTH, expand=True)

    inset = 4
    glow_rect = _highlight_canvas.create_rectangle(
        inset, inset,
        max(inset + 2, width - inset), max(inset + 2, height - inset),
        outline=color, width=4,
    )
    accent_rect = _highlight_canvas.create_rectangle(
        inset + 6, inset + 6,
        max(inset + 8, width - inset - 6), max(inset + 8, height - inset - 6),
        outline="#ffffff", width=1,
    )

    corner = 18
    _highlight_outline_ids = [glow_rect, accent_rect]
    corners = [
        (inset, inset, inset + corner, inset, inset, inset + corner),
        (width - inset, inset, width - inset - corner, inset, width - inset, inset + corner),
        (inset, height - inset, inset + corner, height - inset, inset, height - inset - corner),
        (width - inset, height - inset, width - inset - corner, height - inset, width - inset, height - inset - corner),
    ]
    for x1, y1, x2, y2, x3, y3 in corners:
        _highlight_outline_ids.append(
            _highlight_canvas.create_line(x1, y1, x2, y2, fill=color, width=3)
        )
        _highlight_outline_ids.append(
            _highlight_canvas.create_line(x1, y1, x3, y3, fill=color, width=3)
        )

    pulse_colors = [color, "#7fffe6", "#ffffff", "#7fffe6"]

    def pulse(index=0):
        if not _highlight_canvas:
            return
        current_color = pulse_colors[index % len(pulse_colors)]
        for item_id in _highlight_outline_ids:
            w = 4 if item_id == glow_rect else 2
            if item_id in (glow_rect, accent_rect):
                _highlight_canvas.itemconfig(
                    item_id,
                    outline=current_color if item_id == glow_rect else "#ffffff",
                    width=w,
                )
            else:
                _highlight_canvas.itemconfig(
                    item_id,
                    fill=current_color,
                    width=2 if current_color == "#ffffff" else 3,
                )
        global _highlight_pulse_job
        _highlight_pulse_job = root.after(140, lambda: pulse(index + 1))

    pulse()
    _highlight_job = root.after(duration_ms, lambda: _remove_highlight(root))


def _get_widget_region(widget, pad=8):
    try:
        widget.update_idletasks()
        return (
            widget.winfo_rootx() - pad,
            widget.winfo_rooty() - pad,
            widget.winfo_width() + pad * 2,
            widget.winfo_height() + pad * 2,
        )
    except tk.TclError:
        return None


def _widget_is_descendant_of(widget, ancestor):
    if not widget or not ancestor:
        return False
    current = widget
    while current:
        if current == ancestor:
            return True
        current = getattr(current, "master", None)
    return False


def _get_viewport_config(app, widget):
    viewport_candidates = [
        {"canvas": getattr(app, "scene_canvas", None), "frame": getattr(app, "scene_scrollable_frame", None), "tab": getattr(app, "video_tab", None)},
        {"canvas": getattr(app, "settings_canvas", None), "frame": getattr(app, "settings_frame", None), "tab": getattr(app, "video_tab", None)},
        {"canvas": getattr(app, "image_canvas", None), "frame": getattr(app, "image_scrollable_frame", None), "tab": getattr(app, "image_tab", None)},
        {"canvas": getattr(app, "image_tab_canvas", None), "frame": getattr(app, "image_main_frame", None), "tab": getattr(app, "image_tab", None)},
        {"canvas": getattr(app, "gallery_canvas", None), "frame": getattr(app, "gallery_inner_frame", None), "tab": getattr(app, "gallery_tab", None)},
        {"canvas": getattr(app, "music_canvas", None), "frame": getattr(app, "music_main_frame", None), "tab": getattr(app, "music_tab", None)},
        {"canvas": getattr(app, "chatbot_transcript_canvas", None), "frame": getattr(app, "chatbot_transcript_frame", None), "tab": getattr(app, "chatbot_tab", None)},
        {"canvas": getattr(app, "chatbot_history_canvas", None), "frame": getattr(app, "chatbot_history_frame", None), "tab": getattr(app, "chatbot_tab", None)},
    ]
    for vp in viewport_candidates:
        if _widget_is_descendant_of(widget, vp.get("frame")):
            return vp
    return None


def _get_relative_y(widget, ancestor):
    current = widget
    relative_y = 0
    while current and current != ancestor:
        relative_y += int(current.winfo_y())
        current = getattr(current, "master", None)
    return relative_y if current == ancestor else None


def _scroll_widget_into_view(app, widget, align="center"):
    viewport = _get_viewport_config(app, widget)
    if not widget or not viewport:
        return False
    canvas = viewport.get("canvas")
    anchor_frame = viewport.get("frame")
    tab_widget = viewport.get("tab")
    if not canvas or not anchor_frame:
        return False
    try:
        if tab_widget and hasattr(app, "notebook"):
            app.notebook.select(tab_widget)
        app.root.update_idletasks()
        relative_y = _get_relative_y(widget, anchor_frame)
        if relative_y is None:
            return False
        content_height = max(int(anchor_frame.winfo_height()), 1)
        viewport_height = max(int(canvas.winfo_height()), 1)
        widget_height = max(int(widget.winfo_height()), 1)
        max_offset = max(content_height - viewport_height, 0)
        if align == "top":
            target_offset = relative_y
        else:
            target_offset = relative_y - max((viewport_height - widget_height) // 2, 0)
        target_offset = max(0, min(target_offset, max_offset))
        canvas.yview_moveto(0 if content_height <= 0 else target_offset / max(content_height, 1))
        app.root.update_idletasks()
        return True
    except tk.TclError:
        return False


def _highlight_widget(root, app, widget, duration_ms=3000, pad=8, color="#00ffcc"):
    """Scroll widget into view, then show highlight overlay."""
    if not widget:
        return
    _scroll_widget_into_view(app, widget)
    region = _get_widget_region(widget, pad=pad)
    if not region:
        return
    x, y, w, h = region
    _show_highlight(root, x, y, w, h, duration_ms=duration_ms, color=color)
    with suppress(tk.TclError):
        widget.focus_set()


# ═════════════════════════════════════════════════════════════════════════════
# Screenshot capture helpers
# ═════════════════════════════════════════════════════════════════════════════

def _grab_window(root):
    root.lift()
    root.attributes("-topmost", True)
    _settle(root, 0.3)
    root.attributes("-topmost", False)
    x = root.winfo_rootx()
    y = root.winfo_rooty()
    w = root.winfo_width()
    h = root.winfo_height()
    return ImageGrab.grab(bbox=(x, y, x + w, y + h))


def _save(img, name):
    ratio = TARGET_WIDTH / img.width
    new_size = (TARGET_WIDTH, int(img.height * ratio))
    img = img.resize(new_size, resample=3)
    path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    img.save(path, "PNG", optimize=True)
    print(f"  saved {path}  ({new_size[0]}x{new_size[1]})")
    return path


def _capture(root, app, name, highlight_widget=None, highlight_color="#00ffcc",
             highlight_duration=3000, highlight_pad=8):
    """Highlight a widget and capture the screenshot."""
    if highlight_widget:
        _highlight_widget(root, app, highlight_widget,
                          duration_ms=highlight_duration, pad=highlight_pad,
                          color=highlight_color)
        _settle(root, 0.8)
    img = _grab_window(root)
    _remove_highlight(root)
    return _save(img, name)


def _open_section(app, key):
    app._set_collapsible_section_open(key, True)


# ═════════════════════════════════════════════════════════════════════════════
# Tutorial helper methods (ported from tutorial_runner.py)
# ═════════════════════════════════════════════════════════════════════════════

def _has_chatbot_scene_plan(app):
    result = getattr(app, "chatbot_last_result", None) or {}
    scenes = result.get("scenes") if isinstance(result, dict) else None
    return isinstance(scenes, list) and any(
        str((scene or {}).get("prompt") or "").strip() for scene in scenes
    )


def _get_latest_image_asset(app):
    image_assets = getattr(app, "image_assets", []) or []
    generated = []
    for asset in image_assets:
        if not isinstance(asset, dict):
            continue
        path = str(asset.get("project_path") or "").strip()
        if not path or not os.path.exists(path):
            continue
        if os.path.normcase(os.path.dirname(path)) != os.path.normcase(app.generated_image_dir):
            continue
        generated.append(asset)
    if not generated:
        return None
    return max(generated, key=lambda a: os.path.getmtime(str(a.get("project_path") or "")))


def _set_first_scene_to_i2v(app, image_asset):
    scene_frames = getattr(app, "scene_entry_frames", []) or []
    if not scene_frames or not isinstance(image_asset, dict):
        return False
    scene_frame = scene_frames[0]
    image_asset_id = str(image_asset.get("asset_id") or "").strip()
    if not image_asset_id:
        return False
    if hasattr(app, "_refresh_scene_asset_choices"):
        app._refresh_scene_asset_choices()
    if hasattr(scene_frame, "mode_var"):
        scene_frame.mode_var.set("Image to Video")
    if hasattr(app, "_refresh_scene_entry_rows"):
        app._refresh_scene_entry_rows()
    option_reverse_map = getattr(scene_frame, "asset_option_reverse_map", {}) or {}
    image_label = option_reverse_map.get(image_asset_id)
    if not image_label:
        return False
    scene_frame.image_asset_var.set(image_label)
    if hasattr(app, "_handle_scene_asset_selection"):
        app._handle_scene_asset_selection(scene_frame)
    app.scene_timeline = app._normalize_scene_timeline(app._collect_scene_timeline_from_widgets())
    app.save_project_state()
    return True


def _get_scene_output_path(app):
    st = getattr(app, "scene_timeline", []) or []
    if not st or not isinstance(st[0], dict):
        return None
    return st[0].get("output_path")


def _select_gallery_video_for_stitching(app, video_path):
    app.refresh_gallery()
    app.clear_selection()
    for var, path in getattr(app, "video_checkbox_vars", []):
        if os.path.normcase(path) != os.path.normcase(video_path):
            continue
        var.set(True)
        app.toggle_video_selection(path, var)
        return True
    return False


def _get_newest_file(folder, pattern):
    files = glob.glob(os.path.join(folder, pattern))
    return max(files, key=os.path.getmtime) if files else None


# ═════════════════════════════════════════════════════════════════════════════
# Monkeypatch messagebox for the app module too
# ═════════════════════════════════════════════════════════════════════════════

def _monkeypatch_app_messagebox():
    """Also patch the messagebox imported inside ltx_queue_manager."""
    app_module = sys.modules.get("ltx_queue_manager")
    if app_module and hasattr(app_module, "messagebox"):
        app_module.messagebox.showinfo = _intercept_showinfo
        app_module.messagebox.showerror = _intercept_showerror
        app_module.messagebox.showwarning = _intercept_showwarning


# ═════════════════════════════════════════════════════════════════════════════
# Main capture flow — 13 screenshots mirroring tutorial phases
# ═════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 64)
    print("  Prompt2MTV — Tutorial-Flow Screenshot Capture (13 shots)")
    print("=" * 64)

    import ltx_queue_manager as mod

    _monkeypatch_app_messagebox()

    # ── Phase A: Launch app ─────────────────────────────────────────────
    print("\n[A] Launching app ...")
    root = mod.Prompt2MTVWindow(themename=mod.THEME_NAME)
    app = mod.LTXQueueManager(root)
    _settle(root, 2.0)

    # Wait for ComfyUI
    print("  Waiting for ComfyUI at 127.0.0.1:8188 ...")
    if not _wait_for(root, _comfyui_reachable, timeout=180, interval=2.0, label="ComfyUI ready"):
        print("  ComfyUI not reachable — generation phases will skip.")
    else:
        # Clear any pre-existing jobs so our jobs run immediately
        try:
            import json as _json
            req_int = urllib.request.Request("http://127.0.0.1:8188/interrupt", method="POST")
            urllib.request.urlopen(req_int, timeout=5)
            data = _json.dumps({"clear": True}).encode()
            req_clr = urllib.request.Request(
                "http://127.0.0.1:8188/queue", data=data, method="POST",
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req_clr, timeout=5)
            print("    Cleared ComfyUI queue.")
        except Exception as e:
            print(f"    Warning: could not clear queue: {e}")

    # ── Phase B: Project setup (mirrors tutorial phase_project_setup) ───
    print("\n[B] Creating Screenshots_Demo project ...")
    demo_dir = os.path.join(app.base_output_dir, "Screenshots_Demo")
    app.set_project(demo_dir)
    if hasattr(app, "clear_ui_fields"):
        app.clear_ui_fields()
    _settle(root, 1.0)

    # Clean prior outputs (same safety pattern as tutorial)
    project_root = os.path.normcase(os.path.realpath(demo_dir))
    cleanup_dirs = [
        app.scenes_dir, app.audio_dir,
        app.generated_image_dir, app.imported_image_dir,
        app.stitched_dir, app.final_mv_dir,
    ]
    dirs_safe = all(
        os.path.normcase(os.path.realpath(d)).startswith(project_root)
        for d in cleanup_dirs if d
    )
    if dirs_safe:
        for pattern in [
            os.path.join(app.scenes_dir, "*.mp4"),
            os.path.join(app.audio_dir, "*.wav"),
            os.path.join(app.audio_dir, "*.mp3"),
            os.path.join(app.generated_image_dir, "*.png"),
            os.path.join(app.generated_image_dir, "*.jpg"),
            os.path.join(app.generated_image_dir, "*.jpeg"),
            os.path.join(app.imported_image_dir, "*.png"),
            os.path.join(app.imported_image_dir, "*.jpg"),
            os.path.join(app.imported_image_dir, "*.jpeg"),
            os.path.join(app.stitched_dir, "*.mp4"),
            os.path.join(app.final_mv_dir, "*.mp4"),
        ]:
            for f in glob.glob(pattern):
                with suppress(OSError):
                    os.remove(f)
    app.current_generated_audio = None
    app.current_audio_source = None
    app.current_final_video = None
    app.selected_video_for_music = None
    app.selected_videos.clear()
    app.image_assets = []
    app.image_prompt_queue = []
    app.scene_timeline = []
    if hasattr(app, "_rebuild_image_prompt_queue_from_texts"):
        app._rebuild_image_prompt_queue_from_texts([])
    if hasattr(app, "_rebuild_scene_timeline_from_state"):
        app._rebuild_scene_timeline_from_state([])
    app.refresh_gallery()
    app.save_project_state()
    _settle(root, 0.5)

    saved = []
    phase_times = {}

    # ════════════════════════════════════════════════════════════════════
    # CHATBOT PHASE
    # ════════════════════════════════════════════════════════════════════

    # ── Screenshot 01: Chatbot Ready ────────────────────────────────────
    print("\n[01/13] Chatbot — ensuring model readiness ...")
    t0 = time.time()
    app.notebook.select(app.chatbot_tab)
    _settle(root, 0.3)
    _open_section(app, "chatbot_readiness")
    _settle(root, 0.3)

    chatbot_ok = False
    if app.ensure_chatbot_model_ready(interactive=False):
        if app._chatbot_generation_prerequisites_ready():
            chatbot_ok = True
    if not chatbot_ok:
        print("  Chatbot backend not immediately ready, waiting ...")
        chatbot_ok = _wait_for(
            root,
            lambda: app._chatbot_generation_prerequisites_ready(),
            timeout=60,
            interval=2.0,
            label="chatbot prerequisites",
        )

    saved.append(_capture(root, app, "01_chatbot_ready",
                          highlight_widget=getattr(app, "chatbot_setup_btn", None),
                          highlight_color="#00ffcc"))
    phase_times["01_chatbot_ready"] = time.time() - t0

    # ── Screenshot 02: Chatbot Plan ─────────────────────────────────────
    print("\n[02/13] Chatbot — planning scenes ...")
    t0 = time.time()
    app.notebook.select(app.chatbot_tab)
    _open_section(app, "chatbot_focus_workspace")
    _settle(root, 0.3)

    if chatbot_ok:
        # Set task to Plan Scenes
        app.chatbot_task_var.set("Plan Scenes")
        if hasattr(app, "_on_chatbot_task_changed"):
            app._on_chatbot_task_changed()
        _settle(root, 0.2)

        # Fill briefing
        app.chatbot_briefing_text.delete("1.0", tk.END)
        app.chatbot_briefing_text.insert("1.0", CHATBOT_BRIEF)
        _settle(root, 0.2)

        # Invoke plan
        if hasattr(app, "chatbot_scene_plan_btn"):
            app.chatbot_scene_plan_btn.invoke()

        plan_ok = _wait_for(
            root,
            lambda: not getattr(app, "chatbot_generation_in_progress", True),
            timeout=180,
            interval=0.5,
            label="chatbot plan complete",
        )

        if not plan_ok or not _has_chatbot_scene_plan(app):
            print("  Chatbot plan failed — injecting fallback")
            chatbot_ok = False

    if not chatbot_ok:
        conv_id = app._ensure_active_chatbot_conversation(title="Screenshot Demo")
        for role, content in CHATBOT_FALLBACK_TURNS:
            app._append_chatbot_turn(role, content, kind="plan", conversation_id=conv_id)
        app._refresh_chatbot_transcript()
        _settle(root, 0.3)

    saved.append(_capture(root, app, "02_chatbot_planning",
                          highlight_widget=getattr(app, "chatbot_briefing_text", None),
                          highlight_color="#00ffcc", highlight_pad=6))
    phase_times["02_chatbot_plan"] = time.time() - t0

    # ── Screenshot 03: Apply Plan ───────────────────────────────────────
    print("\n[03/13] Chatbot — applying plan to scene timeline ...")
    t0 = time.time()
    app.notebook.select(app.chatbot_tab)
    _open_section(app, "chatbot_focus_workspace")
    _settle(root, 0.2)

    if hasattr(app, "chatbot_apply_btn"):
        app.chatbot_apply_btn.invoke()
    _settle(root, 0.5)

    # Verify scenes populated
    scene_frames = getattr(app, "scene_entry_frames", [])
    if not scene_frames:
        print("  Apply did not populate scenes — adding manual scene")
        app._clear_all_scene_timeline_entries()
        scene_data = app._create_scene_entry(
            order_index=1,
            mode=mod.SCENE_MODE_T2V,
            prompt="A glowing futuristic neon cube spinning in empty space, cinematic lighting, "
                   "clean background, high contrast, polished reflections",
        )
        app.add_scene_timeline_entry(scene_data)
        _settle(root, 0.3)

    saved.append(_capture(root, app, "03_chatbot_apply",
                          highlight_widget=getattr(app, "chatbot_apply_btn", None),
                          highlight_color="#00ffcc"))
    phase_times["03_chatbot_apply"] = time.time() - t0

    # ════════════════════════════════════════════════════════════════════
    # IMAGE PHASE
    # ════════════════════════════════════════════════════════════════════

    # ── Sync prompt from scene timeline to image queue ──────────────────
    print("\n[--] Syncing prompts to image queue ...")
    app.notebook.select(app.video_tab)
    _settle(root, 0.2)
    if hasattr(app, "sync_t2v_to_image_queue_btn"):
        app.sync_t2v_to_image_queue_btn.invoke()
    _settle(root, 0.3)

    # ── Screenshot 04: Image Config ─────────────────────────────────────
    print("\n[04/13] Image — configuring settings ...")
    t0 = time.time()
    app.notebook.select(app.image_tab)
    _settle(root, 0.3)
    _open_section(app, "image_utilities")
    _open_section(app, "image_workflow_settings")
    _settle(root, 0.2)

    # Configure image settings (tutorial pattern)
    if hasattr(app, "reset_image_settings_defaults"):
        app.reset_image_settings_defaults()
    app.refresh_image_model_choices()

    app.image_width_var.set(str(TUTORIAL_IMAGE_WIDTH))
    app.image_height_var.set(str(TUTORIAL_IMAGE_HEIGHT))
    app.image_steps_var.set(str(TUTORIAL_IMAGE_STEPS))
    app.image_cfg_var.set(str(TUTORIAL_IMAGE_CFG))
    app.image_denoise_var.set(str(TUTORIAL_IMAGE_DENOISE))

    image_choices = getattr(app, "image_model_choices", {}) or {}
    for field_name, var_name in [
        ("clip_name", "image_clip_name_var"),
        ("vae_name", "image_vae_name_var"),
        ("unet_name", "image_unet_name_var"),
    ]:
        var = getattr(app, var_name, None)
        if not var:
            continue
        if str(var.get() or "").strip():
            continue
        choices = image_choices.get(field_name) or []
        if choices:
            var.set(str(choices[0]))

    _settle(root, 0.3)

    saved.append(_capture(root, app, "04_image_config",
                          highlight_widget=getattr(app, "reset_image_settings_btn", None),
                          highlight_color="#ff6ec7"))
    phase_times["04_image_config"] = time.time() - t0

    # ── Screenshot 05: Image Generated ──────────────────────────────────
    print("\n[05/13] Image — generating ...")
    t0 = time.time()
    app.notebook.select(app.image_tab)
    _open_section(app, "image_prompt_queue")
    _settle(root, 0.3)

    starting_image_count = len(getattr(app, "image_assets", []) or [])

    if _comfyui_reachable() and app.image_workflow:
        app.start_image_queue()
        _wait_for(
            root,
            lambda: str(app.run_image_queue_btn.cget("state")) == "disabled",
            timeout=5, interval=0.3, label="image queue started",
        )
        _wait_for(
            root,
            lambda: str(app.run_image_queue_btn.cget("state")) == "normal",
            timeout=600, interval=1.0, label="image queue complete",
        )
        app.refresh_gallery()
        _settle(root, 0.5)
    else:
        print("  ComfyUI not reachable or image workflow missing — skipping generation")

    saved.append(_capture(root, app, "05_image_generated",
                          highlight_widget=getattr(app, "run_image_queue_btn", None),
                          highlight_color="#ff6ec7"))
    phase_times["05_image_generated"] = time.time() - t0

    # ════════════════════════════════════════════════════════════════════
    # VIDEO PHASE
    # ════════════════════════════════════════════════════════════════════

    # ── Screenshot 06: Video Config ─────────────────────────────────────
    print("\n[06/13] Video — configuring settings ...")
    t0 = time.time()
    app.notebook.select(app.video_tab)
    _settle(root, 0.3)
    _open_section(app, "scene_timeline")
    _settle(root, 0.2)
    _open_section(app, "video_settings")
    _settle(root, 0.2)

    # Configure video settings (tutorial pattern)
    if hasattr(app, "reset_video_profile_defaults"):
        app.reset_video_profile_defaults()
    app.refresh_video_model_choices()

    app.video_length_var.set(str(TUTORIAL_LENGTH_FRAMES))
    app.video_width_var.set(str(TUTORIAL_WIDTH))
    app.video_height_var.set(str(TUTORIAL_HEIGHT))
    app.video_fps_var.set(str(TUTORIAL_FPS))

    video_choices = getattr(app, "video_model_choices", {}) or {}
    for field_name, var_name in [
        ("checkpoint_name", "video_checkpoint_var"),
        ("text_encoder_name", "video_text_encoder_var"),
        ("lora_name", "video_lora_var"),
        ("upscaler_name", "video_upscaler_var"),
    ]:
        var = getattr(app, var_name, None)
        if not var:
            continue
        if str(var.get() or "").strip():
            continue
        choices = video_choices.get(field_name) or []
        if choices:
            var.set(str(choices[0]))

    _settle(root, 0.3)

    saved.append(_capture(root, app, "06_video_config",
                          highlight_widget=getattr(app, "reset_video_profile_btn", None),
                          highlight_color="#c084fc"))
    phase_times["06_video_config"] = time.time() - t0

    # ── Screenshot 07: I2V Setup ────────────────────────────────────────
    print("\n[07/13] Video — setting up Image-to-Video ...")
    t0 = time.time()
    app.notebook.select(app.video_tab)
    _open_section(app, "scene_timeline")
    _settle(root, 0.3)

    image_asset = _get_latest_image_asset(app)
    i2v_ok = False
    if image_asset:
        i2v_ok = _set_first_scene_to_i2v(app, image_asset)
        if i2v_ok and hasattr(app, "_rebuild_scene_timeline_from_state"):
            app._rebuild_scene_timeline_from_state(app.scene_timeline)
        _settle(root, 0.5)
    if not i2v_ok:
        print("  No image asset for I2V — keeping T2V mode")

    scene_frames = getattr(app, "scene_entry_frames", []) or []
    highlight_target = None
    if scene_frames:
        highlight_target = getattr(scene_frames[0], "mode_combo", None) or scene_frames[0]

    saved.append(_capture(root, app, "07_video_i2v_setup",
                          highlight_widget=highlight_target,
                          highlight_color="#c084fc"))
    phase_times["07_video_i2v"] = time.time() - t0

    # ── Screenshot 08: Video Rendered ───────────────────────────────────
    print("\n[08/13] Video — rendering scene ...")
    t0 = time.time()
    app.notebook.select(app.video_tab)
    _open_section(app, "scene_timeline")
    _settle(root, 0.3)

    current_video_path = None
    if _comfyui_reachable() and app.workflow:
        app.start_scene_timeline_render()
        _wait_for(
            root,
            lambda: str(app.render_scene_timeline_btn.cget("state")) == "disabled",
            timeout=5, interval=0.3, label="render started",
        )
        _wait_for(
            root,
            lambda: (
                (_get_scene_output_path(app) and os.path.exists(_get_scene_output_path(app)))
                or str(app.render_scene_timeline_btn.cget("state")) == "normal"
            ),
            timeout=1800, interval=2.0, label="render complete",
        )
        output = _get_scene_output_path(app)
        if output and os.path.exists(output):
            current_video_path = output
        app.refresh_gallery()
        _settle(root, 0.5)
    else:
        print("  ComfyUI not reachable or video workflow missing — skipping render")

    saved.append(_capture(root, app, "08_video_rendered",
                          highlight_widget=getattr(app, "render_scene_timeline_btn", None),
                          highlight_color="#c084fc"))
    phase_times["08_video_rendered"] = time.time() - t0

    # ════════════════════════════════════════════════════════════════════
    # GALLERY PHASE
    # ════════════════════════════════════════════════════════════════════

    # ── Screenshot 09: Gallery Review ───────────────────────────────────
    print("\n[09/13] Gallery — reviewing outputs ...")
    t0 = time.time()
    app.notebook.select(app.gallery_tab)
    _settle(root, 0.3)
    _open_section(app, "gallery_browser")
    app.refresh_gallery()
    _settle(root, 0.8)

    # Try to highlight the first video card
    gallery_highlight = None
    if current_video_path:
        cards = getattr(app, "gallery_video_cards", {}) or {}
        card = cards.get(os.path.normcase(current_video_path))
        if card:
            gallery_highlight = card.get("frame")

    saved.append(_capture(root, app, "09_gallery_review",
                          highlight_widget=gallery_highlight,
                          highlight_color="#fbbf24"))
    phase_times["09_gallery_review"] = time.time() - t0

    # ── Screenshot 10: Stitch ───────────────────────────────────────────
    print("\n[10/13] Gallery — stitching video ...")
    t0 = time.time()
    current_stitched_path = None

    if current_video_path and os.path.exists(current_video_path):
        _select_gallery_video_for_stitching(app, current_video_path)
        _settle(root, 0.3)

        existing_stitched = set(glob.glob(os.path.join(app.stitched_dir, "*.mp4")))

        app.notebook.select(app.video_tab)
        _open_section(app, "video_utilities")
        _settle(root, 0.2)

        if hasattr(app, "stitch_btn"):
            app.stitch_btn.invoke()

        def _stitch_done():
            newest = _get_newest_file(app.stitched_dir, "*.mp4")
            return newest and newest not in existing_stitched and os.path.exists(newest)

        _wait_for(root, _stitch_done, timeout=120, interval=1.0, label="stitch complete")

        newest = _get_newest_file(app.stitched_dir, "*.mp4")
        if newest and newest not in existing_stitched:
            current_stitched_path = newest

        app.refresh_gallery()
        _settle(root, 0.5)
    else:
        print("  No rendered video to stitch — skipping")
        app.notebook.select(app.video_tab)
        _open_section(app, "video_utilities")
        _settle(root, 0.3)

    saved.append(_capture(root, app, "10_gallery_stitch",
                          highlight_widget=getattr(app, "stitch_btn", None),
                          highlight_color="#fbbf24"))
    phase_times["10_gallery_stitch"] = time.time() - t0

    # ════════════════════════════════════════════════════════════════════
    # MUSIC PHASE
    # ════════════════════════════════════════════════════════════════════

    # Select video for music (tutorial's phase_select_for_music pattern)
    selected_for_music = current_stitched_path or current_video_path
    if selected_for_music and os.path.exists(selected_for_music):
        app.notebook.select(app.gallery_tab)
        app.refresh_gallery()
        _settle(root, 0.3)
        # Use gallery "add music" action
        cards = getattr(app, "gallery_video_cards", {}) or {}
        card = cards.get(os.path.normcase(selected_for_music))
        if card and card.get("add_music_btn"):
            card["add_music_btn"].invoke()
            _settle(root, 0.3)

    # ── Screenshot 11: Music Config ─────────────────────────────────────
    print("\n[11/13] Music — configuring ...")
    t0 = time.time()
    app.notebook.select(app.music_tab)
    _settle(root, 0.3)

    _open_section(app, "music_prompt")
    _settle(root, 0.2)

    app.music_tags_text.delete("1.0", tk.END)
    app.music_tags_text.insert("1.0", MUSIC_TAGS)

    app.music_duration_var.set(TUTORIAL_DURATION_SECONDS)
    _settle(root, 0.3)

    saved.append(_capture(root, app, "11_music_config",
                          highlight_widget=getattr(app, "music_tags_text", None),
                          highlight_color="#34d399"))
    phase_times["11_music_config"] = time.time() - t0

    # ── Screenshot 12: Music Generated ──────────────────────────────────
    print("\n[12/13] Music — generating soundtrack ...")
    t0 = time.time()
    app.notebook.select(app.music_tab)
    _open_section(app, "music_actions")
    _settle(root, 0.3)

    audio_before = getattr(app, "current_generated_audio", None)
    if _comfyui_reachable() and getattr(app, "music_workflow", None):
        app.generate_music()

        def _music_done():
            cur = getattr(app, "current_generated_audio", None)
            if cur and cur != audio_before and os.path.exists(cur):
                return True
            try:
                if str(app.gen_music_btn.cget("state")) == "normal":
                    cur2 = getattr(app, "current_generated_audio", None)
                    return cur2 and cur2 != audio_before
            except Exception:
                pass
            return False

        _wait_for(root, _music_done, timeout=900, interval=2.0, label="music generation complete")
        _settle(root, 0.5)
    else:
        print("  ComfyUI not reachable or music workflow missing — skipping generation")

    # Show playback section
    _open_section(app, "music_playback")
    _settle(root, 0.3)

    saved.append(_capture(root, app, "12_music_generated",
                          highlight_widget=getattr(app, "gen_music_btn", None),
                          highlight_color="#34d399"))
    phase_times["12_music_generated"] = time.time() - t0

    # ── Screenshot 13: Final Merged Output ──────────────────────────────
    print("\n[13/13] Music — merging final video ...")
    t0 = time.time()
    app.notebook.select(app.music_tab)
    _open_section(app, "music_media_state")
    _open_section(app, "music_actions")
    _settle(root, 0.3)

    final_before = getattr(app, "current_final_video", None)
    audio_now = getattr(app, "current_generated_audio", None)
    if audio_now and os.path.exists(audio_now) and selected_for_music:
        if hasattr(app, "merge_music_btn"):
            app.merge_music_btn.invoke()

        def _merge_done():
            fv = getattr(app, "current_final_video", None)
            if fv and fv != final_before and os.path.exists(fv):
                return True
            try:
                if str(app.merge_music_btn.cget("state")) == "normal":
                    fv2 = getattr(app, "current_final_video", None)
                    return fv2 and fv2 != final_before
            except Exception:
                pass
            return False

        _wait_for(root, _merge_done, timeout=120, interval=1.0, label="merge complete")
        _settle(root, 0.5)
    else:
        print("  No audio or video for merge — skipping")

    # Show final result in gallery
    app.notebook.select(app.gallery_tab)
    app.refresh_gallery()
    _settle(root, 0.8)

    final_highlight = None
    final_path = getattr(app, "current_final_video", None)
    if final_path and os.path.exists(final_path):
        cards = getattr(app, "gallery_video_cards", {}) or {}
        card = cards.get(os.path.normcase(final_path))
        if card:
            final_highlight = card.get("frame")

    saved.append(_capture(root, app, "13_final_output",
                          highlight_widget=final_highlight,
                          highlight_color="#34d399", highlight_pad=10))
    phase_times["13_final_output"] = time.time() - t0

    # ── Cleanup ─────────────────────────────────────────────────────────
    _remove_highlight(root)
    root.destroy()

    print(f"\n{'=' * 64}")
    print(f"  Done — {len(saved)} screenshots saved to {SCREENSHOT_DIR}")
    print(f"{'=' * 64}")
    total = 0
    for name, elapsed in phase_times.items():
        print(f"  {name:25s}  {elapsed:7.1f}s")
        total += elapsed
    print(f"  {'TOTAL':25s}  {total:7.1f}s")
    print()
    for p in saved:
        print(f"  {p}")


if __name__ == "__main__":
    main()
