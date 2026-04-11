import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import copy
import json
import math
import urllib.request
import urllib.error
import urllib.parse
import time
import random
import threading
import os
import re
import sys
import subprocess
import shutil
import tempfile
import ctypes
import uuid
from datetime import datetime
from PIL import Image, ImageTk
import ttkbootstrap as tb
try:
    import websocket as _ws_mod
    WS_AVAILABLE = True
except ImportError:
    _ws_mod = None
    WS_AVAILABLE = False
from model_downloader import DownloadCancelledError, calculate_sha256, download_file, probe_download_size

try:
    from tkinterdnd2 import COPY, DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    COPY = "copy"
    DND_FILES = "DND_Files"
    TkinterDnD = None
    DND_AVAILABLE = False

# Try to get ffmpeg from imageio_ffmpeg, fallback to 'ffmpeg'
try:
    import imageio_ffmpeg
    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FFMPEG_PATH = shutil.which('ffmpeg') or 'ffmpeg'

DEFAULT_VIDEO_PROFILE = "ltx_2_3_t2v"
ACE_STEP_15_MIN_P_DEFAULT = 0.0
SUPPORTED_VIDEO_EXTENSIONS = (".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v")
SUPPORTED_AUDIO_EXTENSIONS = (".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg")
SUPPORTED_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".bmp")
PROJECT_STATE_SCHEMA_VERSION = 3
CHATBOT_CREATIVE_STATE_SCHEMA_VERSION = 1
TUTORIAL_PHASE_HISTORY_SCHEMA_VERSION = 1
TUTORIAL_PHASE_HISTORY_MAX_SAMPLES = 12
SCENE_MODE_T2V = "t2v"
SCENE_MODE_I2V = "i2v"
MUSIC_SAMPLER_OPTIONS = [
    "euler",
    "euler_ancestral",
    "heun",
    "heunpp2",
    "dpm_2",
    "dpm_2_ancestral",
    "lms",
    "dpm_fast",
    "dpm_adaptive",
    "dpmpp_2s_ancestral",
    "dpmpp_sde",
    "dpmpp_sde_gpu",
    "dpmpp_2m",
    "dpmpp_2m_sde",
    "dpmpp_2m_sde_gpu",
    "dpmpp_3m_sde",
    "dpmpp_3m_sde_gpu",
    "ddpm",
    "lcm",
    "ipndm",
    "ipndm_v",
    "deis",
    "uni_pc",
    "uni_pc_bh2"
]
MUSIC_SCHEDULER_OPTIONS = [
    "normal",
    "karras",
    "exponential",
    "sgm_uniform",
    "simple",
    "ddim_uniform",
    "beta",
    "linear_quadratic",
    "kl_optimal"
]
MUSIC_LANGUAGE_OPTIONS = [
    "en",
    "ja",
    "zh",
    "es",
    "de",
    "fr",
    "pt",
    "ru",
    "it",
    "nl",
    "pl",
    "tr",
    "vi",
    "cs",
    "fa",
    "id",
    "ko",
    "uk",
    "hu",
    "ar",
    "sv",
    "ro",
    "el"
]
MUSIC_TIME_SIGNATURE_OPTIONS = ["2", "3", "4", "6"]
MUSIC_MP3_QUALITY_OPTIONS = [f"V{i}" for i in range(10)]
MUSIC_MODEL_VARIANT_OPTIONS = ["Turbo (fast, 8 steps)", "XL Turbo (fast, 8 steps)", "XL SFT (best quality, 50 steps)"]
MUSIC_MODEL_VARIANT_MAP = {
    "Turbo (fast, 8 steps)": {"filename": "acestep_v1.5_turbo.safetensors", "steps": 8, "manifest_id": "music_unet_turbo", "backend": "comfyui"},
    "XL Turbo (fast, 8 steps)": {"filename": "acestep_v1.5_xl_turbo_bf16.safetensors", "steps": 8, "manifest_id": "music_unet_xl_turbo", "backend": "acestep_api", "api_model_id": "acestep-v15-xl-turbo"},
    "XL SFT (best quality, 50 steps)": {"filename": "acestep_v1.5_xl_sft_bf16.safetensors", "steps": 50, "manifest_id": "music_unet_xl_sft", "backend": "acestep_api", "api_model_id": "acestep-v15-xl-sft"},
}
MUSIC_MODEL_VARIANT_DEFAULT = "Turbo (fast, 8 steps)"
ACESTEP_API_URL = "http://127.0.0.1:8001"
ACESTEP_API_POLL_INTERVAL = 2  # seconds between polling for XL generation results
ACESTEP_API_TIMEOUT = 1800  # max seconds to wait for XL generation (first run downloads ~20GB of models)
XL_PHASE_SUBMIT_COLD = "xl_submit_cold"
XL_PHASE_SUBMIT_WARM = "xl_submit_warm"
XL_PHASE_GENERATION = "xl_generation"
XL_PHASE_DOWNLOAD = "xl_download"
XL_COLD_START_DEFAULT_SECONDS = 420  # 7 min fallback for first cold start
XL_WARM_SUBMIT_DEFAULT_SECONDS = 5
XL_GENERATION_DEFAULT_SECONDS = 15
XL_DOWNLOAD_DEFAULT_SECONDS = 3
CHATBOT_PHASE_CHAT_COLD = "chatbot_chat_cold"
CHATBOT_PHASE_CHAT_WARM = "chatbot_chat_warm"
CHATBOT_PHASE_SCENE_PLAN_COLD = "chatbot_scene_plan_cold"
CHATBOT_PHASE_SCENE_PLAN_WARM = "chatbot_scene_plan_warm"
CHATBOT_PHASE_T2I_OPTIMIZE_COLD = "chatbot_t2i_optimize_cold"
CHATBOT_PHASE_T2I_OPTIMIZE_WARM = "chatbot_t2i_optimize_warm"
CHATBOT_PHASE_SONG_FINALIZE_COLD = "chatbot_song_finalize_cold"
CHATBOT_PHASE_SONG_FINALIZE_WARM = "chatbot_song_finalize_warm"
CHATBOT_COLD_START_DEFAULT_SECONDS = 45
CHATBOT_WARM_DEFAULT_SECONDS = 10
AUTONOMOUS_STATE_IDLE = "idle"
AUTONOMOUS_STATE_EXPANDING_CONCEPT = "expanding_concept"
AUTONOMOUS_STATE_PLANNING_SCENES = "planning_scenes"
AUTONOMOUS_STATE_PLANNING_SONG = "planning_song"
AUTONOMOUS_STATE_GENERATING_IMAGES = "generating_images"
AUTONOMOUS_STATE_BUILDING_TIMELINE = "building_timeline"
AUTONOMOUS_STATE_RENDERING = "rendering"
AUTONOMOUS_STATE_STITCHING = "stitching"
AUTONOMOUS_STATE_GENERATING_MUSIC = "generating_music"
AUTONOMOUS_STATE_MERGING = "merging"
AUTONOMOUS_STATE_COMPLETE = "complete"
AUTONOMOUS_STATE_FAILED = "failed"
AUTONOMOUS_PHASE_LABELS = {
    AUTONOMOUS_STATE_EXPANDING_CONCEPT: "Expanding Concept",
    AUTONOMOUS_STATE_PLANNING_SCENES: "Planning Scenes",
    AUTONOMOUS_STATE_PLANNING_SONG: "Writing Song",
    AUTONOMOUS_STATE_GENERATING_IMAGES: "Generating Images",
    AUTONOMOUS_STATE_BUILDING_TIMELINE: "Building Timeline",
    AUTONOMOUS_STATE_RENDERING: "Rendering Videos",
    AUTONOMOUS_STATE_STITCHING: "Stitching Clips",
    AUTONOMOUS_STATE_GENERATING_MUSIC: "Generating Music",
    AUTONOMOUS_STATE_MERGING: "Final Merge",
}
AUTONOMOUS_PHASE_ORDER = [
    AUTONOMOUS_STATE_EXPANDING_CONCEPT,
    AUTONOMOUS_STATE_PLANNING_SCENES,
    AUTONOMOUS_STATE_PLANNING_SONG,
    AUTONOMOUS_STATE_GENERATING_IMAGES,
    AUTONOMOUS_STATE_BUILDING_TIMELINE,
    AUTONOMOUS_STATE_RENDERING,
    AUTONOMOUS_STATE_STITCHING,
    AUTONOMOUS_STATE_GENERATING_MUSIC,
    AUTONOMOUS_STATE_MERGING,
]
AUTONOMOUS_PHASE_WEIGHTS = {
    AUTONOMOUS_STATE_EXPANDING_CONCEPT: 0.03,
    AUTONOMOUS_STATE_PLANNING_SCENES: 0.04,
    AUTONOMOUS_STATE_PLANNING_SONG: 0.03,
    AUTONOMOUS_STATE_GENERATING_IMAGES: 0.25,
    AUTONOMOUS_STATE_BUILDING_TIMELINE: 0.01,
    AUTONOMOUS_STATE_RENDERING: 0.40,
    AUTONOMOUS_STATE_STITCHING: 0.04,
    AUTONOMOUS_STATE_GENERATING_MUSIC: 0.15,
    AUTONOMOUS_STATE_MERGING: 0.05,
}
PERSISTED_MUSIC_SECTION_KEYS = [
    "music_prompt",
    "music_lyrics",
    "music_playback",
    "music_generation",
    "music_advanced",
    "music_actions",
    "music_media_state",
    "music_preview"
]
WINDOWS_HIDE = 0
WINDOWS_SHOW = 5
WINDOWS_RESTORE = 9
APP_NAME = "Prompt2MTV"
APP_VERSION = "1.5.1"
APP_PUBLISHER = "Prompt2MTV"
APP_TAGLINE = "Local AI Music Video Studio"
ENV_COMFYUI_ROOT_KEYS = ("PROMPT2MTV_COMFYUI_ROOT", "COMFYUI_ROOT")
ENV_COMFYUI_LAUNCHER_KEY = "PROMPT2MTV_COMFYUI_LAUNCHER"
ENV_MODEL_ROOTS_KEY = "PROMPT2MTV_MODEL_ROOTS"
DEFAULT_COMFYUI_ROOT_CANDIDATES = [
    r"D:\ComfyUI",
    r"D:\ComfyUI\ComfyUI"
]
DEFAULT_COMFYUI_LAUNCHER_NAMES = [
    "run_ltx2_queue_manager.bat",
    "run_nvidia_gpu.bat",
    "run_cpu.bat"
]
MODEL_MANIFEST_FILE = "model_manifest.json"
CHATBOT_MODEL_FILENAME = "Qwen_Qwen3-14B-Q4_K_M.gguf"
CHATBOT_MODEL_URL = "https://huggingface.co/bartowski/Qwen_Qwen3-14B-GGUF/resolve/main/Qwen_Qwen3-14B-Q4_K_M.gguf?download=true"
CHATBOT_MODEL_SOURCE_PAGE = "https://huggingface.co/bartowski/Qwen_Qwen3-14B-GGUF"
DEFAULT_CHATBOT_SERVER_URL = "http://127.0.0.1:8080"
DEFAULT_OLLAMA_SERVER_URL = "http://127.0.0.1:11434"
DEFAULT_CHATBOT_CONTEXT_SIZE = 16384
DEFAULT_CHATBOT_REQUEST_TIMEOUT = 120
DEFAULT_CHATBOT_TEMPERATURE = 0.7
DEFAULT_CHATBOT_TOP_P = 0.8
DEFAULT_CHATBOT_TOP_K = 20
DEFAULT_CHATBOT_MIN_P = 0.0
DEFAULT_CHATBOT_REPEAT_PENALTY = 1.5
DEFAULT_CHATBOT_DEFAULT_TO_NON_THINKING = True
CHATBOT_MODEL_FAMILY_QWEN3 = "qwen3"
CHATBOT_MODEL_FAMILY_GEMMA4 = "gemma4"
DEFAULT_CHATBOT_MODEL_FAMILY = CHATBOT_MODEL_FAMILY_QWEN3
DEFAULT_GEMMA4_OLLAMA_TAG = "gemma4:e4b"
GEMMA4_OLLAMA_TAG_OPTIONS = ["gemma4:e2b", "gemma4:e4b", "gemma4:26b", "gemma4:31b"]
DEFAULT_GEMMA4_TEMPERATURE = 1.0
DEFAULT_GEMMA4_TOP_P = 0.95
DEFAULT_GEMMA4_TOP_K = 64
DEFAULT_GEMMA4_MIN_P = 0.0
DEFAULT_GEMMA4_REPEAT_PENALTY = 1.0
PHASE_DISPLAY_NAMES = {
    "video_single": "Generating Video Clip",
    "video_queue": "Running Video Queue",
    "video_render": "Rendering Scene Timeline",
    "image_single": "Generating Image",
    "image_generate": "Running Image Queue",
    "music_generate": "Generating Soundtrack",
    "music_generate_xl": "Generating Soundtrack (XL)",
    "merge": "Merging Audio & Video",
    "stitch": "Stitching Videos",
    "chatbot_chat": "Chatbot Responding",
    "chatbot_task": "Generating Prompt Draft",
    "chatbot_chat_cold": "Chatbot Responding (loading model)",
    "chatbot_chat_warm": "Chatbot Responding",
    "chatbot_scene_plan_cold": "Planning Scenes (loading model)",
    "chatbot_scene_plan_warm": "Planning Scenes",
    "chatbot_t2i_optimize_cold": "Generating Prompt Draft (loading model)",
    "chatbot_t2i_optimize_warm": "Generating Prompt Draft",
    "chatbot_song_finalize_cold": "Finalizing Song (loading model)",
    "chatbot_song_finalize_warm": "Finalizing Song",
    "autonomous_pipeline": "Autonomous Music Video Pipeline",
}
CHATBOT_BACKEND_MODE_CONNECT = "connect"
CHATBOT_BACKEND_MODE_MANAGED = "managed"
CHATBOT_BACKEND_MODE_OLLAMA = "ollama"
CHATBOT_TASK_CHAT = "Chat / Explore"
CHATBOT_TASK_T2I_OPTIMIZE = "Optimize Image Prompt (T2I)"
CHATBOT_TASK_SCENE_PLAN = "Plan Scenes"
CHATBOT_TASK_SCENE_OUTLINE = "Plan Scene Outline"
CHATBOT_TASK_JIT_IMAGE_PROMPT = "Generate Image Prompt (JIT)"
CHATBOT_TASK_JIT_VIDEO_PROMPT = "Generate Video Prompt (JIT)"
CHATBOT_TASK_SONG_BRAINSTORM = "Brainstorm Song (Lyrics & Style)"
CHATBOT_TASK_CONCEPT_EXPAND = "Expand Creative Concept"
BUNDLED_MODEL_DIR = "bundled_models"
MODEL_SUBDIRECTORIES = {
    "checkpoint_name": "checkpoints",
    "text_encoder_name": "text_encoders",
    "lora_name": "loras",
    "upscaler_name": "latent_upscale_models",
    "clip_name": "text_encoders",
    "vae_name": "vae",
    "unet_name": "diffusion_models"
}
WORKFLOW_MODEL_LABELS = {
    "video": "Video Workflow",
    "music": "Music Workflow",
    "image": "Image Workflow"
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

IMAGE_WORKFLOW_PROFILE = {
    "label": "Z-Image",
    "workflow_path": "image_z_image.json",
    "roles": {
        "prompt": {"node_id": "76:67", "input": "text"},
        "negative_prompt": {"node_id": "76:71", "input": "text"},
        "width": {"node_id": "76:68", "input": "width"},
        "height": {"node_id": "76:68", "input": "height"},
        "filename_prefix": {"node_id": "9", "input": "filename_prefix"},
        "clip_name": {"node_id": "76:62", "input": "clip_name"},
        "vae_name": {"node_id": "76:63", "input": "vae_name"},
        "unet_name": {"node_id": "76:66", "input": "unet_name"},
        "seed": {"node_id": "76:69", "input": "seed"},
        "steps": {"node_id": "76:69", "input": "steps"},
        "cfg": {"node_id": "76:69", "input": "cfg"},
        "sampler_name": {"node_id": "76:69", "input": "sampler_name"},
        "scheduler": {"node_id": "76:69", "input": "scheduler"},
        "denoise": {"node_id": "76:69", "input": "denoise"}
    }
}

I2V_WORKFLOW_PROFILE = {
    "label": "LTX 2.3 Image to Video",
    "workflow_path": "video_ltx2_3_i2v.json",
    "roles": {
        "prompt": {"node_id": "267:266", "input": "value"},
        "negative_prompt": {"node_id": "267:247", "input": "text"},
        "width": {"node_id": "267:257", "input": "value"},
        "height": {"node_id": "267:258", "input": "value"},
        "fps": {"node_id": "267:260", "input": "value"},
        "length": {"node_id": "267:225", "input": "value"},
        "t2v_enabled": {"node_id": "267:201", "input": "value"},
        "filename_prefix": {"node_id": "273", "input": "filename_prefix"},
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
        "upscaler_name": {"node_id": "267:233", "input": "model_name"},
        "image_path": {"node_id": "269", "input": "image"}
    }
}

if DND_AVAILABLE:
    class Prompt2MTVWindow(tb.Window, TkinterDnD.DnDWrapper):
        def __init__(self, *args, **kwargs):
            tb.Window.__init__(self, *args, **kwargs)
            self.TkdndVersion = TkinterDnD._require(self)
else:
    class Prompt2MTVWindow(tb.Window):
        pass

class LTXQueueManager:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} {APP_VERSION}")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        default_width = min(1320, max(1080, int(screen_width * 0.9)))
        default_height = min(920, max(760, int(screen_height * 0.86)))
        self.root.geometry(f"{default_width}x{default_height}")
        self.root.minsize(980, 720)
        self.root.after(0, self._maximize_window)
        self.colors = dict(UI_COLORS)
        self.fonts = dict(UI_FONTS)
        self.app_root_dir = self._get_app_root_dir()
        self.resource_root_dir = self._get_resource_root_dir()
        self.user_data_dir = self._get_user_data_dir()
        os.makedirs(self.user_data_dir, exist_ok=True)
        self._configure_theme_system()
        
        self.api_json_path = VIDEO_WORKFLOW_PROFILES[DEFAULT_VIDEO_PROFILE]["workflow_path"]
        self.image_json_path = IMAGE_WORKFLOW_PROFILE["workflow_path"]
        self.i2v_json_path = I2V_WORKFLOW_PROFILE["workflow_path"]
        self.music_json_path = "ACE_Step_AI_Music_Generator_Workflow.json"
        self.workflow = None
        self.image_workflow = None
        self.i2v_workflow = None
        self.music_workflow = None
        self.prompts = []
        self.image_prompts = []
        self.scene_entry_frames = []
        self.comfyui_process = None
        self.global_settings_file = os.path.join(self.user_data_dir, "app_settings.json")
        self.legacy_global_settings_file = os.path.join(self.app_root_dir, "app_settings.json")
        self.tutorial_phase_history_file = os.path.join(self.user_data_dir, "tutorial_phase_history.json")
        self.comfyui_readiness_history_file = os.path.join(self.user_data_dir, "comfyui_readiness_history.json")
        self.is_first_launch = False
        self.selected_videos = set()
        self.video_checkbox_vars = []
        self.gallery_video_cards = {}
        self.selected_video_for_music = None
        self.current_generated_audio = None
        self.current_audio_source = None
        self.current_project_dir = None
        self.comfyui_console_hwnd = None
        self.comfyui_console_visible = False
        self.comfyui_console_title = None
        self.comfyui_console_poll_after_id = None
        self.comfyui_console_pending_visibility = None
        self.comfyui_ready = False
        self.comfyui_ready_poll_id = None
        self.comfyui_readiness_history = {"samples": [], "average_seconds": 0.0}
        self.comfyui_poll_started_at = None
        self.comfyui_readiness_eta_job = None
        self.comfyui_readiness_flash_job = None
        self.debug_lock = threading.Lock()
        self.debug_log_file = None
        self.comfyui_root = None
        self.comfyui_launcher_path = None
        self.model_search_roots = []
        self.model_manifest_path = self._make_workflow_path_absolute(MODEL_MANIFEST_FILE)
        self.model_manifest = {"version": 1, "models": []}
        self.last_model_audit = None
        self.video_model_choices = {field_name: [] for field_name in ["checkpoint_name", "text_encoder_name", "lora_name", "upscaler_name"]}
        self.image_model_choices = {field_name: [] for field_name in ["clip_name", "vae_name", "unet_name"]}
        self.collapsible_sections = {}
        self.collapsible_section_groups = {}
        self.responsive_layout_mode = None
        self.chatbot_workspace_layout_mode = None
        self.drag_drop_enabled = DND_AVAILABLE
        self.global_image_settings_defaults = {}
        self.remember_section_open_states = False
        self.imported_video_dir = None
        self.imported_audio_dir = None
        self.project_state_restore_in_progress = False
        self.project_state_save_after_id = None
        self.chatbot_model_url = CHATBOT_MODEL_URL
        self.chatbot_model_filename = CHATBOT_MODEL_FILENAME
        self.chatbot_model_root = self._get_recommended_chatbot_model_root()
        self.chatbot_model_path = self._get_chatbot_model_path_from_root(self.chatbot_model_root)
        self.chatbot_preferred_drive = "M"
        self.chatbot_backend_mode = CHATBOT_BACKEND_MODE_CONNECT
        self.chatbot_model_family = DEFAULT_CHATBOT_MODEL_FAMILY
        self.chatbot_gemma4_ollama_tag = DEFAULT_GEMMA4_OLLAMA_TAG
        self.chatbot_server_url = DEFAULT_CHATBOT_SERVER_URL
        self.chatbot_server_executable_path = ""
        self.chatbot_context_size = DEFAULT_CHATBOT_CONTEXT_SIZE
        self.chatbot_request_timeout = DEFAULT_CHATBOT_REQUEST_TIMEOUT
        self.chatbot_temperature = DEFAULT_CHATBOT_TEMPERATURE
        self.chatbot_top_p = DEFAULT_CHATBOT_TOP_P
        self.chatbot_top_k = DEFAULT_CHATBOT_TOP_K
        self.chatbot_min_p = DEFAULT_CHATBOT_MIN_P
        self.chatbot_repeat_penalty = DEFAULT_CHATBOT_REPEAT_PENALTY
        self.chatbot_default_to_non_thinking = DEFAULT_CHATBOT_DEFAULT_TO_NON_THINKING
        self.chatbot_auto_launch_server = False
        self.chatbot_backend_health_text = "Backend check: Not tested yet."
        self.chatbot_discovered_model_ids = []
        self.chatbot_server_process = None
        self.chatbot_server_managed_by_app = False
        self.chatbot_server_command = []
        self.chatbot_model_warm = False
        self.chatbot_state = self._create_empty_chatbot_state()
        self.chatbot_last_result = None
        self.chatbot_result_history = []
        self.chatbot_output_show_raw = False
        self.chatbot_output_preview_cache = ""
        self.chatbot_generation_in_progress = False
        self.chatbot_pending_request_mode = None
        self.chatbot_download_cancel_requested = False
        self.chatbot_setup_prompted_this_session = False
        self.autonomous_active = False
        self.autonomous_state = AUTONOMOUS_STATE_IDLE
        self.autonomous_target_duration = 120
        self.autonomous_cancel_requested = False
        self.autonomous_scene_count = 0
        self.autonomous_actual_duration = 0
        self.autonomous_creative_brief = ""
        self.autonomous_completed_phases = set()
        self.autonomous_rendered_scene_paths = []
        self.autonomous_music_tags = ""
        self.autonomous_music_lyrics = ""
        self.autonomous_expanded_concept = ""
        self.autonomous_scene_outline = []
        self.autonomous_image_prompts = []
        self.autonomous_video_prompts = []
        self.autonomous_i2v_prompts = []
        self.autonomous_image_asset_map = {}
        self.tutorial_runtime_progress = {}
        self.tutorial_phase_history = self._create_empty_tutorial_phase_history()
        self.eta_active_phase = None
        self.eta_item_start_time = None
        self.eta_phase_start_time = None
        self.eta_tick_id = None
        self.comfyui_client_id = str(uuid.uuid4())
        self.ws_progress = {"step": 0, "total": 0, "active": False}
        self.ws_thread = None
        self.eta_variant_timing_key = None
        self.acestep_api_process = None
        self.acestep_api_healthy = False
        self.acestep_model_loaded = False
        self.xl_gen_phase = None
        self.xl_gen_phase_start = None
        self.xl_gen_progress = 0.0
        self.xl_gen_stage_text = ""
        
        # Setup base output directory
        self.base_output_dir = self._get_default_output_dir()
        os.makedirs(self.base_output_dir, exist_ok=True)
        self._load_model_manifest()
        
        self.thumbnail_images = []
        self.generated_image_dir = None
        self.imported_image_dir = None
        self.image_assets = []
        self.scene_timeline = []
        self.image_prompt_queue = []
        
        self.setup_ui()
        self._enable_drag_and_drop()
        self.load_default_json()
        self.load_global_settings() # Load global settings after workflows are available so project state restoration wins
        self.run_startup_preflight(interactive=True)
        self.launch_comfyui()
        self._start_comfyui_readiness_poll()

    def _get_app_root_dir(self):
        if getattr(sys, "frozen", False):
            return os.path.dirname(os.path.abspath(sys.executable))
        return os.path.dirname(os.path.abspath(__file__))

    def _get_resource_root_dir(self):
        return getattr(sys, "_MEIPASS", self.app_root_dir)

    def _get_user_data_dir(self):
        local_app_data = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        if not local_app_data:
            return self.app_root_dir
        return os.path.join(local_app_data, APP_NAME)

    def _normalize_path(self, path_value):
        if not path_value:
            return None
        normalized_text = str(path_value).strip()
        if len(normalized_text) >= 2 and normalized_text[0] == normalized_text[-1] and normalized_text[0] in {'"', "'"}:
            normalized_text = normalized_text[1:-1].strip()
        expanded = os.path.expandvars(os.path.expanduser(normalized_text))
        if not expanded:
            return None
        return os.path.normpath(expanded)

    def _append_unique_path(self, collection, path_value):
        normalized_path = self._normalize_path(path_value)
        if not normalized_path:
            return
        normalized_key = os.path.normcase(normalized_path)
        if normalized_key not in {os.path.normcase(existing) for existing in collection}:
            collection.append(normalized_path)

    def _chatbot_drive_available(self, drive_letter):
        normalized_drive = str(drive_letter or "").strip().upper().rstrip(":")
        if not normalized_drive:
            return False
        return os.path.exists(f"{normalized_drive}:\\")

    def _get_chatbot_model_root_candidates(self):
        candidates = []
        if self._chatbot_drive_available("M"):
            candidates.append(r"M:\AiStudio\Prompt2MTV\LLM_Models")
        if self._chatbot_drive_available("D"):
            candidates.append(r"D:\Prompt2MTV\LLM_Models")
        candidates.append(os.path.join(self.user_data_dir, "llm_models"))

        normalized_candidates = []
        for candidate in candidates:
            self._append_unique_path(normalized_candidates, candidate)
        return normalized_candidates

    def _get_recommended_chatbot_model_root(self):
        candidates = self._get_chatbot_model_root_candidates()
        return candidates[0] if candidates else None

    def _get_chatbot_model_path_from_root(self, root_path=None):
        normalized_root = self._normalize_path(root_path)
        if not normalized_root:
            return None
        return os.path.join(normalized_root, self.chatbot_model_filename)

    def _chatbot_model_is_ready(self):
        model_path = self._normalize_path(self.chatbot_model_path)
        return bool(model_path and os.path.exists(model_path))

    def _get_default_chatbot_server_url(self, backend_mode=None):
        mode_value = str(backend_mode or self.chatbot_backend_mode or CHATBOT_BACKEND_MODE_CONNECT).strip().lower()
        if mode_value == CHATBOT_BACKEND_MODE_OLLAMA:
            return DEFAULT_OLLAMA_SERVER_URL
        return DEFAULT_CHATBOT_SERVER_URL

    def _chatbot_requires_local_model(self):
        return self.chatbot_backend_mode == CHATBOT_BACKEND_MODE_MANAGED

    def _chatbot_can_generate_without_local_model(self):
        return self.chatbot_backend_mode in {CHATBOT_BACKEND_MODE_CONNECT, CHATBOT_BACKEND_MODE_OLLAMA}

    def _chatbot_generation_prerequisites_ready(self):
        return self._chatbot_model_is_ready() or self._chatbot_can_generate_without_local_model()

    def _get_ollama_executable_candidates(self):
        candidates = []
        which_result = shutil.which("ollama") or shutil.which("ollama.exe")
        if which_result:
            candidates.append(which_result)
        candidates.extend([
            r"C:\Users\Tesla\AppData\Local\Programs\Ollama\ollama.exe",
            os.path.join(os.environ.get("LOCALAPPDATA") or "", "Programs", "Ollama", "ollama.exe"),
        ])

        normalized_candidates = []
        for candidate in candidates:
            self._append_unique_path(normalized_candidates, candidate)
        return normalized_candidates

    def _detect_ollama_executable(self):
        for candidate in self._get_ollama_executable_candidates():
            if candidate and os.path.exists(candidate):
                return candidate
        return ""

    def _sanitize_chatbot_server_executable_path(self, path_value, backend_mode=None):
        normalized_path = self._normalize_path(path_value)
        if not normalized_path:
            return ""

        mode_value = str(backend_mode or self.chatbot_backend_mode or CHATBOT_BACKEND_MODE_CONNECT).strip().lower()
        basename = os.path.basename(normalized_path).strip().lower()
        if mode_value == CHATBOT_BACKEND_MODE_OLLAMA:
            return normalized_path if "ollama" in basename else ""
        if "ollama" in basename and mode_value == CHATBOT_BACKEND_MODE_MANAGED:
            return ""
        return normalized_path

    def _chatbot_server_executable_is_valid(self, backend_mode=None, executable_path=None):
        mode_value = str(backend_mode or self.chatbot_backend_mode or CHATBOT_BACKEND_MODE_CONNECT).strip().lower()
        normalized_path = self._sanitize_chatbot_server_executable_path(executable_path if executable_path is not None else self.chatbot_server_executable_path, backend_mode=mode_value)
        if not normalized_path:
            return False
        if not os.path.exists(normalized_path):
            return False
        basename = os.path.basename(normalized_path).strip().lower()
        if mode_value == CHATBOT_BACKEND_MODE_OLLAMA:
            return "ollama" in basename
        return "llama" in basename and "server" in basename

    def _get_active_chatbot_server_executable_path(self, backend_mode=None):
        mode_value = str(backend_mode or self.chatbot_backend_mode or CHATBOT_BACKEND_MODE_CONNECT).strip().lower()
        saved_path = self._sanitize_chatbot_server_executable_path(self.chatbot_server_executable_path, backend_mode=mode_value)
        if self._chatbot_server_executable_is_valid(backend_mode=mode_value, executable_path=saved_path):
            return saved_path
        if mode_value == CHATBOT_BACKEND_MODE_OLLAMA:
            detected_path = self._detect_ollama_executable()
            if self._chatbot_server_executable_is_valid(backend_mode=mode_value, executable_path=detected_path):
                return detected_path
        return ""

    def _get_chatbot_preferred_ollama_model_name(self):
        stem_value = os.path.splitext(os.path.basename(self.chatbot_model_path or self.chatbot_model_filename or "qwen-chatbot"))[0]
        slug_value = re.sub(r"[^a-z0-9]+", "-", stem_value.strip().lower()).strip("-")
        if not slug_value:
            slug_value = "qwen-chatbot"
        return f"prompt2mtv-{slug_value}"

    def _chatbot_base_url(self):
        default_url = self._get_default_chatbot_server_url()
        return (str(self.chatbot_server_url or default_url).strip() or default_url).rstrip("/")

    def _get_chatbot_server_host_port(self):
        parsed_url = urllib.parse.urlparse(self._chatbot_base_url())
        host_value = parsed_url.hostname or "127.0.0.1"
        port_value = parsed_url.port
        if port_value is None:
            port_value = 443 if parsed_url.scheme == "https" else 80
        return host_value, int(port_value)

    def _is_chatbot_server_process_running(self):
        return bool(self.chatbot_server_process and self.chatbot_server_process.poll() is None)

    def _build_managed_chatbot_server_command(self):
        backend_mode = str(self.chatbot_backend_mode or CHATBOT_BACKEND_MODE_CONNECT).strip().lower()
        executable_path = self._get_active_chatbot_server_executable_path(backend_mode=backend_mode)
        if backend_mode == CHATBOT_BACKEND_MODE_OLLAMA:
            if not executable_path or not self._chatbot_server_executable_is_valid(backend_mode=backend_mode, executable_path=executable_path):
                raise ValueError("Ollama mode requires a valid ollama executable.")
            return [executable_path, "serve"]

        if not executable_path or not self._chatbot_server_executable_is_valid(backend_mode=backend_mode, executable_path=executable_path):
            raise ValueError("Managed mode requires a valid llama-server executable.")
        if not self._chatbot_model_is_ready():
            raise ValueError("Managed mode requires a local GGUF model file.")

        host_value, port_value = self._get_chatbot_server_host_port()
        command = [
            executable_path,
            "-m",
            self.chatbot_model_path,
            "--host",
            host_value,
            "--port",
            str(port_value),
            "--ctx-size",
            str(max(1024, int(self.chatbot_context_size or DEFAULT_CHATBOT_CONTEXT_SIZE))),
        ]
        return command

    def _ensure_ollama_model_registered(self, timeout_seconds=180):
        if self.chatbot_model_family == CHATBOT_MODEL_FAMILY_GEMMA4:
            return self._ensure_gemma4_ollama_model(timeout_seconds=timeout_seconds)
        preferred_model_id = self._get_chatbot_preferred_ollama_model_name()
        try:
            discovered_model_ids = self._fetch_chatbot_backend_models(timeout_seconds=min(10, timeout_seconds))
        except Exception:
            discovered_model_ids = []

        for discovered_model_id in discovered_model_ids:
            if str(discovered_model_id).strip().lower() == preferred_model_id.lower():
                return preferred_model_id

        if not self._chatbot_model_is_ready():
            if discovered_model_ids:
                return discovered_model_ids[0]
            raise ValueError("Ollama is running, but no model is installed yet and no local GGUF is configured for automatic import.")

        executable_path = self._get_active_chatbot_server_executable_path(backend_mode=CHATBOT_BACKEND_MODE_OLLAMA)
        if not executable_path:
            raise ValueError("Prompt2MTV could not find ollama.exe to register the local GGUF automatically.")

        modelfile_path = ""
        try:
            modelfile_handle, modelfile_path = tempfile.mkstemp(prefix="prompt2mtv-ollama-", suffix=".Modelfile")
            os.close(modelfile_handle)
            with open(modelfile_path, "w", encoding="utf-8") as modelfile:
                modelfile.write(f"FROM {self.chatbot_model_path}\n")

            creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0
            completed_process = subprocess.run(
                [executable_path, "create", preferred_model_id, "-f", modelfile_path],
                capture_output=True,
                timeout=max(120, int(timeout_seconds)),
                creationflags=creation_flags,
            )
            if completed_process.returncode != 0:
                error_output = (completed_process.stderr or completed_process.stdout or b"")
                if isinstance(error_output, bytes):
                    error_output = error_output.decode("utf-8", errors="replace")
                error_output = str(error_output or "").strip()
                raise RuntimeError(error_output or "Ollama create failed without an error message.")
        finally:
            if modelfile_path and os.path.exists(modelfile_path):
                try:
                    os.remove(modelfile_path)
                except OSError:
                    pass

        deadline = time.time() + max(10, min(20, timeout_seconds))
        poll_delay_seconds = 0.75
        refreshed_model_ids = []
        while time.time() < deadline:
            try:
                refreshed_model_ids = self._fetch_chatbot_backend_models(timeout_seconds=min(10, timeout_seconds))
            except Exception:
                refreshed_model_ids = []

            for discovered_model_id in refreshed_model_ids:
                if str(discovered_model_id).strip().lower() == preferred_model_id.lower():
                    return discovered_model_id

            if refreshed_model_ids:
                self.chatbot_discovered_model_ids = refreshed_model_ids
            time.sleep(poll_delay_seconds)
            poll_delay_seconds = min(3.0, poll_delay_seconds * 1.5)

        if refreshed_model_ids:
            self.chatbot_discovered_model_ids = refreshed_model_ids
            return refreshed_model_ids[0]
        raise ValueError("Ollama completed model registration, but Prompt2MTV could not discover a usable model from /v1/models.")

    def _ensure_gemma4_ollama_model(self, timeout_seconds=180):
        tag = str(self.chatbot_gemma4_ollama_tag or DEFAULT_GEMMA4_OLLAMA_TAG).strip()
        try:
            discovered_model_ids = self._fetch_chatbot_backend_models(timeout_seconds=min(10, timeout_seconds))
        except Exception:
            discovered_model_ids = []

        for discovered_model_id in discovered_model_ids:
            if str(discovered_model_id).strip().lower().startswith("gemma4"):
                if tag.replace(":", "-") in discovered_model_id.replace(":", "-") or discovered_model_id.strip().lower() == tag.lower():
                    return discovered_model_id

        for discovered_model_id in discovered_model_ids:
            if str(discovered_model_id).strip().lower().startswith("gemma4"):
                return discovered_model_id

        executable_path = self._get_active_chatbot_server_executable_path(backend_mode=CHATBOT_BACKEND_MODE_OLLAMA)
        if not executable_path:
            raise ValueError("Prompt2MTV could not find ollama.exe to pull the Gemma4 model.")

        creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0
        completed_process = subprocess.run(
            [executable_path, "pull", tag],
            capture_output=True,
            timeout=max(300, int(timeout_seconds)),
            creationflags=creation_flags,
        )
        if completed_process.returncode != 0:
            error_output = (completed_process.stderr or completed_process.stdout or b"")
            if isinstance(error_output, bytes):
                error_output = error_output.decode("utf-8", errors="replace")
            raise RuntimeError(f"Ollama pull {tag} failed: {str(error_output or '').strip() or 'unknown error'}")

        deadline = time.time() + max(10, min(30, timeout_seconds))
        poll_delay_seconds = 0.75
        while time.time() < deadline:
            try:
                refreshed_model_ids = self._fetch_chatbot_backend_models(timeout_seconds=min(10, timeout_seconds))
            except Exception:
                refreshed_model_ids = []

            for discovered_model_id in refreshed_model_ids:
                if str(discovered_model_id).strip().lower().startswith("gemma4"):
                    self.chatbot_discovered_model_ids = refreshed_model_ids
                    return discovered_model_id

            time.sleep(poll_delay_seconds)
            poll_delay_seconds = min(3.0, poll_delay_seconds * 1.5)

        raise ValueError(f"Ollama pull {tag} completed, but Prompt2MTV could not discover the model from /v1/models.")

    def _get_chatbot_model_resolution_status(self, model_id):
        normalized_model_id = str(model_id or "").strip()
        preferred_model_id = self._get_chatbot_preferred_ollama_model_name().lower()
        if normalized_model_id.lower() == preferred_model_id:
            return f"preferred model: {normalized_model_id}"
        return f"fallback model: {normalized_model_id}"

    def _stop_managed_chatbot_server(self):
        if not self.chatbot_server_process:
            return

        try:
            if self.chatbot_server_process.poll() is None:
                if sys.platform == "win32":
                    subprocess.run(
                        ["TASKKILL", "/F", "/T", "/PID", str(self.chatbot_server_process.pid)],
                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                else:
                    self.chatbot_server_process.terminate()
        except Exception:
            pass
        finally:
            self.chatbot_server_process = None
            self.chatbot_server_managed_by_app = False
            self.chatbot_server_command = []
            self.chatbot_model_warm = False

    def _start_managed_chatbot_server(self):
        if self._is_chatbot_server_process_running():
            return self.chatbot_server_process

        command = self._build_managed_chatbot_server_command()
        creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0
        self.chatbot_server_process = subprocess.Popen(
            command,
            cwd=os.path.dirname(command[0]),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creation_flags,
        )
        self.chatbot_server_managed_by_app = True
        self.chatbot_server_command = command
        self.log_debug(
            "CHATBOT_SERVER_LAUNCH_REQUESTED",
            pid=self.chatbot_server_process.pid,
            command=" ".join(command),
        )
        return self.chatbot_server_process

    def _wait_for_chatbot_backend_ready(self, timeout_seconds=45, poll_interval_seconds=1.0):
        deadline = time.time() + max(5, timeout_seconds)
        last_probe = None
        while time.time() < deadline:
            if self.chatbot_server_process and self.chatbot_server_process.poll() is not None:
                backend_label = self._get_chatbot_backend_mode_label()
                return {
                    "ok": False,
                    "status": f"{backend_label} exited with code {self.chatbot_server_process.returncode}.",
                    "detail": "Prompt2MTV started the backend process, but it stopped before the chatbot runtime became ready.",
                }

            last_probe = self._probe_chatbot_backend(timeout_seconds=3)
            if last_probe.get("ok"):
                return last_probe
            time.sleep(max(0.25, poll_interval_seconds))

        return last_probe or {
            "ok": False,
            "status": "Timed out waiting for the chatbot backend to become ready.",
            "detail": "Prompt2MTV did not receive a successful response from /v1/models before the startup timeout expired.",
        }

    def _ensure_chatbot_backend_ready_for_use(self, action_label="chatbot request"):
        initial_probe = self._probe_chatbot_backend(timeout_seconds=3)
        if initial_probe.get("ok"):
            if self.chatbot_backend_mode == CHATBOT_BACKEND_MODE_OLLAMA:
                try:
                    model_id = self._ensure_ollama_model_registered(timeout_seconds=max(120, int(self.chatbot_request_timeout or DEFAULT_CHATBOT_REQUEST_TIMEOUT)))
                    initial_probe["model_ids"] = self.chatbot_discovered_model_ids
                    initial_probe["status"] = f"{initial_probe.get('status')} | {self._get_chatbot_model_resolution_status(model_id)}"
                except Exception as exc:
                    return {
                        "ok": False,
                        "status": "Ollama is running, but Prompt2MTV could not prepare the chatbot model automatically.",
                        "detail": str(exc),
                    }
            return initial_probe

        if self.chatbot_backend_mode not in {CHATBOT_BACKEND_MODE_MANAGED, CHATBOT_BACKEND_MODE_OLLAMA}:
            return initial_probe

        if not self.chatbot_auto_launch_server:
            return {
                "ok": False,
                "status": f"{self._get_chatbot_backend_mode_label()} is selected, but automatic launch is disabled.",
                "detail": "Enable automatic launch in Advanced Chatbot Runtime Settings or start the local backend yourself.",
            }

        try:
            executable_path = self._get_active_chatbot_server_executable_path(backend_mode=self.chatbot_backend_mode)
            if executable_path and executable_path != self.chatbot_server_executable_path:
                self.chatbot_server_executable_path = executable_path
                self.save_global_settings()
            self._start_managed_chatbot_server()
        except Exception as exc:
            return {
                "ok": False,
                "status": f"Prompt2MTV could not start {self._get_chatbot_backend_mode_label()} for {action_label}.",
                "detail": str(exc),
            }

        self.log_debug("CHATBOT_SERVER_WAITING_FOR_READY", action=action_label)
        ready_probe = self._wait_for_chatbot_backend_ready(timeout_seconds=min(60, max(15, int(self.chatbot_request_timeout or 30))))
        if ready_probe.get("ok") and self.chatbot_backend_mode == CHATBOT_BACKEND_MODE_OLLAMA:
            try:
                model_id = self._ensure_ollama_model_registered(timeout_seconds=max(120, int(self.chatbot_request_timeout or DEFAULT_CHATBOT_REQUEST_TIMEOUT)))
                ready_probe["model_ids"] = self.chatbot_discovered_model_ids
                ready_probe["status"] = f"{ready_probe.get('status')} | {self._get_chatbot_model_resolution_status(model_id)}"
            except Exception as exc:
                return {
                    "ok": False,
                    "status": "Ollama started, but Prompt2MTV could not prepare the chatbot model automatically.",
                    "detail": str(exc),
                }
        return ready_probe

    def _chatbot_http_json(self, url, method="GET", payload=None, timeout_seconds=15, headers=None):
        request_headers = {"Accept": "application/json"}
        if payload is not None:
            request_headers["Content-Type"] = "application/json"
        if headers:
            request_headers.update(headers)

        request_body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(url, data=request_body, headers=request_headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                raw_body = response.read().decode("utf-8")
                parsed_body = json.loads(raw_body) if raw_body else {}
                return parsed_body, getattr(response, "status", 200)
        except urllib.error.HTTPError as exc:
            error_body = ""
            try:
                error_body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                error_body = ""
            message = f"HTTP {exc.code}"
            if error_body:
                message = f"{message}: {error_body}"
            elif exc.reason:
                message = f"{message}: {exc.reason}"
            raise RuntimeError(message) from exc

    def _fetch_chatbot_backend_models(self, timeout_seconds=5):
        response_payload, _status_code = self._chatbot_http_json(
            f"{self._chatbot_base_url()}/v1/models",
            method="GET",
            timeout_seconds=timeout_seconds,
        )
        model_entries = response_payload.get("data") or []
        model_ids = []
        for entry in model_entries:
            if not isinstance(entry, dict):
                continue
            model_id = str(entry.get("id") or "").strip()
            if model_id and model_id not in model_ids:
                model_ids.append(model_id)
        if not model_ids:
            raise ValueError("The chatbot backend did not return any model ids from /v1/models.")
        self.chatbot_discovered_model_ids = model_ids
        return model_ids

    def _resolve_chatbot_generation_model_id(self, timeout_seconds=5):
        model_ids = self._fetch_chatbot_backend_models(timeout_seconds=timeout_seconds)
        if self.chatbot_model_family == CHATBOT_MODEL_FAMILY_GEMMA4:
            tag = str(self.chatbot_gemma4_ollama_tag or DEFAULT_GEMMA4_OLLAMA_TAG).strip().lower()
            for discovered_model_id in model_ids:
                mid = str(discovered_model_id).strip().lower()
                if mid == tag or (mid.startswith("gemma4") and tag.replace(":", "-") in mid.replace(":", "-")):
                    return discovered_model_id
            for discovered_model_id in model_ids:
                if str(discovered_model_id).strip().lower().startswith("gemma4"):
                    return discovered_model_id
        if self.chatbot_backend_mode == CHATBOT_BACKEND_MODE_OLLAMA:
            preferred_model_id = self._get_chatbot_preferred_ollama_model_name().lower()
            for discovered_model_id in model_ids:
                if str(discovered_model_id).strip().lower() == preferred_model_id:
                    return discovered_model_id
        local_model_id = os.path.splitext(os.path.basename(self.chatbot_model_path or ""))[0].strip().lower()
        if local_model_id:
            for discovered_model_id in model_ids:
                if str(discovered_model_id).strip().lower() == local_model_id:
                    return discovered_model_id
        return model_ids[0]

    def _chatbot_supports_response_format_retry(self, error_message):
        lowered_message = str(error_message or "").lower()
        retry_tokens = [
            "response_format",
            "json_schema",
            "json_object",
            "unsupported",
            "unknown field",
            "additional properties",
            "extra inputs are not permitted",
        ]
        return any(token in lowered_message for token in retry_tokens)

    def _get_chatbot_backend_mode_label(self, backend_mode=None):
        mode_value = str(backend_mode or self.chatbot_backend_mode or CHATBOT_BACKEND_MODE_CONNECT).strip().lower()
        if mode_value == CHATBOT_BACKEND_MODE_MANAGED:
            return "Managed llama.cpp server"
        if mode_value == CHATBOT_BACKEND_MODE_OLLAMA:
            return "Managed Ollama server"
        return "Connect to running local server"

    def _get_chatbot_runtime_state_text(self):
        if self._chatbot_model_is_ready() or self._chatbot_can_generate_without_local_model():
            lines = [
                (
                    f"Model ready: {os.path.basename(self.chatbot_model_path)}"
                    if self._chatbot_model_is_ready()
                    else "Local GGUF not configured. Connect mode can use the model already loaded by your running llama.cpp server."
                ),
                f"Backend: {self._get_chatbot_backend_mode_label()}",
            ]
            if self.chatbot_backend_mode == CHATBOT_BACKEND_MODE_MANAGED:
                if self._chatbot_server_executable_is_valid():
                    lines.append("Managed launch is configured. Prompt2MTV will use your saved llama-server path when runtime actions are added.")
                elif self.chatbot_server_executable_path:
                    lines.append("The saved runtime executable is not a llama-server binary. Prompt2MTV ignored it and cleared managed launch readiness.")
                else:
                    lines.append("Managed launch is selected, but no llama-server executable is saved yet. Use Advanced Runtime Settings to add it.")
            elif self.chatbot_backend_mode == CHATBOT_BACKEND_MODE_OLLAMA:
                active_ollama_path = self._get_active_chatbot_server_executable_path(backend_mode=CHATBOT_BACKEND_MODE_OLLAMA)
                if active_ollama_path:
                    lines.append("Ollama mode is configured. Prompt2MTV can auto-start Ollama and auto-register your local GGUF model when needed.")
                else:
                    lines.append("Ollama mode is selected, but Prompt2MTV could not find ollama.exe yet. Install Ollama or browse to it in Advanced Runtime Settings.")
                lines.append(f"Server URL: {self.chatbot_server_url or self._get_default_chatbot_server_url(CHATBOT_BACKEND_MODE_OLLAMA)}")
            else:
                lines.append(f"Server URL: {self.chatbot_server_url or self._get_default_chatbot_server_url(CHATBOT_BACKEND_MODE_CONNECT)}")
            return "\n".join(lines)
        if self.chatbot_backend_mode == CHATBOT_BACKEND_MODE_CONNECT:
            return "Local GGUF not configured. This is optional in connect mode, but Prompt2MTV still needs a reachable llama.cpp server to generate output."
        if self.chatbot_backend_mode == CHATBOT_BACKEND_MODE_OLLAMA:
            return "Local GGUF not configured. Ollama mode can still use a model you already installed in Ollama, but Prompt2MTV needs a reachable Ollama server first."
        if self.chatbot_model_path:
            return "Model not found. Run model setup to download Qwen or point Prompt2MTV to an existing GGUF file."
        return "Model not configured. Run setup to download Qwen locally."

    def _get_chatbot_readiness_summary(self):
        if self.chatbot_generation_in_progress:
            return "Generating"
        if self._chatbot_requires_local_model() and not self._chatbot_model_is_ready():
            return "Model missing"
        if not self._chatbot_model_is_ready() and self.chatbot_backend_mode != CHATBOT_BACKEND_MODE_CONNECT:
            return "Model not linked"
        health_text = str(self.chatbot_backend_health_text or "").lower()
        if "backend check: online" in health_text:
            return "Ready"
        if self.chatbot_backend_mode == CHATBOT_BACKEND_MODE_CONNECT:
            return "Needs backend"
        if self.chatbot_auto_launch_server:
            return "Ready to start backend"
        return "Needs runtime"

    def _get_chatbot_next_step_text(self):
        if self._chatbot_requires_local_model() and not self._chatbot_model_is_ready():
            return "Set up the local Qwen GGUF first."
        if self.chatbot_backend_mode == CHATBOT_BACKEND_MODE_CONNECT:
            return "Test the configured local server before generating."
        if self.chatbot_backend_mode == CHATBOT_BACKEND_MODE_OLLAMA:
            return "Prompt2MTV can start Ollama for you when generation begins."
        if self.chatbot_backend_mode == CHATBOT_BACKEND_MODE_MANAGED:
            return "Prompt2MTV can start llama-server for you when generation begins."
        return "Start chatting, then generate a prompt draft when you are ready."

    def _get_chatbot_task_options(self):
        return [
            CHATBOT_TASK_CHAT,
            CHATBOT_TASK_SCENE_PLAN,
            CHATBOT_TASK_T2I_OPTIMIZE,
            CHATBOT_TASK_SONG_BRAINSTORM,
        ]

    def _get_selected_chatbot_task(self):
        selected_task = str(self.chatbot_task_var.get() if hasattr(self, "chatbot_task_var") else CHATBOT_TASK_CHAT).strip()
        if selected_task not in self._get_chatbot_task_options():
            return CHATBOT_TASK_CHAT
        return selected_task

    def _get_chatbot_task_description(self, task_name=None):
        task_label = str(task_name or CHATBOT_TASK_CHAT).strip() or CHATBOT_TASK_CHAT
        if task_label == CHATBOT_TASK_CHAT:
            return "Use the assistant as a creative collaborator first. Talk through concept, pacing, references, and scene ideas before committing to a structured plan or production prompt."
        if task_label == CHATBOT_TASK_SCENE_PLAN:
            return "Use this mode when you want the assistant to turn the current direction into a scene-by-scene draft you can review and apply to the timeline."
        if task_label == CHATBOT_TASK_T2I_OPTIMIZE:
            return "Use this mode when the creative direction is clear enough to turn into a tighter production-ready image prompt for the image queue."
        if task_label == CHATBOT_TASK_SONG_BRAINSTORM:
            return "Brainstorm song lyrics, hooks, and style tags with the assistant. Chat back and forth to refine ideas, then Finalize to send lyrics and style to the Music tab."
        return "Select a task to see its generation workflow."

    def _get_chatbot_task_briefing_hint(self, task_name=None):
        task_label = str(task_name or CHATBOT_TASK_CHAT).strip() or CHATBOT_TASK_CHAT
        if task_label == CHATBOT_TASK_CHAT:
            return (
                "Chat naturally about concept, pacing, mood, lyric ideas, scene ideas, camera language, and style references. "
                "When the direction feels strong, switch to Plan Scenes or Generate Prompt Draft."
            )
        if task_label == CHATBOT_TASK_SCENE_PLAN:
            return (
                "Describe the music video direction, emotional arc, pacing, and any must-have beats. "
                "The assistant will turn that into a structured scene flow you can review and apply."
            )
        if task_label == CHATBOT_TASK_T2I_OPTIMIZE:
            return (
                "Summarize the strongest direction, subject, mood, composition, lighting, and style choices. "
                "The assistant will convert that into a more production-ready image prompt."
            )
        if task_label == CHATBOT_TASK_SONG_BRAINSTORM:
            return (
                "Describe the mood, genre, theme, or concept for your song. "
                "Chat naturally to brainstorm lyrics, hooks, and style ideas, then click Finalize Song when ready."
            )
        return "Describe what you want the chatbot to generate."

    def _get_chatbot_task_output_hint(self, task_name=None):
        task_label = str(task_name or CHATBOT_TASK_CHAT).strip() or CHATBOT_TASK_CHAT
        if task_label == CHATBOT_TASK_CHAT:
            return "Replies appear here as a running conversation. Stay in chat mode while you are still exploring the concept, then switch modes when you want a structured artifact."
        if task_label == CHATBOT_TASK_SCENE_PLAN:
            return "Scene plans appear here as reusable assistant artifacts. Review the breakdown, compare saved drafts, then apply the plan to the Scene Timeline when it is ready."
        if task_label == CHATBOT_TASK_T2I_OPTIMIZE:
            return "Prompt drafts appear here as reusable assistant artifacts. Review the wording, copy it, or send it straight to the Image Phase queue when it is ready."
        if task_label == CHATBOT_TASK_SONG_BRAINSTORM:
            return "Chat to brainstorm lyrics and style ideas. When happy, click Finalize Song to produce sendable lyrics and style tags, then Send to Music Tab."
        return "Assistant replies and generated results appear here."

    def _get_chatbot_task_primary_action_copy(self, task_name=None):
        task_label = str(task_name or CHATBOT_TASK_CHAT).strip() or CHATBOT_TASK_CHAT
        if task_label == CHATBOT_TASK_SCENE_PLAN:
            return "Primary action: Plan Scenes"
        if task_label == CHATBOT_TASK_T2I_OPTIMIZE:
            return "Primary action: Generate Prompt Draft"
        if task_label == CHATBOT_TASK_SONG_BRAINSTORM:
            return "Primary action: Send  |  Finalize Song when ready"
        return "Primary action: Send"

    def _get_chatbot_empty_state_heading(self, task_name=None):
        task_label = str(task_name or CHATBOT_TASK_CHAT).strip() or CHATBOT_TASK_CHAT
        if task_label == CHATBOT_TASK_SCENE_PLAN:
            return "Scene planning starts here"
        if task_label == CHATBOT_TASK_T2I_OPTIMIZE:
            return "Prompt drafting starts here"
        if task_label == CHATBOT_TASK_SONG_BRAINSTORM:
            return "Song brainstorming starts here"
        return "Conversation starts here"

    def _get_chatbot_empty_state_text(self, task_name=None):
        task_label = str(task_name or CHATBOT_TASK_CHAT).strip() or CHATBOT_TASK_CHAT
        if task_label == CHATBOT_TASK_SCENE_PLAN:
            return "Describe the concept, flow, and must-hit beats, then use Plan Scenes when you want a first scene breakdown."
        if task_label == CHATBOT_TASK_T2I_OPTIMIZE:
            return "Summarize the strongest visual direction here, then use Generate Prompt Draft when you want a tighter image prompt."
        if task_label == CHATBOT_TASK_SONG_BRAINSTORM:
            return "Describe your song concept, mood, or genre and start chatting. The assistant will help brainstorm lyrics and style ideas. Click Finalize Song when you are happy."
        return "Start a conversation here. Explore the idea naturally before you ask for a structured plan or prompt draft."

    def _get_chatbot_idle_status_text(self, task_name=None):
        task_label = str(task_name or CHATBOT_TASK_CHAT).strip() or CHATBOT_TASK_CHAT
        if task_label == CHATBOT_TASK_SCENE_PLAN:
            return "No scene plan yet. Describe the creative direction, then use Plan Scenes when you want a structured breakdown."
        if task_label == CHATBOT_TASK_T2I_OPTIMIZE:
            return "No prompt draft yet. Define the strongest visual direction, then use Generate Prompt Draft when you want structured output."
        if task_label == CHATBOT_TASK_SONG_BRAINSTORM:
            return "No song draft yet. Chat about your song concept to brainstorm lyrics and style, then use Finalize Song when the direction feels strong."
        return "No reply yet. Start chatting, then switch modes when you want a structured plan or prompt draft."
    
    def _get_chatbot_focus_section_meta(self):
        selected_task = self._get_selected_chatbot_task()
        if self.chatbot_generation_in_progress:
            status_text = "Working"
        elif not self._chatbot_generation_prerequisites_ready():
            status_text = "Needs preflight"
        else:
            status_text = "Ready"
        return f"{selected_task} | {status_text}"

    def _refresh_chatbot_task_ui(self):
        selected_task = self._get_selected_chatbot_task()
        if hasattr(self, "chatbot_task_hint_label"):
            self.chatbot_task_hint_label.config(text=self._get_chatbot_task_description(selected_task))
        if hasattr(self, "chatbot_briefing_hint_label"):
            self.chatbot_briefing_hint_label.config(text=self._get_chatbot_task_briefing_hint(selected_task))
        if hasattr(self, "chatbot_output_hint_label"):
            self.chatbot_output_hint_label.config(text=self._get_chatbot_task_output_hint(selected_task))
        if hasattr(self, "chatbot_mode_summary_label"):
            self.chatbot_mode_summary_label.config(text=self._get_chatbot_task_primary_action_copy(selected_task))

        send_variant = "primary" if selected_task in (CHATBOT_TASK_CHAT, CHATBOT_TASK_SONG_BRAINSTORM) else "secondary"
        scene_variant = "primary" if selected_task == CHATBOT_TASK_SCENE_PLAN else "secondary"
        generate_variant = "primary" if selected_task == CHATBOT_TASK_T2I_OPTIMIZE else "accent"
        finalize_song_variant = "primary" if selected_task == CHATBOT_TASK_SONG_BRAINSTORM else "secondary"
        apply_music_variant = "success" if selected_task == CHATBOT_TASK_SONG_BRAINSTORM else "secondary"

        if hasattr(self, "chatbot_send_btn"):
            self._style_button(self.chatbot_send_btn, send_variant)
        if hasattr(self, "chatbot_scene_plan_btn"):
            self._style_button(self.chatbot_scene_plan_btn, scene_variant)
        if hasattr(self, "chatbot_generate_btn"):
            self._style_button(self.chatbot_generate_btn, generate_variant)
        if hasattr(self, "chatbot_finalize_song_btn"):
            self._style_button(self.chatbot_finalize_song_btn, finalize_song_variant)
        if hasattr(self, "chatbot_new_chat_btn"):
            self._style_button(self.chatbot_new_chat_btn, "ghost")
        if hasattr(self, "chatbot_clear_chat_btn"):
            self._style_button(self.chatbot_clear_chat_btn, "ghost")
        if hasattr(self, "chatbot_output_mode_btn"):
            self._style_button(self.chatbot_output_mode_btn, "ghost", compact=True)
        if hasattr(self, "chatbot_copy_output_btn"):
            self._style_button(self.chatbot_copy_output_btn, "secondary", compact=True)
        if hasattr(self, "chatbot_apply_btn"):
            self._style_button(self.chatbot_apply_btn, "success", compact=True)
        if hasattr(self, "chatbot_apply_scene_btn"):
            self._style_button(self.chatbot_apply_scene_btn, "success", compact=True)
        if hasattr(self, "chatbot_apply_music_btn"):
            self._style_button(self.chatbot_apply_music_btn, apply_music_variant, compact=True)
        if "chatbot_focus_workspace" in self.collapsible_sections:
            self._update_collapsible_section_meta("chatbot_focus_workspace", self._get_chatbot_focus_section_meta())

    def _on_chatbot_task_changed(self, _event=None):
        selected_task = self._get_selected_chatbot_task()
        if hasattr(self, "chatbot_task_var") and self.chatbot_task_var.get() != selected_task:
            self.chatbot_task_var.set(selected_task)
        self._refresh_chatbot_task_ui()
        if not self.chatbot_last_result and not self._get_chatbot_transcript_turns():
            self.chatbot_output_preview_cache = self._get_chatbot_empty_state_text(selected_task)
        self._refresh_chatbot_output_preview()

    def _on_chatbot_model_family_changed(self, _event=None):
        chosen_family = str(self.chatbot_model_family_var.get() or "").strip().lower()
        if chosen_family not in {CHATBOT_MODEL_FAMILY_QWEN3, CHATBOT_MODEL_FAMILY_GEMMA4}:
            chosen_family = CHATBOT_MODEL_FAMILY_QWEN3
        self.chatbot_model_family = chosen_family
        if chosen_family == CHATBOT_MODEL_FAMILY_GEMMA4:
            if self.chatbot_backend_mode != CHATBOT_BACKEND_MODE_OLLAMA:
                self._pre_gemma4_backend_mode = self.chatbot_backend_mode
                self._pre_gemma4_server_url = self.chatbot_server_url
            self.chatbot_backend_mode = CHATBOT_BACKEND_MODE_OLLAMA
            self.chatbot_server_url = self._get_default_chatbot_server_url(CHATBOT_BACKEND_MODE_OLLAMA)
            if not self.chatbot_server_executable_path:
                self.chatbot_server_executable_path = self._get_active_chatbot_server_executable_path(backend_mode=CHATBOT_BACKEND_MODE_OLLAMA)
            self.chatbot_gemma4_tag_row.pack(fill=tk.X, pady=(6, 0), after=self.chatbot_model_family_row)
        else:
            if hasattr(self, "chatbot_gemma4_tag_row"):
                self.chatbot_gemma4_tag_row.pack_forget()
            restored_mode = getattr(self, "_pre_gemma4_backend_mode", None)
            if restored_mode and restored_mode in {CHATBOT_BACKEND_MODE_CONNECT, CHATBOT_BACKEND_MODE_MANAGED, CHATBOT_BACKEND_MODE_OLLAMA}:
                self.chatbot_backend_mode = restored_mode
                self.chatbot_server_url = getattr(self, "_pre_gemma4_server_url", "") or self._get_default_chatbot_server_url(restored_mode)
            elif self.chatbot_backend_mode == CHATBOT_BACKEND_MODE_OLLAMA:
                self.chatbot_backend_mode = CHATBOT_BACKEND_MODE_CONNECT
                self.chatbot_server_url = self._get_default_chatbot_server_url(CHATBOT_BACKEND_MODE_CONNECT)
        self.save_global_settings()
        self._refresh_chatbot_runtime_ui()

    def _on_chatbot_gemma4_tag_changed(self, _event=None):
        chosen_tag = str(self.chatbot_gemma4_tag_var.get() or "").strip()
        if chosen_tag in GEMMA4_OLLAMA_TAG_OPTIONS:
            self.chatbot_gemma4_ollama_tag = chosen_tag
        self.save_global_settings()
        self._refresh_chatbot_runtime_ui()

    def _create_empty_chatbot_state(self):
        return {
            "schema_version": CHATBOT_CREATIVE_STATE_SCHEMA_VERSION,
            "conversations": [],
            "artifacts": [],
            "view": {
                "active_conversation_id": None,
                "selected_artifact_id": None,
                "composer_draft": "",
                "selected_scene_id": None,
                "selected_scene_order": None,
            },
        }

    def _chatbot_timestamp(self):
        return datetime.now().isoformat(timespec="seconds")

    def _generate_chatbot_state_id(self, prefix):
        return f"{prefix}_{uuid.uuid4().hex[:12]}"

    def _get_chatbot_view_state(self):
        if not isinstance(getattr(self, "chatbot_state", None), dict):
            self.chatbot_state = self._create_empty_chatbot_state()
        view_state = self.chatbot_state.setdefault("view", {})
        for key, default_value in {
            "active_conversation_id": None,
            "selected_artifact_id": None,
            "composer_draft": "",
            "selected_scene_id": None,
            "selected_scene_order": None,
        }.items():
            view_state.setdefault(key, default_value)
        return view_state

    def _get_chatbot_conversation_by_id(self, conversation_id):
        normalized_id = str(conversation_id or "").strip()
        if not normalized_id:
            return None
        for conversation in self.chatbot_state.get("conversations", []):
            if str(conversation.get("conversation_id") or "").strip() == normalized_id:
                return conversation
        return None

    def _get_chatbot_artifact_by_id(self, artifact_id):
        normalized_id = str(artifact_id or "").strip()
        if not normalized_id:
            return None
        for artifact in self.chatbot_state.get("artifacts", []):
            if str(artifact.get("artifact_id") or "").strip() == normalized_id:
                return artifact
        return None

    def _ensure_active_chatbot_conversation(self, title=None):
        view_state = self._get_chatbot_view_state()
        active_conversation = self._get_chatbot_conversation_by_id(view_state.get("active_conversation_id"))
        if active_conversation:
            return active_conversation.get("conversation_id")

        timestamp = self._chatbot_timestamp()
        conversation_id = self._generate_chatbot_state_id("conversation")
        conversation = {
            "conversation_id": conversation_id,
            "created_at": timestamp,
            "updated_at": timestamp,
            "title": str(title or "Creative Assistant").strip() or "Creative Assistant",
            "status": "active",
            "turns": [],
        }
        self.chatbot_state.setdefault("conversations", []).append(conversation)
        view_state["active_conversation_id"] = conversation_id
        return conversation_id

    def _append_chatbot_turn(self, role, content, kind="chat", related_artifact_ids=None, conversation_id=None):
        related_ids = [
            str(artifact_id or "").strip()
            for artifact_id in (related_artifact_ids or [])
            if str(artifact_id or "").strip()
        ]
        content_text = str(content or "").strip()
        if not content_text and not related_ids:
            return None

        resolved_conversation_id = str(conversation_id or self._ensure_active_chatbot_conversation()).strip()
        conversation = self._get_chatbot_conversation_by_id(resolved_conversation_id)
        if not conversation:
            resolved_conversation_id = self._ensure_active_chatbot_conversation()
            conversation = self._get_chatbot_conversation_by_id(resolved_conversation_id)
        if not conversation:
            return None

        timestamp = self._chatbot_timestamp()
        turn = {
            "turn_id": self._generate_chatbot_state_id("turn"),
            "role": str(role or "assistant").strip() or "assistant",
            "kind": str(kind or "chat").strip() or "chat",
            "content": content_text,
            "created_at": timestamp,
            "artifact_ids": related_ids,
        }
        conversation.setdefault("turns", []).append(turn)
        conversation["updated_at"] = timestamp
        return turn.get("turn_id")

    def _get_chatbot_conversation_turns(self, conversation_id=None, limit=12):
        resolved_conversation_id = str(conversation_id or self._get_chatbot_view_state().get("active_conversation_id") or "").strip()
        conversation = self._get_chatbot_conversation_by_id(resolved_conversation_id)
        if not conversation:
            return []

        turns = []
        for turn in conversation.get("turns", []):
            if not isinstance(turn, dict):
                continue
            if str(turn.get("kind") or "chat").strip() != "chat":
                continue
            role = str(turn.get("role") or "").strip()
            content = str(turn.get("content") or "").strip()
            if role not in {"user", "assistant"} or not content:
                continue
            turns.append({"role": role, "content": content})
        return turns[-max(1, int(limit or 12)):]

    def _get_chatbot_active_conversation(self):
        conversation_id = self._ensure_active_chatbot_conversation()
        return self._get_chatbot_conversation_by_id(conversation_id)

    def _get_chatbot_transcript_turns(self):
        conversation = self._get_chatbot_active_conversation()
        if not conversation:
            return []
        transcript_turns = []
        for turn in conversation.get("turns", []):
            if isinstance(turn, dict):
                transcript_turns.append(turn)
        return transcript_turns

    def _format_chatbot_turn_timestamp(self, timestamp_value):
        timestamp_text = str(timestamp_value or "").strip()
        if not timestamp_text:
            return ""
        if "T" in timestamp_text:
            return timestamp_text.split("T", 1)[1][:5]
        if " " in timestamp_text:
            return timestamp_text.rsplit(" ", 1)[-1][:5]
        return timestamp_text[:5]

    def _get_chatbot_transcript_signature(self):
        signature_parts = []
        for turn in self._get_chatbot_transcript_turns():
            if not isinstance(turn, dict):
                continue
            signature_parts.append(
                (
                    str(turn.get("turn_id") or "").strip(),
                    str(turn.get("created_at") or "").strip(),
                    tuple(
                        str(artifact_id or "").strip()
                        for artifact_id in (turn.get("artifact_ids") or [])
                        if str(artifact_id or "").strip()
                    ),
                )
            )
        return tuple(signature_parts)

    def _get_chatbot_transcript_view(self):
        if not hasattr(self, "chatbot_transcript_canvas"):
            return (0.0, 1.0)
        try:
            return self.chatbot_transcript_canvas.yview()
        except tk.TclError:
            return (0.0, 1.0)

    def _chatbot_transcript_is_near_bottom(self, threshold=0.98):
        _top, bottom = self._get_chatbot_transcript_view()
        return bottom >= threshold

    def _on_chatbot_transcript_scrollbar(self, *args):
        if hasattr(self, "chatbot_transcript_canvas"):
            self.chatbot_transcript_canvas.yview(*args)

    def _on_chatbot_transcript_mousewheel(self, event):
        if not hasattr(self, "chatbot_transcript_canvas"):
            return None
        delta = 0
        if getattr(event, "delta", 0):
            delta = int(-1 * (event.delta / 120))
        elif getattr(event, "num", None) == 4:
            delta = -1
        elif getattr(event, "num", None) == 5:
            delta = 1
        if delta:
            self.chatbot_transcript_canvas.yview_scroll(delta, "units")
            return "break"
        return None

    def _refresh_chatbot_transcript(self):
        if not hasattr(self, "chatbot_transcript_frame"):
            return

        previous_view_top, previous_view_bottom = self._get_chatbot_transcript_view()
        previous_signature = getattr(self, "chatbot_transcript_last_signature", ())
        next_signature = self._get_chatbot_transcript_signature()
        transcript_changed = next_signature != previous_signature
        should_follow_latest = transcript_changed and previous_view_bottom >= 0.98

        for child in self.chatbot_transcript_frame.winfo_children():
            child.destroy()

        transcript_turns = self._get_chatbot_transcript_turns()
        selected_task = self._get_selected_chatbot_task()
        placeholder_text = str(self.chatbot_output_preview_cache or "").strip() or self._get_chatbot_empty_state_text(selected_task)

        if not transcript_turns:
            empty_card = tk.Frame(self.chatbot_transcript_frame, padx=16, pady=16)
            empty_card.pack(fill=tk.X, expand=False, pady=(0, 8))
            self._style_panel(empty_card, self.colors["surface"], border=True)
            empty_title = tk.Label(empty_card, text=self._get_chatbot_empty_state_heading(selected_task))
            empty_title.pack(anchor="w")
            self._style_label(empty_title, "section", empty_card.cget("bg"))
            empty_copy = tk.Label(empty_card, text=placeholder_text, anchor="w", justify=tk.LEFT, wraplength=520)
            empty_copy.pack(anchor="w", fill=tk.X, pady=(8, 0))
            self._style_label(empty_copy, "muted", empty_card.cget("bg"))
        else:
            for turn in transcript_turns:
                role = str(turn.get("role") or "assistant").strip() or "assistant"
                kind = str(turn.get("kind") or "chat").strip() or "chat"
                content = str(turn.get("content") or "").strip()
                timestamp_text = self._format_chatbot_turn_timestamp(turn.get("created_at"))
                is_user_turn = role == "user"

                row = tk.Frame(self.chatbot_transcript_frame)
                row.pack(fill=tk.X, expand=False, pady=(0, 10))
                self._style_panel(row, self.colors["card"])

                bubble = tk.Frame(row, padx=12, pady=10)
                bubble.pack(anchor="e" if is_user_turn else "w")
                bubble_color = self.colors["primary"] if is_user_turn else self.colors["surface_soft"]
                bubble_tone = self.colors["text"] if is_user_turn else self.colors["text"]
                if kind == "status":
                    bubble_color = self.colors["surface"]
                self._style_panel(bubble, bubble_color, border=not is_user_turn)

                heading_text = "You" if is_user_turn else ("Assistant" if role == "assistant" else role.title())
                if timestamp_text:
                    heading_text = f"{heading_text}  {timestamp_text}"
                heading = tk.Label(bubble, text=heading_text, anchor="w")
                heading.pack(anchor="w")
                self._style_label(heading, "muted", bubble.cget("bg"))
                heading.configure(
                    fg=self.colors["text"] if is_user_turn else self.colors["text_muted"],
                    font=self.fonts["small"],
                )

                if content:
                    content_label = tk.Label(bubble, text=content, anchor="w", justify=tk.LEFT, wraplength=520)
                    content_label.pack(anchor="w", fill=tk.X, pady=(6, 0))
                    content_label.configure(fg=bubble_tone)
                    self._style_label(content_label, "body", bubble.cget("bg"))

                if content:
                    actions_row = tk.Frame(bubble)
                    actions_row.pack(anchor="w", fill=tk.X, pady=(4, 0))
                    self._style_panel(actions_row, bubble_color)
                    copy_btn = tk.Button(
                        actions_row, text="Copy", cursor="hand2",
                        command=lambda msg=content: self._copy_chatbot_message_to_clipboard(msg),
                    )
                    copy_btn.pack(side=tk.LEFT)
                    self._style_button(copy_btn, "ghost", compact=True)

                artifact_ids = [
                    str(artifact_id or "").strip()
                    for artifact_id in (turn.get("artifact_ids") or [])
                    if str(artifact_id or "").strip()
                ]
                for artifact_id in artifact_ids:
                    artifact = self._get_chatbot_artifact_by_id(artifact_id)
                    if not artifact:
                        continue
                    artifact_card = tk.Frame(bubble, padx=10, pady=10)
                    artifact_card.pack(fill=tk.X, pady=(8, 0))
                    self._style_panel(artifact_card, self.colors["surface"], border=True)
                    artifact_card.configure(cursor="hand2")

                    selected_artifact = self._get_selected_chatbot_artifact()
                    is_selected_artifact = bool(
                        selected_artifact
                        and str(selected_artifact.get("artifact_id") or "").strip() == str(artifact.get("artifact_id") or "").strip()
                    )
                    if is_selected_artifact:
                        artifact_card.configure(highlightbackground=self.colors["accent"], highlightthickness=2)

                    artifact_title = tk.Label(artifact_card, text=str(artifact.get("title") or "Prompt Draft").strip() or "Prompt Draft", anchor="w")
                    artifact_title.pack(anchor="w")
                    self._style_label(artifact_title, "body_strong", artifact_card.cget("bg"))

                    artifact_meta = tk.Label(
                        artifact_card,
                        text=f"{str(artifact.get('task_label') or CHATBOT_TASK_T2I_OPTIMIZE).strip()} | {str(artifact.get('status') or 'generated').strip().title()}",
                        anchor="w",
                        justify=tk.LEFT,
                        wraplength=500,
                    )
                    artifact_meta.pack(anchor="w", fill=tk.X, pady=(4, 0))
                    self._style_label(artifact_meta, "muted", artifact_card.cget("bg"))

                    structured_payload = artifact.get("structured_payload") or {}
                    preview_text = str(structured_payload.get("optimized_prompt") or "").strip()
                    if not preview_text and str(artifact.get("artifact_type") or "").strip() == "scene_plan":
                        planned_scenes = structured_payload.get("scenes") if isinstance(structured_payload.get("scenes"), list) else []
                        if planned_scenes:
                            preview_text = f"{len(planned_scenes)} planned scenes ready to review and apply."
                    if preview_text:
                        artifact_preview = tk.Label(artifact_card, text=preview_text, anchor="w", justify=tk.LEFT, wraplength=500)
                        artifact_preview.pack(anchor="w", fill=tk.X, pady=(8, 0))
                        self._style_label(artifact_preview, "body", artifact_card.cget("bg"))

                    clickable_widgets = [artifact_card, artifact_title, artifact_meta]
                    if preview_text:
                        clickable_widgets.append(artifact_preview)
                    for clickable_widget in clickable_widgets:
                        clickable_widget.configure(cursor="hand2")
                        clickable_widget.bind(
                            "<Button-1>",
                            lambda _event, selected_artifact_id=artifact.get("artifact_id"): self._handle_chatbot_artifact_card_click(selected_artifact_id)
                        )

        self.chatbot_transcript_frame.update_idletasks()
        self.chatbot_transcript_canvas.configure(scrollregion=self.chatbot_transcript_canvas.bbox("all"))
        self.chatbot_transcript_last_signature = next_signature
        if should_follow_latest:
            self.chatbot_transcript_canvas.yview_moveto(1.0)
        else:
            self.chatbot_transcript_canvas.yview_moveto(max(0.0, previous_view_top))

    def _get_chatbot_chat_system_prompt(self):
        selected_task = self._get_selected_chatbot_task()
        if selected_task == CHATBOT_TASK_SONG_BRAINSTORM:
            return (
                "You are Prompt2MTV's songwriting assistant. "
                "Help the user brainstorm song lyrics, hooks, verse/chorus/bridge structures, and style direction. "
                "Suggest genre tags, mood, texture, instrumentation, and vocal style that work well together. "
                "When writing lyrics, use section markers like [verse], [chorus], [bridge], [outro], and [intro] "
                "because the music generator (ACE-Step) expects that format. "
                "Stay conversational and collaborative. Offer alternatives, variations, and creative pivots. "
                "Ask clarifying questions about vibe, tempo, theme, and emotion to sharpen the direction. "
                "Do not return JSON or structured output during chat. "
                "Do not expose chain-of-thought, reasoning markers, or control tokens "
                "like /think, /no_think, <think>, or <|channel>thought in the visible reply. "
                "Keep replies practical, focused, and creatively useful."
            )
        return (
            "You are Prompt2MTV's creative assistant for music video development. "
            "Reply conversationally and collaboratively. Help the user shape concept, mood, pacing, scene ideas, visual motifs, and prompt direction. "
            "Do not return JSON or schema output unless the app explicitly requests a structured artifact. "
            "Do not expose chain-of-thought, reasoning markers, or control tokens "
            "like /think, /no_think, <think>, or <|channel>thought in the visible reply. "
            "Keep replies practical, focused, and creatively useful."
        )

    def _chatbot_request_targets_qwen3(self, model_id=None):
        resolved_model_id = str(model_id or "").strip().lower()
        if "qwen3" in resolved_model_id or "qwen-qwen3" in resolved_model_id:
            return True
        resolved_model_path = str(self.chatbot_model_path or self.chatbot_model_filename or "").strip().lower()
        return "qwen3" in resolved_model_path

    def _chatbot_request_targets_gemma4(self, model_id=None):
        if self.chatbot_model_family == CHATBOT_MODEL_FAMILY_GEMMA4:
            return True
        resolved_model_id = str(model_id or "").strip().lower()
        return "gemma4" in resolved_model_id

    def _chatbot_should_force_non_thinking(self, model_id=None):
        if not self.chatbot_default_to_non_thinking:
            return False
        if self.chatbot_backend_mode != CHATBOT_BACKEND_MODE_OLLAMA:
            return False
        return self._chatbot_request_targets_qwen3(model_id=model_id) or self._chatbot_request_targets_gemma4(model_id=model_id)

    def _apply_chatbot_non_thinking_suffix(self, text, force_non_thinking=False, model_id=None):
        content_text = str(text or "").strip()
        if not content_text:
            return content_text
        if not force_non_thinking:
            return content_text
        if self._chatbot_request_targets_gemma4(model_id=model_id):
            return content_text
        lowered_text = content_text.lower()
        if "/no_think" in lowered_text or "/think" in lowered_text:
            return content_text
        return f"{content_text}\n/no_think"

    def _build_chatbot_request_messages(self, base_messages, model_id=None, force_non_thinking=False):
        request_messages = []
        for message in base_messages or []:
            if not isinstance(message, dict):
                continue
            role = str(message.get("role") or "").strip()
            content = str(message.get("content") or "").strip()
            if role not in {"system", "user", "assistant"} or not content:
                continue
            request_messages.append({"role": role, "content": content})

        if force_non_thinking and request_messages:
            for message_index in range(len(request_messages) - 1, -1, -1):
                if request_messages[message_index].get("role") != "user":
                    continue
                request_messages[message_index] = dict(
                    request_messages[message_index],
                    content=self._apply_chatbot_non_thinking_suffix(request_messages[message_index].get("content"), force_non_thinking=True, model_id=model_id),
                )
                break
        return request_messages

    def _get_chatbot_effective_defaults(self):
        if self.chatbot_model_family == CHATBOT_MODEL_FAMILY_GEMMA4:
            return {
                "temperature": DEFAULT_GEMMA4_TEMPERATURE,
                "top_p": DEFAULT_GEMMA4_TOP_P,
                "top_k": DEFAULT_GEMMA4_TOP_K,
                "min_p": DEFAULT_GEMMA4_MIN_P,
                "repeat_penalty": DEFAULT_GEMMA4_REPEAT_PENALTY,
            }
        return {
            "temperature": DEFAULT_CHATBOT_TEMPERATURE,
            "top_p": DEFAULT_CHATBOT_TOP_P,
            "top_k": DEFAULT_CHATBOT_TOP_K,
            "min_p": DEFAULT_CHATBOT_MIN_P,
            "repeat_penalty": DEFAULT_CHATBOT_REPEAT_PENALTY,
        }

    def _build_chatbot_sampling_payload(self):
        defaults = self._get_chatbot_effective_defaults()
        payload = {
            "temperature": float(self.chatbot_temperature if self.chatbot_temperature is not None else defaults["temperature"]),
            "top_p": float(self.chatbot_top_p if self.chatbot_top_p is not None else defaults["top_p"]),
            "top_k": max(1, int(self.chatbot_top_k if self.chatbot_top_k is not None else defaults["top_k"])),
            "min_p": max(0.0, float(self.chatbot_min_p if self.chatbot_min_p is not None else defaults["min_p"])),
        }
        repeat_penalty = float(self.chatbot_repeat_penalty if self.chatbot_repeat_penalty is not None else defaults["repeat_penalty"])
        if repeat_penalty > 0:
            payload["repeat_penalty"] = repeat_penalty
        return payload

    def _sanitize_chatbot_visible_response(self, text):
        visible_text = str(text or "")
        if not visible_text:
            return ""

        visible_text = re.sub(r"<think>.*?</think>", "", visible_text, flags=re.DOTALL | re.IGNORECASE)
        visible_text = re.sub(r"(?im)^[ \t]*/(?:no_)?think[ \t]*\r?\n?", "", visible_text)
        visible_text = re.sub(r"(?im)^[ \t]*</?think>[ \t]*\r?\n?", "", visible_text)
        visible_text = re.sub(r"<\|channel>thought\n.*?<channel\|>", "", visible_text, flags=re.DOTALL)
        visible_text = re.sub(r"(?m)^[ \t]*<\|channel>thought[ \t]*\r?\n?", "", visible_text)
        visible_text = re.sub(r"(?m)^[ \t]*<channel\|>[ \t]*\r?\n?", "", visible_text)
        return visible_text.strip()

    def _extract_chatbot_response_parts(self, response_payload):
        choices = response_payload.get("choices") or []
        if not choices:
            raise ValueError("The chatbot server returned no choices.")

        message_payload = choices[0].get("message") or {}
        reasoning_parts = []
        content_parts = []

        reasoning_content = message_payload.get("reasoning_content")
        if isinstance(reasoning_content, list):
            reasoning_parts.extend(str(part.get("text") or part.get("content") or "") for part in reasoning_content if isinstance(part, dict))
        elif reasoning_content is not None:
            reasoning_parts.append(str(reasoning_content or ""))

        content = message_payload.get("content")
        if isinstance(content, list):
            for part in content:
                if not isinstance(part, dict):
                    part_text = str(part or "").strip()
                    if part_text:
                        content_parts.append(part_text)
                    continue
                part_type = str(part.get("type") or "text").strip().lower()
                part_text = str(part.get("text") or part.get("content") or "").strip()
                if not part_text:
                    continue
                if "think" in part_type or "reason" in part_type:
                    reasoning_parts.append(part_text)
                else:
                    content_parts.append(part_text)
        elif content is not None:
            content_parts.append(str(content or ""))

        visible_content = "\n".join(part for part in content_parts if str(part or "").strip()).strip()
        hidden_reasoning = "\n".join(part for part in reasoning_parts if str(part or "").strip()).strip()

        think_match = re.match(r"\s*<think>(.*?)</think>\s*(.*)\Z", visible_content, flags=re.DOTALL | re.IGNORECASE)
        if think_match:
            inline_reasoning = str(think_match.group(1) or "").strip()
            visible_content = str(think_match.group(2) or "").strip()
            if inline_reasoning:
                hidden_reasoning = "\n\n".join(part for part in [hidden_reasoning, inline_reasoning] if part).strip()

        visible_content = self._sanitize_chatbot_visible_response(visible_content)
        visible_content = re.sub(r"^```(?:json)?\s*", "", visible_content, flags=re.IGNORECASE).strip() if visible_content.startswith("```") else visible_content

        return {
            "content": visible_content,
            "reasoning": hidden_reasoning,
        }

    def _extract_chatbot_response_text(self, response_payload):
        response_parts = self._extract_chatbot_response_parts(response_payload)
        content_text = str(response_parts.get("content") or "").strip()
        if not content_text:
            raise ValueError("The chatbot reply was empty.")
        return content_text

    def _request_chatbot_chat_reply(self, conversation_id=None):
        timeout_seconds = max(15, int(self.chatbot_request_timeout or DEFAULT_CHATBOT_REQUEST_TIMEOUT))
        model_id = self._resolve_chatbot_generation_model_id(timeout_seconds=min(timeout_seconds, 10))
        force_non_thinking = self._chatbot_should_force_non_thinking(model_id=model_id)
        selected_task = self._get_selected_chatbot_task()
        is_song_mode = selected_task == CHATBOT_TASK_SONG_BRAINSTORM
        messages = self._build_chatbot_request_messages(
            [{"role": "system", "content": self._get_chatbot_chat_system_prompt()}] + self._get_chatbot_conversation_turns(conversation_id=conversation_id, limit=12),
            model_id=model_id,
            force_non_thinking=force_non_thinking,
        )
        payload = {
            "model": model_id,
            "messages": messages,
            "max_tokens": 4096,
            "stream": False,
        }
        payload.update(self._build_chatbot_sampling_payload())
        if force_non_thinking and self._chatbot_request_targets_gemma4(model_id=model_id):
            payload["think"] = False
        response_payload = self._post_chatbot_completion_payload(
            payload,
            timeout_seconds=timeout_seconds,
        )
        response_parts = self._extract_chatbot_response_parts(response_payload)
        response_text = str(response_parts.get("content") or "").strip()
        if not response_text:
            raise ValueError("The chatbot reply was empty.")
        return {
            "content": response_text,
            "model_id": model_id,
            "raw_content": response_text,
            "reasoning_content": str(response_parts.get("reasoning") or "").strip(),
        }

    def _start_new_chatbot_conversation(self):
        self._capture_chatbot_view_state_from_widgets()
        self.chatbot_state["view"]["active_conversation_id"] = None
        self.chatbot_state["view"]["selected_artifact_id"] = None
        self.chatbot_state["view"]["composer_draft"] = ""
        self.chatbot_pending_request_mode = None
        self._ensure_active_chatbot_conversation(title="Creative Assistant")
        self.chatbot_last_result = None
        self.chatbot_output_show_raw = False
        self.chatbot_output_preview_cache = self._get_chatbot_empty_state_text(self._get_selected_chatbot_task())
        self._apply_chatbot_view_state_to_widgets()
        self._refresh_chatbot_output_preview()
        self.update_status("Started a new chatbot conversation.", "blue")

    def _clear_chatbot_conversation(self):
        if self.chatbot_generation_in_progress:
            return
        conversation = self._get_chatbot_active_conversation()
        if not conversation or not conversation.get("turns"):
            return
        conversation["turns"] = []
        self.chatbot_last_result = None
        self.chatbot_output_show_raw = False
        self.chatbot_pending_request_mode = None
        self.chatbot_output_preview_cache = self._get_chatbot_empty_state_text(self._get_selected_chatbot_task())
        self._refresh_chatbot_output_preview()
        self.update_status("Chat history cleared.", "blue")

    def _infer_chatbot_artifact_type(self, task_name=None):
        task_label = str(task_name or "").strip() or CHATBOT_TASK_T2I_OPTIMIZE
        if task_label == CHATBOT_TASK_T2I_OPTIMIZE:
            return "t2i_prompt_optimize"
        if task_label == CHATBOT_TASK_SCENE_PLAN:
            return "scene_plan"
        if task_label == CHATBOT_TASK_SONG_BRAINSTORM:
            return "song_brainstorm"
        return "chatbot_result"

    def _get_chatbot_recent_history_entries(self, limit=20):
        history_entries = []
        for artifact in self.chatbot_state.get("artifacts", []):
            structured_payload = artifact.get("structured_payload") if isinstance(artifact.get("structured_payload"), dict) else {}
            history_entries.append({
                "artifact_id": str(artifact.get("artifact_id") or "").strip(),
                "created_at": str(artifact.get("created_at") or "").strip() or datetime.now().strftime("%H:%M:%S"),
                "task_label": str(artifact.get("task_label") or artifact.get("artifact_type") or CHATBOT_TASK_T2I_OPTIMIZE).strip(),
                "briefing": str(artifact.get("source_prompt_summary") or artifact.get("briefing") or "").strip(),
                "result": copy.deepcopy(structured_payload),
                "status": str(artifact.get("status") or "generated").strip(),
                "apply_count": len(artifact.get("applied_links") or []),
            })
        return history_entries[:limit]

    def _sync_chatbot_compatibility_state(self):
        self.chatbot_result_history = self._get_chatbot_recent_history_entries()
        view_state = self._get_chatbot_view_state()
        selected_artifact = self._get_chatbot_artifact_by_id(view_state.get("selected_artifact_id"))
        if not selected_artifact and self.chatbot_state.get("artifacts"):
            selected_artifact = self.chatbot_state["artifacts"][0]
            view_state["selected_artifact_id"] = selected_artifact.get("artifact_id")

        structured_payload = selected_artifact.get("structured_payload") if selected_artifact else None
        self.chatbot_last_result = copy.deepcopy(structured_payload) if isinstance(structured_payload, dict) else None

    def _get_selected_chatbot_artifact(self):
        view_state = self._get_chatbot_view_state()
        return self._get_chatbot_artifact_by_id(view_state.get("selected_artifact_id"))

    def _capture_chatbot_view_state_from_widgets(self):
        view_state = self._get_chatbot_view_state()
        if hasattr(self, "chatbot_briefing_text"):
            view_state["composer_draft"] = self.chatbot_briefing_text.get("1.0", tk.END).strip()
        return view_state

    def _apply_chatbot_view_state_to_widgets(self):
        view_state = self._get_chatbot_view_state()
        if hasattr(self, "chatbot_briefing_text"):
            self.chatbot_briefing_text.delete("1.0", tk.END)
            composer_draft = str(view_state.get("composer_draft") or "").strip()
            if composer_draft:
                self.chatbot_briefing_text.insert("1.0", composer_draft)

    def _create_chatbot_artifact(self, task_name, briefing_text, result, conversation_id=None, artifact_type=None):
        resolved_conversation_id = str(conversation_id or self._ensure_active_chatbot_conversation()).strip()
        timestamp = self._chatbot_timestamp()
        structured_payload = copy.deepcopy(result) if isinstance(result, dict) else {"content": str(result or "")}
        artifact = {
            "artifact_id": self._generate_chatbot_state_id("artifact"),
            "conversation_id": resolved_conversation_id,
            "artifact_type": str(artifact_type or self._infer_chatbot_artifact_type(task_name)).strip(),
            "status": "generated",
            "created_at": timestamp,
            "updated_at": timestamp,
            "task_label": str(task_name or "").strip() or CHATBOT_TASK_T2I_OPTIMIZE,
            "title": str((structured_payload or {}).get("title") or "Untitled result").strip() or "Untitled result",
            "briefing": str(briefing_text or "").strip(),
            "source_prompt_summary": str(briefing_text or "").strip()[:240],
            "structured_payload": structured_payload,
            "display_payload": self._format_chatbot_result_for_display(structured_payload, show_raw=False),
            "generation_metadata": {
                "model_id": str((structured_payload or {}).get("model_id") or "").strip(),
                "temperature": float(self.chatbot_temperature or DEFAULT_CHATBOT_TEMPERATURE),
                "top_p": float(self.chatbot_top_p if self.chatbot_top_p is not None else DEFAULT_CHATBOT_TOP_P),
                "top_k": int(self.chatbot_top_k or DEFAULT_CHATBOT_TOP_K),
                "min_p": float(self.chatbot_min_p if self.chatbot_min_p is not None else DEFAULT_CHATBOT_MIN_P),
                "repeat_penalty": float(self.chatbot_repeat_penalty if self.chatbot_repeat_penalty is not None else DEFAULT_CHATBOT_REPEAT_PENALTY),
                "request_timeout": int(self.chatbot_request_timeout or DEFAULT_CHATBOT_REQUEST_TIMEOUT),
                "backend_mode": str(self.chatbot_backend_mode or "").strip(),
                "default_to_non_thinking": bool(self.chatbot_default_to_non_thinking),
            },
            "supersedes_artifact_id": None,
            "applied_links": [],
        }
        self.chatbot_state.setdefault("artifacts", []).insert(0, artifact)
        return artifact

    def _select_chatbot_artifact(self, artifact_id):
        artifact = self._get_chatbot_artifact_by_id(artifact_id)
        if not artifact:
            return None
        view_state = self._get_chatbot_view_state()
        view_state["selected_artifact_id"] = artifact.get("artifact_id")
        if artifact.get("conversation_id"):
            view_state["active_conversation_id"] = artifact.get("conversation_id")
        self._sync_chatbot_compatibility_state()
        return artifact

    def _focus_chatbot_artifact(self, artifact_id, announce=False):
        artifact = self._select_chatbot_artifact(artifact_id)
        if not artifact:
            return None
        self._refresh_chatbot_output_preview()
        self._refresh_chatbot_history_list()
        if announce:
            self.update_status("Selected chatbot result for review.", "blue")
        return artifact

    def _handle_chatbot_artifact_card_click(self, artifact_id):
        self._focus_chatbot_artifact(artifact_id, announce=True)

    def _record_chatbot_artifact_apply(self, target_type, target_scope, apply_mode="append", artifact_id=None, summary=None):
        resolved_artifact_id = str(artifact_id or self._get_chatbot_view_state().get("selected_artifact_id") or "").strip()
        artifact = self._get_chatbot_artifact_by_id(resolved_artifact_id)
        if not artifact:
            return None

        apply_link = {
            "apply_id": self._generate_chatbot_state_id("apply"),
            "artifact_id": artifact.get("artifact_id"),
            "target_type": str(target_type or "").strip(),
            "target_scope": str(target_scope or "").strip(),
            "apply_mode": str(apply_mode or "append").strip(),
            "applied_at": self._chatbot_timestamp(),
            "summary": str(summary or "").strip(),
        }
        artifact.setdefault("applied_links", []).append(apply_link)
        artifact["status"] = "applied"
        artifact["updated_at"] = apply_link["applied_at"]
        self._sync_chatbot_compatibility_state()
        return apply_link

    def _serialize_chatbot_creative_state(self):
        self._capture_chatbot_view_state_from_widgets()
        payload = copy.deepcopy(self.chatbot_state if isinstance(self.chatbot_state, dict) else self._create_empty_chatbot_state())
        payload["schema_version"] = CHATBOT_CREATIVE_STATE_SCHEMA_VERSION
        return payload

    def _load_chatbot_creative_state(self, payload):
        normalized_state = self._create_empty_chatbot_state()
        if isinstance(payload, dict):
            normalized_state["schema_version"] = int(payload.get("schema_version") or CHATBOT_CREATIVE_STATE_SCHEMA_VERSION)

            for conversation in payload.get("conversations", []):
                if not isinstance(conversation, dict):
                    continue
                conversation_id = str(conversation.get("conversation_id") or self._generate_chatbot_state_id("conversation")).strip()
                turns = []
                for turn in conversation.get("turns", []):
                    if not isinstance(turn, dict):
                        continue
                    turns.append({
                        "turn_id": str(turn.get("turn_id") or self._generate_chatbot_state_id("turn")).strip(),
                        "role": str(turn.get("role") or "assistant").strip() or "assistant",
                        "kind": str(turn.get("kind") or "chat").strip() or "chat",
                        "content": str(turn.get("content") or "").strip(),
                        "created_at": str(turn.get("created_at") or self._chatbot_timestamp()).strip(),
                        "artifact_ids": [
                            str(artifact_id or "").strip()
                            for artifact_id in (turn.get("artifact_ids") or [])
                            if str(artifact_id or "").strip()
                        ],
                    })

                normalized_state["conversations"].append({
                    "conversation_id": conversation_id,
                    "created_at": str(conversation.get("created_at") or self._chatbot_timestamp()).strip(),
                    "updated_at": str(conversation.get("updated_at") or conversation.get("created_at") or self._chatbot_timestamp()).strip(),
                    "title": str(conversation.get("title") or "Creative Assistant").strip() or "Creative Assistant",
                    "status": str(conversation.get("status") or "active").strip() or "active",
                    "turns": turns,
                })

            for artifact in payload.get("artifacts", []):
                if not isinstance(artifact, dict):
                    continue
                structured_payload = artifact.get("structured_payload") if isinstance(artifact.get("structured_payload"), dict) else {}
                applied_links = []
                for apply_link in artifact.get("applied_links", []):
                    if not isinstance(apply_link, dict):
                        continue
                    applied_links.append({
                        "apply_id": str(apply_link.get("apply_id") or self._generate_chatbot_state_id("apply")).strip(),
                        "artifact_id": str(apply_link.get("artifact_id") or artifact.get("artifact_id") or "").strip(),
                        "target_type": str(apply_link.get("target_type") or "").strip(),
                        "target_scope": str(apply_link.get("target_scope") or "").strip(),
                        "apply_mode": str(apply_link.get("apply_mode") or "append").strip(),
                        "applied_at": str(apply_link.get("applied_at") or self._chatbot_timestamp()).strip(),
                        "summary": str(apply_link.get("summary") or "").strip(),
                    })

                normalized_state["artifacts"].append({
                    "artifact_id": str(artifact.get("artifact_id") or self._generate_chatbot_state_id("artifact")).strip(),
                    "conversation_id": str(artifact.get("conversation_id") or normalized_state["view"].get("active_conversation_id") or "").strip(),
                    "artifact_type": str(artifact.get("artifact_type") or self._infer_chatbot_artifact_type(artifact.get("task_label"))).strip(),
                    "status": str(artifact.get("status") or "generated").strip() or "generated",
                    "created_at": str(artifact.get("created_at") or self._chatbot_timestamp()).strip(),
                    "updated_at": str(artifact.get("updated_at") or artifact.get("created_at") or self._chatbot_timestamp()).strip(),
                    "task_label": str(artifact.get("task_label") or CHATBOT_TASK_T2I_OPTIMIZE).strip(),
                    "title": str(artifact.get("title") or structured_payload.get("title") or "Untitled result").strip() or "Untitled result",
                    "briefing": str(artifact.get("briefing") or "").strip(),
                    "source_prompt_summary": str(artifact.get("source_prompt_summary") or artifact.get("briefing") or "").strip(),
                    "structured_payload": structured_payload,
                    "display_payload": str(artifact.get("display_payload") or self._format_chatbot_result_for_display(structured_payload, show_raw=False)).strip(),
                    "generation_metadata": copy.deepcopy(artifact.get("generation_metadata") or {}),
                    "supersedes_artifact_id": str(artifact.get("supersedes_artifact_id") or "").strip() or None,
                    "applied_links": applied_links,
                })

            if isinstance(payload.get("view"), dict):
                normalized_state["view"].update({
                    "active_conversation_id": str(payload["view"].get("active_conversation_id") or "").strip() or None,
                    "selected_artifact_id": str(payload["view"].get("selected_artifact_id") or "").strip() or None,
                    "composer_draft": str(payload["view"].get("composer_draft") or "").strip(),
                    "selected_scene_id": str(payload["view"].get("selected_scene_id") or "").strip() or None,
                    "selected_scene_order": payload["view"].get("selected_scene_order"),
                })

        self.chatbot_state = normalized_state
        if not self._get_chatbot_conversation_by_id(self._get_chatbot_view_state().get("active_conversation_id")):
            self._ensure_active_chatbot_conversation()
        self._sync_chatbot_compatibility_state()

    def _reset_chatbot_creative_state(self, refresh_ui=False):
        self.chatbot_state = self._create_empty_chatbot_state()
        self.chatbot_last_result = None
        self.chatbot_result_history = []
        self.chatbot_output_show_raw = False
        self.chatbot_output_preview_cache = ""
        if hasattr(self, "chatbot_briefing_text"):
            self.chatbot_briefing_text.delete("1.0", tk.END)
        if refresh_ui:
            self._refresh_chatbot_history_list()
            self._refresh_chatbot_output_preview()
            self._refresh_chatbot_runtime_ui()

    def _format_chatbot_result_for_display(self, result, show_raw=False):
        if not isinstance(result, dict):
            return str(result or "")
        if show_raw:
            return json.dumps({key: value for key, value in result.items() if key != "raw_content"}, indent=2, ensure_ascii=False)

        task_label = str(result.get("task_label") or result.get("task") or "").strip()
        if task_label == CHATBOT_TASK_SCENE_PLAN or str(result.get("task") or "").strip() == "scene_plan":
            lines = []
            title_value = str(result.get("title") or "").strip()
            rationale = str(result.get("planning_rationale") or "").strip()
            model_id = str(result.get("model_id") or "").strip()
            scenes = result.get("scenes") if isinstance(result.get("scenes"), list) else []
            if task_label:
                lines.append(f"Task\n{task_label}")
            if title_value:
                lines.append(f"Title\n{title_value}")
            if rationale:
                lines.append(f"Planning Rationale\n{rationale}")
            if scenes:
                scene_lines = []
                for index, scene in enumerate(scenes, start=1):
                    if not isinstance(scene, dict):
                        continue
                    scene_number = int(scene.get("scene_number") or index)
                    scene_title = str(scene.get("title") or f"Scene {scene_number:02d}").strip()
                    scene_prompt = str(scene.get("prompt") or "").strip()
                    scene_notes = str(scene.get("notes") or "").strip()
                    scene_block = [f"Scene {scene_number:02d}: {scene_title}"]
                    if scene_prompt:
                        scene_block.append(scene_prompt)
                    if scene_notes:
                        scene_block.append(f"Notes: {scene_notes}")
                    scene_lines.append("\n".join(scene_block).strip())
                if scene_lines:
                    lines.append("Scene Drafts\n" + "\n\n".join(scene_lines))
            if model_id:
                lines.append(f"Model\n{model_id}")
            return "\n\n".join(lines).strip()

        if task_label == CHATBOT_TASK_SONG_BRAINSTORM or str(result.get("task") or "").strip() == "song_brainstorm":
            lines = []
            title_value = str(result.get("title") or "").strip()
            lyrics = str(result.get("lyrics") or "").strip()
            style_tags = str(result.get("style_tags") or "").strip()
            rationale = str(result.get("rationale") or "").strip()
            model_id = str(result.get("model_id") or "").strip()
            if task_label:
                lines.append(f"Task\n{task_label}")
            if title_value:
                lines.append(f"Title\n{title_value}")
            if style_tags:
                lines.append(f"Style Tags\n{style_tags}")
            if lyrics:
                lines.append(f"Lyrics\n{lyrics}")
            if rationale:
                lines.append(f"Creative Choices\n{rationale}")
            if model_id:
                lines.append(f"Model\n{model_id}")
            return "\n\n".join(lines).strip()

        lines = []
        title_value = str(result.get("title") or "").strip()
        optimized_prompt = str(result.get("optimized_prompt") or "").strip()
        negative_prompt = str(result.get("negative_prompt") or "").strip()
        rationale = str(result.get("rationale") or "").strip()
        model_id = str(result.get("model_id") or "").strip()

        if task_label:
            lines.append(f"Task\n{task_label}")
        if title_value:
            lines.append(f"Title\n{title_value}")
        if optimized_prompt:
            lines.append(f"Optimized Prompt\n{optimized_prompt}")
        if negative_prompt:
            lines.append(f"Negative Prompt\n{negative_prompt}")
        if rationale:
            lines.append(f"Why This Works\n{rationale}")
        if model_id:
            lines.append(f"Model\n{model_id}")
        return "\n\n".join(lines).strip()

    def _get_chatbot_artifact_destination_label(self, task_label=None):
        resolved_task = str(task_label or "").strip()
        if resolved_task == CHATBOT_TASK_SCENE_PLAN or resolved_task == "scene_plan":
            return "Apply target: Scene Timeline"
        if resolved_task == CHATBOT_TASK_SONG_BRAINSTORM or resolved_task == "song_brainstorm":
            return "Apply target: Music Tab (Lyrics & Style)"
        return "Apply target: Image Phase queue"

    def _build_chatbot_artifact_preview_text(self, artifact, show_raw=False, max_length=420):
        if not isinstance(artifact, dict):
            return ""
        structured_payload = artifact.get("structured_payload") if isinstance(artifact.get("structured_payload"), dict) else {}
        preview_text = self._format_chatbot_result_for_display(structured_payload, show_raw=show_raw)
        preview_text = str(preview_text or "").strip()
        if not preview_text:
            return ""
        if len(preview_text) <= max_length:
            return preview_text
        clipped_text = preview_text[: max_length - 1].rstrip()
        split_index = clipped_text.rfind(" ")
        if split_index > 120:
            clipped_text = clipped_text[:split_index].rstrip()
        return f"{clipped_text}..."

    def _refresh_chatbot_artifact_review_panel(self):
        if not hasattr(self, "chatbot_artifact_review_card"):
            return

        selected_artifact = self._get_selected_chatbot_artifact()
        if not selected_artifact:
            self.chatbot_artifact_review_card.pack_forget()
            return

        task_label = str(selected_artifact.get("task_label") or selected_artifact.get("artifact_type") or CHATBOT_TASK_T2I_OPTIMIZE).strip()
        artifact_status = str(selected_artifact.get("status") or "generated").strip().title()
        artifact_title = str(selected_artifact.get("title") or "Untitled result").strip() or "Untitled result"
        artifact_brief = str(selected_artifact.get("source_prompt_summary") or selected_artifact.get("briefing") or "").strip()
        apply_count = len(selected_artifact.get("applied_links") or [])
        applied_suffix = f" | Applied {apply_count} time(s)" if apply_count else ""
        preview_text = self._build_chatbot_artifact_preview_text(selected_artifact, show_raw=self.chatbot_output_show_raw) or "Select a result to review its structured output here."

        if not self.chatbot_artifact_review_card.winfo_manager():
            self.chatbot_artifact_review_card.pack(fill=tk.X, pady=(0, 10), before=self.chatbot_transcript_shell)

        self.chatbot_artifact_review_eyebrow_label.config(text="Selected Result")
        self.chatbot_artifact_review_title_label.config(text=artifact_title)
        self.chatbot_artifact_review_meta_label.config(text=f"{task_label} | {artifact_status}{applied_suffix}")
        self.chatbot_artifact_review_destination_label.config(text=self._get_chatbot_artifact_destination_label(task_label))
        if artifact_brief:
            self.chatbot_artifact_review_brief_label.config(text=f"From brief: {artifact_brief}")
        else:
            self.chatbot_artifact_review_brief_label.config(text="From brief: no saved briefing summary")
        self.chatbot_artifact_review_preview_label.config(text=preview_text)

    def _refresh_chatbot_output_preview(self):
        display_text = self.chatbot_output_preview_cache
        if self.chatbot_last_result:
            display_text = self._format_chatbot_result_for_display(self.chatbot_last_result, show_raw=self.chatbot_output_show_raw)
        self._refresh_chatbot_artifact_review_panel()
        self._refresh_chatbot_transcript()
        if hasattr(self, "chatbot_output_mode_btn"):
            self.chatbot_output_mode_btn.config(
                text="Show Guided View" if self.chatbot_output_show_raw else "Show Raw JSON",
                state=tk.NORMAL if self.chatbot_last_result else tk.DISABLED,
            )
        if hasattr(self, "chatbot_copy_output_btn"):
            self.chatbot_copy_output_btn.config(state=tk.NORMAL if display_text.strip() else tk.DISABLED)
        if hasattr(self, "chatbot_result_status_label"):
            selected_task = self._get_selected_chatbot_task()
            task_label = str((self.chatbot_last_result or {}).get("task_label") or (self.chatbot_last_result or {}).get("task") or "").strip()
            if self.chatbot_generation_in_progress:
                status_text = "The assistant is working. The latest visible reply or prompt draft will stay here until the next response arrives."
            elif task_label == CHATBOT_TASK_SCENE_PLAN or task_label == "scene_plan":
                status_text = "Scene plan ready. Review it, copy it, or apply it to the Scene Timeline."
            elif self.chatbot_last_result:
                status_text = "Prompt draft ready. Review it, copy it, or send it to the Image Phase queue."
            elif str(display_text or "").strip():
                status_text = "Latest assistant reply ready. Keep refining the direction, or switch modes when you want structured output."
            else:
                status_text = self._get_chatbot_idle_status_text(selected_task)
            self.chatbot_result_status_label.config(text=status_text)

    def _set_chatbot_backend_health_text(self, text):
        self.chatbot_backend_health_text = str(text or "Backend check: Not tested yet.")
        if hasattr(self, "chatbot_readiness_health_label"):
            self.chatbot_readiness_health_label.config(text=self.chatbot_backend_health_text)

    def _set_chatbot_output_preview(self, text):
        self.chatbot_output_preview_cache = str(text or "")
        if not self.chatbot_last_result:
            self._refresh_chatbot_output_preview()

    def _toggle_chatbot_output_view(self):
        self.chatbot_output_show_raw = not self.chatbot_output_show_raw
        self._refresh_chatbot_output_preview()

    def _copy_chatbot_output_to_clipboard(self):
        output_text = self._format_chatbot_result_for_display(self.chatbot_last_result, show_raw=self.chatbot_output_show_raw) if self.chatbot_last_result else self.chatbot_output_preview_cache
        output_text = str(output_text or "")
        if not output_text.strip():
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(output_text)
        self.update_status("Chatbot result copied to clipboard.", "green")

    def _copy_chatbot_message_to_clipboard(self, text):
        text = str(text or "").strip()
        if not text:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.update_status("Message copied to clipboard.", "green")

    def _record_chatbot_history_entry(self, task_name, briefing_text, result):
        conversation_id = self._ensure_active_chatbot_conversation()
        artifact = self._create_chatbot_artifact(task_name, briefing_text, result, conversation_id=conversation_id)
        self._append_chatbot_turn(
            "assistant",
            str(artifact.get("title") or "Generated result").strip(),
            kind="artifact-reference",
            related_artifact_ids=[artifact.get("artifact_id")],
            conversation_id=conversation_id,
        )
        self._select_chatbot_artifact(artifact.get("artifact_id"))
        self._refresh_chatbot_history_list()

    def _refresh_chatbot_history_list(self):
        if not hasattr(self, "chatbot_history_frame"):
            return

        for child in self.chatbot_history_frame.winfo_children():
            child.destroy()

        selected_artifact = self._get_selected_chatbot_artifact()
        for entry in self.chatbot_result_history:
            artifact_id = str(entry.get("artifact_id") or "").strip()
            title_value = str((entry.get("result") or {}).get("title") or "Untitled result").strip()
            task_label = str(entry.get("task_label") or CHATBOT_TASK_T2I_OPTIMIZE).strip()
            created_at = str(entry.get("created_at") or "").strip()
            apply_count = int(entry.get("apply_count") or 0)
            status_label = "Applied" if apply_count > 0 else str(entry.get("status") or "generated").strip().title()
            briefing_text = str(entry.get("briefing") or "").strip()
            is_selected = bool(
                selected_artifact
                and str(selected_artifact.get("artifact_id") or "").strip() == artifact_id
            )

            result_card = tk.Frame(self.chatbot_history_frame, padx=12, pady=10)
            result_card.pack(fill=tk.X, pady=(0, 8))
            self._style_panel(result_card, self.colors["surface_soft"] if is_selected else self.colors["surface"], border=True)
            result_card.configure(cursor="hand2")
            if is_selected:
                result_card.configure(highlightbackground=self.colors["accent"], highlightthickness=2)

            top_row = tk.Frame(result_card)
            top_row.pack(fill=tk.X)
            self._style_panel(top_row, result_card.cget("bg"))

            title_label = tk.Label(top_row, text=title_value or "Untitled result", anchor="w")
            title_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self._style_label(title_label, "body_strong", top_row.cget("bg"))

            time_label = tk.Label(top_row, text=created_at, anchor="e")
            time_label.pack(side=tk.RIGHT)
            self._style_label(time_label, "muted", top_row.cget("bg"))

            meta_label = tk.Label(
                result_card,
                text=f"{task_label} | {status_label}{f' | Applied {apply_count}x' if apply_count > 0 else ''}",
                anchor="w",
                justify=tk.LEFT,
                wraplength=820,
            )
            meta_label.pack(anchor="w", fill=tk.X, pady=(4, 0))
            self._style_label(meta_label, "muted", result_card.cget("bg"))

            if briefing_text:
                summary_label = tk.Label(
                    result_card,
                    text=briefing_text,
                    anchor="w",
                    justify=tk.LEFT,
                    wraplength=820,
                )
                summary_label.pack(anchor="w", fill=tk.X, pady=(8, 0))
                self._style_label(summary_label, "body", result_card.cget("bg"))
                summary_widgets = [summary_label]
            else:
                summary_widgets = []

            clickable_widgets = [result_card, top_row, title_label, time_label, meta_label] + summary_widgets
            for clickable_widget in clickable_widgets:
                clickable_widget.configure(cursor="hand2")
                clickable_widget.bind(
                    "<Button-1>",
                    lambda _event, selected_artifact_id=artifact_id: self._focus_chatbot_artifact(selected_artifact_id, announce=True)
                )

        self.chatbot_history_frame.update_idletasks()
        self.chatbot_history_canvas.configure(scrollregion=self.chatbot_history_canvas.bbox("all"))
        if "chatbot_history" in self.collapsible_sections:
            history_count = len(self.chatbot_result_history)
            self._update_collapsible_section_meta("chatbot_history", f"{history_count} saved results" if history_count else "No saved results")

    def _set_chatbot_generation_state(self, is_running):
        self.chatbot_generation_in_progress = bool(is_running)
        pending_mode = str(self.chatbot_pending_request_mode or "").strip()
        if hasattr(self, "chatbot_send_btn"):
            self.chatbot_send_btn.config(
                state=tk.DISABLED if is_running or not self._chatbot_generation_prerequisites_ready() else tk.NORMAL,
                text="Replying..." if is_running and pending_mode == "chat" else "Send",
            )
        if hasattr(self, "chatbot_scene_plan_btn"):
            self.chatbot_scene_plan_btn.config(
                state=tk.DISABLED if is_running or not self._chatbot_generation_prerequisites_ready() else tk.NORMAL,
                text="Planning Scenes..." if is_running and pending_mode == "artifact" else "Plan Scenes",
            )
        if hasattr(self, "chatbot_generate_btn"):
            self.chatbot_generate_btn.config(
                state=tk.DISABLED if is_running or not self._chatbot_generation_prerequisites_ready() else tk.NORMAL,
                text="Generating Prompt..." if is_running and pending_mode == "artifact" else "Generate Prompt Draft",
            )
        if hasattr(self, "chatbot_finalize_song_btn"):
            self.chatbot_finalize_song_btn.config(
                state=tk.DISABLED if is_running or not self._chatbot_generation_prerequisites_ready() else tk.NORMAL,
                text="Finalizing Song..." if is_running and pending_mode == "artifact" else "Finalize Song",
            )
        if hasattr(self, "chatbot_apply_btn"):
            task_label = str((self.chatbot_last_result or {}).get("task_label") or (self.chatbot_last_result or {}).get("task") or "").strip()
            can_apply = bool(
                not is_running
                and self.chatbot_last_result
                and (
                    (
                        task_label == CHATBOT_TASK_T2I_OPTIMIZE
                        and str(self.chatbot_last_result.get("optimized_prompt") or "").strip()
                    )
                    or (
                        (task_label == CHATBOT_TASK_SCENE_PLAN or task_label == "scene_plan")
                        and isinstance(self.chatbot_last_result.get("scenes"), list)
                        and any(str((scene or {}).get("video_prompt") or (scene or {}).get("image_prompt") or (scene or {}).get("prompt") or "").strip() for scene in self.chatbot_last_result.get("scenes") or [])
                    )
                )
            )
            self.chatbot_apply_btn.config(state=tk.NORMAL if can_apply else tk.DISABLED)
            self.chatbot_apply_btn.config(
                text="Apply Plan to Scene Timeline"
                if task_label == CHATBOT_TASK_SCENE_PLAN or task_label == "scene_plan"
                else "Add Prompt to Image Queue"
            )
        if hasattr(self, "chatbot_apply_scene_btn"):
            is_scene_plan = task_label == CHATBOT_TASK_SCENE_PLAN or task_label == "scene_plan"
            if is_scene_plan:
                self.chatbot_apply_scene_btn.pack_forget()
            else:
                self.chatbot_apply_scene_btn.config(state=tk.NORMAL if can_apply else tk.DISABLED)
                self.chatbot_apply_scene_btn.pack(side=tk.LEFT, padx=(10, 0))
        if hasattr(self, "chatbot_apply_music_btn"):
            is_song = task_label == CHATBOT_TASK_SONG_BRAINSTORM or task_label == "song_brainstorm"
            can_apply_music = bool(
                not is_running
                and self.chatbot_last_result
                and is_song
                and (str(self.chatbot_last_result.get("lyrics") or "").strip() or str(self.chatbot_last_result.get("style_tags") or "").strip())
            )
            self.chatbot_apply_music_btn.config(state=tk.NORMAL if can_apply_music else tk.DISABLED)
        if hasattr(self, "chatbot_task_combo"):
            self.chatbot_task_combo.config(state=tk.DISABLED if is_running else "readonly")
        if hasattr(self, "chatbot_new_chat_btn"):
            self.chatbot_new_chat_btn.config(state=tk.DISABLED if is_running else tk.NORMAL)
        if hasattr(self, "chatbot_clear_chat_btn"):
            self.chatbot_clear_chat_btn.config(state=tk.DISABLED if is_running else tk.NORMAL)
        if hasattr(self, "chatbot_briefing_text"):
            self.chatbot_briefing_text.config(state=tk.DISABLED if is_running else tk.NORMAL)
        if "chatbot_focus_workspace" in self.collapsible_sections:
            self._update_collapsible_section_meta("chatbot_focus_workspace", self._get_chatbot_focus_section_meta())
        self._refresh_chatbot_output_preview()

    def _extract_json_object_from_text(self, raw_text):
        cleaned_text = str(raw_text or "").strip()
        if not cleaned_text:
            raise ValueError("The chatbot response was empty.")

        if cleaned_text.startswith("```"):
            cleaned_text = re.sub(r"^```(?:json)?\s*", "", cleaned_text, flags=re.IGNORECASE)
            cleaned_text = re.sub(r"\s*```$", "", cleaned_text).strip()

        try:
            parsed = json.loads(cleaned_text)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

        start_index = cleaned_text.find("{")
        end_index = cleaned_text.rfind("}")
        if start_index == -1 or end_index == -1 or end_index <= start_index:
            raise ValueError("The chatbot response did not contain a valid JSON object.")

        candidate = cleaned_text[start_index:end_index + 1]
        try:
            parsed = json.loads(candidate)
            if not isinstance(parsed, dict):
                raise ValueError("The chatbot response JSON must be an object.")
            return parsed
        except json.JSONDecodeError:
            pass

        truncated = cleaned_text[start_index:]
        repaired = self._attempt_json_repair(truncated)
        parsed = json.loads(repaired)
        if not isinstance(parsed, dict):
            raise ValueError("The chatbot response JSON must be an object.")
        return parsed

    @staticmethod
    def _attempt_json_repair(text):
        """Try to close a truncated JSON object so it can be parsed."""
        in_string = False
        escape_next = False
        brace_depth = 0
        bracket_depth = 0
        last_good = 0
        for i, ch in enumerate(text):
            if escape_next:
                escape_next = False
                continue
            if ch == '\\':
                if in_string:
                    escape_next = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == '{':
                brace_depth += 1
            elif ch == '}':
                brace_depth -= 1
            elif ch == '[':
                bracket_depth += 1
            elif ch == ']':
                bracket_depth -= 1
            if brace_depth == 0 and bracket_depth == 0:
                last_good = i
                break
            last_good = i
        repaired = text[:last_good + 1]
        if in_string:
            repaired += '"'
        while bracket_depth > 0:
            repaired += ']'
            bracket_depth -= 1
        while brace_depth > 0:
            repaired += '}'
            brace_depth -= 1
        return repaired

    def _get_chatbot_task_config(self, task_name):
        task_label = str(task_name or CHATBOT_TASK_T2I_OPTIMIZE).strip() or CHATBOT_TASK_T2I_OPTIMIZE

        if task_label == CHATBOT_TASK_CONCEPT_EXPAND:
            schema_hint = {
                "task": "concept_expand",
                "title": "Short creative title for the music video",
                "mood": "Primary emotional tone and atmosphere",
                "color_palette": "3-5 dominant colors/tones that define the visual feel",
                "visual_style": "Art direction / aesthetic reference",
                "narrative_arc": "Brief story arc: opening -> development -> climax -> resolution",
                "genre_direction": "Musical genre and sub-genre",
                "tempo_energy": "BPM range and energy curve",
                "visual_motifs": "2-4 recurring visual elements that tie scenes together",
                "camera_style": "Dominant camera language",
                "expanded_brief": "Rich 2-3 sentence paragraph synthesizing all the above into a cohesive vision"
            }
            json_schema = {
                "name": "prompt2mtv_concept_expand",
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "task": {"type": "string", "const": "concept_expand"},
                        "title": {"type": "string"},
                        "mood": {"type": "string"},
                        "color_palette": {"type": "string"},
                        "visual_style": {"type": "string"},
                        "narrative_arc": {"type": "string"},
                        "genre_direction": {"type": "string"},
                        "tempo_energy": {"type": "string"},
                        "visual_motifs": {"type": "string"},
                        "camera_style": {"type": "string"},
                        "expanded_brief": {"type": "string"}
                    },
                    "required": ["task", "title", "mood", "color_palette", "visual_style",
                                 "narrative_arc", "genre_direction", "tempo_energy",
                                 "visual_motifs", "camera_style", "expanded_brief"]
                }
            }
            user_prompt_template = (
                "Task: expand a brief music video idea into a rich creative concept.\n"
                "The user's raw idea:\n__BRIEFING_TEXT__\n\n"
                "Produce exactly this JSON schema:\n"
                f"{json.dumps(schema_hint, indent=2)}\n\n"
                "Requirements:\n"
                "- Transform even a vague idea into a specific, producible vision.\n"
                "- The expanded_brief must synthesize all fields into a cohesive 2-3 sentence paragraph.\n"
                "- color_palette should name specific colors (e.g. 'deep indigo, electric cyan, warm amber').\n"
                "- visual_motifs should be concrete recurring elements (e.g. 'floating jellyfish, cracking glass, neon rain').\n"
                "- camera_style should use real cinematography terms (dolly, tracking, whip pan, crane, handheld).\n"
                "- genre_direction and tempo_energy should be specific enough to guide song creation.\n"
                "- If the idea is vague, make bold creative choices — do not hedge or stay generic.\n"
                "- Avoid markdown, avoid prose outside JSON.\n"
            )
            return {
                "label": CHATBOT_TASK_CONCEPT_EXPAND,
                "output_task": "concept_expand",
                "required_fields": ["task", "title", "mood", "color_palette", "visual_style",
                                    "narrative_arc", "genre_direction", "tempo_energy",
                                    "visual_motifs", "camera_style", "expanded_brief"],
                "non_empty_fields": ["task", "title", "mood", "color_palette", "visual_style",
                                     "narrative_arc", "genre_direction", "expanded_brief"],
                "json_schema": json_schema,
                "system_prompt": (
                    "You are a music video creative director with a strong visual imagination. "
                    "Your job is to take a brief idea — even a single phrase — and expand it into a rich, specific creative concept "
                    "that will guide scene planning, image generation, and songwriting. "
                    "Be bold and specific. Never return vague or generic descriptions. "
                    "Return only a JSON object with no markdown fences, no prose outside JSON, and no extra keys."
                ),
                "user_prompt_template": user_prompt_template,
            }

        if task_label == CHATBOT_TASK_SCENE_PLAN:
            schema_hint = {
                "task": "scene_plan",
                "title": "Short title for the scene plan",
                "planning_rationale": "Why this scene count and progression fit the concept",
                "scenes": [
                    {
                        "scene_number": 1,
                        "title": "Short scene title",
                        "image_prompt": "Detailed text-to-image prompt for generating a still frame",
                        "video_prompt": "Motion description for animating the still image into video",
                        "notes": "Optional story beat, pacing, or transition note"
                    }
                ]
            }
            json_schema = {
                "name": "prompt2mtv_scene_plan",
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "task": {"type": "string", "const": "scene_plan"},
                        "title": {"type": "string"},
                        "planning_rationale": {"type": "string"},
                        "scenes": {
                            "type": "array",
                            "minItems": 1,
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "scene_number": {"type": "integer"},
                                    "title": {"type": "string"},
                                    "image_prompt": {"type": "string"},
                                    "video_prompt": {"type": "string"},
                                    "notes": {"type": "string"}
                                },
                                "required": ["scene_number", "title", "image_prompt", "video_prompt", "notes"]
                            }
                        }
                    },
                    "required": ["task", "title", "planning_rationale", "scenes"]
                }
            }
            user_prompt_template = (
                "Task: plan scenes for a music video. Each scene will be produced in two steps:\n"
                "1. A still image is generated from the image_prompt (using text-to-image)\n"
                "2. The still image is animated using the video_prompt (using image-to-video)\n\n"
                "Creative concept:\n__BRIEFING_TEXT__\n\n"
                "Produce exactly this JSON schema:\n"
                f"{json.dumps(schema_hint, indent=2)}\n\n"
                "IMAGE PROMPT GUIDELINES (for text-to-image generation):\n"
                "- Describe a single, striking still frame — think of it as a photograph or painting.\n"
                "- Include: subject, composition, lighting, color palette, medium/style, atmosphere.\n"
                "- Be visually specific: 'a lone astronaut on a crimson dune under a violet sky with two moons' not 'a space scene'.\n"
                "- Example: 'Close-up portrait of a woman with electric blue tears, neon pink backlighting, shallow depth of field, cyberpunk aesthetic, rain on glass in foreground'\n"
                "- Example: 'Wide aerial shot of a bioluminescent forest at night, turquoise and magenta mushrooms glowing, mist between ancient trees, cinematic color grading'\n\n"
                "VIDEO PROMPT GUIDELINES (for image-to-video animation):\n"
                "- Describe how the still image comes alive — what moves and how the camera behaves.\n"
                "- Focus on: camera movement (dolly in, slow pan, crane up, tracking shot), subject motion, atmospheric effects.\n"
                "- Each scene is ~5 seconds. Keep motion achievable for that duration.\n"
                "- Example: 'Slow dolly in toward the astronaut as sand particles drift upward in low gravity, subtle camera shake, sky shifts from violet to crimson'\n"
                "- Example: 'Gentle crane shot rising through the canopy, mushrooms pulse with light in a breathing rhythm, firefly particles drift across frame'\n\n"
                "SCENE PLANNING RULES:\n"
                "- Choose a scene count that fits the concept (typically 3-8 for a music video).\n"
                "- Maintain a narrative arc: establish the world -> build tension -> peak moment -> resolution.\n"
                "- Vary shot types: mix wide/medium/close-up, vary camera movements.\n"
                "- Each scene must be visually distinct but thematically connected.\n"
                "- notes should mention pacing, lyric alignment, or transition style.\n"
                "- If you reason internally, do not expose reasoning in the visible answer.\n"
                "- Avoid markdown and avoid prose outside JSON.\n"
            )
            return {
                "label": CHATBOT_TASK_SCENE_PLAN,
                "output_task": "scene_plan",
                "required_fields": ["task", "title", "planning_rationale", "scenes"],
                "non_empty_fields": ["task", "title", "planning_rationale"],
                "json_schema": json_schema,
                "system_prompt": (
                    "You are an expert music video director and cinematographer. "
                    "You plan scenes with two prompts each: an image_prompt for generating a still frame "
                    "(composition, lighting, color, subject) and a video_prompt for animating that frame "
                    "(camera movement, subject motion, atmospheric effects). "
                    "Your image prompts are visually rich art direction briefs. "
                    "Your video prompts are focused camera direction notes about motion and timing. "
                    "Return only a JSON object with no markdown fences, no prose outside JSON, and no extra keys."
                ),
                "user_prompt_template": user_prompt_template,
            }

        if task_label == CHATBOT_TASK_SONG_BRAINSTORM:
            schema_hint = {
                "task": "song_brainstorm",
                "title": "Short title for the song",
                "lyrics": "Full song lyrics with [verse], [chorus], [bridge], [outro] section markers",
                "style_tags": "Comma-separated ACE-Step descriptors: genre, mood, instrumentation, texture, vocal style, BPM",
                "rationale": "Brief explanation of creative choices and how lyrics connect to the visuals"
            }
            json_schema = {
                "name": "prompt2mtv_song_brainstorm",
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "task": {"type": "string", "const": "song_brainstorm"},
                        "title": {"type": "string"},
                        "lyrics": {"type": "string"},
                        "style_tags": {"type": "string"},
                        "rationale": {"type": "string"}
                    },
                    "required": ["task", "title", "lyrics", "style_tags", "rationale"]
                }
            }
            user_prompt_template = (
                "Task: write original song lyrics and style tags for a music video.\n\n"
                "Creative concept:\n__BRIEFING_TEXT__\n\n"
                "Produce exactly this JSON schema:\n"
                f"{json.dumps(schema_hint, indent=2)}\n\n"
                "LYRICS GUIDELINES:\n"
                "- Write complete lyrics with section markers: [intro], [verse], [chorus], [bridge], [outro].\n"
                "- Lyrics should complement the visual narrative — reference imagery, emotions, and themes from the concept.\n"
                "- Use vivid, evocative language. Avoid cliches.\n"
                "- Structure: verses tell the story, choruses deliver the hook, bridges provide contrast.\n\n"
                "STYLE TAGS GUIDELINES (for ACE-Step music generation):\n"
                "- Provide a comma-separated list covering: genre, sub-genre, mood, instrumentation, texture, vocal style, tempo.\n"
                "- Be specific and layered. Examples of good style tags:\n"
                "  'ethereal synth-pop, reverb-heavy female vocals, pulsing bass, ambient pads, 95 BPM, dreamy'\n"
                "  'dark trap, distorted 808s, whispering male vocals, haunting bells, lo-fi texture, 140 BPM'\n"
                "  'cinematic orchestral rock, soaring strings, driving drums, powerful choir, epic crescendo, 120 BPM'\n"
                "  'lo-fi chillhop, vinyl crackle, mellow piano, soft Rhodes, jazzy chords, 80 BPM, nostalgic'\n"
                "- Always include a BPM estimate.\n\n"
                "Requirements:\n"
                "- Make bold creative choices — write a complete, original song.\n"
                "- If you reason internally, do not expose reasoning in the visible answer.\n"
                "- Avoid markdown and avoid prose outside JSON.\n"
            )
            return {
                "label": CHATBOT_TASK_SONG_BRAINSTORM,
                "output_task": "song_brainstorm",
                "required_fields": ["task", "title", "lyrics", "style_tags", "rationale"],
                "non_empty_fields": ["task", "title", "lyrics", "style_tags"],
                "json_schema": json_schema,
                "system_prompt": (
                    "You are a talented songwriter creating original music for a music video. "
                    "You write lyrics that complement visual storytelling — vivid, emotional, and rhythmically strong. "
                    "You craft precise ACE-Step style tags covering genre, mood, instrumentation, texture, and tempo. "
                    "Return only a JSON object with no markdown fences, no prose outside JSON, and no extra keys."
                ),
                "user_prompt_template": user_prompt_template,
            }

        if task_label == CHATBOT_TASK_SCENE_OUTLINE:
            schema_hint = {
                "task": "scene_outline",
                "title": "Short title for the music video",
                "planning_rationale": "Why this progression fits the concept",
                "scenes": [
                    {
                        "scene_number": 1,
                        "title": "Short scene title",
                        "shot_type": "wide / medium / close-up / aerial / POV",
                        "mood": "Dominant mood or emotion",
                        "visual_hook": "One-sentence visual centerpiece",
                        "notes": "Pacing, transition, or lyric-alignment note"
                    }
                ]
            }
            json_schema = {
                "name": "prompt2mtv_scene_outline",
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "task": {"type": "string", "const": "scene_outline"},
                        "title": {"type": "string"},
                        "planning_rationale": {"type": "string"},
                        "scenes": {
                            "type": "array",
                            "minItems": 1,
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "scene_number": {"type": "integer"},
                                    "title": {"type": "string"},
                                    "shot_type": {"type": "string"},
                                    "mood": {"type": "string"},
                                    "visual_hook": {"type": "string"},
                                    "notes": {"type": "string"}
                                },
                                "required": ["scene_number", "title", "shot_type", "mood", "visual_hook", "notes"]
                            }
                        }
                    },
                    "required": ["task", "title", "planning_rationale", "scenes"]
                }
            }
            user_prompt_template = (
                "Task: plan a lightweight scene outline for a music video.\n"
                "Do NOT write detailed image or video prompts — only a brief outline per scene.\n\n"
                "Creative concept:\n__BRIEFING_TEXT__\n\n"
                "Produce exactly this JSON schema:\n"
                f"{json.dumps(schema_hint, indent=2)}\n\n"
                "SCENE OUTLINE RULES:\n"
                "- Each scene entry must be SHORT: title (3-6 words), shot_type, mood (1-3 words), "
                "visual_hook (one vivid sentence), and notes (one sentence).\n"
                "- Maintain a narrative arc: establish the world -> build tension -> peak moment -> resolution.\n"
                "- Vary shot types: mix wide/medium/close-up, vary camera movements.\n"
                "- Each scene must be visually distinct but thematically connected.\n"
                "- notes should mention pacing, lyric alignment, or transition style.\n"
                "- If you reason internally, do not expose reasoning in the visible answer.\n"
                "- Avoid markdown and avoid prose outside JSON.\n"
            )
            return {
                "label": CHATBOT_TASK_SCENE_OUTLINE,
                "output_task": "scene_outline",
                "required_fields": ["task", "title", "planning_rationale", "scenes"],
                "non_empty_fields": ["task", "title", "planning_rationale"],
                "max_tokens": 4096,
                "json_schema": json_schema,
                "system_prompt": (
                    "You are an expert music video director. "
                    "You plan concise scene outlines — short titles, shot types, moods, and one visual hook per scene. "
                    "Do NOT write full image prompts or motion descriptions yet. Keep each scene entry brief. "
                    "Return only a JSON object with no markdown fences, no prose outside JSON, and no extra keys."
                ),
                "user_prompt_template": user_prompt_template,
            }

        if task_label == CHATBOT_TASK_JIT_IMAGE_PROMPT:
            schema_hint = {
                "task": "jit_image_prompt",
                "image_prompt": "Detailed text-to-image prompt for generating a still frame",
                "negative_prompt": "Optional negative prompt, can be empty"
            }
            json_schema = {
                "name": "prompt2mtv_jit_image_prompt",
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "task": {"type": "string", "const": "jit_image_prompt"},
                        "image_prompt": {"type": "string"},
                        "negative_prompt": {"type": "string"}
                    },
                    "required": ["task", "image_prompt", "negative_prompt"]
                }
            }
            user_prompt_template = (
                "Task: write a detailed text-to-image prompt for ONE scene in a music video.\n\n"
                "__BRIEFING_TEXT__\n\n"
                "Produce exactly this JSON schema:\n"
                f"{json.dumps(schema_hint, indent=2)}\n\n"
                "IMAGE PROMPT GUIDELINES:\n"
                "- Describe a single, striking still frame — think of it as a photograph or painting.\n"
                "- Include: subject, composition, lighting, color palette, medium/style, atmosphere.\n"
                "- Be visually specific: 'a lone astronaut on a crimson dune under a violet sky with two moons' "
                "not 'a space scene'.\n"
                "- The prompt should be 2-4 sentences of vivid visual direction.\n"
                "- If you reason internally, do not expose reasoning in the visible answer.\n"
                "- Avoid markdown and avoid prose outside JSON.\n"
            )
            return {
                "label": CHATBOT_TASK_JIT_IMAGE_PROMPT,
                "output_task": "jit_image_prompt",
                "required_fields": ["task", "image_prompt", "negative_prompt"],
                "non_empty_fields": ["task", "image_prompt"],
                "max_tokens": 1024,
                "json_schema": json_schema,
                "system_prompt": (
                    "You are a cinematographer writing a text-to-image prompt for one scene of a music video. "
                    "Write a visually rich, specific prompt describing composition, lighting, color, subject, and mood. "
                    "Return only a JSON object with no markdown fences, no prose outside JSON, and no extra keys."
                ),
                "user_prompt_template": user_prompt_template,
            }

        if task_label == CHATBOT_TASK_JIT_VIDEO_PROMPT:
            schema_hint = {
                "task": "jit_video_prompt",
                "video_prompt": "Motion description for animating the still image into video"
            }
            json_schema = {
                "name": "prompt2mtv_jit_video_prompt",
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "task": {"type": "string", "const": "jit_video_prompt"},
                        "video_prompt": {"type": "string"}
                    },
                    "required": ["task", "video_prompt"]
                }
            }
            user_prompt_template = (
                "Task: write a motion description for animating a still image into a ~5 second video clip.\n\n"
                "__BRIEFING_TEXT__\n\n"
                "Produce exactly this JSON schema:\n"
                f"{json.dumps(schema_hint, indent=2)}\n\n"
                "VIDEO PROMPT GUIDELINES:\n"
                "- Describe how the still image comes alive — what moves and how the camera behaves.\n"
                "- Focus on: camera movement (dolly in, slow pan, crane up, tracking shot), "
                "subject motion, atmospheric effects.\n"
                "- The scene is ~5 seconds. Keep motion achievable for that duration.\n"
                "- 1-3 sentences of focused camera direction.\n"
                "- If you reason internally, do not expose reasoning in the visible answer.\n"
                "- Avoid markdown and avoid prose outside JSON.\n"
            )
            return {
                "label": CHATBOT_TASK_JIT_VIDEO_PROMPT,
                "output_task": "jit_video_prompt",
                "required_fields": ["task", "video_prompt"],
                "non_empty_fields": ["task", "video_prompt"],
                "max_tokens": 512,
                "json_schema": json_schema,
                "system_prompt": (
                    "You are a camera director writing motion instructions for animating a still image into video. "
                    "Focus on camera movement, subject motion, and atmospheric effects. "
                    "Return only a JSON object with no markdown fences, no prose outside JSON, and no extra keys."
                ),
                "user_prompt_template": user_prompt_template,
            }

        if task_label != CHATBOT_TASK_T2I_OPTIMIZE:
            raise ValueError(f"Unsupported chatbot task: {task_label}")

        schema_hint = {
            "task": "t2i_prompt_optimize",
            "title": "Short title for the concept",
            "optimized_prompt": "Single polished text-to-image prompt",
            "negative_prompt": "Optional negative prompt string, can be empty",
            "rationale": "Short explanation of what was improved"
        }
        json_schema = {
            "name": "prompt2mtv_t2i_prompt_optimize",
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "task": {"type": "string", "const": "t2i_prompt_optimize"},
                    "title": {"type": "string"},
                    "optimized_prompt": {"type": "string"},
                    "negative_prompt": {"type": "string"},
                    "rationale": {"type": "string"}
                },
                "required": ["task", "title", "optimized_prompt", "negative_prompt", "rationale"]
            }
        }
        user_prompt_template = (
            "Task: optimize a text-to-image prompt for Prompt2MTV.\n"
            "Use the user's briefing and produce exactly this JSON schema:\n"
            f"{json.dumps(schema_hint, indent=2)}\n\n"
            "Requirements:\n"
            "- Keep the result visually specific and cinematic.\n"
            "- Avoid safety disclaimers and avoid markdown.\n"
            "- optimized_prompt must be concise but detailed enough to use directly.\n"
            "- negative_prompt may be empty if not needed.\n\n"
            "- If you reason internally, do not expose reasoning in the visible answer.\n\n"
            "User briefing:\n__BRIEFING_TEXT__"
        )
        return {
            "label": CHATBOT_TASK_T2I_OPTIMIZE,
            "output_task": "t2i_prompt_optimize",
            "required_fields": ["task", "title", "optimized_prompt", "negative_prompt", "rationale"],
            "non_empty_fields": ["task", "title", "optimized_prompt", "rationale"],
            "json_schema": json_schema,
            "system_prompt": (
                "You are a prompt engineering assistant for high-quality text-to-image generation. "
                "Return only a JSON object with no markdown fences, no prose outside JSON, and no extra keys. "
                "The optimized_prompt must be one production-ready prompt string suitable for direct use in an image model."
            ),
            "user_prompt_template": user_prompt_template,
        }

    def _validate_chatbot_structured_output(self, task_config, parsed_output):
        if not isinstance(parsed_output, dict):
            raise ValueError("The chatbot response JSON must be an object.")

        if str(task_config.get("output_task") or "").strip() in ("scene_plan", "scene_outline"):
            is_outline = str(task_config.get("output_task") or "").strip() == "scene_outline"
            expected_task_name = "scene_outline" if is_outline else "scene_plan"
            validated_output = {}
            for field_name in task_config.get("required_fields", []):
                if field_name not in parsed_output:
                    raise ValueError(f"The chatbot response is missing required field '{field_name}'.")
            validated_output["task"] = str(parsed_output.get("task") or "").strip()
            validated_output["title"] = str(parsed_output.get("title") or "").strip()
            validated_output["planning_rationale"] = str(parsed_output.get("planning_rationale") or "").strip()
            if validated_output["task"] != expected_task_name:
                validated_output["task"] = expected_task_name
            if not validated_output["title"] or not validated_output["planning_rationale"]:
                raise ValueError("Scene plan title and planning rationale must not be empty.")

            scenes = parsed_output.get("scenes")
            if not isinstance(scenes, list) or not scenes:
                raise ValueError("The chatbot response must include at least one planned scene.")

            validated_scenes = []
            for index, scene in enumerate(scenes, start=1):
                if not isinstance(scene, dict):
                    raise ValueError("Each planned scene must be an object.")
                try:
                    scene_number = int(scene.get("scene_number") or index)
                except (TypeError, ValueError):
                    raise ValueError("Each planned scene needs a numeric scene_number.")
                scene_title = str(scene.get("title") or "").strip()
                if not scene_title:
                    raise ValueError("Each planned scene needs a non-empty title.")

                if is_outline:
                    shot_type = str(scene.get("shot_type") or "").strip()
                    mood = str(scene.get("mood") or "").strip()
                    visual_hook = str(scene.get("visual_hook") or "").strip()
                    scene_notes = str(scene.get("notes") or "").strip()
                    if not visual_hook:
                        raise ValueError("Each outlined scene needs a non-empty visual_hook.")
                    validated_scenes.append(
                        {
                            "scene_number": scene_number,
                            "title": scene_title,
                            "shot_type": shot_type,
                            "mood": mood,
                            "visual_hook": visual_hook,
                            "notes": scene_notes,
                        }
                    )
                else:
                    scene_image_prompt = str(scene.get("image_prompt") or "").strip()
                    scene_video_prompt = str(scene.get("video_prompt") or "").strip()
                    scene_notes = str(scene.get("notes") or "").strip()
                    if not scene_image_prompt or not scene_video_prompt:
                        raise ValueError("Each planned scene needs a non-empty image_prompt and video_prompt.")
                    validated_scenes.append(
                        {
                            "scene_number": scene_number,
                            "title": scene_title,
                            "image_prompt": scene_image_prompt,
                            "video_prompt": scene_video_prompt,
                            "notes": scene_notes,
                        }
                    )

            validated_output["scenes"] = validated_scenes
            return validated_output

        validated_output = {}
        for field_name in task_config.get("required_fields", []):
            if field_name not in parsed_output:
                raise ValueError(f"The chatbot response is missing required field '{field_name}'.")
            field_value = parsed_output.get(field_name)
            if isinstance(field_value, (dict, list)):
                raise ValueError(f"Field '{field_name}' must be a string value.")
            validated_output[field_name] = str(field_value if field_value is not None else "").strip()

        expected_task = str(task_config.get("output_task") or "").strip()
        if expected_task and validated_output.get("task") != expected_task:
            raise ValueError(f"The chatbot response reported task '{validated_output.get('task')}', expected '{expected_task}'.")

        for field_name in task_config.get("non_empty_fields", []):
            if not validated_output.get(field_name):
                raise ValueError(f"Field '{field_name}' must not be empty.")

        return validated_output

    def _chatbot_chat_completions_url(self):
        return f"{self._chatbot_base_url()}/v1/chat/completions"

    def _post_chatbot_completion_payload(self, payload, timeout_seconds):
        response_payload, _status_code = self._chatbot_http_json(
            self._chatbot_chat_completions_url(),
            method="POST",
            payload=payload,
            timeout_seconds=timeout_seconds,
        )
        return response_payload

    def _build_chatbot_completion_payload_variants(self, task_config, briefing_text, model_id, keep_alive=None):
        force_non_thinking = self._chatbot_should_force_non_thinking(model_id=model_id)
        base_payload = {
            "model": model_id,
            "messages": self._build_chatbot_request_messages(
                [
                    {"role": "system", "content": task_config["system_prompt"]},
                    {"role": "user", "content": task_config["user_prompt_template"].replace("__BRIEFING_TEXT__", briefing_text.strip())},
                ],
                model_id=model_id,
                force_non_thinking=force_non_thinking,
            ),
            "max_tokens": task_config.get("max_tokens", 4096),
            "stream": False,
        }
        base_payload.update(self._build_chatbot_sampling_payload())
        if force_non_thinking and self._chatbot_request_targets_gemma4(model_id=model_id):
            base_payload["think"] = False
        if keep_alive is not None and self.chatbot_backend_mode == CHATBOT_BACKEND_MODE_OLLAMA:
            base_payload["keep_alive"] = keep_alive
        return [
            dict(base_payload, response_format={"type": "json_schema", "json_schema": task_config["json_schema"]}),
            dict(base_payload, response_format={"type": "json_object"}),
            dict(base_payload),
        ]

    def _request_chatbot_structured_output(self, task_name, briefing_text, keep_alive=None):
        task_config = self._get_chatbot_task_config(task_name)
        timeout_seconds = max(15, int(self.chatbot_request_timeout or DEFAULT_CHATBOT_REQUEST_TIMEOUT))
        model_id = self._resolve_chatbot_generation_model_id(timeout_seconds=min(timeout_seconds, 10))
        response_payload = None
        last_error = None
        payload_variants = self._build_chatbot_completion_payload_variants(task_config, briefing_text, model_id, keep_alive=keep_alive)
        for payload_index, payload in enumerate(payload_variants):
            try:
                response_payload = self._post_chatbot_completion_payload(payload, timeout_seconds=timeout_seconds)
                break
            except Exception as exc:
                last_error = exc
                if payload_index >= len(payload_variants) - 1 or not self._chatbot_supports_response_format_retry(str(exc)):
                    raise

        response_parts = self._extract_chatbot_response_parts(response_payload)
        content = str(response_parts.get("content") or "").strip()
        if not content:
            raise ValueError("The chatbot reply was empty.")
        parsed_output = self._extract_json_object_from_text(content)
        validated_output = self._validate_chatbot_structured_output(task_config, parsed_output)
        validated_output["task_label"] = task_name
        validated_output["model_id"] = model_id
        validated_output["raw_content"] = str(content or "")
        validated_output["reasoning_content"] = str(response_parts.get("reasoning") or "").strip()
        return validated_output

    def _append_prompt_to_image_queue(self, prompt_text):
        resolved_prompt = str(prompt_text or "").strip()
        if not resolved_prompt:
            raise ValueError("The optimized prompt is empty.")

        self.add_image_prompt_entry()
        target_widget = self.image_prompts[-1]
        target_widget.delete("1.0", tk.END)
        target_widget.insert("1.0", resolved_prompt)
        self.notebook.select(self.image_tab)
        self.update_image_scroll_region()
        self._update_prompt_collection_summary()

    def apply_chatbot_result_to_image_queue(self):
        task_label = str((self.chatbot_last_result or {}).get("task_label") or (self.chatbot_last_result or {}).get("task") or "").strip()
        if task_label == CHATBOT_TASK_SCENE_PLAN or task_label == "scene_plan":
            self.apply_chatbot_scene_plan_to_timeline()
            return

        if not self.chatbot_last_result:
            messagebox.showwarning("Chatbot", "Generate a prompt draft first.")
            return

        optimized_prompt = str(self.chatbot_last_result.get("optimized_prompt") or "").strip()
        if not optimized_prompt:
            messagebox.showwarning("Chatbot", "The current chatbot result does not include an optimized image prompt.")
            return

        self._append_prompt_to_image_queue(optimized_prompt)
        self._record_chatbot_artifact_apply(
            target_type="image_prompt_queue",
            target_scope="append_queue",
            apply_mode="append",
            summary="Added optimized prompt to the Image Phase queue.",
        )
        self.update_status("Chatbot prompt added to the Image Phase queue.", "green")
        messagebox.showinfo("Chatbot", "The optimized prompt was added to the Image Phase queue.")

    def apply_chatbot_result_to_scene_timeline(self):
        task_label = str((self.chatbot_last_result or {}).get("task_label") or (self.chatbot_last_result or {}).get("task") or "").strip()
        if task_label == CHATBOT_TASK_SCENE_PLAN or task_label == "scene_plan":
            self.apply_chatbot_scene_plan_to_timeline()
            return

        if not self.chatbot_last_result:
            messagebox.showwarning("Chatbot", "Generate a prompt draft first.")
            return

        optimized_prompt = str(self.chatbot_last_result.get("optimized_prompt") or "").strip()
        if not optimized_prompt:
            messagebox.showwarning("Chatbot", "The current chatbot result does not include an optimized prompt.")
            return

        next_index = len(self.scene_timeline) + 1
        new_entry = self._create_scene_entry(next_index, mode=SCENE_MODE_T2V, prompt=optimized_prompt)
        self.scene_timeline.append(new_entry)
        self.scene_timeline = self._normalize_scene_timeline(self.scene_timeline)
        if hasattr(self, "scene_scrollable_frame"):
            self._rebuild_scene_timeline_from_state(self.scene_timeline)
        self._record_chatbot_artifact_apply(
            target_type="scene_timeline",
            target_scope="append_timeline",
            apply_mode="append",
            summary="Added optimized prompt as a new scene in the Scene Timeline.",
        )
        self.update_status("Chatbot prompt added to the Scene Timeline.", "green")
        if hasattr(self, "notebook") and hasattr(self, "video_tab"):
            self.notebook.select(self.video_tab)
        messagebox.showinfo("Chatbot", "The optimized prompt was added to the Scene Timeline.")

    def apply_chatbot_scene_plan_to_timeline(self):
        if not self.chatbot_last_result:
            messagebox.showwarning("Chatbot", "Generate a scene plan first.")
            return

        scenes = self.chatbot_last_result.get("scenes") if isinstance(self.chatbot_last_result.get("scenes"), list) else []
        normalized_timeline = []
        for index, scene in enumerate(scenes, start=1):
            if not isinstance(scene, dict):
                continue
            prompt_text = str(scene.get("video_prompt") or scene.get("image_prompt") or scene.get("prompt") or "").strip()
            if not prompt_text:
                continue
            scene_number = int(scene.get("scene_number") or index)
            normalized_timeline.append(self._create_scene_entry(scene_number, mode=SCENE_MODE_T2V, prompt=prompt_text))

        if not normalized_timeline:
            messagebox.showwarning("Chatbot", "The current scene plan does not include any usable scene prompts.")
            return

        self.scene_timeline = self._normalize_scene_timeline(normalized_timeline)
        if hasattr(self, "scene_scrollable_frame"):
            self._rebuild_scene_timeline_from_state(self.scene_timeline)
        self._record_chatbot_artifact_apply(
            target_type="scene_timeline",
            target_scope="replace_timeline",
            apply_mode="replace",
            summary="Applied planned scenes to the Scene Timeline.",
        )
        self.update_status("Scene plan applied to the Scene Timeline.", "green")
        if hasattr(self, "notebook") and hasattr(self, "video_tab"):
            self.notebook.select(self.video_tab)
        messagebox.showinfo("Chatbot", "The planned scenes were applied to the Scene Timeline.")

    def _handle_chatbot_plan_scenes(self):
        self._handle_chatbot_structured_task(
            CHATBOT_TASK_SCENE_PLAN,
            empty_message="Please enter a message first.",
            loading_text="Planning scene flow from the current creative direction...",
            start_status="Scene planning started.",
            success_status="Scene plan ready.",
            failure_title="Failed to plan scenes",
            phase_key_base="chatbot_scene_plan",
        )

    def _handle_chatbot_finalize_song(self):
        if not self.ensure_chatbot_model_ready(interactive=True):
            return
        conversation_id = self._ensure_active_chatbot_conversation()
        conversation_turns = self._get_chatbot_conversation_turns(conversation_id=conversation_id, limit=12)
        if not conversation_turns:
            messagebox.showwarning("Chatbot", "Chat about your song idea first, then click Finalize Song.")
            return

        task_config = self._get_chatbot_task_config(CHATBOT_TASK_SONG_BRAINSTORM)
        briefing_summary = "Finalize the song lyrics and style tags from our brainstorming conversation."
        self._append_chatbot_turn("user", briefing_summary, kind="chat", conversation_id=conversation_id)
        self.chatbot_last_result = None
        self.chatbot_output_show_raw = False
        self.chatbot_pending_request_mode = "artifact"
        self._set_chatbot_generation_state(True)
        self._set_chatbot_output_preview("Finalizing song lyrics and style tags from the conversation...")
        self.update_status("Song finalization started.", "blue")
        is_cold = not self.chatbot_model_warm
        phase_key = CHATBOT_PHASE_SONG_FINALIZE_COLD if is_cold else CHATBOT_PHASE_SONG_FINALIZE_WARM
        preparing_status = "Starting chatbot backend & loading model..." if is_cold else "Finalizing song..."
        self._set_tutorial_runtime_progress(phase_key, reset=True, status=preparing_status, current=0, total=1, item_label="Song finalize", stage="preparing")

        def worker():
            task_start = time.time()
            try:
                backend_result = self._ensure_chatbot_backend_ready_for_use(action_label="song finalization")
                if not backend_result.get("ok"):
                    raise RuntimeError(backend_result.get("detail") or backend_result.get("status") or "The chatbot backend is not ready.")
                self.chatbot_model_warm = True
                self._set_tutorial_runtime_progress(phase_key, status="Waiting for finalized song...", current=1, total=1, item_label="Song finalize", stage="running")
                result = self._request_chatbot_song_finalization(task_config, conversation_id)
            except Exception as exc:
                error_message = str(exc)
                self._set_tutorial_runtime_progress(phase_key, status="Song finalization failed.", current=1, total=1, item_label="Song finalize", stage="failed")

                def on_error():
                    self.chatbot_pending_request_mode = None
                    self._append_chatbot_turn("assistant", error_message, kind="status", conversation_id=conversation_id)
                    self._set_chatbot_generation_state(False)
                    self._set_chatbot_output_preview(f"Failed to finalize song.\n\n{error_message}")
                    self.update_status("Song finalization failed.", "red")
                    messagebox.showerror("Chatbot", f"Failed to finalize song:\n{error_message}")

                self.root.after(0, on_error)
                return

            self.record_tutorial_phase_timing(phase_key, time.time() - task_start)
            self._set_tutorial_runtime_progress(phase_key, status="Song finalized.", current=1, total=1, item_label="Song finalize", stage="complete")

            def on_success():
                self.chatbot_pending_request_mode = None
                self._record_chatbot_history_entry(CHATBOT_TASK_SONG_BRAINSTORM, briefing_summary, result)
                self._refresh_chatbot_output_preview()
                self._set_chatbot_generation_state(False)
                self.update_status("Song lyrics and style tags finalized.", "green")

            self.root.after(0, on_success)

        threading.Thread(target=worker, daemon=True).start()

    def _request_chatbot_song_finalization(self, task_config, conversation_id):
        timeout_seconds = max(15, int(self.chatbot_request_timeout or DEFAULT_CHATBOT_REQUEST_TIMEOUT))
        model_id = self._resolve_chatbot_generation_model_id(timeout_seconds=min(timeout_seconds, 10))
        force_non_thinking = self._chatbot_should_force_non_thinking(model_id=model_id)
        conversation_turns = self._get_chatbot_conversation_turns(conversation_id=conversation_id, limit=12)
        finalize_instruction = task_config["user_prompt_template"].replace("__BRIEFING_TEXT__", "Finalize the song based on our brainstorming conversation above.")
        messages = self._build_chatbot_request_messages(
            [{"role": "system", "content": task_config["system_prompt"]}]
            + conversation_turns
            + [{"role": "user", "content": finalize_instruction}],
            model_id=model_id,
            force_non_thinking=force_non_thinking,
        )
        base_payload = {
            "model": model_id,
            "messages": messages,
            "max_tokens": 4096,
            "stream": False,
        }
        base_payload.update(self._build_chatbot_sampling_payload())
        if force_non_thinking and self._chatbot_request_targets_gemma4(model_id=model_id):
            base_payload["think"] = False
        payload_variants = [
            dict(base_payload, response_format={"type": "json_schema", "json_schema": task_config["json_schema"]}),
            dict(base_payload, response_format={"type": "json_object"}),
            dict(base_payload),
        ]
        response_payload = None
        for payload_index, payload in enumerate(payload_variants):
            try:
                response_payload = self._post_chatbot_completion_payload(payload, timeout_seconds=timeout_seconds)
                break
            except Exception as exc:
                if payload_index >= len(payload_variants) - 1 or not self._chatbot_supports_response_format_retry(str(exc)):
                    raise
        response_parts = self._extract_chatbot_response_parts(response_payload)
        content = str(response_parts.get("content") or "").strip()
        if not content:
            raise ValueError("The chatbot reply was empty.")
        parsed_output = self._extract_json_object_from_text(content)
        validated_output = self._validate_chatbot_structured_output(task_config, parsed_output)
        validated_output["task_label"] = CHATBOT_TASK_SONG_BRAINSTORM
        validated_output["model_id"] = model_id
        validated_output["raw_content"] = str(content or "")
        validated_output["reasoning_content"] = str(response_parts.get("reasoning") or "").strip()
        return validated_output

    def apply_chatbot_result_to_music_tab(self):
        if not self.chatbot_last_result:
            messagebox.showwarning("Chatbot", "Finalize a song first.")
            return
        task_label = str(self.chatbot_last_result.get("task_label") or self.chatbot_last_result.get("task") or "").strip()
        if task_label != CHATBOT_TASK_SONG_BRAINSTORM and task_label != "song_brainstorm":
            messagebox.showwarning("Chatbot", "The current result is not a finalized song. Use Finalize Song first.")
            return
        lyrics = str(self.chatbot_last_result.get("lyrics") or "").strip()
        style_tags = str(self.chatbot_last_result.get("style_tags") or "").strip()
        if not lyrics and not style_tags:
            messagebox.showwarning("Chatbot", "The finalized song has no lyrics or style tags.")
            return
        if hasattr(self, "music_lyrics_text"):
            self.music_lyrics_text.delete("1.0", tk.END)
            if lyrics:
                self.music_lyrics_text.insert("1.0", lyrics)
        if hasattr(self, "music_tags_text"):
            self.music_tags_text.delete("1.0", tk.END)
            if style_tags:
                self.music_tags_text.insert("1.0", style_tags)
        self._record_chatbot_artifact_apply(
            target_type="music_lyrics_and_tags",
            target_scope="replace_music_fields",
            apply_mode="replace",
            summary="Sent finalized lyrics and style tags to the Music tab.",
        )
        self.update_status("Song lyrics and style tags sent to the Music tab.", "green")
        if hasattr(self, "notebook") and hasattr(self, "music_tab"):
            self.notebook.select(self.music_tab)
        messagebox.showinfo("Chatbot", "Lyrics and style tags were sent to the Music tab.")

    def _handle_chatbot_structured_task(self, task_name, empty_message, loading_text, start_status, success_status, failure_title, phase_key_base="chatbot_task"):
        if not self.ensure_chatbot_model_ready(interactive=True):
            return
        briefing_text = self.chatbot_briefing_text.get("1.0", tk.END).strip() if hasattr(self, "chatbot_briefing_text") else ""
        if not briefing_text:
            messagebox.showwarning("Chatbot", empty_message)
            return

        conversation_id = self._ensure_active_chatbot_conversation()
        self._append_chatbot_turn("user", briefing_text, kind="chat", conversation_id=conversation_id)
        self.chatbot_last_result = None
        self.chatbot_output_show_raw = False
        self.chatbot_pending_request_mode = "artifact"
        is_cold = not self.chatbot_model_warm
        phase_key = f"{phase_key_base}_cold" if is_cold else f"{phase_key_base}_warm"
        self._set_chatbot_generation_state(True)
        self._set_chatbot_output_preview(loading_text)
        self.update_status(start_status, "blue")
        preparing_status = "Starting chatbot backend & loading model..." if is_cold else "Connecting to chatbot backend..."
        self._set_tutorial_runtime_progress(phase_key, reset=True, status=preparing_status, current=0, total=1, item_label=PHASE_DISPLAY_NAMES.get(phase_key, "Chatbot task"), stage="preparing")

        def worker():
            task_start = time.time()
            try:
                backend_result = self._ensure_chatbot_backend_ready_for_use(action_label=str(task_name or "chatbot generation").lower())
                if not backend_result.get("ok"):
                    raise RuntimeError(backend_result.get("detail") or backend_result.get("status") or "The chatbot backend is not ready.")
                self.chatbot_model_warm = True
                self._set_tutorial_runtime_progress(phase_key, status="Waiting for chatbot output...", current=1, total=1, item_label=PHASE_DISPLAY_NAMES.get(phase_key, "Chatbot task"), stage="running")
                result = self._request_chatbot_structured_output(task_name, briefing_text)
            except Exception as exc:
                error_message = str(exc)
                self._set_tutorial_runtime_progress(phase_key, status="Chatbot task failed.", current=1, total=1, item_label=PHASE_DISPLAY_NAMES.get(phase_key, "Chatbot task"), stage="failed")

                def on_error():
                    self.chatbot_pending_request_mode = None
                    self._append_chatbot_turn("assistant", error_message, kind="status", conversation_id=conversation_id)
                    self._set_chatbot_generation_state(False)
                    self._set_chatbot_output_preview(f"{failure_title}.\n\n{error_message}")
                    self.update_status(failure_title + ".", "red")
                    messagebox.showerror("Chatbot", f"{failure_title}:\n{error_message}")

                self.root.after(0, on_error)
                return

            self.record_tutorial_phase_timing(phase_key, time.time() - task_start)
            self._set_tutorial_runtime_progress(phase_key, status="Chatbot task complete.", current=1, total=1, item_label=PHASE_DISPLAY_NAMES.get(phase_key, "Chatbot task"), stage="complete")

            def on_success():
                self.chatbot_pending_request_mode = None
                self._record_chatbot_history_entry(task_name, briefing_text, result)
                if hasattr(self, "chatbot_briefing_text"):
                    self.chatbot_briefing_text.delete("1.0", tk.END)
                self.chatbot_state["view"]["composer_draft"] = ""
                self._refresh_chatbot_output_preview()
                self._set_chatbot_generation_state(False)
                self.update_status(success_status, "green")

            self.root.after(0, on_success)

        threading.Thread(target=worker, daemon=True).start()

    def _handle_chatbot_send(self):
        if not self.ensure_chatbot_model_ready(interactive=True):
            return
        message_text = self.chatbot_briefing_text.get("1.0", tk.END).strip() if hasattr(self, "chatbot_briefing_text") else ""
        if not message_text:
            messagebox.showwarning("Chatbot", "Please enter a message first.")
            return

        conversation_id = self._ensure_active_chatbot_conversation()
        self._append_chatbot_turn("user", message_text, kind="chat", conversation_id=conversation_id)
        if hasattr(self, "chatbot_briefing_text"):
            self.chatbot_briefing_text.delete("1.0", tk.END)
        self.chatbot_last_result = None
        self.chatbot_output_show_raw = False
        self.chatbot_pending_request_mode = "chat"
        is_cold = not self.chatbot_model_warm
        phase_key = CHATBOT_PHASE_CHAT_COLD if is_cold else CHATBOT_PHASE_CHAT_WARM
        self._set_chatbot_generation_state(True)
        self._set_chatbot_output_preview("The assistant is thinking about your latest message...")
        self.update_status("Chatbot reply started.", "blue")
        preparing_status = "Starting chatbot backend & loading model..." if is_cold else "Connecting to chatbot backend..."
        self._set_tutorial_runtime_progress(phase_key, reset=True, status=preparing_status, current=0, total=1, item_label="Chat reply", stage="preparing")

        def worker():
            chat_start = time.time()
            try:
                backend_result = self._ensure_chatbot_backend_ready_for_use(action_label="chat reply")
                if not backend_result.get("ok"):
                    raise RuntimeError(backend_result.get("detail") or backend_result.get("status") or "The chatbot backend is not ready.")
                self.chatbot_model_warm = True
                self._set_tutorial_runtime_progress(phase_key, status="Waiting for chatbot reply...", current=1, total=1, item_label="Chat reply", stage="running")
                reply = self._request_chatbot_chat_reply(conversation_id=conversation_id)
            except Exception as exc:
                error_message = str(exc)
                self._set_tutorial_runtime_progress(phase_key, status="Chat reply failed.", current=1, total=1, item_label="Chat reply", stage="failed")

                def on_error():
                    self.chatbot_pending_request_mode = None
                    self._append_chatbot_turn("assistant", error_message, kind="status", conversation_id=conversation_id)
                    self._set_chatbot_generation_state(False)
                    self._set_chatbot_output_preview(f"Chat reply failed.\n\n{error_message}")
                    self.update_status("Chatbot reply failed.", "red")
                    messagebox.showerror("Chatbot", f"Failed to generate chat reply:\n{error_message}")

                self.root.after(0, on_error)
                return

            self.record_tutorial_phase_timing(phase_key, time.time() - chat_start)
            self._set_tutorial_runtime_progress(phase_key, status="Chat reply ready.", current=1, total=1, item_label="Chat reply", stage="complete")

            def on_success():
                self.chatbot_pending_request_mode = None
                self._append_chatbot_turn("assistant", reply.get("content"), kind="chat", conversation_id=conversation_id)
                if hasattr(self, "chatbot_briefing_text"):
                    self.chatbot_briefing_text.delete("1.0", tk.END)
                self.chatbot_state["view"]["composer_draft"] = ""
                self._set_chatbot_output_preview(reply.get("content"))
                self._set_chatbot_generation_state(False)
                self.update_status("Chatbot reply ready.", "green")

            self.root.after(0, on_success)

        threading.Thread(target=worker, daemon=True).start()

    def _get_chatbot_probe_urls(self):
        base_url = str(self.chatbot_server_url or DEFAULT_CHATBOT_SERVER_URL).strip()
        if not base_url:
            base_url = DEFAULT_CHATBOT_SERVER_URL
        base_url = base_url.rstrip("/")
        return [
            f"{base_url}/health",
            f"{base_url}/v1/models",
        ]

    def _probe_chatbot_backend(self, timeout_seconds=3):
        last_error = None
        try:
            model_ids = self._fetch_chatbot_backend_models(timeout_seconds=timeout_seconds)
            return {
                "ok": True,
                "status": f"Backend reachable at {self._chatbot_base_url()}/v1/models | models: {', '.join(model_ids[:3])}",
                "reachable_url": f"{self._chatbot_base_url()}/v1/models",
                "model_ids": model_ids,
            }
        except Exception as exc:
            last_error = str(exc)

        probe_url = f"{self._chatbot_base_url()}/health"
        try:
            request = urllib.request.Request(probe_url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                status_code = getattr(response, "status", 200)
                if 200 <= status_code < 300:
                    return {
                        "ok": True,
                        "status": "Backend responded to /health, but model discovery from /v1/models failed.",
                        "reachable_url": probe_url,
                        "detail": last_error,
                    }
        except Exception as exc:
            last_error = f"{probe_url} failed: {exc}"

        if self.chatbot_backend_mode == CHATBOT_BACKEND_MODE_MANAGED and self._chatbot_server_executable_is_valid():
            return {
                "ok": False,
                "status": "Managed mode is configured, but the llama.cpp server is not responding yet.",
                "reachable_url": None,
                "detail": last_error,
            }

        if self.chatbot_backend_mode == CHATBOT_BACKEND_MODE_MANAGED:
            return {
                "ok": False,
                "status": "Managed mode is selected, but no valid llama-server executable is configured and the server is offline.",
                "reachable_url": None,
                "detail": last_error,
            }

        if self.chatbot_backend_mode == CHATBOT_BACKEND_MODE_OLLAMA:
            active_ollama_path = self._get_active_chatbot_server_executable_path(backend_mode=CHATBOT_BACKEND_MODE_OLLAMA)
            status_text = "Ollama mode is configured, but the Ollama server is not responding yet."
            if not active_ollama_path:
                status_text = "Ollama mode is selected, but Prompt2MTV could not find ollama.exe and the server is offline."
            return {
                "ok": False,
                "status": status_text,
                "reachable_url": None,
                "detail": last_error,
            }

        return {
            "ok": False,
            "status": "Could not reach the configured llama.cpp server.",
            "reachable_url": None,
            "detail": last_error,
        }

    def _apply_chatbot_runtime_settings(
        self,
        model_root=None,
        model_path=None,
        model_family=None,
        gemma4_ollama_tag=None,
        backend_mode=None,
        server_url=None,
        server_executable_path=None,
        context_size=None,
        request_timeout=None,
        temperature=None,
        top_p=None,
        top_k=None,
        min_p=None,
        repeat_penalty=None,
        default_to_non_thinking=None,
        auto_launch_server=None,
        preferred_drive=None,
    ):
        previous_backend_mode = self.chatbot_backend_mode
        if model_family is not None:
            normalized_family = str(model_family or "").strip().lower()
            if normalized_family not in {CHATBOT_MODEL_FAMILY_QWEN3, CHATBOT_MODEL_FAMILY_GEMMA4}:
                normalized_family = CHATBOT_MODEL_FAMILY_QWEN3
            self.chatbot_model_family = normalized_family
        if gemma4_ollama_tag is not None:
            tag = str(gemma4_ollama_tag or "").strip()
            if tag in GEMMA4_OLLAMA_TAG_OPTIONS:
                self.chatbot_gemma4_ollama_tag = tag
        if model_root is not None:
            self.chatbot_model_root = self._normalize_path(model_root)
        if model_path is not None:
            self.chatbot_model_path = self._normalize_path(model_path)
        elif self.chatbot_model_root:
            self.chatbot_model_path = self._get_chatbot_model_path_from_root(self.chatbot_model_root)

        if backend_mode is not None:
            normalized_mode = str(backend_mode or "").strip().lower()
            if normalized_mode not in {CHATBOT_BACKEND_MODE_CONNECT, CHATBOT_BACKEND_MODE_MANAGED, CHATBOT_BACKEND_MODE_OLLAMA}:
                normalized_mode = CHATBOT_BACKEND_MODE_CONNECT
            self.chatbot_backend_mode = normalized_mode
        if server_url is not None:
            self.chatbot_server_url = str(server_url or "").strip() or self._get_default_chatbot_server_url()
        elif backend_mode is not None and (
            not self.chatbot_server_url
            or self.chatbot_server_url.rstrip("/") in {DEFAULT_CHATBOT_SERVER_URL, DEFAULT_OLLAMA_SERVER_URL}
            or previous_backend_mode != self.chatbot_backend_mode
        ):
            self.chatbot_server_url = self._get_default_chatbot_server_url(self.chatbot_backend_mode)
        if server_executable_path is not None:
            self.chatbot_server_executable_path = self._sanitize_chatbot_server_executable_path(server_executable_path, backend_mode=self.chatbot_backend_mode) or ""
        elif self.chatbot_backend_mode == CHATBOT_BACKEND_MODE_OLLAMA and not self.chatbot_server_executable_path:
            self.chatbot_server_executable_path = self._get_active_chatbot_server_executable_path(backend_mode=CHATBOT_BACKEND_MODE_OLLAMA)
        if context_size is not None:
            try:
                self.chatbot_context_size = max(1024, int(context_size))
            except (TypeError, ValueError):
                self.chatbot_context_size = DEFAULT_CHATBOT_CONTEXT_SIZE
        if request_timeout is not None:
            try:
                self.chatbot_request_timeout = max(15, int(request_timeout))
            except (TypeError, ValueError):
                self.chatbot_request_timeout = DEFAULT_CHATBOT_REQUEST_TIMEOUT
        if temperature is not None:
            try:
                self.chatbot_temperature = max(0.0, float(temperature))
            except (TypeError, ValueError):
                self.chatbot_temperature = DEFAULT_CHATBOT_TEMPERATURE
        if top_p is not None:
            try:
                self.chatbot_top_p = min(1.0, max(0.0, float(top_p)))
            except (TypeError, ValueError):
                self.chatbot_top_p = DEFAULT_CHATBOT_TOP_P
        if top_k is not None:
            try:
                self.chatbot_top_k = max(1, int(top_k))
            except (TypeError, ValueError):
                self.chatbot_top_k = DEFAULT_CHATBOT_TOP_K
        if min_p is not None:
            try:
                self.chatbot_min_p = min(1.0, max(0.0, float(min_p)))
            except (TypeError, ValueError):
                self.chatbot_min_p = DEFAULT_CHATBOT_MIN_P
        if repeat_penalty is not None:
            try:
                self.chatbot_repeat_penalty = max(0.0, float(repeat_penalty))
            except (TypeError, ValueError):
                self.chatbot_repeat_penalty = DEFAULT_CHATBOT_REPEAT_PENALTY
        if default_to_non_thinking is not None:
            self.chatbot_default_to_non_thinking = bool(default_to_non_thinking)
        if auto_launch_server is not None:
            self.chatbot_auto_launch_server = bool(auto_launch_server)
        if preferred_drive is not None:
            preferred_value = str(preferred_drive or "").strip().upper().rstrip(":")
            self.chatbot_preferred_drive = preferred_value or "M"

        self.save_global_settings()
        self._refresh_chatbot_runtime_ui()

    def _refresh_chatbot_runtime_ui(self):
        runtime_ready = self._chatbot_generation_prerequisites_ready()
        if hasattr(self, "chatbot_runtime_state_value_label"):
            self.chatbot_runtime_state_value_label.config(text=self._get_chatbot_readiness_summary())
        if hasattr(self, "chatbot_model_value_label"):
            if self._chatbot_model_is_ready():
                self.chatbot_model_value_label.config(text=os.path.basename(self.chatbot_model_path))
            elif self._chatbot_can_generate_without_local_model():
                self.chatbot_model_value_label.config(text="Server-managed")
            else:
                self.chatbot_model_value_label.config(text="Not installed")
        if hasattr(self, "chatbot_destination_value_label"):
            self.chatbot_destination_value_label.config(text=self.chatbot_model_root or "Unset")
        if hasattr(self, "chatbot_backend_value_label"):
            self.chatbot_backend_value_label.config(text=self._get_chatbot_backend_mode_label())
        if hasattr(self, "chatbot_model_family_var"):
            self.chatbot_model_family_var.set(self.chatbot_model_family or DEFAULT_CHATBOT_MODEL_FAMILY)
        if hasattr(self, "chatbot_gemma4_tag_var"):
            self.chatbot_gemma4_tag_var.set(self.chatbot_gemma4_ollama_tag or DEFAULT_GEMMA4_OLLAMA_TAG)
        if hasattr(self, "chatbot_next_step_value_label"):
            self.chatbot_next_step_value_label.config(text=self._get_chatbot_next_step_text())
        if hasattr(self, "chatbot_runtime_status_label"):
            self.chatbot_runtime_status_label.config(text=self._get_chatbot_runtime_state_text())
        if hasattr(self, "chatbot_readiness_summary_label"):
            self.chatbot_readiness_summary_label.config(text=self._get_chatbot_readiness_summary())
        if hasattr(self, "chatbot_readiness_next_step_label"):
            self.chatbot_readiness_next_step_label.config(text=self._get_chatbot_next_step_text())
        if hasattr(self, "chatbot_readiness_health_label"):
            self.chatbot_readiness_health_label.config(text=self.chatbot_backend_health_text)
        if "chatbot_readiness" in self.collapsible_sections:
            self._update_collapsible_section_meta("chatbot_readiness", self._get_chatbot_readiness_summary())
        if "chatbot_history" in self.collapsible_sections:
            history_count = len(self.chatbot_result_history)
            self._update_collapsible_section_meta("chatbot_history", f"{history_count} saved" if history_count else "No saved results")
        self._refresh_chatbot_task_ui()
        if hasattr(self, "chatbot_generate_btn"):
            self._set_chatbot_generation_state(self.chatbot_generation_in_progress)
        self._refresh_chatbot_output_preview()

    def _create_chatbot_download_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Downloading Qwen Chatbot Model")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.geometry("620x240")
        dialog.minsize(560, 220)
        self._style_panel(dialog, self.colors["bg"])

        shell = tk.Frame(dialog, padx=20, pady=18)
        shell.pack(fill=tk.BOTH, expand=True)
        self._style_panel(shell, self.colors["bg"])

        title_label = tk.Label(shell, text="Downloading Qwen Chatbot Model")
        title_label.pack(anchor="w")
        self._style_label(title_label, "title", self.colors["bg"])

        summary_var = tk.StringVar(value=f"Preparing to download {self.chatbot_model_filename}...")
        summary_label = tk.Label(shell, textvariable=summary_var, justify=tk.LEFT, anchor="w", wraplength=560)
        summary_label.pack(fill=tk.X, pady=(8, 6))
        self._style_label(summary_label, "body", self.colors["bg"])

        detail_var = tk.StringVar(value="Waiting for download to start...")
        detail_label = tk.Label(shell, textvariable=detail_var, justify=tk.LEFT, anchor="w", wraplength=560)
        detail_label.pack(fill=tk.X, pady=(0, 10))
        self._style_label(detail_label, "muted", self.colors["bg"])

        progress_bar = ttk.Progressbar(shell, mode="determinate", maximum=100)
        progress_bar.pack(fill=tk.X)

        progress_var = tk.StringVar(value="0%")
        progress_label = tk.Label(shell, textvariable=progress_var, anchor="e")
        progress_label.pack(fill=tk.X, pady=(6, 10))
        self._style_label(progress_label, "small", self.colors["bg"])

        footer = tk.Frame(shell)
        footer.pack(fill=tk.X, pady=(8, 0))
        self._style_panel(footer, self.colors["bg"])

        cancel_button = tk.Button(footer, text="Cancel", command=lambda: setattr(self, "chatbot_download_cancel_requested", True))
        cancel_button.pack(side=tk.RIGHT)
        self._style_button(cancel_button, "secondary", compact=True)

        dialog.protocol("WM_DELETE_WINDOW", lambda: setattr(self, "chatbot_download_cancel_requested", True))
        return {
            "dialog": dialog,
            "summary_var": summary_var,
            "detail_var": detail_var,
            "progress_var": progress_var,
            "progress_bar": progress_bar,
            "indeterminate": False,
        }

    def _update_chatbot_download_dialog(self, dialog_state, downloaded_bytes=None, total_bytes=None, resumed=False):
        if not dialog_state:
            return

        dialog = dialog_state.get("dialog")
        if not dialog or not dialog.winfo_exists():
            return

        dialog_state["summary_var"].set(f"Downloading {self.chatbot_model_filename}")
        if total_bytes is None:
            detail_text = f"{self._format_byte_count(downloaded_bytes)} downloaded from Hugging Face"
            if not dialog_state["indeterminate"]:
                dialog_state["progress_bar"].configure(mode="indeterminate")
                dialog_state["progress_bar"].start(12)
                dialog_state["indeterminate"] = True
            dialog_state["progress_var"].set("Downloading...")
        else:
            if dialog_state["indeterminate"]:
                dialog_state["progress_bar"].stop()
                dialog_state["progress_bar"].configure(mode="determinate")
                dialog_state["indeterminate"] = False

            completion_ratio = 0 if total_bytes <= 0 else min(1.0, downloaded_bytes / total_bytes)
            dialog_state["progress_bar"]["value"] = completion_ratio * 100
            dialog_state["progress_var"].set(f"{completion_ratio * 100:.1f}%")
            detail_text = f"{self._format_byte_count(downloaded_bytes)} of {self._format_byte_count(total_bytes)} downloaded from Hugging Face"

        if resumed:
            detail_text = f"{detail_text} | resuming partial download"

        dialog_state["detail_var"].set(detail_text)
        try:
            dialog.update()
        except tk.TclError:
            pass

    def _close_chatbot_download_dialog(self, dialog_state):
        if not dialog_state:
            return

        dialog = dialog_state.get("dialog")
        try:
            if dialog_state.get("indeterminate"):
                dialog_state["progress_bar"].stop()
            if dialog and dialog.winfo_exists():
                dialog.destroy()
        except tk.TclError:
            pass

    def _prompt_chatbot_model_destination(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Set Up Chatbot Model")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.geometry("780x400")
        dialog.minsize(720, 360)
        self._style_panel(dialog, self.colors["bg"])

        shell = tk.Frame(dialog, padx=18, pady=18)
        shell.pack(fill=tk.BOTH, expand=True)
        self._style_panel(shell, self.colors["bg"])

        header = tk.Label(shell, text="Set Up Qwen Chatbot Model")
        header.pack(anchor="w")
        self._style_label(header, "title", self.colors["bg"])

        subheader = tk.Label(
            shell,
            text="Prompt2MTV can download the Qwen GGUF automatically, or you can point the app to an existing GGUF file you already have on disk."
        )
        subheader.pack(anchor="w", pady=(6, 14))
        self._style_label(subheader, "muted", self.colors["bg"])

        card = tk.Frame(shell, padx=16, pady=16)
        card.pack(fill=tk.BOTH, expand=True)
        self._style_panel(card, self.colors["surface"], border=True)
        card.grid_columnconfigure(1, weight=1)

        recommended_root = self._get_recommended_chatbot_model_root() or self.user_data_dir
        destination_var = tk.StringVar(value=self.chatbot_model_root or recommended_root)
        existing_model_var = tk.StringVar(value=self.chatbot_model_path if self._chatbot_model_is_ready() else "")
        download_size = probe_download_size(self.chatbot_model_url)

        info_lines = [
            f"Filename: {self.chatbot_model_filename}",
            f"Source: {CHATBOT_MODEL_SOURCE_PAGE}",
            f"Estimated size: {self._format_byte_count(download_size)}" if download_size is not None else "Estimated size: unavailable",
            "Recommended destination: M drive first when available, then D drive.",
            "Advanced llama.cpp runtime settings live in a separate dialog."
        ]
        info_label = tk.Label(card, text="\n".join(info_lines), justify=tk.LEFT, anchor="w", wraplength=640)
        info_label.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 14))
        self._style_label(info_label, "body", self.colors["surface"])

        destination_label = tk.Label(card, text="Model folder")
        destination_label.grid(row=1, column=0, sticky="w", padx=(0, 12), pady=(0, 10))
        self._style_label(destination_label, "body_strong", self.colors["surface"])

        destination_entry = tk.Entry(card, textvariable=destination_var)
        destination_entry.grid(row=1, column=1, sticky="ew", pady=(0, 10))
        self._style_text_input(destination_entry)

        browse_btn = tk.Button(card, text="Browse", command=lambda: self._browse_directory_into_var(destination_var, "Select Chatbot Model Folder", destination_var.get() or recommended_root))
        browse_btn.grid(row=1, column=2, sticky="e", padx=(8, 0), pady=(0, 10))
        self._style_button(browse_btn, "secondary", compact=True)

        existing_label = tk.Label(card, text="Existing GGUF file")
        existing_label.grid(row=2, column=0, sticky="w", padx=(0, 12), pady=(0, 10))
        self._style_label(existing_label, "body_strong", self.colors["surface"])

        existing_entry = tk.Entry(card, textvariable=existing_model_var)
        existing_entry.grid(row=2, column=1, sticky="ew", pady=(0, 10))
        self._style_text_input(existing_entry)

        browse_existing_btn = tk.Button(
            card,
            text="Browse",
            command=lambda: self._browse_file_into_var(existing_model_var, "Select Existing Qwen GGUF", (("GGUF model", "*.gguf"), ("All files", "*.*")), destination_var.get() or recommended_root)
        )
        browse_existing_btn.grid(row=2, column=2, sticky="e", padx=(8, 0), pady=(0, 10))
        self._style_button(browse_existing_btn, "secondary", compact=True)

        status_var = tk.StringVar(value="Choose a destination folder for the GGUF model.")
        status_label = tk.Label(shell, textvariable=status_var, anchor="w", justify=tk.LEFT)
        status_label.pack(fill=tk.X, pady=(12, 0))
        self._style_label(status_label, "muted", self.colors["bg"])

        result = {"confirmed": False}

        def choose_recommended_root():
            destination_var.set(recommended_root)
            status_var.set(f"Recommended destination selected: {recommended_root}")

        def use_existing_model():
            chosen_root = self._normalize_path(destination_var.get())
            existing_model_path = self._normalize_path(existing_model_var.get())
            if existing_model_path:
                if not os.path.isfile(existing_model_path):
                    messagebox.showerror("Chatbot Model", "The selected GGUF file does not exist.", parent=dialog)
                    return
                if not existing_model_path.lower().endswith(".gguf"):
                    messagebox.showerror("Chatbot Model", "Please select a GGUF model file.", parent=dialog)
                    return
                chosen_root = os.path.dirname(existing_model_path)
                chosen_path = existing_model_path
            else:
                if not chosen_root:
                    messagebox.showerror("Chatbot Model", "Please choose a model folder or browse to an existing GGUF file.", parent=dialog)
                    return
                chosen_path = os.path.join(chosen_root, self.chatbot_model_filename)
                if not os.path.isfile(chosen_path):
                    messagebox.showerror(
                        "Chatbot Model",
                        "No GGUF file was found at the selected folder. Browse to an existing GGUF file or use Download Model.",
                        parent=dialog,
                    )
                    return
            result.update({
                "confirmed": True,
                "download": False,
                "model_root": chosen_root,
                "model_path": chosen_path,
            })
            dialog.destroy()

        def save_without_download():
            use_existing_model()

        def confirm_and_download():
            chosen_root = self._normalize_path(destination_var.get())
            if not chosen_root:
                messagebox.showerror("Chatbot Model", "Please choose a model folder.", parent=dialog)
                return
            result.update({
                "confirmed": True,
                "download": True,
                "model_root": chosen_root,
                "model_path": os.path.join(chosen_root, self.chatbot_model_filename),
            })
            dialog.destroy()

        footer = tk.Frame(shell)
        footer.pack(fill=tk.X, pady=(14, 0))
        self._style_panel(footer, self.colors["bg"])

        cancel_btn = tk.Button(footer, text="Skip for Now", command=dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT)
        self._style_button(cancel_btn, "secondary", compact=True)

        save_btn = tk.Button(footer, text="Use Existing GGUF", command=save_without_download)
        save_btn.pack(side=tk.RIGHT, padx=(8, 0))
        self._style_button(save_btn, "ghost", compact=True)

        download_btn = tk.Button(footer, text="Download Model", command=confirm_and_download)
        download_btn.pack(side=tk.RIGHT, padx=(8, 0))
        self._style_button(download_btn, "primary", compact=True)

        recommended_btn = tk.Button(footer, text="Use Recommended Folder", command=choose_recommended_root)
        recommended_btn.pack(side=tk.LEFT)
        self._style_button(recommended_btn, "ghost", compact=True)

        dialog.bind("<Escape>", lambda _event: dialog.destroy())
        dialog.wait_visibility()
        dialog.focus_set()
        dialog.wait_window()
        return result

    def _prompt_chatbot_runtime_configuration(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Advanced Chatbot Runtime Settings")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.geometry("760x510")
        dialog.minsize(700, 470)
        self._style_panel(dialog, self.colors["bg"])

        shell = tk.Frame(dialog, padx=18, pady=18)
        shell.pack(fill=tk.BOTH, expand=True)
        self._style_panel(shell, self.colors["bg"])

        header = tk.Label(shell, text="Advanced Chatbot Runtime Settings")
        header.pack(anchor="w")
        self._style_label(header, "title", self.colors["bg"])

        subheader = tk.Label(
            shell,
            text="Choose whether Prompt2MTV should connect to an already running llama.cpp server or prepare for a managed llama-server launch later."
        )
        subheader.pack(anchor="w", pady=(6, 14))
        self._style_label(subheader, "muted", self.colors["bg"])

        card = tk.Frame(shell, padx=16, pady=16)
        card.pack(fill=tk.BOTH, expand=True)
        self._style_panel(card, self.colors["surface"], border=True)
        card.grid_columnconfigure(1, weight=1)

        backend_mode_var = tk.StringVar(value=self.chatbot_backend_mode or CHATBOT_BACKEND_MODE_CONNECT)
        model_family_var = tk.StringVar(value=self.chatbot_model_family or DEFAULT_CHATBOT_MODEL_FAMILY)
        gemma4_tag_var = tk.StringVar(value=self.chatbot_gemma4_ollama_tag or DEFAULT_GEMMA4_OLLAMA_TAG)
        server_url_var = tk.StringVar(value=self.chatbot_server_url or DEFAULT_CHATBOT_SERVER_URL)
        server_executable_var = tk.StringVar(value=self.chatbot_server_executable_path or "")
        auto_launch_var = tk.BooleanVar(value=bool(self.chatbot_auto_launch_server) or self.chatbot_backend_mode == CHATBOT_BACKEND_MODE_MANAGED)
        context_size_var = tk.StringVar(value=str(self.chatbot_context_size or DEFAULT_CHATBOT_CONTEXT_SIZE))
        timeout_var = tk.StringVar(value=str(self.chatbot_request_timeout or DEFAULT_CHATBOT_REQUEST_TIMEOUT))
        temperature_var = tk.StringVar(value=str(self.chatbot_temperature or DEFAULT_CHATBOT_TEMPERATURE))
        top_p_var = tk.StringVar(value=str(self.chatbot_top_p if self.chatbot_top_p is not None else DEFAULT_CHATBOT_TOP_P))
        top_k_var = tk.StringVar(value=str(self.chatbot_top_k if self.chatbot_top_k is not None else DEFAULT_CHATBOT_TOP_K))
        min_p_var = tk.StringVar(value=str(self.chatbot_min_p if self.chatbot_min_p is not None else DEFAULT_CHATBOT_MIN_P))
        repeat_penalty_var = tk.StringVar(value=str(self.chatbot_repeat_penalty if self.chatbot_repeat_penalty is not None else DEFAULT_CHATBOT_REPEAT_PENALTY))
        non_thinking_var = tk.BooleanVar(value=bool(self.chatbot_default_to_non_thinking))

        info_label = tk.Label(
            card,
            text="Backend mode controls how Prompt2MTV will reach llama.cpp once structured generation is wired in. Model download and model storage are configured separately.",
            justify=tk.LEFT,
            anchor="w",
            wraplength=640,
        )
        info_label.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 14))
        self._style_label(info_label, "body", self.colors["surface"])

        backend_label = tk.Label(card, text="Backend mode")
        backend_label.grid(row=1, column=0, sticky="w", padx=(0, 12), pady=(0, 10))
        self._style_label(backend_label, "body_strong", self.colors["surface"])

        backend_combo = ttk.Combobox(
            card,
            textvariable=backend_mode_var,
            state="readonly",
            values=[CHATBOT_BACKEND_MODE_CONNECT, CHATBOT_BACKEND_MODE_MANAGED, CHATBOT_BACKEND_MODE_OLLAMA],
        )
        backend_combo.grid(row=1, column=1, columnspan=2, sticky="ew", pady=(0, 10))
        backend_combo.configure(style="TCombobox")

        model_family_label = tk.Label(card, text="Model family")
        model_family_label.grid(row=2, column=0, sticky="w", padx=(0, 12), pady=(0, 10))
        self._style_label(model_family_label, "body_strong", self.colors["surface"])

        model_family_combo = ttk.Combobox(
            card,
            textvariable=model_family_var,
            state="readonly",
            values=[CHATBOT_MODEL_FAMILY_QWEN3, CHATBOT_MODEL_FAMILY_GEMMA4],
        )
        model_family_combo.grid(row=2, column=1, columnspan=2, sticky="ew", pady=(0, 10))
        model_family_combo.configure(style="TCombobox")

        gemma4_tag_label = tk.Label(card, text="Gemma4 model tag")
        gemma4_tag_label.grid(row=3, column=0, sticky="w", padx=(0, 12), pady=(0, 10))
        self._style_label(gemma4_tag_label, "body_strong", self.colors["surface"])

        gemma4_tag_combo = ttk.Combobox(
            card,
            textvariable=gemma4_tag_var,
            state="readonly",
            values=GEMMA4_OLLAMA_TAG_OPTIONS,
        )
        gemma4_tag_combo.grid(row=3, column=1, columnspan=2, sticky="ew", pady=(0, 10))
        gemma4_tag_combo.configure(style="TCombobox")

        def _refresh_model_family_widgets(*_args):
            is_gemma4 = model_family_var.get() == CHATBOT_MODEL_FAMILY_GEMMA4
            state = "readonly" if is_gemma4 else "disabled"
            gemma4_tag_combo.configure(state=state)
            if is_gemma4:
                backend_mode_var.set(CHATBOT_BACKEND_MODE_OLLAMA)
                refresh_mode_hint()

        model_family_var.trace_add("write", _refresh_model_family_widgets)
        _refresh_model_family_widgets()

        labels_and_vars = [
            (4, "Local server URL", server_url_var),
            (5, "Runtime executable", server_executable_var),
            (6, "Context size", context_size_var),
            (7, "Request timeout (s)", timeout_var),
            (8, "Temperature", temperature_var),
            (9, "Top P", top_p_var),
            (10, "Top K", top_k_var),
            (11, "Min P", min_p_var),
            (12, "Repeat Penalty", repeat_penalty_var),
        ]
        for row_index, label_text, variable in labels_and_vars:
            label = tk.Label(card, text=label_text)
            label.grid(row=row_index, column=0, sticky="w", padx=(0, 12), pady=(0, 10))
            self._style_label(label, "body_strong", self.colors["surface"])

            entry = tk.Entry(card, textvariable=variable)
            entry.grid(row=row_index, column=1, columnspan=2 if row_index != 5 else 1, sticky="ew", pady=(0, 10))
            self._style_text_input(entry)

            if row_index == 5:
                browse_exec_btn = tk.Button(
                    card,
                    text="Browse",
                    command=lambda: self._browse_file_into_var(server_executable_var, "Select chatbot runtime executable", (("Executable files", "*.exe"), ("All files", "*.*")), self.app_root_dir)
                )
                browse_exec_btn.grid(row=row_index, column=2, sticky="e", padx=(8, 0), pady=(0, 10))
                self._style_button(browse_exec_btn, "secondary", compact=True)

        non_thinking_cb = tk.Checkbutton(card, text="Default normal chat to non-thinking mode when using Ollama", variable=non_thinking_var)
        non_thinking_cb.grid(row=13, column=0, columnspan=3, sticky="w", pady=(0, 10))
        self._style_checkbutton(non_thinking_cb)

        auto_launch_cb = tk.Checkbutton(card, text="Automatically start the selected local chatbot backend when the chatbot is used", variable=auto_launch_var)
        auto_launch_cb.grid(row=14, column=0, columnspan=3, sticky="w", pady=(0, 10))
        self._style_checkbutton(auto_launch_cb)

        status_var = tk.StringVar(value="Connect mode uses the server URL. Managed llama.cpp needs llama-server. Ollama mode can auto-detect ollama.exe.")
        status_label = tk.Label(shell, textvariable=status_var, anchor="w", justify=tk.LEFT)
        status_label.pack(fill=tk.X, pady=(12, 0))
        self._style_label(status_label, "muted", self.colors["bg"])

        def refresh_mode_hint(*_args):
            if backend_mode_var.get() == CHATBOT_BACKEND_MODE_MANAGED:
                if not auto_launch_var.get():
                    auto_launch_var.set(True)
                status_var.set("Managed mode will auto-start llama-server with the saved GGUF model when chatbot actions need it.")
            elif backend_mode_var.get() == CHATBOT_BACKEND_MODE_OLLAMA:
                if not server_url_var.get().strip() or server_url_var.get().strip().rstrip("/") == DEFAULT_CHATBOT_SERVER_URL:
                    server_url_var.set(DEFAULT_OLLAMA_SERVER_URL)
                detected_ollama_path = self._get_active_chatbot_server_executable_path(backend_mode=CHATBOT_BACKEND_MODE_OLLAMA)
                if detected_ollama_path and not server_executable_var.get().strip():
                    server_executable_var.set(detected_ollama_path)
                if not auto_launch_var.get():
                    auto_launch_var.set(True)
                status_var.set("Ollama mode will auto-start ollama serve and auto-register your local GGUF into Ollama when the chatbot needs it.")
            else:
                status_var.set("Connect mode expects you to run a local llama.cpp server separately and point Prompt2MTV at its URL.")

        backend_mode_var.trace_add("write", refresh_mode_hint)
        refresh_mode_hint()

        result = {"confirmed": False}

        def save_settings():
            sanitized_exec_path = self._sanitize_chatbot_server_executable_path(server_executable_var.get(), backend_mode=backend_mode_var.get())
            if backend_mode_var.get() == CHATBOT_BACKEND_MODE_MANAGED and server_executable_var.get().strip() and not sanitized_exec_path:
                messagebox.showerror("Chatbot Runtime", "Select a llama-server executable for managed mode. Ollama is not supported here.", parent=dialog)
                return
            if backend_mode_var.get() == CHATBOT_BACKEND_MODE_OLLAMA and server_executable_var.get().strip() and not sanitized_exec_path:
                messagebox.showerror("Chatbot Runtime", "Select ollama.exe for Ollama mode, or leave the field blank and let Prompt2MTV auto-detect it.", parent=dialog)
                return
            result.update({
                "confirmed": True,
                "model_family": model_family_var.get(),
                "gemma4_ollama_tag": gemma4_tag_var.get(),
                "backend_mode": backend_mode_var.get(),
                "server_url": server_url_var.get(),
                "server_executable_path": sanitized_exec_path,
                "context_size": context_size_var.get(),
                "request_timeout": timeout_var.get(),
                "temperature": temperature_var.get(),
                "top_p": top_p_var.get(),
                "top_k": top_k_var.get(),
                "min_p": min_p_var.get(),
                "repeat_penalty": repeat_penalty_var.get(),
                "default_to_non_thinking": non_thinking_var.get(),
                "auto_launch_server": auto_launch_var.get(),
            })
            dialog.destroy()

        footer = tk.Frame(shell)
        footer.pack(fill=tk.X, pady=(14, 0))
        self._style_panel(footer, self.colors["bg"])

        cancel_btn = tk.Button(footer, text="Cancel", command=dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT)
        self._style_button(cancel_btn, "secondary", compact=True)

        save_btn = tk.Button(footer, text="Save Runtime Settings", command=save_settings)
        save_btn.pack(side=tk.RIGHT, padx=(8, 0))
        self._style_button(save_btn, "primary", compact=True)

        dialog.bind("<Escape>", lambda _event: dialog.destroy())
        dialog.wait_visibility()
        dialog.focus_set()
        dialog.wait_window()
        return result

    def download_chatbot_model(self, destination_root=None, interactive=True):
        resolved_root = self._normalize_path(destination_root or self.chatbot_model_root or self._get_recommended_chatbot_model_root())
        if not resolved_root:
            if interactive:
                messagebox.showerror("Chatbot Runtime", "Prompt2MTV could not determine where to save the chatbot model.")
            return False

        os.makedirs(resolved_root, exist_ok=True)
        dest_path = os.path.join(resolved_root, self.chatbot_model_filename)
        expected_size = probe_download_size(self.chatbot_model_url)
        if expected_size is not None:
            free_bytes = shutil.disk_usage(resolved_root).free
            if free_bytes < expected_size:
                message = (
                    "Prompt2MTV does not have enough free disk space for the chatbot model download.\n\n"
                    f"Required: {self._format_byte_count(expected_size)}\n"
                    f"Available: {self._format_byte_count(free_bytes)}"
                )
                if interactive:
                    messagebox.showerror("Chatbot Runtime", message)
                self.update_status("Not enough free disk space for Qwen download.", "red")
                return False

        if interactive:
            lines = [
                f"Prompt2MTV will download {self.chatbot_model_filename}.",
                "",
                f"Source: {CHATBOT_MODEL_SOURCE_PAGE}",
                f"Destination: {dest_path}",
            ]
            if expected_size is not None:
                lines.append(f"Estimated size: {self._format_byte_count(expected_size)}")
            lines.extend(["", "Continue?"])
            if not messagebox.askyesno("Download Chatbot Model", "\n".join(lines)):
                self.update_status("Chatbot model download cancelled.", "orange")
                return False

        dialog_state = self._create_chatbot_download_dialog() if interactive else None
        self.chatbot_download_cancel_requested = False
        try:
            download_file(
                self.chatbot_model_url,
                dest_path,
                progress_callback=lambda downloaded_bytes, total_bytes, resumed: self._update_chatbot_download_dialog(
                    dialog_state,
                    downloaded_bytes,
                    total_bytes,
                    resumed,
                ),
                cancel_check=lambda: getattr(self, "chatbot_download_cancel_requested", False),
            )
        except DownloadCancelledError:
            self._close_chatbot_download_dialog(dialog_state)
            self.update_status("Chatbot model download cancelled.", "orange")
            return False
        except Exception as exc:
            self._close_chatbot_download_dialog(dialog_state)
            if os.path.exists(dest_path):
                try:
                    os.remove(dest_path)
                except OSError:
                    pass
            if interactive:
                messagebox.showerror("Chatbot Runtime", f"Failed to download chatbot model:\n{exc}")
            self.update_status("Failed to download Qwen chatbot model.", "red")
            return False

        self._close_chatbot_download_dialog(dialog_state)
        self._apply_chatbot_runtime_settings(model_root=resolved_root, model_path=dest_path)
        self.update_status("Chatbot model downloaded successfully.", "green")
        return True

    def ensure_chatbot_model_ready(self, interactive=True):
        if self._chatbot_model_is_ready() or self._chatbot_can_generate_without_local_model():
            self._refresh_chatbot_runtime_ui()
            return True

        if not interactive:
            self._refresh_chatbot_runtime_ui()
            return False

        setup_result = self._prompt_chatbot_model_destination()
        if not setup_result.get("confirmed"):
            self.chatbot_setup_prompted_this_session = True
            self._refresh_chatbot_runtime_ui()
            return False

        chosen_root = setup_result.get("model_root")
        chosen_path = self._normalize_path(setup_result.get("model_path")) or os.path.join(chosen_root, self.chatbot_model_filename)
        self._apply_chatbot_runtime_settings(
            model_root=chosen_root,
            model_path=chosen_path,
            preferred_drive=(os.path.splitdrive(chosen_root)[0] or self.chatbot_preferred_drive),
        )

        if os.path.exists(chosen_path):
            self.update_status("Chatbot model configured with an existing GGUF file.", "green")
            return True

        if setup_result.get("download"):
            return self.download_chatbot_model(chosen_root, interactive=True)

        messagebox.showwarning("Chatbot Model", "The selected GGUF file does not exist yet. Use Download Model to fetch it first.")
        self._refresh_chatbot_runtime_ui()
        return False

    def configure_chatbot_runtime(self):
        runtime_result = self._prompt_chatbot_runtime_configuration()
        if not runtime_result.get("confirmed"):
            return

        self._apply_chatbot_runtime_settings(
            model_family=runtime_result.get("model_family"),
            gemma4_ollama_tag=runtime_result.get("gemma4_ollama_tag"),
            backend_mode=runtime_result.get("backend_mode"),
            server_url=runtime_result.get("server_url"),
            server_executable_path=runtime_result.get("server_executable_path"),
            context_size=runtime_result.get("context_size"),
            request_timeout=runtime_result.get("request_timeout"),
            temperature=runtime_result.get("temperature"),
            top_p=runtime_result.get("top_p"),
            top_k=runtime_result.get("top_k"),
            min_p=runtime_result.get("min_p"),
            repeat_penalty=runtime_result.get("repeat_penalty"),
            default_to_non_thinking=runtime_result.get("default_to_non_thinking"),
            auto_launch_server=runtime_result.get("auto_launch_server"),
        )
        self.update_status("Advanced chatbot runtime settings updated.", "blue")

    def test_chatbot_runtime_connection(self):
        self._set_chatbot_backend_health_text("Backend check: Testing connection...")
        self.root.update_idletasks()
        if self.chatbot_backend_mode == CHATBOT_BACKEND_MODE_MANAGED:
            self._set_chatbot_backend_health_text("Backend check: Starting managed llama.cpp server...")
            self.root.update_idletasks()
        elif self.chatbot_backend_mode == CHATBOT_BACKEND_MODE_OLLAMA:
            self._set_chatbot_backend_health_text("Backend check: Starting Ollama and preparing the chatbot model...")
            self.root.update_idletasks()
        probe_result = self._ensure_chatbot_backend_ready_for_use(action_label="backend test")

        detail = probe_result.get("detail")
        if probe_result.get("ok"):
            self._set_chatbot_backend_health_text(f"Backend check: Online. {probe_result.get('status')}")
            self.update_status("Chatbot backend is reachable.", "green")
            messagebox.showinfo("Chatbot Backend", probe_result.get("status"))
            return

        summary = probe_result.get("status") or "Chatbot backend is not reachable."
        self._set_chatbot_backend_health_text(f"Backend check: Offline. {summary}")
        self.update_status("Chatbot backend is not reachable yet.", "orange")
        if detail:
            summary = f"{summary}\n\nDetails:\n{detail}"
        messagebox.showwarning("Chatbot Backend", summary)

    def prompt_and_download_chatbot_model(self):
        setup_result = self._prompt_chatbot_model_destination()
        if not setup_result.get("confirmed"):
            return False

        chosen_root = setup_result.get("model_root")
        chosen_path = self._normalize_path(setup_result.get("model_path")) or os.path.join(chosen_root, self.chatbot_model_filename)
        self._apply_chatbot_runtime_settings(
            model_root=chosen_root,
            model_path=chosen_path,
            preferred_drive=(os.path.splitdrive(chosen_root)[0] or self.chatbot_preferred_drive),
        )
        return self.download_chatbot_model(chosen_root, interactive=True)

    def _on_notebook_tab_changed(self, _event=None):
        try:
            selected_tab = self.notebook.select()
        except tk.TclError:
            return

        if selected_tab == str(self.chatbot_tab) and not self._chatbot_model_is_ready() and not self.chatbot_setup_prompted_this_session:
            self.chatbot_setup_prompted_this_session = True
            self.root.after(100, lambda: self.ensure_chatbot_model_ready(interactive=True))

    def _handle_chatbot_generate(self):
        self._handle_chatbot_structured_task(
            CHATBOT_TASK_T2I_OPTIMIZE,
            empty_message="Please enter a message first.",
            loading_text="Preparing a prompt draft from the local chatbot backend...",
            start_status="Prompt draft generation started.",
            success_status="Prompt draft generated.",
            failure_title="Failed to generate prompt draft",
            phase_key_base="chatbot_t2i_optimize",
        )

    def _get_default_output_dir(self):
        legacy_output_dir = os.path.join(self.app_root_dir, "outputs")
        if not getattr(sys, "frozen", False) and os.path.isdir(legacy_output_dir):
            return legacy_output_dir
        return os.path.join(self.user_data_dir, "outputs")

    def _has_supported_extension(self, path_value, supported_extensions):
        return os.path.splitext(str(path_value or ""))[1].lower() in supported_extensions

    def _is_supported_video_file(self, path_value):
        return self._has_supported_extension(path_value, SUPPORTED_VIDEO_EXTENSIONS)

    def _is_supported_audio_file(self, path_value):
        return self._has_supported_extension(path_value, SUPPORTED_AUDIO_EXTENSIONS)

    def _is_supported_image_file(self, path_value):
        return self._has_supported_extension(path_value, SUPPORTED_IMAGE_EXTENSIONS)

    def _generate_entity_id(self, prefix):
        return f"{prefix}_{uuid.uuid4().hex[:12]}"

    def _normalize_string_list(self, values):
        normalized_values = []
        for value in values or []:
            text_value = str(value or "").strip()
            if text_value:
                normalized_values.append(text_value)
        return normalized_values

    def _reindex_ordered_entries(self, entries, order_field="order_index"):
        normalized_entries = []
        for index, entry in enumerate(entries or [], start=1):
            if not isinstance(entry, dict):
                continue
            entry_copy = dict(entry)
            entry_copy[order_field] = index
            normalized_entries.append(entry_copy)
        return normalized_entries

    def _infer_image_source(self, image_path):
        normalized_image_path = self._normalize_path(image_path)
        if not normalized_image_path:
            return None

        normalized_imported_image_dir = self._normalize_path(self.imported_image_dir)
        normalized_generated_image_dir = self._normalize_path(self.generated_image_dir)

        if normalized_imported_image_dir and os.path.normcase(os.path.dirname(normalized_image_path)) == os.path.normcase(normalized_imported_image_dir):
            return "imported"
        if normalized_generated_image_dir and os.path.normcase(os.path.dirname(normalized_image_path)) == os.path.normcase(normalized_generated_image_dir):
            return "generated"
        return "linked"

    def _create_image_asset_record(self, project_path, source="generated", prompt_text="", original_path=None, asset_id=None, order_index=None, status="ready"):
        normalized_project_path = self._normalize_path(project_path)
        normalized_original_path = self._normalize_path(original_path)
        resolved_source = str(source or self._infer_image_source(normalized_project_path) or "generated").strip().lower()
        timestamp = datetime.now().isoformat(timespec="seconds")
        filename = os.path.basename(normalized_project_path) if normalized_project_path else ""
        fallback_label = os.path.splitext(filename)[0] if filename else ""
        return {
            "asset_id": str(asset_id or self._generate_entity_id("img")),
            "order_index": int(order_index or (len(self.image_assets) + 1)),
            "source": resolved_source,
            "label": fallback_label,
            "notes": "",
            "prompt_text": str(prompt_text or "").strip(),
            "project_path": normalized_project_path,
            "original_path": normalized_original_path,
            "filename": filename,
            "status": str(status or "ready").strip().lower(),
            "created_at": timestamp,
            "updated_at": timestamp
        }

    def _normalize_image_assets(self, image_assets):
        normalized_assets = []
        seen_paths = set()

        for index, asset in enumerate(image_assets or [], start=1):
            if not isinstance(asset, dict):
                continue

            project_path = self._normalize_path(asset.get("project_path") or asset.get("path"))
            if not project_path:
                continue

            normalized_key = os.path.normcase(project_path)
            if normalized_key in seen_paths:
                continue
            seen_paths.add(normalized_key)

            normalized_asset = self._create_image_asset_record(
                project_path,
                source=asset.get("source") or self._infer_image_source(project_path) or "generated",
                prompt_text=asset.get("prompt_text", ""),
                original_path=asset.get("original_path"),
                asset_id=asset.get("asset_id"),
                order_index=asset.get("order_index", index),
                status=asset.get("status", "ready")
            )
            normalized_asset["created_at"] = str(asset.get("created_at") or normalized_asset["created_at"])
            normalized_asset["updated_at"] = str(asset.get("updated_at") or normalized_asset["updated_at"])
            normalized_asset["label"] = str(asset.get("label") or normalized_asset.get("label") or "").strip()
            normalized_asset["notes"] = str(asset.get("notes") or "").strip()
            normalized_assets.append(normalized_asset)

        return self._reindex_ordered_entries(normalized_assets)

    def _upsert_image_asset(self, project_path, source="generated", prompt_text="", original_path=None, status="ready"):
        normalized_project_path = self._normalize_path(project_path)
        if not normalized_project_path:
            return None

        timestamp = datetime.now().isoformat(timespec="seconds")
        for asset in self.image_assets:
            if os.path.normcase(asset.get("project_path", "")) != os.path.normcase(normalized_project_path):
                continue
            asset["source"] = str(source or asset.get("source") or "generated").strip().lower()
            asset["filename"] = os.path.basename(normalized_project_path)
            asset["project_path"] = normalized_project_path
            asset["status"] = str(status or asset.get("status") or "ready").strip().lower()
            asset["updated_at"] = timestamp
            asset["label"] = str(asset.get("label") or os.path.splitext(asset["filename"])[0]).strip()
            asset["notes"] = str(asset.get("notes") or "").strip()
            if prompt_text:
                asset["prompt_text"] = str(prompt_text).strip()
            if original_path:
                asset["original_path"] = self._normalize_path(original_path)
            self.image_assets = self._reindex_ordered_entries(self.image_assets)
            return asset

        image_asset = self._create_image_asset_record(
            normalized_project_path,
            source=source,
            prompt_text=prompt_text,
            original_path=original_path,
            order_index=len(self.image_assets) + 1,
            status=status
        )
        self.image_assets.append(image_asset)
        self.image_assets = self._reindex_ordered_entries(self.image_assets)
        return image_asset

    def _get_image_asset_by_id(self, asset_id):
        normalized_asset_id = str(asset_id or "").strip()
        if not normalized_asset_id:
            return None

        for asset in self.image_assets:
            if str(asset.get("asset_id", "")).strip() == normalized_asset_id:
                return asset
        return None

    def _get_image_asset_by_path(self, image_path):
        normalized_image_path = self._normalize_path(image_path)
        if not normalized_image_path:
            return None

        for asset in self.image_assets:
            if os.path.normcase(asset.get("project_path", "")) == os.path.normcase(normalized_image_path):
                return asset
        return None

    def _get_image_asset_display_name(self, asset):
        if not isinstance(asset, dict):
            return "Unassigned"

        project_path = asset.get("project_path")
        filename = os.path.basename(project_path) if project_path else "Missing image"
        source = str(asset.get("source", "linked")).strip().title() or "Linked"
        order_index = int(asset.get("order_index") or 0)
        usage_map = self._get_image_asset_usage_map()
        usage_count = len(usage_map.get(str(asset.get("asset_id") or "").strip(), []))
        label = str(asset.get("label") or "").strip() or os.path.splitext(filename)[0]
        usage_text = f"used {usage_count}x" if usage_count else "unused"
        return f"{order_index:02d} | {source} | {usage_text} | {self._truncate_text(label, 32)}"

    def _get_scene_usage_snapshot(self):
        if hasattr(self, "scene_scrollable_frame") and self._collect_scene_entry_frames():
            return self._collect_scene_timeline_from_widgets()
        return self._normalize_scene_timeline(self.scene_timeline or [])

    def _get_image_asset_usage_map(self, scene_timeline=None):
        usage_map = {}
        normalized_scene_timeline = self._normalize_scene_timeline(scene_timeline if scene_timeline is not None else self._get_scene_usage_snapshot())
        for entry in normalized_scene_timeline:
            asset_id = str(entry.get("image_asset_id") or "").strip()
            if not asset_id:
                continue
            usage_map.setdefault(asset_id, []).append({
                "scene_id": str(entry.get("scene_id") or "").strip(),
                "order_index": int(entry.get("order_index") or 0),
                "mode": str(entry.get("mode") or "").strip().lower() or SCENE_MODE_T2V
            })
        return usage_map

    def _get_image_asset_scene_numbers(self, asset_id, scene_timeline=None):
        scene_numbers = []
        for usage in self._get_image_asset_usage_map(scene_timeline).get(str(asset_id or "").strip(), []):
            order_index = int(usage.get("order_index") or 0)
            if order_index > 0 and order_index not in scene_numbers:
                scene_numbers.append(order_index)
        return sorted(scene_numbers)

    def _get_assignable_image_assets(self, include_used=True, scene_timeline=None):
        usage_map = self._get_image_asset_usage_map(scene_timeline)
        assignable_assets = []
        for asset in self._normalize_image_assets(self.image_assets):
            project_path = self._normalize_path(asset.get("project_path"))
            if not project_path or not os.path.exists(project_path):
                continue
            asset_id = str(asset.get("asset_id") or "").strip()
            if not include_used and usage_map.get(asset_id):
                continue
            assignable_assets.append(asset)
        return assignable_assets

    def _build_scene_asset_summary_text(self, asset_id, scene_id=None, scene_timeline=None):
        normalized_asset_id = str(asset_id or "").strip()
        if not normalized_asset_id:
            return "No source image assigned."

        asset = self._get_image_asset_by_id(normalized_asset_id)
        if not asset:
            return "Assigned image record could not be found."

        project_path = self._normalize_path(asset.get("project_path"))
        filename = os.path.basename(project_path) if project_path else asset.get("filename") or "Missing image"
        if not project_path or not os.path.exists(project_path):
            return f"Assigned image missing: {filename}"

        usage_entries = self._get_image_asset_usage_map(scene_timeline).get(normalized_asset_id, [])
        linked_scene_numbers = [
            str(entry.get("order_index"))
            for entry in usage_entries
            if str(entry.get("scene_id") or "").strip() != str(scene_id or "").strip()
        ]
        source = str(asset.get("source") or "linked").strip().title() or "Linked"
        label = str(asset.get("label") or os.path.splitext(filename)[0]).strip() or filename
        usage_text = "Shared with scenes " + ", ".join(linked_scene_numbers) if linked_scene_numbers else "Only used in this scene"
        return f"{source} image: {self._truncate_text(label, 56)} | {usage_text}"

    def _refresh_scene_asset_summaries(self):
        scene_timeline = self._collect_scene_timeline_from_widgets() if hasattr(self, "scene_scrollable_frame") else self.scene_timeline
        for frame in self._collect_scene_entry_frames():
            if not hasattr(frame, "asset_summary_label"):
                continue
            frame.asset_summary_label.config(
                text=self._build_scene_asset_summary_text(
                    getattr(frame, "selected_asset_id", ""),
                    scene_id=getattr(frame, "scene_id", None),
                    scene_timeline=scene_timeline
                )
            )

    def auto_assign_i2v_scenes_by_asset_order(self):
        scene_timeline = self._collect_scene_timeline_from_widgets()
        i2v_scene_entries = [
            entry for entry in scene_timeline
            if entry.get("mode") == SCENE_MODE_I2V and not str(entry.get("image_asset_id") or "").strip()
        ]
        if not i2v_scene_entries:
            messagebox.showinfo("Scene Timeline", "There are no unassigned Image to Video scenes to auto-fill.")
            return

        available_assets = self._get_assignable_image_assets(include_used=False, scene_timeline=scene_timeline)
        if not available_assets:
            messagebox.showwarning("Scene Timeline", "No unused project images are available for auto-assignment.")
            return

        assigned_count = 0
        for scene_entry, asset in zip(i2v_scene_entries, available_assets):
            scene_entry["image_asset_id"] = str(asset.get("asset_id") or "").strip() or None
            assigned_count += 1

        if not assigned_count:
            messagebox.showwarning("Scene Timeline", "No image assignments were applied.")
            return

        self.scene_timeline = self._normalize_scene_timeline(scene_timeline)
        self._rebuild_scene_timeline_from_state(self.scene_timeline)
        self.save_project_state()
        self.refresh_gallery()

        remaining_count = len(i2v_scene_entries) - assigned_count
        status_message = f"Auto-assigned {assigned_count} image{'s' if assigned_count != 1 else ''} to I2V scenes by asset order."
        if remaining_count > 0:
            status_message += f" {remaining_count} scene{'s' if remaining_count != 1 else ''} still need images."
        self.update_status(status_message, "blue")

    def _snapshot_media_files(self, directory_path, extensions):
        normalized_directory = self._normalize_path(directory_path)
        if not normalized_directory or not os.path.isdir(normalized_directory):
            return set()

        return {
            os.path.join(normalized_directory, filename)
            for filename in os.listdir(normalized_directory)
            if filename.lower().endswith(tuple(extension.lower() for extension in extensions))
        }

    def _get_newest_rendered_media(self, before_files, directory_path, extensions):
        after_files = self._snapshot_media_files(directory_path, extensions)
        new_files = [path for path in after_files if path not in (before_files or set()) and os.path.exists(path)]
        if not new_files:
            return None
        return max(new_files, key=os.path.getmtime)

    def _create_scene_entry(self, order_index, mode=SCENE_MODE_T2V, prompt="", prompt_text="", image_asset_id=None, i2v_prompt_text="", scene_id=None, output_path=None, render_status="pending"):
        resolved_mode = str(mode or SCENE_MODE_T2V).strip().lower()
        if resolved_mode not in {SCENE_MODE_T2V, SCENE_MODE_I2V}:
            resolved_mode = SCENE_MODE_T2V
        canonical_prompt = str(prompt or "").strip()
        legacy_t2v_prompt = str(prompt_text or "").strip()
        legacy_i2v_prompt = str(i2v_prompt_text or "").strip()
        if not canonical_prompt:
            canonical_prompt = legacy_i2v_prompt or legacy_t2v_prompt if resolved_mode == SCENE_MODE_I2V else legacy_t2v_prompt or legacy_i2v_prompt
        timestamp = datetime.now().isoformat(timespec="seconds")
        return {
            "scene_id": str(scene_id or self._generate_entity_id("scene")),
            "order_index": int(order_index),
            "mode": resolved_mode,
            "prompt": canonical_prompt,
            "prompt_text": canonical_prompt,
            "image_asset_id": str(image_asset_id or "").strip() or None,
            "i2v_prompt_text": canonical_prompt,
            "output_path": self._normalize_path(output_path),
            "render_status": str(render_status or "pending").strip().lower(),
            "updated_at": timestamp
        }

    def _get_scene_prompt_text(self, scene_entry):
        if not isinstance(scene_entry, dict):
            return ""

        prompt_text = str(scene_entry.get("prompt") or "").strip()
        if prompt_text:
            return prompt_text

        mode_value = str(scene_entry.get("mode") or SCENE_MODE_T2V).strip().lower()
        legacy_t2v_prompt = str(scene_entry.get("prompt_text") or "").strip()
        legacy_i2v_prompt = str(scene_entry.get("i2v_prompt_text") or "").strip()
        if mode_value == SCENE_MODE_I2V and legacy_i2v_prompt:
            return legacy_i2v_prompt
        return legacy_t2v_prompt or legacy_i2v_prompt

    def _build_scene_timeline_from_prompts(self, prompts_text):
        normalized_prompts = self._normalize_string_list(prompts_text)
        return [
            self._create_scene_entry(index, mode=SCENE_MODE_T2V, prompt=prompt_text)
            for index, prompt_text in enumerate(normalized_prompts, start=1)
        ]

    def _normalize_scene_timeline(self, scene_timeline, fallback_prompts=None):
        normalized_timeline = []
        for index, entry in enumerate(scene_timeline or [], start=1):
            if not isinstance(entry, dict):
                continue
            normalized_timeline.append(
                self._create_scene_entry(
                    entry.get("order_index", index),
                    mode=entry.get("mode", SCENE_MODE_T2V),
                    prompt=entry.get("prompt", ""),
                    prompt_text=entry.get("prompt_text", ""),
                    image_asset_id=entry.get("image_asset_id"),
                    i2v_prompt_text=entry.get("i2v_prompt_text", ""),
                    scene_id=entry.get("scene_id"),
                    output_path=entry.get("output_path"),
                    render_status=entry.get("render_status", "pending")
                )
            )

        if not normalized_timeline:
            normalized_timeline = self._build_scene_timeline_from_prompts(fallback_prompts or [])

        return self._reindex_ordered_entries(normalized_timeline)

    def _sync_scene_timeline_with_prompts(self, prompts_text):
        normalized_prompts = self._normalize_string_list(prompts_text)
        if not self.scene_timeline:
            return self._build_scene_timeline_from_prompts(normalized_prompts)

        synchronized_timeline = []
        prompt_index = 0
        for entry in self._normalize_scene_timeline(self.scene_timeline):
            if entry.get("mode") == SCENE_MODE_T2V:
                if prompt_index >= len(normalized_prompts):
                    continue
                entry["prompt"] = normalized_prompts[prompt_index]
                entry["prompt_text"] = normalized_prompts[prompt_index]
                entry["i2v_prompt_text"] = normalized_prompts[prompt_index]
                prompt_index += 1
            synchronized_timeline.append(entry)

        while prompt_index < len(normalized_prompts):
            synchronized_timeline.append(
                self._create_scene_entry(
                    len(synchronized_timeline) + 1,
                    mode=SCENE_MODE_T2V,
                    prompt=normalized_prompts[prompt_index]
                )
            )
            prompt_index += 1

        return self._reindex_ordered_entries(synchronized_timeline)

    def _get_t2v_prompts_from_scene_timeline(self, scene_timeline=None):
        prompts_text = []
        for entry in self._normalize_scene_timeline(scene_timeline or self.scene_timeline or []):
            if entry.get("mode") != SCENE_MODE_T2V:
                continue
            prompt_text = self._get_scene_prompt_text(entry)
            if prompt_text:
                prompts_text.append(prompt_text)
        return prompts_text

    def _build_image_prompt_queue_from_scene_timeline(self, scene_timeline=None):
        labeled_prompts = []
        for entry in self._normalize_scene_timeline(scene_timeline or self.scene_timeline or []):
            if entry.get("mode") != SCENE_MODE_T2V:
                continue
            prompt_text = self._get_scene_prompt_text(entry)
            if not prompt_text:
                continue
            scene_number = int(entry.get("order_index") or (len(labeled_prompts) + 1))
            labeled_prompts.append(f"Scene {scene_number:02d}\n\n{prompt_text}")
        return labeled_prompts

    def _parse_image_prompt_queue_entry(self, prompt_text):
        raw_text = str(prompt_text or "").strip()
        parsed_entry = {
            "raw_text": raw_text,
            "prompt_text": raw_text,
            "scene_order": None,
            "has_scene_label": False,
            "label_was_malformed": False
        }

        if not raw_text:
            return parsed_entry

        lines = raw_text.splitlines()
        first_line = lines[0].strip()
        label_match = re.match(r"^scene\s+(\d+)(?:\s*[:\-]\s*)?$", first_line, flags=re.IGNORECASE)
        if not label_match:
            if first_line.lower().startswith("scene"):
                parsed_entry["label_was_malformed"] = True
            return parsed_entry

        parsed_entry["scene_order"] = int(label_match.group(1))
        parsed_entry["has_scene_label"] = True
        parsed_entry["prompt_text"] = "\n".join(lines[1:]).strip()
        return parsed_entry

    def _update_scene_entry_prompt(self, scene_entry, prompt_text):
        updated_entry = dict(scene_entry or {})
        normalized_prompt = str(prompt_text or "").strip()
        updated_entry["prompt"] = normalized_prompt
        updated_entry["prompt_text"] = normalized_prompt
        updated_entry["i2v_prompt_text"] = normalized_prompt
        updated_entry["updated_at"] = datetime.now().isoformat(timespec="seconds")
        return updated_entry

    def _insert_scene_entry_at_order(self, scene_timeline, scene_entry, target_order):
        insert_index = len(scene_timeline)
        for index, existing_entry in enumerate(scene_timeline):
            existing_order = int(existing_entry.get("order_index") or 0)
            if existing_order >= int(target_order or 0):
                insert_index = index
                break
        scene_timeline.insert(insert_index, scene_entry)

    def _apply_image_prompts_to_scene_timeline(self, scene_timeline, prompts_text):
        updated_timeline = self._normalize_scene_timeline(scene_timeline or [])
        parsed_prompts = [
            self._parse_image_prompt_queue_entry(prompt_text)
            for prompt_text in self._normalize_string_list(prompts_text)
        ]
        labeled_prompts = [entry for entry in parsed_prompts if entry.get("has_scene_label") and entry.get("prompt_text")]
        unlabeled_prompts = [entry for entry in parsed_prompts if not entry.get("has_scene_label") and entry.get("prompt_text")]
        touched_scene_ids = set()
        sync_summary = {
            "updated": 0,
            "created": 0,
            "preserved_i2v": len([entry for entry in updated_timeline if entry.get("mode") == SCENE_MODE_I2V]),
            "malformed_labels": len([entry for entry in parsed_prompts if entry.get("label_was_malformed")]),
            "labeled": len(labeled_prompts),
            "unlabeled": len(unlabeled_prompts)
        }

        for parsed_entry in labeled_prompts:
            matching_index = next(
                (
                    index for index, existing_entry in enumerate(updated_timeline)
                    if existing_entry.get("mode") == SCENE_MODE_T2V
                    and int(existing_entry.get("order_index") or 0) == int(parsed_entry["scene_order"])
                ),
                None
            )
            if matching_index is not None:
                existing_entry = updated_timeline[matching_index]
                updated_timeline[matching_index] = self._update_scene_entry_prompt(existing_entry, parsed_entry["prompt_text"])
                touched_scene_ids.add(existing_entry.get("scene_id"))
                sync_summary["updated"] += 1
                continue

            created_entry = self._create_scene_entry(
                parsed_entry["scene_order"],
                mode=SCENE_MODE_T2V,
                prompt=parsed_entry["prompt_text"]
            )
            self._insert_scene_entry_at_order(updated_timeline, created_entry, parsed_entry["scene_order"])
            touched_scene_ids.add(created_entry.get("scene_id"))
            sync_summary["created"] += 1

        available_t2v_indices = [
            index for index, existing_entry in enumerate(updated_timeline)
            if existing_entry.get("mode") == SCENE_MODE_T2V
            and existing_entry.get("scene_id") not in touched_scene_ids
        ]

        for parsed_entry in unlabeled_prompts:
            if available_t2v_indices:
                matching_index = available_t2v_indices.pop(0)
                existing_entry = updated_timeline[matching_index]
                updated_timeline[matching_index] = self._update_scene_entry_prompt(existing_entry, parsed_entry["prompt_text"])
                touched_scene_ids.add(existing_entry.get("scene_id"))
                sync_summary["updated"] += 1
                continue

            created_entry = self._create_scene_entry(
                len(updated_timeline) + 1,
                mode=SCENE_MODE_T2V,
                prompt=parsed_entry["prompt_text"]
            )
            updated_timeline.append(created_entry)
            touched_scene_ids.add(created_entry.get("scene_id"))
            sync_summary["created"] += 1

        return self._reindex_ordered_entries(updated_timeline), sync_summary

    def _build_unique_media_copy_path(self, destination_dir, source_path):
        filename = os.path.basename(source_path)
        name_root, extension = os.path.splitext(filename)
        candidate_path = os.path.join(destination_dir, filename)
        source_normalized = self._normalize_path(source_path)

        if os.path.exists(candidate_path):
            try:
                if source_normalized and os.path.samefile(source_normalized, candidate_path):
                    return candidate_path
            except OSError:
                pass

        suffix = 1
        while os.path.exists(candidate_path):
            candidate_path = os.path.join(destination_dir, f"{name_root}_{suffix}{extension}")
            suffix += 1
        return candidate_path

    def _copy_media_file_to_project(self, source_path, destination_dir):
        normalized_source = self._normalize_path(source_path)
        if not normalized_source or not os.path.isfile(normalized_source):
            raise FileNotFoundError(f"File not found: {source_path}")

        os.makedirs(destination_dir, exist_ok=True)
        destination_path = self._build_unique_media_copy_path(destination_dir, normalized_source)
        if os.path.normcase(normalized_source) != os.path.normcase(destination_path):
            shutil.copy2(normalized_source, destination_path)
        return destination_path

    def _infer_audio_source(self, audio_path):
        normalized_audio_path = self._normalize_path(audio_path)
        if not normalized_audio_path:
            return None

        normalized_imported_audio_dir = self._normalize_path(self.imported_audio_dir)
        normalized_generated_audio_dir = self._normalize_path(self.audio_dir)

        if normalized_imported_audio_dir and os.path.normcase(os.path.dirname(normalized_audio_path)) == os.path.normcase(normalized_imported_audio_dir):
            return "imported"
        if normalized_generated_audio_dir and os.path.normcase(os.path.dirname(normalized_audio_path)) == os.path.normcase(normalized_generated_audio_dir):
            return "generated"
        return "linked"

    def _format_audio_state(self):
        if not self.current_generated_audio or not os.path.exists(self.current_generated_audio):
            return "No audio linked"

        audio_source = self.current_audio_source or self._infer_audio_source(self.current_generated_audio)
        source_label = {
            "generated": "Generated",
            "imported": "Imported",
            "linked": "Linked"
        }.get(audio_source, "Linked")
        return f"{source_label}: {os.path.basename(self.current_generated_audio)}"

    def _parse_drop_file_list(self, raw_drop_data):
        if not raw_drop_data:
            return []

        try:
            candidates = self.root.tk.splitlist(raw_drop_data)
        except tk.TclError:
            candidates = [raw_drop_data]

        parsed_paths = []
        for candidate in candidates:
            normalized_candidate = self._normalize_path(candidate)
            if normalized_candidate:
                parsed_paths.append(normalized_candidate)
        return parsed_paths

    def _register_drop_target(self, widget, handler):
        if not self.drag_drop_enabled:
            return

        try:
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<DropEnter>>", lambda _event: COPY)
            widget.dnd_bind("<<DropPosition>>", lambda _event: COPY)
            widget.dnd_bind("<<Drop>>", handler)
        except Exception as exc:
            self.drag_drop_enabled = False
            self.log_debug("DRAG_DROP_DISABLED", reason=str(exc))

    def _enable_drag_and_drop(self):
        if not self.drag_drop_enabled:
            return

        gallery_targets = [
            self.gallery_header_frame,
            self.gallery_shell_frame,
            self.gallery_canvas,
            self.gallery_inner_frame
        ]
        music_targets = [
            self.music_actions_section["container"],
            self.music_actions_card,
            self.music_action_frame,
            self.music_primary_actions_frame,
            self.music_right_frame
        ]

        for widget in gallery_targets:
            self._register_drop_target(widget, self._handle_gallery_drop)
        for widget in music_targets:
            self._register_drop_target(widget, self._handle_audio_drop)

    def _handle_gallery_drop(self, event):
        dropped_paths = self._parse_drop_file_list(getattr(event, "data", ""))
        imported_videos = self.import_video_files(dropped_paths, from_drop=True)
        imported_images = self.import_image_files(dropped_paths, from_drop=True)
        return COPY if imported_videos or imported_images else ""

    def _handle_audio_drop(self, event):
        imported_path = self.import_audio_files(self._parse_drop_file_list(getattr(event, "data", "")), from_drop=True)
        return COPY if imported_path else ""

    def import_images_dialog(self):
        selected_paths = filedialog.askopenfilenames(
            title="Import Images",
            initialdir=self.current_project_dir or self.base_output_dir,
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.webp *.bmp"),
                ("All files", "*.*")
            ]
        )
        self.import_image_files(selected_paths)

    def import_videos_dialog(self):
        selected_paths = filedialog.askopenfilenames(
            title="Import Video Clips",
            initialdir=self.current_project_dir or self.base_output_dir,
            filetypes=[
                ("Video files", "*.mp4 *.mov *.mkv *.avi *.webm *.m4v"),
                ("All files", "*.*")
            ]
        )
        self.import_video_files(selected_paths)

    def import_audio_dialog(self):
        selected_path = filedialog.askopenfilename(
            title="Import Music / Audio",
            initialdir=self.current_project_dir or self.base_output_dir,
            filetypes=[
                ("Audio files", "*.mp3 *.wav *.flac *.m4a *.aac *.ogg"),
                ("All files", "*.*")
            ]
        )
        if selected_path:
            self.import_audio_files([selected_path])

    def import_image_files(self, file_paths, from_drop=False):
        if not self.current_project_dir or not self.imported_image_dir:
            messagebox.showwarning("Warning", "Open or create a project before importing images.")
            return []

        imported_paths = []
        skipped_paths = []
        failed_imports = []

        for source_path in file_paths or []:
            if not self._is_supported_image_file(source_path):
                skipped_paths.append(source_path)
                continue
            try:
                copied_path = self._copy_media_file_to_project(source_path, self.imported_image_dir)
                self._upsert_image_asset(copied_path, source="imported", original_path=source_path, status="ready")
                imported_paths.append(copied_path)
            except Exception as exc:
                failed_imports.append(f"{os.path.basename(str(source_path))}: {exc}")

        if imported_paths:
            self.save_project_state()
            self.update_status(f"Imported {len(imported_paths)} image{'s' if len(imported_paths) != 1 else ''}.", "green")

        if failed_imports:
            messagebox.showerror("Image Import Error", "\n".join(failed_imports[:5]))
        elif skipped_paths and not from_drop:
            messagebox.showwarning(
                "Unsupported Files",
                "Only common image formats are supported for import.\n\nSkipped:\n" + "\n".join(os.path.basename(str(path)) for path in skipped_paths[:5])
            )
        elif skipped_paths:
            self.update_status("Ignored dropped files that were not recognized as images.", "orange")

        return imported_paths

    def import_video_files(self, file_paths, from_drop=False):
        if not self.current_project_dir or not self.imported_video_dir:
            messagebox.showwarning("Warning", "Open or create a project before importing videos.")
            return []

        imported_paths = []
        skipped_paths = []
        failed_imports = []

        for source_path in file_paths or []:
            if not self._is_supported_video_file(source_path):
                skipped_paths.append(source_path)
                continue
            try:
                imported_paths.append(self._copy_media_file_to_project(source_path, self.imported_video_dir))
            except Exception as exc:
                failed_imports.append(f"{os.path.basename(str(source_path))}: {exc}")

        if imported_paths:
            self.refresh_gallery()
            self.save_project_state()
            self.update_status(f"Imported {len(imported_paths)} video clip{'s' if len(imported_paths) != 1 else ''}.", "green")

        if failed_imports:
            messagebox.showerror("Video Import Error", "\n".join(failed_imports[:5]))
        elif skipped_paths and not from_drop:
            messagebox.showwarning(
                "Unsupported Files",
                "Only common video formats are supported for import.\n\nSkipped:\n" + "\n".join(os.path.basename(str(path)) for path in skipped_paths[:5])
            )
        elif skipped_paths:
            self.update_status("Ignored dropped files that were not recognized as video clips.", "orange")

        return imported_paths

    def import_audio_files(self, file_paths, from_drop=False):
        if not self.current_project_dir or not self.imported_audio_dir:
            messagebox.showwarning("Warning", "Open or create a project before importing audio.")
            return None

        imported_audio_path = None
        skipped_paths = []
        failed_imports = []

        for source_path in file_paths or []:
            if not self._is_supported_audio_file(source_path):
                skipped_paths.append(source_path)
                continue
            try:
                imported_audio_path = self._copy_media_file_to_project(source_path, self.imported_audio_dir)
                break
            except Exception as exc:
                failed_imports.append(f"{os.path.basename(str(source_path))}: {exc}")

        if imported_audio_path:
            self.current_generated_audio = imported_audio_path
            self.current_audio_source = "imported"
            self.preview_music_btn.config(state=tk.NORMAL)
            if self.selected_video_for_music:
                self.merge_music_btn.config(state=tk.NORMAL)
            self._refresh_music_sidebar_state()
            self.save_project_state()
            self.update_music_status(f"Imported audio ready: {os.path.basename(imported_audio_path)}", "green")

            if len(file_paths or []) > 1 and from_drop:
                self.update_music_status(f"Imported audio ready: {os.path.basename(imported_audio_path)} (first supported file used)", "green")
        elif failed_imports:
            messagebox.showerror("Audio Import Error", "\n".join(failed_imports[:5]))
        elif skipped_paths and not from_drop:
            messagebox.showwarning(
                "Unsupported Files",
                "Only common audio formats are supported for import.\n\nSkipped:\n" + "\n".join(os.path.basename(str(path)) for path in skipped_paths[:5])
            )
        elif skipped_paths:
            self.update_music_status("Ignored dropped files that were not recognized as audio.", "orange")

        return imported_audio_path

    def _get_env_value(self, keys):
        for key in keys:
            value = self._normalize_path(os.environ.get(key))
            if value:
                return value
        return None

    def _get_candidate_comfyui_roots(self, preferred_root=None):
        candidates = []
        self._append_unique_path(candidates, preferred_root)
        self._append_unique_path(candidates, self._get_env_value(ENV_COMFYUI_ROOT_KEYS))

        launcher_env = self._normalize_path(os.environ.get(ENV_COMFYUI_LAUNCHER_KEY))
        if launcher_env:
            self._append_unique_path(candidates, os.path.dirname(launcher_env))

        for default_root in DEFAULT_COMFYUI_ROOT_CANDIDATES:
            self._append_unique_path(candidates, default_root)

        return [candidate for candidate in candidates if os.path.isdir(candidate)]

    def _discover_comfyui_root(self, preferred_root=None):
        candidates = self._get_candidate_comfyui_roots(preferred_root)
        return candidates[0] if candidates else None

    def _discover_comfyui_launcher(self, preferred_path=None, comfyui_root=None):
        candidates = []
        self._append_unique_path(candidates, preferred_path)
        self._append_unique_path(candidates, os.environ.get(ENV_COMFYUI_LAUNCHER_KEY))

        for root in self._get_candidate_comfyui_roots(comfyui_root):
            for launcher_name in DEFAULT_COMFYUI_LAUNCHER_NAMES:
                self._append_unique_path(candidates, os.path.join(root, launcher_name))
                self._append_unique_path(candidates, os.path.join(os.path.dirname(root), launcher_name))

        for candidate in candidates:
            if os.path.isfile(candidate):
                return candidate
        return None

    def _find_window_handle_for_pid(self, process_id):
        if sys.platform != "win32" or not process_id:
            return None

        console_handles = []
        user32 = ctypes.windll.user32
        callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        def enum_callback(hwnd, _lparam):
            pid = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if pid.value == process_id and user32.IsWindow(hwnd):
                class_name_buffer = ctypes.create_unicode_buffer(256)
                user32.GetClassNameW(hwnd, class_name_buffer, len(class_name_buffer))
                if class_name_buffer.value == "ConsoleWindowClass":
                    console_handles.append(hwnd)
            return True

        user32.EnumWindows(callback_type(enum_callback), 0)
        if console_handles:
            return console_handles[0]
        return None

    def _find_window_handle_for_title(self, window_title):
        if sys.platform != "win32" or not window_title:
            return None

        user32 = ctypes.windll.user32
        hwnd = user32.FindWindowW("ConsoleWindowClass", window_title)
        if not hwnd:
            hwnd = user32.FindWindowW(None, window_title)
        return hwnd if hwnd and user32.IsWindow(hwnd) else None

    def _find_window_handle_for_title_prefix(self, title_prefix):
        if sys.platform != "win32" or not title_prefix:
            return None

        matching_handles = []
        user32 = ctypes.windll.user32
        callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        def enum_callback(hwnd, _lparam):
            if not user32.IsWindow(hwnd):
                return True

            class_name_buffer = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, class_name_buffer, len(class_name_buffer))
            if class_name_buffer.value != "ConsoleWindowClass":
                return True

            title_buffer = ctypes.create_unicode_buffer(512)
            user32.GetWindowTextW(hwnd, title_buffer, len(title_buffer))
            if title_buffer.value.startswith(title_prefix):
                matching_handles.append(hwnd)
                return False
            return True

        user32.EnumWindows(callback_type(enum_callback), 0)
        return matching_handles[0] if matching_handles else None

    def _get_comfyui_console_title_prefix(self):
        return f"{APP_NAME} ComfyUI"

    def _recover_app_owned_comfyui_console(self):
        if sys.platform != "win32":
            return None

        hwnd = self._find_window_handle_for_title(self.comfyui_console_title)
        if not hwnd:
            hwnd = self._find_window_handle_for_title_prefix(self._get_comfyui_console_title_prefix())
        if not hwnd:
            return None

        title_buffer = ctypes.create_unicode_buffer(512)
        ctypes.windll.user32.GetWindowTextW(hwnd, title_buffer, len(title_buffer))
        recovered_title = title_buffer.value or None
        self.comfyui_console_hwnd = hwnd
        if recovered_title:
            self.comfyui_console_title = recovered_title
        self.log_debug(
            "COMFYUI_CONSOLE_WINDOW_RECOVERED",
            hwnd=hwnd,
            console_title=self.comfyui_console_title,
            process_owned=bool(self.comfyui_process and self.comfyui_process.poll() is None)
        )
        return hwnd

    def _cancel_comfyui_console_poll(self):
        if not self.comfyui_console_poll_after_id:
            return

        try:
            self.root.after_cancel(self.comfyui_console_poll_after_id)
        except Exception:
            pass
        self.comfyui_console_poll_after_id = None

    def _queue_comfyui_console_visibility(self, visible, attempts=24, delay_ms=250, source="unknown"):
        if sys.platform != "win32":
            return False
        if not (self.comfyui_process and self.comfyui_process.poll() is None):
            return False

        self.comfyui_console_pending_visibility = bool(visible)
        self._cancel_comfyui_console_poll()
        self.log_debug(
            "COMFYUI_CONSOLE_VISIBILITY_QUEUED",
            visible=self.comfyui_console_pending_visibility,
            attempts=attempts,
            delay_ms=delay_ms,
            source=source,
            pid=self.comfyui_process.pid,
            console_title=self.comfyui_console_title
        )
        self.comfyui_console_poll_after_id = self.root.after(
            delay_ms,
            lambda: self._poll_comfyui_console_window(attempts=attempts, delay_ms=delay_ms, source=source)
        )
        return True

    def _poll_comfyui_console_window(self, attempts=24, delay_ms=250, source="unknown"):
        self.comfyui_console_poll_after_id = None
        if sys.platform != "win32":
            return

        process_running = bool(self.comfyui_process and self.comfyui_process.poll() is None)
        if not process_running:
            self.comfyui_console_hwnd = None
            self.comfyui_console_pending_visibility = None
            self._refresh_comfyui_terminal_button()
            return

        hwnd = self._resolve_comfyui_console_window()
        if hwnd:
            self.log_debug(
                "COMFYUI_CONSOLE_WINDOW_FOUND",
                hwnd=hwnd,
                source=source,
                pid=self.comfyui_process.pid,
                console_title=self.comfyui_console_title
            )
            desired_visibility = self.comfyui_console_pending_visibility
            if desired_visibility is not None:
                if self._set_comfyui_terminal_visibility(desired_visibility, retry_on_missing=False):
                    self.comfyui_console_pending_visibility = None
            self._refresh_comfyui_terminal_button()
            return

        if attempts > 1:
            self.comfyui_console_poll_after_id = self.root.after(
                delay_ms,
                lambda: self._poll_comfyui_console_window(attempts=attempts - 1, delay_ms=delay_ms, source=source)
            )
            return

        self.log_debug(
            "COMFYUI_CONSOLE_WINDOW_NOT_FOUND",
            source=source,
            pid=self.comfyui_process.pid,
            console_title=self.comfyui_console_title
        )
        self._refresh_comfyui_terminal_button()

    def _resolve_comfyui_console_window(self):
        if sys.platform != "win32":
            return None

        if self.comfyui_console_hwnd:
            try:
                if ctypes.windll.user32.IsWindow(self.comfyui_console_hwnd):
                    return self.comfyui_console_hwnd
            except Exception:
                pass

        if self.comfyui_process and self.comfyui_process.poll() is None:
            self.comfyui_console_hwnd = self._find_window_handle_for_title(self.comfyui_console_title)
            if not self.comfyui_console_hwnd:
                self.comfyui_console_hwnd = self._find_window_handle_for_title_prefix(self._get_comfyui_console_title_prefix())
            if not self.comfyui_console_hwnd:
                self.comfyui_console_hwnd = self._find_window_handle_for_pid(self.comfyui_process.pid)
            if self.comfyui_console_hwnd:
                title_buffer = ctypes.create_unicode_buffer(512)
                ctypes.windll.user32.GetWindowTextW(self.comfyui_console_hwnd, title_buffer, len(title_buffer))
                if title_buffer.value:
                    self.comfyui_console_title = title_buffer.value
                self.log_debug(
                    "COMFYUI_CONSOLE_WINDOW_RESOLVED",
                    hwnd=self.comfyui_console_hwnd,
                    pid=self.comfyui_process.pid,
                    console_title=self.comfyui_console_title
                )
        elif self._is_comfyui_running():
            self.comfyui_console_hwnd = self._recover_app_owned_comfyui_console()
        else:
            self.comfyui_console_hwnd = None
            self.comfyui_console_title = None
            self.comfyui_console_pending_visibility = None
        return self.comfyui_console_hwnd

    def _set_comfyui_terminal_visibility(self, visible, retry_on_missing=True):
        if sys.platform != "win32":
            return False

        hwnd = self._resolve_comfyui_console_window()
        if not hwnd and retry_on_missing and self.comfyui_process and self.comfyui_process.poll() is None:
            self.comfyui_console_hwnd = None
            hwnd = self._resolve_comfyui_console_window()
        if not hwnd:
            return False

        try:
            user32 = ctypes.windll.user32
            user32.ShowWindow(hwnd, WINDOWS_RESTORE if visible else WINDOWS_HIDE)
            if visible:
                try:
                    user32.BringWindowToTop(hwnd)
                    user32.SetForegroundWindow(hwnd)
                except Exception:
                    pass
            self.comfyui_console_visible = bool(visible)
            self.comfyui_console_pending_visibility = None
            self.log_debug(
                "COMFYUI_CONSOLE_VISIBILITY_SET",
                hwnd=hwnd,
                visible=self.comfyui_console_visible,
                pid=self.comfyui_process.pid if self.comfyui_process else None,
                console_title=self.comfyui_console_title
            )
            self._refresh_comfyui_terminal_button()
            return True
        except Exception:
            return False

    def _refresh_comfyui_terminal_button(self):
        process_running = bool(self.comfyui_process and self.comfyui_process.poll() is None)
        console_available = bool(process_running)
        if sys.platform == "win32" and not console_available and self._is_comfyui_running():
            console_available = bool(self._resolve_comfyui_console_window())

        if not console_available:
            self.comfyui_console_hwnd = None
            self.comfyui_console_visible = False
            self.comfyui_console_title = None
        elif self.comfyui_console_hwnd and sys.platform == "win32":
            try:
                user32 = ctypes.windll.user32
                self.comfyui_console_visible = bool(user32.IsWindowVisible(self.comfyui_console_hwnd) and not user32.IsIconic(self.comfyui_console_hwnd))
            except Exception:
                pass

        button_state = tk.NORMAL if console_available and sys.platform == "win32" else tk.DISABLED
        button_text = "Hide ComfyUI Terminal" if self.comfyui_console_visible else "Show ComfyUI Terminal"
        if hasattr(self, "toggle_comfyui_terminal_btn"):
            self.toggle_comfyui_terminal_btn.config(text=button_text, state=button_state)
        if hasattr(self, "help_menu") and hasattr(self, "help_menu_toggle_terminal_index"):
            self.help_menu.entryconfig(self.help_menu_toggle_terminal_index, label=button_text, state=button_state)

    def toggle_comfyui_terminal(self):
        target_visibility = not self.comfyui_console_visible
        if not self._set_comfyui_terminal_visibility(target_visibility):
            if self._queue_comfyui_console_visibility(target_visibility, source="toggle"):
                self.update_status("ComfyUI terminal is still initializing; requested visibility will apply when it becomes available.", "orange")
                self._refresh_comfyui_terminal_button()
                return
            self.update_status("ComfyUI terminal window is not available to toggle.", "orange")
            self._refresh_comfyui_terminal_button()
            return

        self.update_status("ComfyUI terminal shown." if target_visibility else "ComfyUI terminal hidden.", "blue")

    def _resolve_model_search_roots(self, saved_roots=None, comfyui_root=None):
        configured_roots = []
        if isinstance(saved_roots, list):
            for saved_root in saved_roots:
                self._append_unique_path(configured_roots, saved_root)

        env_model_roots = os.environ.get(ENV_MODEL_ROOTS_KEY)
        if env_model_roots:
            for env_root in env_model_roots.split(os.pathsep):
                self._append_unique_path(configured_roots, env_root)

        for root in self._get_candidate_comfyui_roots(comfyui_root):
            self._append_unique_path(configured_roots, os.path.join(root, "models"))
            if os.path.basename(root).lower() != "comfyui":
                self._append_unique_path(configured_roots, os.path.join(root, "ComfyUI", "models"))

        return configured_roots

    def _candidate_resource_paths(self, relative_path):
        if not relative_path:
            return []

        candidate_paths = []
        normalized_relative = str(relative_path).strip()
        if os.path.isabs(normalized_relative):
            self._append_unique_path(candidate_paths, normalized_relative)
            return candidate_paths

        for base_dir in [self.app_root_dir, self.resource_root_dir]:
            self._append_unique_path(candidate_paths, os.path.join(base_dir, normalized_relative))
        return candidate_paths

    def _resolve_resource_path(self, relative_path):
        candidate_paths = self._candidate_resource_paths(relative_path)
        for candidate in candidate_paths:
            if candidate and os.path.exists(candidate):
                return candidate
        return candidate_paths[0] if candidate_paths else None

    def _load_model_manifest(self):
        manifest_payload = {"version": 1, "models": []}
        resolved_manifest_path = self._resolve_resource_path(MODEL_MANIFEST_FILE)
        if resolved_manifest_path:
            self.model_manifest_path = resolved_manifest_path

        if resolved_manifest_path and os.path.exists(resolved_manifest_path):
            try:
                with open(resolved_manifest_path, 'r', encoding='utf-8') as manifest_file:
                    loaded_manifest = json.load(manifest_file)
                if isinstance(loaded_manifest, dict) and isinstance(loaded_manifest.get("models"), list):
                    manifest_payload = loaded_manifest
                else:
                    print(f"Invalid model manifest structure: {resolved_manifest_path}")
            except Exception as exc:
                print(f"Error loading model manifest: {exc}")

        self.model_manifest = manifest_payload
        return self.model_manifest

    def _get_workflow_payload_for_models(self, workflow_key):
        if workflow_key == "video":
            return self.workflow
        if workflow_key == "image":
            return self.image_workflow
        if workflow_key == "music":
            return self.music_workflow
        return None

    def _get_workflow_label_for_models(self, workflow_key):
        return WORKFLOW_MODEL_LABELS.get(workflow_key, str(workflow_key or "workflow").title())

    def _get_workflow_node_input_value(self, workflow_payload, node_id, input_name):
        if not workflow_payload:
            return ""
        node_data = workflow_payload.get(str(node_id), {})
        value = node_data.get("inputs", {}).get(input_name, "")
        if isinstance(value, list):
            return ""
        return "" if value is None else str(value).strip()

    def _resolve_manifest_entry_filename(self, entry):
        workflow_key = str(entry.get("workflow", "")).strip().lower()
        workflow_payload = self._get_workflow_payload_for_models(workflow_key)
        observed_values = []
        notes = []

        for node_ref in entry.get("node_refs", []):
            node_id = node_ref.get("node_id")
            input_name = node_ref.get("input")
            if not node_id or not input_name:
                continue
            observed_value = self._get_workflow_node_input_value(workflow_payload, node_id, input_name)
            if observed_value:
                observed_values.append(observed_value)

        manifest_filename = str(entry.get("filename", "")).strip()
        active_filename = observed_values[0] if observed_values else manifest_filename

        unique_observed_values = sorted(set(observed_values), key=str.lower)
        if len(unique_observed_values) > 1:
            notes.append(
                f"{entry.get('label', entry.get('id', 'Model'))}: workflow node references disagree on filename ({', '.join(unique_observed_values)})."
            )
        if manifest_filename and observed_values and any(value != manifest_filename for value in observed_values):
            notes.append(
                f"{entry.get('label', entry.get('id', 'Model'))}: manifest filename differs from workflow JSON value ({manifest_filename} vs {active_filename})."
            )

        return active_filename, notes

    def _resolve_manifest_local_source(self, entry, filename):
        candidate_paths = []
        for source in entry.get("sources", []):
            if str(source.get("type", "")).strip().lower() != "local":
                continue
            relative_path = source.get("relative_path")
            if relative_path:
                for candidate in self._candidate_resource_paths(relative_path):
                    self._append_unique_path(candidate_paths, candidate)

        dest_subdir = str(entry.get("dest_subdir", "")).strip()
        if filename and dest_subdir:
            default_relative_path = os.path.join(BUNDLED_MODEL_DIR, dest_subdir, filename)
            for candidate in self._candidate_resource_paths(default_relative_path):
                self._append_unique_path(candidate_paths, candidate)

        for candidate in candidate_paths:
            if candidate and os.path.exists(candidate):
                return candidate
        return None

    def _resolve_manifest_download_url(self, entry):
        for source in entry.get("sources", []):
            if str(source.get("type", "")).strip().lower() != "download":
                continue
            url = str(source.get("url", "")).strip()
            if url:
                return url

        direct_url = str(entry.get("download_url", "")).strip()
        return direct_url or None

    def _get_manifest_source_name(self, entry):
        source_name = str(entry.get("source_name", "")).strip()
        if source_name:
            return source_name

        for source in entry.get("sources", []):
            if str(source.get("type", "")).strip().lower() != "download":
                continue
            source_name = str(source.get("source_name", "")).strip()
            if source_name:
                return source_name
        return "Direct download"

    def _get_manifest_source_page_url(self, entry):
        source_page_url = str(entry.get("source_page_url", "")).strip()
        if source_page_url:
            return source_page_url

        for source in entry.get("sources", []):
            if str(source.get("type", "")).strip().lower() != "download":
                continue
            source_page_url = str(source.get("source_page_url", "")).strip()
            if source_page_url:
                return source_page_url
        return None

    def _get_manifest_size_bytes(self, entry):
        raw_value = entry.get("size_bytes")
        if raw_value is None:
            return None

        try:
            parsed_value = int(raw_value)
        except (TypeError, ValueError):
            return None
        return parsed_value if parsed_value >= 0 else None

    def _get_manifest_sha256(self, entry):
        raw_value = str(entry.get("sha256", "")).strip().lower()
        if len(raw_value) != 64:
            return None
        if not all(character in "0123456789abcdef" for character in raw_value):
            return None
        return raw_value

    def _get_preferred_model_root(self, create_if_missing=False):
        candidate_roots = []
        normalized_comfyui_root = self._normalize_path(self.comfyui_root)

        if normalized_comfyui_root:
            root_name = os.path.basename(os.path.normpath(normalized_comfyui_root)).lower()
            if root_name == "comfyui":
                self._append_unique_path(candidate_roots, os.path.join(normalized_comfyui_root, "models"))
            else:
                self._append_unique_path(candidate_roots, os.path.join(normalized_comfyui_root, "ComfyUI", "models"))
                self._append_unique_path(candidate_roots, os.path.join(normalized_comfyui_root, "models"))

        for configured_root in self.model_search_roots:
            self._append_unique_path(candidate_roots, configured_root)

        for candidate in candidate_roots:
            if os.path.isdir(candidate):
                return candidate

        if candidate_roots:
            if create_if_missing:
                os.makedirs(candidate_roots[0], exist_ok=True)
            return candidate_roots[0]
        return None

    def audit_required_models(self, include_variant_ids=None):
        self._load_model_manifest()

        reports = []
        manifest_notes = []

        active_music_manifest_id = None
        if hasattr(self, "music_model_variant_var"):
            active_music_manifest_id = self._get_active_music_manifest_id()

        for entry in self.model_manifest.get("models", []):
            if entry.get("required", True) is False:
                continue

            entry_id = str(entry.get("id", "")).strip() or "unknown_model"

            variant_group = entry.get("variant_group")
            if variant_group and variant_group == "music_dit":
                if include_variant_ids is not None:
                    if entry_id not in include_variant_ids:
                        continue
                elif active_music_manifest_id and entry_id != active_music_manifest_id:
                    continue

            workflow_key = str(entry.get("workflow", "")).strip().lower()
            label = str(entry.get("label", entry_id)).strip() or entry_id
            dest_subdir = str(entry.get("dest_subdir", "")).strip().replace("/", os.sep).replace("\\", os.sep)
            filename, entry_notes = self._resolve_manifest_entry_filename(entry)
            manifest_notes.extend(entry_notes)

            if not workflow_key or not filename or not dest_subdir:
                manifest_notes.append(
                    f"Model manifest entry '{entry_id}' is missing workflow, filename, or destination folder."
                )
                continue

            resolved_path = self._find_model_file(filename)
            local_source_path = None
            download_url = None
            install_method = None
            if not resolved_path:
                local_source_path = self._resolve_manifest_local_source(entry, filename)
                download_url = self._resolve_manifest_download_url(entry)
                if local_source_path:
                    install_method = "copy"
                elif download_url:
                    install_method = "download"

            destination_root = self._get_preferred_model_root(create_if_missing=False)
            destination_path = os.path.join(destination_root, dest_subdir, filename) if destination_root else None

            reports.append({
                "id": entry_id,
                "workflow": workflow_key,
                "workflow_label": self._get_workflow_label_for_models(workflow_key),
                "label": label,
                "filename": filename,
                "dest_subdir": dest_subdir,
                "resolved_path": resolved_path,
                "destination_path": destination_path,
                "source_path": local_source_path,
                "source_name": self._get_manifest_source_name(entry),
                "source_page_url": self._get_manifest_source_page_url(entry),
                "size_bytes": self._get_manifest_size_bytes(entry),
                "sha256": self._get_manifest_sha256(entry),
                "download_url": download_url,
                "install_method": install_method,
            })

        missing_reports = [report for report in reports if not report["resolved_path"]]
        installable_missing = [report for report in missing_reports if report["install_method"]]
        blocked_missing = [report for report in missing_reports if not report["install_method"]]

        audit = {
            "reports": reports,
            "missing": missing_reports,
            "installable_missing": installable_missing,
            "blocked_missing": blocked_missing,
            "manifest_notes": sorted(set(note for note in manifest_notes if note)),
        }
        self.last_model_audit = audit
        return audit

    def _format_missing_model_lines(self, model_audit):
        lines = []
        for report in model_audit.get("missing", []):
            install_hint = report.get("install_method") or "manual"
            source_text = f", {report['source_name']}" if report.get("source_name") else ""
            lines.append(
                f"- {report['workflow_label']} | {report['label']}: {report['filename']} -> {report['dest_subdir']} ({install_hint}{source_text})"
            )
        return lines

    def _update_model_install_controls(self, model_audit=None):
        audit = model_audit or self.last_model_audit or {"installable_missing": []}
        installable_count = len(audit.get("installable_missing", []))
        button_state = tk.NORMAL if installable_count else tk.DISABLED

        if hasattr(self, "install_models_btn"):
            label_text = f"Install Missing Models ({installable_count})" if installable_count else "Install Missing Models"
            self.install_models_btn.config(text=label_text, state=button_state)

    def _format_byte_count(self, byte_count):
        if byte_count is None:
            return "unknown"

        units = ["B", "KB", "MB", "GB", "TB"]
        size_value = float(byte_count)
        unit_index = 0

        while size_value >= 1024 and unit_index < len(units) - 1:
            size_value /= 1024
            unit_index += 1

        if unit_index == 0:
            return f"{int(size_value)} {units[unit_index]}"
        return f"{size_value:.1f} {units[unit_index]}"

    def _estimate_download_sizes(self, reports):
        total_known_bytes = 0
        unknown_count = 0

        for report in reports:
            if report.get("install_method") != "download":
                continue

            size_bytes = report.get("size_bytes")
            if size_bytes is None and report.get("download_url"):
                size_bytes = probe_download_size(report["download_url"])
                report["size_bytes"] = size_bytes

            if size_bytes is None:
                unknown_count += 1
                continue

            total_known_bytes += size_bytes

        return total_known_bytes, unknown_count

    def _check_download_disk_space(self, destination_root, reports):
        known_total_bytes, unknown_size_count = self._estimate_download_sizes(reports)
        if known_total_bytes <= 0:
            return {
                "ok": True,
                "required_bytes": known_total_bytes,
                "free_bytes": None,
                "unknown_size_count": unknown_size_count,
            }

        free_bytes = shutil.disk_usage(destination_root).free
        return {
            "ok": free_bytes >= known_total_bytes,
            "required_bytes": known_total_bytes,
            "free_bytes": free_bytes,
            "unknown_size_count": unknown_size_count,
        }

    def _create_model_download_dialog(self, total_models):
        dialog = tk.Toplevel(self.root)
        dialog.title("Downloading Models")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.geometry("560x220")
        dialog.minsize(520, 200)
        self._style_panel(dialog, self.colors["bg"])

        shell = tk.Frame(dialog, padx=20, pady=18)
        shell.pack(fill=tk.BOTH, expand=True)
        self._style_panel(shell, self.colors["bg"])

        title_label = tk.Label(shell, text="Downloading Missing Models")
        title_label.pack(anchor="w")
        self._style_label(title_label, "title", self.colors["bg"])

        summary_var = tk.StringVar(value=f"Preparing to install {total_models} model(s)...")
        summary_label = tk.Label(shell, textvariable=summary_var, justify=tk.LEFT, anchor="w", wraplength=500)
        summary_label.pack(fill=tk.X, pady=(8, 6))
        self._style_label(summary_label, "body", self.colors["bg"])

        detail_var = tk.StringVar(value="Waiting for download to start...")
        detail_label = tk.Label(shell, textvariable=detail_var, justify=tk.LEFT, anchor="w", wraplength=500)
        detail_label.pack(fill=tk.X, pady=(0, 10))
        self._style_label(detail_label, "muted", self.colors["bg"])

        progress_bar = ttk.Progressbar(shell, mode="determinate", maximum=100)
        progress_bar.pack(fill=tk.X)

        progress_var = tk.StringVar(value="0%")
        progress_label = tk.Label(shell, textvariable=progress_var, anchor="e")
        progress_label.pack(fill=tk.X, pady=(6, 10))
        self._style_label(progress_label, "small", self.colors["bg"])

        footer = tk.Frame(shell)
        footer.pack(fill=tk.X, pady=(8, 0))
        self._style_panel(footer, self.colors["bg"])

        cancel_button = tk.Button(footer, text="Cancel", command=lambda: setattr(self, "model_download_cancel_requested", True))
        cancel_button.pack(side=tk.RIGHT)
        self._style_button(cancel_button, "secondary", compact=True)

        def handle_dialog_close():
            self.model_download_cancel_requested = True

        dialog.protocol("WM_DELETE_WINDOW", handle_dialog_close)

        return {
            "dialog": dialog,
            "summary_var": summary_var,
            "detail_var": detail_var,
            "progress_var": progress_var,
            "progress_bar": progress_bar,
            "indeterminate": False,
        }

    def _update_model_download_dialog(self, dialog_state, report, index, total_models, downloaded_bytes=None, total_bytes=None, resumed=False):
        if not dialog_state:
            return

        dialog = dialog_state["dialog"]
        if not dialog.winfo_exists():
            return

        dialog_state["summary_var"].set(
            f"Downloading {index} of {total_models}: {report['label']}"
        )

        source_name = report.get("source_name") or "Direct download"
        if total_bytes is None:
            detail_text = f"{report['filename']} from {source_name} | {self._format_byte_count(downloaded_bytes)} downloaded"
            if not dialog_state["indeterminate"]:
                dialog_state["progress_bar"].configure(mode="indeterminate")
                dialog_state["progress_bar"].start(12)
                dialog_state["indeterminate"] = True
            dialog_state["progress_var"].set("Downloading...")
        else:
            if dialog_state["indeterminate"]:
                dialog_state["progress_bar"].stop()
                dialog_state["progress_bar"].configure(mode="determinate")
                dialog_state["indeterminate"] = False

            completion_ratio = 0 if total_bytes <= 0 else min(1.0, downloaded_bytes / total_bytes)
            dialog_state["progress_bar"]["value"] = completion_ratio * 100
            dialog_state["progress_var"].set(f"{completion_ratio * 100:.1f}%")
            detail_text = (
                f"{report['filename']} from {source_name} | "
                f"{self._format_byte_count(downloaded_bytes)} of {self._format_byte_count(total_bytes)}"
            )

        if resumed:
            detail_text = f"{detail_text} | resuming partial download"

        dialog_state["detail_var"].set(detail_text)

        try:
            dialog.update()
        except tk.TclError:
            pass

    def _close_model_download_dialog(self, dialog_state):
        if not dialog_state:
            return

        dialog = dialog_state.get("dialog")
        if not dialog:
            return

        try:
            if dialog_state.get("indeterminate"):
                dialog_state["progress_bar"].stop()
            if dialog.winfo_exists():
                dialog.destroy()
        except tk.TclError:
            pass

    def _ask_music_variant_choice(self):
        """Show a dialog asking which music model variant(s) to include for download.
        Returns a list of manifest IDs, or None if cancelled."""
        self._load_model_manifest()
        variant_entries = [
            e for e in self.model_manifest.get("models", [])
            if e.get("variant_group") == "music_dit"
        ]
        if len(variant_entries) < 2:
            return None

        already_present = []
        not_present = []
        for e in variant_entries:
            entry_id = str(e.get("id", "")).strip()
            filename = str(e.get("filename", "")).strip()
            if self._find_model_file(filename):
                already_present.append(entry_id)
            else:
                not_present.append(entry_id)

        if not not_present:
            return None

        labels = {str(e.get("id", "")).strip(): str(e.get("label", e.get("id", ""))).strip() for e in variant_entries}

        dialog = tk.Toplevel(self.root)
        dialog.title("Music Model Selection")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.transient(self.root)

        frame = tk.Frame(dialog, padx=20, pady=16)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Which music model(s) would you like to download?", wraplength=350, justify=tk.LEFT).pack(anchor="w", pady=(0, 12))

        selected_ids = {}
        for e in variant_entries:
            entry_id = str(e.get("id", "")).strip()
            is_present = entry_id in already_present
            var = tk.BooleanVar(value=not is_present)
            suffix = " (already installed)" if is_present else ""
            cb = tk.Checkbutton(frame, text=f"{labels.get(entry_id, entry_id)}{suffix}", variable=var)
            cb.pack(anchor="w", pady=2)
            if is_present:
                cb.config(state=tk.DISABLED)
                var.set(False)
            selected_ids[entry_id] = var

        result = {"ids": None}

        def on_ok():
            chosen = [eid for eid, var in selected_ids.items() if var.get()]
            chosen.extend(already_present)
            result["ids"] = chosen if chosen else None
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(16, 0))
        tk.Button(btn_frame, text="Continue", width=10, command=on_ok).pack(side=tk.RIGHT, padx=(8, 0))
        tk.Button(btn_frame, text="Cancel", width=10, command=on_cancel).pack(side=tk.RIGHT)

        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        dialog.wait_window()
        return result["ids"]

    def install_missing_models(self, interactive=True, model_audit=None):
        include_variant_ids = None
        if interactive and model_audit is None:
            include_variant_ids = self._ask_music_variant_choice()
            if include_variant_ids is not None and not include_variant_ids:
                self.update_status("Model installation cancelled.", "orange")
                return False

        audit = model_audit or self.audit_required_models(include_variant_ids=include_variant_ids)
        missing_reports = audit.get("missing", [])
        installable_reports = audit.get("installable_missing", [])
        known_total_bytes, unknown_size_count = self._estimate_download_sizes(installable_reports)

        if not missing_reports:
            self._update_model_install_controls(audit)
            if interactive:
                messagebox.showinfo("Model Installer", "All required workflow models are already present.")
            self.update_status("All required workflow models are already present.", "green")
            return True

        if not installable_reports:
            self._update_model_install_controls(audit)
            guidance = [
                "Prompt2MTV found missing workflow models, but none are currently installable automatically.",
                f"Update {os.path.basename(self.model_manifest_path)} with valid direct download URLs or source-page metadata."
            ]
            if interactive:
                messagebox.showwarning("Model Installer", "\n\n".join(guidance))
            self.update_status("Missing models require manual sources or download URLs.", "orange")
            return False

        if interactive:
            preview_lines = self._format_missing_model_lines({"missing": installable_reports})
            size_summary = f"Estimated download size: {self._format_byte_count(known_total_bytes)}"
            if unknown_size_count:
                size_summary = f"{size_summary} + {unknown_size_count} file(s) with unknown size"
            prompt_text = [
                f"Prompt2MTV can install {len(installable_reports)} missing workflow model(s) into your ComfyUI model folders.",
                "",
                size_summary,
                "",
                *preview_lines,
                "",
                "The app will download each file directly from the configured source and place it into the matching ComfyUI models subfolder.",
                "",
                "Continue?"
            ]
            if not messagebox.askyesno("Install Missing Models", "\n".join(prompt_text)):
                self.update_status("Missing model installation was cancelled.", "orange")
                return False

        destination_root = self._get_preferred_model_root(create_if_missing=True)
        if not destination_root:
            message = "Prompt2MTV cannot determine where your ComfyUI models folder lives. Configure runtime paths first."
            if interactive:
                messagebox.showerror("Model Installer", message)
            self.update_status(message, "red")
            return False

        disk_check = self._check_download_disk_space(destination_root, installable_reports)
        if not disk_check["ok"]:
            message = (
                "Prompt2MTV does not have enough free disk space for the missing model downloads.\n\n"
                f"Required: {self._format_byte_count(disk_check['required_bytes'])}\n"
                f"Available: {self._format_byte_count(disk_check['free_bytes'])}"
            )
            if disk_check["unknown_size_count"]:
                message = (
                    f"{message}\n"
                    f"Additional files with unknown size: {disk_check['unknown_size_count']}"
                )
            if interactive:
                messagebox.showerror("Model Installer", message)
            self.update_status("Not enough free disk space for model download.", "red")
            return False

        installed_reports = []
        failed_reports = []
        cancelled_install = False
        dialog_state = None
        self.model_download_cancel_requested = False

        if interactive:
            dialog_state = self._create_model_download_dialog(len(installable_reports))

        for index, report in enumerate(installable_reports, start=1):
            dest_dir = os.path.join(destination_root, report["dest_subdir"])
            dest_path = os.path.join(dest_dir, report["filename"])
            self.update_status(
                f"Installing model {index}/{len(installable_reports)}: {report['filename']}",
                "blue"
            )

            try:
                os.makedirs(dest_dir, exist_ok=True)
                if report["install_method"] == "copy":
                    self._update_model_download_dialog(dialog_state, report, index, len(installable_reports), 0, None, False)
                    shutil.copy2(report["source_path"], dest_path)
                elif report["install_method"] == "download":
                    download_file(
                        report["download_url"],
                        dest_path,
                        progress_callback=lambda downloaded_bytes, total_bytes, resumed, report_ref=report, index_ref=index: self._update_model_download_dialog(
                            dialog_state,
                            report_ref,
                            index_ref,
                            len(installable_reports),
                            downloaded_bytes,
                            total_bytes,
                            resumed,
                        ),
                        cancel_check=lambda: getattr(self, "model_download_cancel_requested", False),
                    )
                else:
                    raise RuntimeError("No supported installation method is available for this model.")

                expected_sha256 = report.get("sha256")
                if expected_sha256:
                    self.update_status(f"Verifying model {index}/{len(installable_reports)}: {report['filename']}", "blue")
                    actual_sha256 = calculate_sha256(dest_path)
                    if actual_sha256.lower() != expected_sha256.lower():
                        raise RuntimeError(
                            f"SHA-256 mismatch for {report['filename']} (expected {expected_sha256}, got {actual_sha256})"
                        )

                installed_reports.append(report)
            except DownloadCancelledError:
                cancelled_install = True
                break
            except Exception as exc:
                if os.path.exists(dest_path):
                    try:
                        os.remove(dest_path)
                    except OSError:
                        pass
                failed_reports.append((report, str(exc)))

        self._close_model_download_dialog(dialog_state)

        if cancelled_install:
            self.update_status("Model download cancelled.", "orange")
            if interactive:
                messagebox.showwarning("Model Installer", "Model download was cancelled. Partial downloads were kept so a later retry can resume where supported.")

        self.model_search_roots = self._resolve_model_search_roots(self.model_search_roots, self.comfyui_root)
        self.refresh_video_model_choices()
        self.refresh_image_model_choices()
        refreshed_audit = self.audit_required_models()
        self._update_model_install_controls(refreshed_audit)
        self.save_global_settings()
        self.run_startup_preflight(interactive=False)

        summary_lines = []
        if installed_reports:
            summary_lines.append(f"Installed {len(installed_reports)} model(s) into {destination_root}.")
        if cancelled_install:
            summary_lines.append("Download cancelled before all requested models were installed.")
        if failed_reports:
            summary_lines.append("")
            summary_lines.append("Failed installs:")
            summary_lines.extend([f"- {report['filename']}: {error_text}" for report, error_text in failed_reports])

        if cancelled_install and not failed_reports:
            return False

        if failed_reports:
            if interactive:
                messagebox.showwarning("Model Installer", "\n".join(summary_lines))
            self.update_status("Some workflow models failed to install.", "orange")
            return False

        success_text = "\n".join(summary_lines) if summary_lines else "Required workflow models were installed successfully."
        if interactive:
            messagebox.showinfo("Model Installer", success_text)
        self.update_status("Required workflow models installed successfully.", "green")
        return True

    def _read_global_settings_payload(self):
        for settings_path in [self.global_settings_file, self.legacy_global_settings_file]:
            if not os.path.exists(settings_path):
                continue
            with open(settings_path, 'r', encoding='utf-8') as file_handle:
                return json.load(file_handle), settings_path
        return {}, None

    def _is_ffmpeg_available(self):
        if not FFMPEG_PATH:
            return False
        if os.path.isabs(FFMPEG_PATH):
            return os.path.exists(FFMPEG_PATH)
        return shutil.which(FFMPEG_PATH) is not None

    def _is_comfyui_running(self):
        try:
            req = urllib.request.Request("http://127.0.0.1:8188/system_stats")
            urllib.request.urlopen(req, timeout=1)
            return True
        except Exception:
            return False

    def _sync_runtime_paths(self, settings):
        self.base_output_dir = self._normalize_path(settings.get("output_root")) or self.base_output_dir or self._get_default_output_dir()
        os.makedirs(self.base_output_dir, exist_ok=True)
        self.comfyui_root = self._discover_comfyui_root(settings.get("comfyui_root"))
        self.comfyui_launcher_path = self._discover_comfyui_launcher(settings.get("comfyui_launcher_path"), self.comfyui_root)
        self.model_search_roots = self._resolve_model_search_roots(settings.get("model_search_roots"), self.comfyui_root)

    def _prompt_for_comfyui_root(self):
        selected_dir = filedialog.askdirectory(
            title="Select ComfyUI Folder",
            initialdir=self.comfyui_root or self.app_root_dir
        )
        if selected_dir:
            self.comfyui_root = self._normalize_path(selected_dir)
            self.comfyui_launcher_path = self._discover_comfyui_launcher(self.comfyui_launcher_path, self.comfyui_root)
            self.model_search_roots = self._resolve_model_search_roots(self.model_search_roots, self.comfyui_root)
            self.save_global_settings()
            return True
        return False

    def _prompt_for_comfyui_launcher(self):
        filepath = filedialog.askopenfilename(
            title="Select ComfyUI Launcher Batch File",
            initialdir=self.comfyui_root or self.app_root_dir,
            filetypes=(("Batch files", "*.bat"), ("All files", "*.*"))
        )
        if filepath:
            self.comfyui_launcher_path = self._normalize_path(filepath)
            self.save_global_settings()
            return True
        return False

    def _paths_to_multiline_text(self, paths):
        return "\n".join(paths or [])

    def _parse_multiline_paths(self, text_value):
        parsed_paths = []
        for raw_line in str(text_value).splitlines():
            self._append_unique_path(parsed_paths, raw_line)
        return parsed_paths

    def _browse_directory_into_var(self, tk_var, title, fallback_dir=None):
        initialdir = self._normalize_path(tk_var.get()) or fallback_dir or self.app_root_dir
        selected_dir = filedialog.askdirectory(title=title, initialdir=initialdir)
        if selected_dir:
            tk_var.set(self._normalize_path(selected_dir) or "")

    def _browse_file_into_var(self, tk_var, title, filetypes, fallback_dir=None):
        initialdir = fallback_dir or self.app_root_dir
        current_value = self._normalize_path(tk_var.get())
        if current_value:
            initialdir = os.path.dirname(current_value) if os.path.isfile(current_value) else current_value
        selected_path = filedialog.askopenfilename(title=title, initialdir=initialdir, filetypes=filetypes)
        if selected_path:
            tk_var.set(self._normalize_path(selected_path) or "")

    def _apply_runtime_path_settings(self, comfyui_root, launcher_path, output_root, model_roots, remember_section_open_states=None):
        resolved_root = self._normalize_path(comfyui_root)
        resolved_output_root = self._normalize_path(output_root) or self._get_default_output_dir()
        resolved_model_roots = self._resolve_model_search_roots(model_roots, resolved_root)

        self.base_output_dir = resolved_output_root
        os.makedirs(self.base_output_dir, exist_ok=True)
        self.comfyui_root = self._discover_comfyui_root(resolved_root) or resolved_root
        self.comfyui_launcher_path = self._discover_comfyui_launcher(launcher_path, self.comfyui_root)
        self.model_search_roots = resolved_model_roots
        if remember_section_open_states is not None:
            self.remember_section_open_states = bool(remember_section_open_states)

        self.save_global_settings()
        self.refresh_video_model_choices()
        self.refresh_image_model_choices()
        self.run_startup_preflight(interactive=False)

    def configure_runtime_paths(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Runtime Paths")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.geometry("760x620")
        dialog.minsize(700, 560)
        self._style_panel(dialog, self.colors["bg"])

        shell = tk.Frame(dialog, padx=18, pady=18)
        shell.pack(fill=tk.BOTH, expand=True)
        self._style_panel(shell, self.colors["bg"])

        header = tk.Label(shell, text="Runtime Paths")
        header.pack(anchor="w")
        self._style_label(header, "title", self.colors["bg"])

        subheader = tk.Label(
            shell,
            text="Configure the local ComfyUI installation, launcher batch file, writable output folder, and optional model search roots."
        )
        subheader.pack(anchor="w", pady=(6, 14))
        self._style_label(subheader, "muted", self.colors["bg"])

        form = tk.Frame(shell, padx=14, pady=14)
        form.pack(fill=tk.BOTH, expand=True)
        self._style_panel(form, self.colors["surface"], border=True)
        form.grid_columnconfigure(0, weight=0)
        form.grid_columnconfigure(1, weight=1)
        form.grid_columnconfigure(2, weight=0)

        comfyui_root_var = tk.StringVar(value=self.comfyui_root or "")
        launcher_var = tk.StringVar(value=self.comfyui_launcher_path or "")
        output_root_var = tk.StringVar(value=self.base_output_dir or self._get_default_output_dir())

        row_index = 0

        def add_path_row(label_text, variable, browse_command):
            nonlocal row_index
            label = tk.Label(form, text=label_text)
            label.grid(row=row_index, column=0, sticky="nw", padx=(0, 12), pady=(0, 10))
            self._style_label(label, "body_strong", self.colors["surface"])

            entry = tk.Entry(form, textvariable=variable)
            entry.grid(row=row_index, column=1, sticky="ew", pady=(0, 10))
            self._style_text_input(entry)

            browse_btn = tk.Button(form, text="Browse", command=browse_command)
            browse_btn.grid(row=row_index, column=2, sticky="e", padx=(8, 0), pady=(0, 10))
            self._style_button(browse_btn, "secondary", compact=True)
            row_index += 1

        add_path_row(
            "ComfyUI folder",
            comfyui_root_var,
            lambda: self._browse_directory_into_var(comfyui_root_var, "Select ComfyUI Folder", self.comfyui_root or self.app_root_dir)
        )
        add_path_row(
            "Launcher batch file",
            launcher_var,
            lambda: self._browse_file_into_var(
                launcher_var,
                "Select ComfyUI Launcher Batch File",
                (("Batch files", "*.bat"), ("All files", "*.*")),
                comfyui_root_var.get() or self.app_root_dir
            )
        )
        add_path_row(
            "Output folder",
            output_root_var,
            lambda: self._browse_directory_into_var(output_root_var, "Select Prompt2MTV Output Folder", self.base_output_dir or self.app_root_dir)
        )

        model_roots_label = tk.Label(form, text="Model search roots")
        model_roots_label.grid(row=row_index, column=0, sticky="nw", padx=(0, 12), pady=(2, 6))
        self._style_label(model_roots_label, "body_strong", self.colors["surface"])

        model_roots_frame = tk.Frame(form)
        model_roots_frame.grid(row=row_index, column=1, columnspan=2, sticky="nsew", pady=(0, 8))
        form.grid_rowconfigure(row_index, weight=1)
        self._style_panel(model_roots_frame, self.colors["surface"])

        model_roots_help = tk.Label(
            model_roots_frame,
            text="One path per line. Leave blank to rely on auto-detected ComfyUI model folders."
        )
        model_roots_help.pack(anchor="w", pady=(0, 6))
        self._style_label(model_roots_help, "muted", self.colors["surface"])

        model_roots_text = tk.Text(model_roots_frame, height=8, wrap="word")
        model_roots_text.pack(fill=tk.BOTH, expand=True)
        self._style_text_input(model_roots_text, multiline=True)
        model_roots_text.insert("1.0", self._paths_to_multiline_text(self.model_search_roots))
        row_index += 1

        remember_sections_var = tk.BooleanVar(value=bool(self.remember_section_open_states))
        remember_sections_frame = tk.Frame(form)
        remember_sections_frame.grid(row=row_index, column=0, columnspan=3, sticky="ew", pady=(4, 0))
        self._style_panel(remember_sections_frame, self.colors["surface"])

        remember_sections_cb = tk.Checkbutton(
            remember_sections_frame,
            text="Remember open sections for each project on launch",
            variable=remember_sections_var,
        )
        remember_sections_cb.pack(anchor="w")
        self._style_checkbutton(remember_sections_cb, self.colors["surface"])

        remember_sections_help = tk.Label(
            remember_sections_frame,
            text="When off, every tab launches collapsed. When on, Prompt2MTV restores the last open/closed section state saved in the current project.",
            anchor="w",
            justify=tk.LEFT,
            wraplength=620,
        )
        remember_sections_help.pack(anchor="w", pady=(4, 0))
        self._style_label(remember_sections_help, "muted", self.colors["surface"])
        row_index += 1

        footer = tk.Frame(shell)
        footer.pack(fill=tk.X, pady=(14, 0))
        self._style_panel(footer, self.colors["bg"])

        status_var = tk.StringVar(value=f"Settings are saved to {self.global_settings_file}")
        status_label = tk.Label(footer, textvariable=status_var, anchor="w", justify=tk.LEFT)
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))
        self._style_label(status_label, "muted", self.colors["bg"])

        def fill_detected_defaults():
            detected_root = self._discover_comfyui_root(comfyui_root_var.get()) or comfyui_root_var.get()
            detected_launcher = self._discover_comfyui_launcher(launcher_var.get(), detected_root) or launcher_var.get()
            detected_model_roots = self._resolve_model_search_roots([], detected_root)

            comfyui_root_var.set(detected_root or "")
            launcher_var.set(detected_launcher or "")
            if detected_model_roots:
                model_roots_text.delete("1.0", tk.END)
                model_roots_text.insert("1.0", self._paths_to_multiline_text(detected_model_roots))
            status_var.set("Detected runtime defaults have been loaded into the form.")

        def save_runtime_settings():
            try:
                parsed_model_roots = self._parse_multiline_paths(model_roots_text.get("1.0", tk.END))
                self._apply_runtime_path_settings(
                    comfyui_root_var.get(),
                    launcher_var.get(),
                    output_root_var.get(),
                    parsed_model_roots,
                    remember_section_open_states=remember_sections_var.get(),
                )
            except Exception as exc:
                messagebox.showerror("Runtime Paths", f"Failed to save runtime paths:\n{exc}", parent=dialog)
                return

            status_var.set("Runtime paths saved.")
            self.update_status("Runtime paths updated.", "green")
            dialog.destroy()

        detect_btn = tk.Button(footer, text="Auto-Detect", command=fill_detected_defaults)
        detect_btn.pack(side=tk.RIGHT, padx=(8, 0))
        self._style_button(detect_btn, "ghost", compact=True)

        save_btn = tk.Button(footer, text="Save", command=save_runtime_settings)
        save_btn.pack(side=tk.RIGHT, padx=(8, 0))
        self._style_button(save_btn, "primary", compact=True)

        cancel_btn = tk.Button(footer, text="Cancel", command=dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT)
        self._style_button(cancel_btn, "secondary", compact=True)

        dialog.bind("<Escape>", lambda _event: dialog.destroy())
        dialog.bind("<Control-s>", lambda _event: save_runtime_settings())
        dialog.wait_visibility()
        dialog.focus_set()

    def run_interactive_tutorial(self):
        from tools.tutorial_runner import TutorialRunner
        TutorialRunner(self).start()

    def show_about_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"About {APP_NAME}")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.geometry("520x340")
        dialog.minsize(480, 300)
        self._style_panel(dialog, self.colors["bg"])

        shell = tk.Frame(dialog, padx=22, pady=20)
        shell.pack(fill=tk.BOTH, expand=True)
        self._style_panel(shell, self.colors["bg"])

        title_label = tk.Label(shell, text=f"{APP_NAME} {APP_VERSION}")
        title_label.pack(anchor="w")
        self._style_label(title_label, "title", self.colors["bg"])

        tagline_label = tk.Label(shell, text=APP_TAGLINE)
        tagline_label.pack(anchor="w", pady=(4, 14))
        self._style_label(tagline_label, "muted", self.colors["bg"])

        details_card = tk.Frame(shell, padx=16, pady=14)
        details_card.pack(fill=tk.BOTH, expand=True)
        self._style_panel(details_card, self.colors["surface"], border=True)

        details_lines = [
            f"Publisher: {APP_PUBLISHER}",
            f"Settings: {self.global_settings_file}",
            f"Outputs: {self.base_output_dir}",
            f"ComfyUI root: {self.comfyui_root or 'Not configured'}",
            f"Launcher: {self.comfyui_launcher_path or 'Not configured'}",
            "",
            "Prompt2MTV is a local desktop workflow for ComfyUI-based video generation, music generation, review, stitching, and final soundtrack merges.",
            "Use Project > Configure Runtime Paths on a new machine if ComfyUI, model folders, or outputs live outside the defaults."
        ]
        details_label = tk.Label(details_card, text="\n".join(details_lines), justify=tk.LEFT, anchor="nw", wraplength=440)
        details_label.pack(fill=tk.BOTH, expand=True)
        self._style_label(details_label, "body", self.colors["surface"])

        footer = tk.Frame(shell)
        footer.pack(fill=tk.X, pady=(14, 0))
        self._style_panel(footer, self.colors["bg"])

        close_btn = tk.Button(footer, text="Close", command=dialog.destroy)
        close_btn.pack(side=tk.RIGHT)
        self._style_button(close_btn, "primary", compact=True)

        dialog.bind("<Escape>", lambda _event: dialog.destroy())
        dialog.wait_visibility()
        dialog.focus_set()

    def run_startup_preflight(self, interactive=False):
        issues = []
        warnings = []

        self.model_search_roots = self._resolve_model_search_roots(self.model_search_roots, self.comfyui_root)
        model_audit = self.audit_required_models()

        if not os.path.exists(self.api_json_path):
            issues.append(f"Video workflow JSON not found: {self.api_json_path}")
        if not os.path.exists(self.music_json_path):
            issues.append(f"Music workflow JSON not found: {self.music_json_path}")

        available_model_roots = self._get_available_model_search_roots()
        if not available_model_roots:
            warnings.append(
                "ComfyUI model folders were not found. Open Project > Configure Runtime Paths and point the app at your ComfyUI installation or add model search roots manually."
            )

        if not self._is_ffmpeg_available():
            warnings.append(
                "FFmpeg is not available. Thumbnail generation, stitching, and final merge actions need FFmpeg. If you launched an installed build, rerun the latest Prompt2MTV setup. If you are running from source, install imageio-ffmpeg or add ffmpeg to PATH."
            )

        if not self._is_comfyui_running() and not self.comfyui_launcher_path:
            warnings.append(
                "No ComfyUI launcher batch file is configured. Prompt2MTV can still connect to an already-running ComfyUI server at http://127.0.0.1:8188, or you can configure a launcher in Project > Configure Runtime Paths."
            )

        if not self.model_manifest.get("models"):
            warnings.append(
                f"Model manifest not found or empty: {self.model_manifest_path or MODEL_MANIFEST_FILE}. Missing-model detection is limited until the manifest is available."
            )

        if model_audit.get("missing"):
            if model_audit.get("installable_missing"):
                warnings.append(
                    f"Required workflow models are missing ({len(model_audit['missing'])}). Use Project > Install Missing Models to download them into your ComfyUI model folders automatically."
                )
            else:
                warnings.append(
                    f"Required workflow models are missing ({len(model_audit['missing'])}). Populate download URLs in {os.path.basename(self.model_manifest_path)} or add source page links for manual recovery."
                )

        preflight_text = self._compose_startup_preflight_text(issues, warnings, model_audit)
        self._update_model_install_controls(model_audit)

        if issues:
            self._set_video_preflight_summary(preflight_text, "Setup required", "red")
            if interactive:
                dialog_title = "First Launch Setup" if self.is_first_launch else "Startup Preflight"
                messagebox.showerror(dialog_title, preflight_text)
            return False

        if warnings:
            self._set_video_preflight_summary(preflight_text, "Warnings", "orange")
            if interactive:
                dialog_title = "First Launch Guidance" if self.is_first_launch else "Startup Preflight"
                messagebox.showwarning(dialog_title, preflight_text)
                if self.is_first_launch and model_audit.get("installable_missing"):
                    self.install_missing_models(interactive=True, model_audit=model_audit)
        else:
            ready_text = self._compose_startup_preflight_text([], [], model_audit)
            self._set_video_preflight_summary(ready_text, "Ready", "green")

        return True

    def _compose_startup_preflight_text(self, issues, warnings, model_audit=None):
        lines = [f"{APP_NAME} {APP_VERSION} | {APP_TAGLINE}"]

        if self.is_first_launch:
            lines.extend([
                "",
                "First launch checks are running against your local ComfyUI and media tools.",
                "Use Project > Configure Runtime Paths if this machine keeps ComfyUI, model folders, or outputs in a custom location."
            ])

        if issues:
            lines.extend(["", "Required setup items:"])
            lines.extend([f"- {issue}" for issue in issues])

        if warnings:
            lines.extend(["", "Recommended fixes:"])
            lines.extend([f"- {warning}" for warning in warnings])

        if model_audit and model_audit.get("manifest_notes"):
            lines.extend(["", "Model manifest notes:"])
            lines.extend([f"- {note}" for note in model_audit["manifest_notes"]])

        if model_audit and model_audit.get("missing"):
            lines.extend(["", "Missing required workflow models:"])
            lines.extend(self._format_missing_model_lines(model_audit))
        elif model_audit and model_audit.get("reports"):
            lines.extend([
                "",
                f"Required workflow models detected: {len(model_audit['reports'])}"
            ])

        if not issues and not warnings:
            lines.extend([
                "",
                "Runtime checks passed.",
                "ComfyUI paths, workflow files, and FFmpeg access look ready for normal use."
            ])

        return "\n".join(lines)

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
        self._update_image_workspace_balance()
        self._update_video_workspace_balance()
        self._update_music_workspace_balance()
        self._refresh_responsive_copy()
        if key in self.collapsible_sections:
            self._schedule_project_state_save()

    def _update_collapsible_section_meta(self, key, meta_text):
        section = self.collapsible_sections.get(key)
        if not section:
            return
        section["meta"].config(text=meta_text)

    def _get_collapsible_launch_defaults(self):
        return {
            "scene_timeline": False,
            "video_settings": False,
            "video_preflight": False,
            "video_debug": False,
            "video_utilities": False,
            "image_utilities": False,
            "image_workflow_settings": False,
            "image_prompt_queue": False,
            "gallery_browser": False,
            "music_prompt": False,
            "music_lyrics": False,
            "music_playback": False,
            "music_generation": False,
            "music_advanced": False,
            "music_actions": False,
            "music_media_state": False,
            "music_preview": False,
            "chatbot_focus_workspace": True,
            "chatbot_history": False,
            "chatbot_readiness": False,
        }

    def _apply_collapsible_launch_defaults(self):
        for key, is_open in self._get_collapsible_launch_defaults().items():
            if key in self.collapsible_sections:
                self._set_collapsible_section_open(key, is_open)

    def _get_collapsible_ui_state_snapshot(self):
        return {
            key: bool(section.get("open"))
            for key, section in self.collapsible_sections.items()
        }

    def _apply_collapsible_ui_state_snapshot(self, ui_state=None):
        if not isinstance(ui_state, dict):
            return

        for key, is_open in ui_state.items():
            if key in self.collapsible_sections:
                self._set_collapsible_section_open(key, bool(is_open))

        self._update_image_workspace_balance()
        self._update_video_workspace_balance()
        self._update_music_workspace_balance()
        self._refresh_responsive_copy()

    def _apply_header_density_mode(self, is_compact):
        self.video_header_eyebrow_label.config(text="" if is_compact else "VIDEO STUDIO")
        self.video_header_copy_label.config(
            text="Workflow, prompts, and output review." if is_compact else "Keep workflow control, prompting, and output review in one screen."
        )
        if hasattr(self, "image_header_eyebrow_label"):
            self.image_header_eyebrow_label.config(text="" if is_compact else "IMAGE PHASE")
        if hasattr(self, "image_header_copy_label"):
            self.image_header_copy_label.config(
                text="Generate and review still assets for I2V." if is_compact else "Generate still-image concepts, import reference frames, and keep assets ready for later image-to-video scenes."
            )
        if hasattr(self, "scene_section_eyebrow_label"):
            self.scene_section_eyebrow_label.config(text="" if is_compact else "SCENE TIMELINE")
        if hasattr(self, "scene_section_copy_label"):
            self.scene_section_copy_label.config(
                text="Mix T2V and I2V shots." if is_compact else "Use the timeline when a project needs both pure T2V shots and image-guided motion shots in a deliberate order."
            )
        if hasattr(self, "gallery_eyebrow_label"):
            self.gallery_eyebrow_label.config(text="" if is_compact else "MEDIA BROWSER")
        if hasattr(self, "gallery_copy_label"):
            self.gallery_copy_label.config(
                text="Scenes, images, imports, stitched renders, and finals." if is_compact else "Review generated scenes, still images, imported clips, stitched renders, and finished music videos without leaving the queue manager."
            )
        if hasattr(self, "music_header_eyebrow_label"):
            self.music_header_eyebrow_label.config(text="" if is_compact else "MUSIC STUDIO")
        if hasattr(self, "music_header_copy_label"):
            self.music_header_copy_label.config(
                text="Score the selected cut." if is_compact else "Generate audio from tags and lyrics or import your own track, then approve the final merge."
            )
        if hasattr(self, "music_sidebar_eyebrow_label"):
            self.music_sidebar_eyebrow_label.config(text="" if is_compact else "LINKED MEDIA")
        if hasattr(self, "music_sidebar_copy_label"):
            self.music_sidebar_copy_label.config(
                text="Clip, audio, and final state." if is_compact else "This panel tracks the source clip, active audio, and final export state for the current music pass."
            )
        if hasattr(self, "music_tags_hint_label"):
            self.music_tags_hint_label.config(
                text="Genre, texture, emotion, instrumentation." if is_compact else "Describe genre, texture, emotion, and instrumentation."
            )
        if hasattr(self, "music_lyrics_hint_label"):
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
        self._update_image_workspace_balance()
        self._update_video_workspace_balance()
        self._update_music_workspace_balance()

    def _protect_primary_workspaces(self):
        music_main_height = self._safe_widget_height(getattr(self, "music_main_frame", None)) or 0
        if music_main_height and music_main_height < 420:
            for key in ["music_preview", "music_media_state", "music_advanced", "music_generation", "music_playback", "music_lyrics", "music_prompt"]:
                self._set_collapsible_section_open(key, False)

    def _update_video_workspace_balance(self):
        if not hasattr(self, "video_config_row"):
            return

        try:
            if int(self.video_config_row.winfo_exists()) != 1:
                return
        except tk.TclError:
            return

        accordion_order = [
            "scene_timeline",
            "video_settings",
            "video_preflight",
            "video_debug"
        ]
        active_support = next(
            (
                key for key in accordion_order
                if self.collapsible_sections.get(key) and self.collapsible_sections[key].get("open")
            ),
            None
        )

        video_workspace_height = self._safe_widget_height(getattr(self, "video_config_row", None)) or self._safe_widget_height(getattr(self, "left_frame", None)) or 0
        scene_focus_height = 620
        settings_focus_height = 320
        support_height = 220
        if video_workspace_height:
            scene_focus_height = max(520, min(video_workspace_height - 170, 860))
            settings_focus_height = max(260, min(video_workspace_height - 250, 420))
            support_height = max(180, min(video_workspace_height // 3, 260))

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
                self.settings_canvas.configure(height=settings_focus_height if active_support == "video_settings" else support_height)

            if hasattr(self, "scene_canvas") and int(self.scene_canvas.winfo_exists()) == 1:
                self.scene_canvas.configure(height=scene_focus_height if active_support == "scene_timeline" else support_height)
        except tk.TclError:
            return

    def _update_image_workspace_balance(self):
        if not hasattr(self, "image_canvas"):
            return

        workspace_height = self._safe_widget_height(getattr(self, "image_scroll_shell", None)) or self._safe_widget_height(getattr(self, "image_tab", None)) or 0
        queue_height = 640
        if workspace_height:
            queue_height = max(480, min(workspace_height - 120, 980))

        if self.collapsible_sections.get("image_utilities", {}).get("open"):
            queue_height = max(420, queue_height - 210)

        try:
            if int(self.image_canvas.winfo_exists()) == 1:
                self.image_canvas.configure(height=queue_height)
        except tk.TclError:
            return

    def _update_music_workspace_balance(self):
        section_layouts = [
            ("music_prompt", {"fill": tk.X, "pady": (18, 12)}),
            ("music_lyrics", {"fill": tk.X, "pady": (0, 12)}),
            ("music_playback", {"fill": tk.X, "pady": (0, 12)}),
            ("music_generation", {"fill": tk.X, "pady": (0, 12)}),
            ("music_advanced", {"fill": tk.X, "pady": (0, 12)}),
            ("music_actions", {"fill": tk.X})
        ]
        right_layouts = [
            ("music_media_state", {"fill": tk.X}),
            ("music_preview", {"fill": tk.BOTH, "expand": self.collapsible_sections.get("music_preview", {}).get("open", False), "pady": (16, 0)})
        ]

        try:
            for key, pack_options in section_layouts:
                section = self.collapsible_sections.get(key)
                if not section or int(section["container"].winfo_exists()) != 1:
                    continue
                section["container"].pack_forget()
                section["container"].pack(**pack_options)

            for key, pack_options in right_layouts:
                section = self.collapsible_sections.get(key)
                if not section or int(section["container"].winfo_exists()) != 1:
                    continue
                section["container"].pack_forget()
                section["container"].pack(**pack_options)
        except tk.TclError:
            return

    def _update_chatbot_workspace_balance(self):
        if not hasattr(self, "chatbot_focus_workspace_frame"):
            return

        try:
            if int(self.chatbot_focus_workspace_frame.winfo_exists()) != 1:
                return
        except tk.TclError:
            return

        workspace_width = (
            self._safe_widget_width(getattr(self, "chatbot_focus_workspace_frame", None))
            or self._safe_widget_width(getattr(self, "chatbot_workspace_frame", None))
            or self._safe_widget_width(getattr(self, "chatbot_shell", None))
            or 0
        )
        layout_mode = "compact" if workspace_width and workspace_width < 1220 else "wide"
        self.chatbot_workspace_layout_mode = layout_mode

        try:
            self.chatbot_workflow_card.grid_forget()
            self.chatbot_output_card.grid_forget()

            if layout_mode == "compact":
                self.chatbot_focus_workspace_frame.grid_columnconfigure(0, weight=1)
                self.chatbot_focus_workspace_frame.grid_columnconfigure(1, weight=0)
                self.chatbot_focus_workspace_frame.grid_rowconfigure(0, weight=0)
                self.chatbot_focus_workspace_frame.grid_rowconfigure(1, weight=1)
                self.chatbot_workflow_card.grid(row=0, column=0, sticky="nsew", pady=(0, 12))
                self.chatbot_output_card.grid(row=1, column=0, sticky="nsew")
            else:
                self.chatbot_focus_workspace_frame.grid_columnconfigure(0, weight=5)
                self.chatbot_focus_workspace_frame.grid_columnconfigure(1, weight=6)
                self.chatbot_focus_workspace_frame.grid_rowconfigure(0, weight=1)
                self.chatbot_focus_workspace_frame.grid_rowconfigure(1, weight=0)
                self.chatbot_workflow_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
                self.chatbot_output_card.grid(row=0, column=1, sticky="nsew")
        except tk.TclError:
            return

        workflow_width = self._safe_widget_width(getattr(self, "chatbot_workflow_card", None)) or max(420, workspace_width // 2)
        output_width = self._safe_widget_width(getattr(self, "chatbot_output_card", None)) or max(480, workspace_width // 2)
        history_width = self._safe_widget_width(getattr(self, "chatbot_history_card", None)) or max(520, workspace_width)

        for widget in [
            getattr(self, "chatbot_workflow_hint_label", None),
            getattr(self, "chatbot_mode_summary_label", None),
            getattr(self, "chatbot_task_hint_label", None),
            getattr(self, "chatbot_briefing_hint_label", None),
        ]:
            self._set_wraplength(widget, workflow_width, padding=48, minimum=260)

        for widget in [
            getattr(self, "chatbot_output_hint_label", None),
            getattr(self, "chatbot_result_status_label", None),
            getattr(self, "chatbot_artifact_review_title_label", None),
            getattr(self, "chatbot_artifact_review_meta_label", None),
            getattr(self, "chatbot_artifact_review_destination_label", None),
            getattr(self, "chatbot_artifact_review_brief_label", None),
            getattr(self, "chatbot_artifact_review_preview_label", None),
        ]:
            self._set_wraplength(widget, output_width, padding=56, minimum=260)

        self._set_wraplength(getattr(self, "chatbot_apply_hint_label", None), history_width, padding=56, minimum=320)

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

        image_tab_header_width = self._safe_widget_width(getattr(self, "image_header_frame", None))
        if image_tab_header_width and hasattr(self, "image_header_copy_label"):
            self._set_wraplength(self.image_header_copy_label, image_tab_header_width, padding=20, minimum=320)

        scene_header_width = self._safe_widget_width(getattr(self, "scene_timeline_header_frame", None))
        if scene_header_width:
            self._set_wraplength(self.scene_section_copy_label, scene_header_width, padding=20, minimum=320)

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

        music_advanced_width = self._safe_widget_width(getattr(self, "music_advanced_card", None))
        if music_advanced_width and hasattr(self, "music_advanced_tuning_hint_label"):
            self._set_wraplength(self.music_advanced_tuning_hint_label, music_advanced_width, padding=40, minimum=260)

        music_actions_width = self._safe_widget_width(getattr(self, "music_actions_card", None))
        if music_actions_width and hasattr(self, "music_drop_hint_label"):
            self._set_wraplength(self.music_drop_hint_label, music_actions_width, padding=40, minimum=260)

        music_sidebar_width = self._safe_widget_width(getattr(self, "music_right_frame", None))
        if music_sidebar_width:
            self._set_wraplength(self.music_sidebar_copy_label, music_sidebar_width, padding=28, minimum=220)
            self._set_wraplength(self.selected_video_lbl, music_sidebar_width, padding=68, minimum=220)
            self._set_wraplength(self.selected_video_meta_label, music_sidebar_width, padding=68, minimum=220)

        chatbot_header_width = self._safe_widget_width(getattr(self, "chatbot_header_frame", None))
        if chatbot_header_width:
            self._set_wraplength(self.chatbot_header_copy_label, chatbot_header_width, padding=24, minimum=320)

        chatbot_runtime_width = self._safe_widget_width(getattr(self, "chatbot_runtime_card", None))
        if chatbot_runtime_width:
            self._set_wraplength(self.chatbot_readiness_next_step_label, chatbot_runtime_width, padding=40, minimum=320)
            self._set_wraplength(self.chatbot_runtime_status_label, chatbot_runtime_width, padding=40, minimum=320)
            self._set_wraplength(self.chatbot_readiness_health_label, chatbot_runtime_width, padding=40, minimum=320)

        self._update_chatbot_workspace_balance()

    def _reflow_video_left_panel(self):
        layout_sequence = [
            (self.video_config_row, {"side": tk.TOP, "fill": tk.BOTH, "expand": True, "padx": 18, "pady": (0, 12)}),
            (self.video_utilities_section["container"], {"side": tk.BOTTOM, "fill": tk.X, "padx": 18, "pady": (0, 12)})
        ]

        for widget, pack_options in layout_sequence:
            widget.pack_forget()
            widget.pack(**pack_options)

    def _on_window_resize(self, _event=None):
        self._apply_responsive_section_defaults()
        self._protect_primary_workspaces()
        self._update_image_workspace_balance()
        self._update_video_workspace_balance()
        self._update_chatbot_workspace_balance()
        self._refresh_responsive_copy()

    def _update_prompt_collection_summary(self):
        if hasattr(self, "prompt_count_value_label"):
            scene_count = len(self.scene_scrollable_frame.winfo_children()) if hasattr(self, "scene_scrollable_frame") else 0
            self.prompt_count_value_label.config(text=f"{scene_count} scene{'s' if scene_count != 1 else ''}")
            if hasattr(self, "selection_count_value_label"):
                selection_count_text = self.selection_count_value_label.cget("text")
                self._update_collapsible_section_meta("video_utilities", f"{scene_count} scenes • {selection_count_text}")

        image_prompt_count = len(self.image_scrollable_frame.winfo_children()) if hasattr(self, "image_scrollable_frame") else 0
        if hasattr(self, "image_queue_count_value_label"):
            self.image_queue_count_value_label.config(text=f"{image_prompt_count} prompt{'s' if image_prompt_count != 1 else ''}")
        if "image_prompt_queue" in self.collapsible_sections:
            self._update_collapsible_section_meta("image_prompt_queue", f"{image_prompt_count} queued")
        if "image_workflow_settings" in self.collapsible_sections:
            self._update_collapsible_section_meta("image_workflow_settings", self._get_image_settings_summary_text())
        if "image_utilities" in self.collapsible_sections:
            image_asset_count = len(self._normalize_image_assets(self.image_assets)) if hasattr(self, "image_assets") else 0
            self._update_collapsible_section_meta("image_utilities", f"{image_prompt_count} queued • {image_asset_count} assets")

        if hasattr(self, "scene_count_value_label"):
            scene_count = len(self.scene_scrollable_frame.winfo_children()) if hasattr(self, "scene_scrollable_frame") else 0
            i2v_count = len([
                frame for frame in getattr(self, "scene_entry_frames", [])
                if getattr(frame, "mode_var", None) and frame.mode_var.get() == "Image to Video"
            ])
            self.scene_count_value_label.config(text=f"{scene_count} scene{'s' if scene_count != 1 else ''}")
            self.scene_i2v_count_value_label.config(text=str(i2v_count))
            self._update_collapsible_section_meta("scene_timeline", f"{scene_count} scenes • {i2v_count} i2v")

    def _update_video_selection_summary(self):
        if hasattr(self, "selection_count_value_label"):
            selection_count = len(self.selected_videos)
            self.selection_count_value_label.config(text=f"{selection_count} selected")
            if hasattr(self, "prompt_count_value_label"):
                scene_count_text = self.prompt_count_value_label.cget("text")
                self._update_collapsible_section_meta("video_utilities", f"{scene_count_text} • {selection_count} selected")

    def _update_gallery_overview(self, final_count=0, stitched_count=0, scenes_count=0, image_count=0):
        if hasattr(self, "gallery_final_count_label"):
            self.gallery_final_count_label.config(text=str(final_count))
        if hasattr(self, "gallery_stitched_count_label"):
            self.gallery_stitched_count_label.config(text=str(stitched_count))
        if hasattr(self, "gallery_scene_count_label"):
            self.gallery_scene_count_label.config(text=str(scenes_count))
        if hasattr(self, "gallery_image_count_label"):
            self.gallery_image_count_label.config(text=str(image_count))
        if hasattr(self, "image_asset_count_value_label"):
            self.image_asset_count_value_label.config(text=f"{image_count} image{'s' if image_count != 1 else ''}")
        if hasattr(self, "gallery_imported_count_label"):
            imported_count = (len(self._get_gallery_video_files(self.imported_video_dir)) if self.imported_video_dir else 0) + (len(self._get_gallery_image_files(self.imported_image_dir)) if self.imported_image_dir else 0)
            self.gallery_imported_count_label.config(text=str(imported_count))
        else:
            imported_count = (len(self._get_gallery_video_files(self.imported_video_dir)) if self.imported_video_dir else 0) + (len(self._get_gallery_image_files(self.imported_image_dir)) if self.imported_image_dir else 0)
        self._update_collapsible_section_meta("gallery_browser", f"{scenes_count} scenes • {image_count} images • {imported_count} imports • {stitched_count} stitched • {final_count} finals")

    def _update_music_config_summary(self, *_args):
        if hasattr(self, "music_duration_value_label"):
            self.music_duration_value_label.config(text=f"{self.music_duration_var.get()}s")
        if hasattr(self, "music_bpm_value_label"):
            self.music_bpm_value_label.config(text=str(self.music_bpm_var.get()))
        if hasattr(self, "music_key_value_label"):
            self.music_key_value_label.config(text=self.music_key_var.get().strip() or "Unset")
        if hasattr(self, "music_sampling_value_label"):
            sampler_name = self.music_sampler_var.get().strip() or "unset"
            self.music_sampling_value_label.config(text=f"{self.music_steps_var.get()} st | cfg {self.music_cfg_var.get():g} | {sampler_name}")
        self._update_collapsible_section_meta(
            "music_prompt",
            "Has tags" if getattr(self, "music_tags_text", None) and self.music_tags_text.get("1.0", tk.END).strip() else "Needs direction"
        )
        self._update_collapsible_section_meta("music_lyrics", "Optional" if not getattr(self, "music_lyrics_text", None) or not self.music_lyrics_text.get("1.0", tk.END).strip() else "Has content")
        self._update_collapsible_section_meta("music_playback", f"{self.music_duration_var.get()}s • {self.music_bpm_var.get()} BPM")
        self._update_collapsible_section_meta("music_generation", f"{self.music_steps_var.get()} st • {self.music_sampler_var.get().strip() or 'sampler'}")
        self._update_collapsible_section_meta("music_advanced", f"Top P {self.music_top_p_var.get():g} • Min P {self.music_min_p_var.get():g}")

    def _refresh_music_sidebar_state(self):
        if hasattr(self, "music_selected_clip_value_label"):
            selected_name = os.path.basename(self.selected_video_for_music) if self.selected_video_for_music else "No clip linked"
            self.music_selected_clip_value_label.config(text=selected_name)
        if hasattr(self, "music_audio_state_value_label"):
            self.music_audio_state_value_label.config(text=self._format_audio_state())
        if hasattr(self, "music_final_state_value_label"):
            final_state = os.path.basename(self.current_final_video) if getattr(self, "current_final_video", None) and os.path.exists(self.current_final_video) else "No final render"
            self.music_final_state_value_label.config(text=final_state)
        media_meta = os.path.basename(self.selected_video_for_music) if self.selected_video_for_music else "No clip linked"
        self._update_collapsible_section_meta("music_media_state", media_meta)
        preview_meta = os.path.basename(self.selected_video_for_music) if self.selected_video_for_music else "Reference clip"
        self._update_collapsible_section_meta("music_preview", preview_meta)

    def _reset_selected_video_preview(self):
        self.selected_video_lbl.config(text="No video selected.\nGo to Video Generation tab\nand click 'Add Music'.")
        self.selected_video_thumb.config(image="")
        self.selected_video_thumb.image = None
        if hasattr(self, "selected_video_meta_label"):
            self.selected_video_meta_label.config(text="Select a stitched or imported clip from the gallery to lock music direction to a specific cut.")
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
        self.help_menu.configure(bg=self.colors["surface"], fg=self.colors["text"], activebackground=self.colors["surface_soft"], activeforeground=self.colors["text"], bd=0)

        for widget in [
            self.status_frame,
            self.video_tab,
            self.image_tab,
            self.gallery_tab,
            self.music_tab,
            self.chatbot_tab,
            self.left_frame,
            self.right_frame,
            self.video_utilities_section["container"],
            self.video_utilities_section["header"],
            self.video_utilities_frame,
            self.video_header_frame,
            self.workflow_toolbar_card,
            self.video_config_row,
            self.image_scroll_shell,
            self.image_main_frame,
            self.image_utilities_section["container"],
            self.image_utilities_section["header"],
            self.image_utilities_frame,
            self.image_header_frame,
            self.image_prompt_queue_section["container"],
            self.image_prompt_queue_section["header"],
            self.image_settings_section["container"],
            self.image_settings_section["header"],
            self.scene_timeline_section["container"],
            self.scene_timeline_section["header"],
            self.video_settings_section["container"],
            self.video_settings_section["header"],
            self.settings_scroll_shell,
            self.settings_frame,
            self.video_preflight_section["container"],
            self.video_preflight_section["header"],
            self.preflight_frame,
            self.image_prompt_section_frame,
            self.scene_timeline_frame,
            self.scene_timeline_header_frame,
            self.video_debug_section["container"],
            self.video_debug_section["header"],
            self.bottom_frame,
            self.post_process_frame,
            self.gallery_header_frame,
            self.gallery_actions_frame,
            self.gallery_section["container"],
            self.gallery_section["header"],
            self.gallery_shell_frame,
            self.gallery_inner_frame,
            self.music_left_frame,
            self.music_scroll_shell,
            self.music_main_frame,
            self.music_header_frame,
            self.music_prompt_section["container"],
            self.music_prompt_section["header"],
            self.music_prompt_card,
            self.music_lyrics_section["container"],
            self.music_lyrics_section["header"],
            self.music_lyrics_card,
            self.music_playback_section["container"],
            self.music_playback_section["header"],
            self.music_playback_card,
            self.music_generation_section["container"],
            self.music_generation_section["header"],
            self.music_generation_card,
            self.music_advanced_section["container"],
            self.music_advanced_section["header"],
            self.music_advanced_card,
            self.music_actions_section["container"],
            self.music_actions_section["header"],
            self.music_actions_card,
            self.music_action_frame,
            self.music_media_state_section["container"],
            self.music_media_state_section["header"],
            self.music_preview_section["container"],
            self.music_preview_section["header"],
            self.music_sidebar_card,
            self.music_sidebar_summary_frame,
            self.music_preview_card,
            self.music_preview_media_frame,
            self.music_preview_actions_frame,
            self.music_preview_status_frame,
            self.chatbot_shell,
            self.chatbot_header_frame,
            self.chatbot_runtime_card,
            self.chatbot_runtime_actions_frame,
            self.chatbot_workspace_frame,
            self.chatbot_focus_workspace_frame,
            self.chatbot_briefing_card,
            self.chatbot_output_card,
            self.chatbot_task_actions_frame,
            self.chatbot_output_actions_frame,
            self.chatbot_history_card
        ]:
            self._style_panel(widget, self.colors["bg"] if widget in [self.video_tab, self.image_tab, self.gallery_tab, self.music_tab, self.chatbot_tab] else self.colors["surface"])

        self._style_panel(self.right_frame, self.colors["surface_alt"])
        if hasattr(self, "main_paned"):
            self._style_panel(self.main_paned, self.colors["bg"])
        self._style_panel(self.image_scroll_shell, self.colors["bg"])
        self._style_panel(self.image_tab_canvas, self.colors["bg"])
        self._style_panel(self.image_canvas, self.colors["surface"])
        self._style_panel(self.settings_canvas, self.colors["surface"])
        self._style_panel(self.gallery_canvas, self.colors["surface_alt"])
        self._style_panel(self.gallery_inner_frame, self.colors["surface_alt"])
        self._style_panel(self.music_scroll_shell, self.colors["bg"])
        self._style_panel(self.music_canvas, self.colors["bg"])
        self._style_panel(self.music_right_frame, self.colors["surface_alt"], border=True)
        self._style_panel(self.music_sidebar_card, self.colors["surface_alt"], border=True)
        self._style_panel(self.music_media_state_card, self.colors["surface_alt"], border=True)
        self._style_panel(self.music_sidebar_card, self.colors["surface_alt"], border=True)
        self._style_panel(self.music_preview_card, self.colors["surface"], border=True)
        self._style_panel(self.settings_frame, self.colors["surface"])
        self._style_panel(self.preflight_frame, self.colors["surface"])
        self._style_panel(self.workflow_toolbar_card, self.colors["surface_alt"], border=True)
        self._style_panel(self.image_prompt_section_frame, self.colors["surface"])
        self._style_panel(self.scene_timeline_frame, self.colors["surface"])
        self._style_panel(self.gallery_shell_frame, self.colors["surface_alt"], border=True)

        for key in ["image_utilities", "image_prompt_queue", "image_workflow_settings", "scene_timeline", "video_settings", "video_preflight", "video_debug", "video_utilities", "gallery_browser", "music_prompt", "music_lyrics", "music_playback", "music_generation", "music_advanced", "music_actions", "music_media_state", "music_preview"]:
            section = self.collapsible_sections[key]
            section_bg = self.colors["surface_alt"] if key in ["image_utilities", "video_utilities", "gallery_browser", "music_media_state", "music_preview"] else self.colors["surface"]
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
        self._style_label(self.image_header_eyebrow_label, "muted", self.image_header_frame.cget("bg"))
        self.image_header_eyebrow_label.configure(font=self.fonts["micro"])
        self._style_label(self.image_header_title_label, "title", self.image_header_frame.cget("bg"))
        self._style_label(self.image_header_copy_label, "muted", self.image_header_frame.cget("bg"))
        self._style_label(self.image_settings_title_label, "section", self.image_settings_card.cget("bg"))
        self._style_label(self.image_settings_hint_label, "muted", self.image_settings_card.cget("bg"))
        self._style_label(self.scene_section_eyebrow_label, "muted", self.scene_timeline_header_frame.cget("bg"))
        self.scene_section_eyebrow_label.configure(font=self.fonts["micro"])
        self._style_label(self.scene_section_title_label, "section", self.scene_timeline_header_frame.cget("bg"))
        self._style_label(self.scene_section_copy_label, "muted", self.scene_timeline_header_frame.cget("bg"))
        self._style_label(self.debug_prompt_label, "muted", self.video_debug_section["body"].cget("bg"))
        self._style_label(self.status_label, "muted", self.bottom_frame.cget("bg"))
        self._style_label(self.version_label, "muted", self.status_frame.cget("bg"))
        self.version_label.configure(font=self.fonts["small"])
        self._style_label(self.music_header_eyebrow_label, "muted", self.music_header_frame.cget("bg"))
        self.music_header_eyebrow_label.configure(font=self.fonts["micro"])
        self._style_label(self.music_header_title_label, "title", self.music_header_frame.cget("bg"))
        self._style_label(self.music_header_copy_label, "muted", self.music_header_frame.cget("bg"))
        self._style_label(self.music_tags_label, "section", self.music_prompt_card.cget("bg"))
        self._style_label(self.music_tags_hint_label, "muted", self.music_prompt_card.cget("bg"))
        self._style_label(self.music_lyrics_label, "section", self.music_lyrics_card.cget("bg"))
        self._style_label(self.music_lyrics_hint_label, "muted", self.music_lyrics_card.cget("bg"))
        self._style_label(self.music_advanced_tuning_hint_label, "muted", self.music_advanced_card.cget("bg"))
        self._style_label(self.music_status_label, "muted", self.music_actions_card.cget("bg"))
        self._style_label(self.music_sidebar_eyebrow_label, "muted", self.music_right_frame.cget("bg"))
        self.music_sidebar_eyebrow_label.configure(font=self.fonts["micro"])
        self._style_label(self.music_sidebar_title_label, "title", self.music_right_frame.cget("bg"))
        self._style_label(self.music_sidebar_copy_label, "muted", self.music_right_frame.cget("bg"))
        self._style_label(self.gallery_title_label, "title", self.right_frame.cget("bg"))
        self._style_label(self.gallery_eyebrow_label, "muted", self.gallery_header_frame.cget("bg"))
        self.gallery_eyebrow_label.configure(font=self.fonts["micro"])
        self._style_label(self.gallery_copy_label, "muted", self.gallery_header_frame.cget("bg"))
        self._style_label(self.chatbot_header_eyebrow_label, "muted", self.chatbot_header_frame.cget("bg"))
        self.chatbot_header_eyebrow_label.configure(font=self.fonts["micro"])
        self._style_label(self.chatbot_header_title_label, "title", self.chatbot_header_frame.cget("bg"))
        self._style_label(self.chatbot_header_copy_label, "muted", self.chatbot_header_frame.cget("bg"))
        self._style_panel(self.chatbot_focus_workspace_section["container"], self.colors["surface"], border=True)
        self._style_panel(self.chatbot_focus_workspace_section["header"], self.colors["surface"])
        self._style_panel(self.chatbot_focus_workspace_section["body"], self.colors["surface"])
        self._style_label(self.chatbot_focus_workspace_section["title"], "section", self.chatbot_focus_workspace_section["header"].cget("bg"))
        self._style_label(self.chatbot_focus_workspace_section["meta"], "muted", self.chatbot_focus_workspace_section["header"].cget("bg"))
        self._style_button(self.chatbot_focus_workspace_section["toggle"], "ghost", compact=True)
        self._style_label(self.chatbot_runtime_title_label, "section", self.chatbot_runtime_card.cget("bg"))
        self._style_label(self.chatbot_readiness_summary_label, "body_strong", self.chatbot_runtime_card.cget("bg"))
        self._style_label(self.chatbot_readiness_next_step_label, "body", self.chatbot_runtime_card.cget("bg"))
        self._style_label(self.chatbot_runtime_status_label, "muted", self.chatbot_runtime_card.cget("bg"))
        self._style_label(self.chatbot_readiness_health_label, "muted", self.chatbot_runtime_card.cget("bg"))
        self._style_label(self.chatbot_workflow_title_label, "section", self.chatbot_briefing_card.cget("bg"))
        self._style_label(self.chatbot_workflow_hint_label, "muted", self.chatbot_briefing_card.cget("bg"))
        self._style_label(self.chatbot_mode_label, "body_strong", self.chatbot_mode_row.cget("bg"))
        self._style_label(self.chatbot_mode_summary_label, "muted", self.chatbot_briefing_card.cget("bg"))
        self._style_label(self.chatbot_briefing_title_label, "section", self.chatbot_briefing_card.cget("bg"))
        self._style_label(self.chatbot_briefing_hint_label, "muted", self.chatbot_briefing_card.cget("bg"))
        self._style_label(self.chatbot_output_title_label, "section", self.chatbot_output_card.cget("bg"))
        self._style_label(self.chatbot_output_hint_label, "muted", self.chatbot_output_card.cget("bg"))
        self._style_label(self.chatbot_result_status_label, "muted", self.chatbot_output_card.cget("bg"))
        self._style_label(self.chatbot_artifact_review_eyebrow_label, "muted", self.chatbot_artifact_review_card.cget("bg"))
        self.chatbot_artifact_review_eyebrow_label.configure(font=self.fonts["micro"])
        self._style_label(self.chatbot_artifact_review_title_label, "body_strong", self.chatbot_artifact_review_card.cget("bg"))
        self._style_label(self.chatbot_artifact_review_meta_label, "muted", self.chatbot_artifact_review_card.cget("bg"))
        self._style_label(self.chatbot_artifact_review_destination_label, "body", self.chatbot_artifact_review_card.cget("bg"))
        self._style_label(self.chatbot_artifact_review_brief_label, "muted", self.chatbot_artifact_review_card.cget("bg"))
        self._style_label(self.chatbot_artifact_review_preview_label, "body", self.chatbot_artifact_review_card.cget("bg"))
        self._style_label(self.chatbot_task_hint_label, "body", self.chatbot_briefing_card.cget("bg"))
        self._style_label(self.chatbot_apply_hint_label, "muted", self.chatbot_history_card.cget("bg"))
        if hasattr(self, "gallery_drop_hint_label"):
            self._style_label(self.gallery_drop_hint_label, "muted", self.gallery_header_frame.cget("bg"))
        if hasattr(self, "music_drop_hint_label"):
            self._style_label(self.music_drop_hint_label, "muted", self.music_actions_card.cget("bg"))
        self._style_label(self.selected_video_header_label, "section", self.music_right_frame.cget("bg"))
        self._style_label(self.selected_video_lbl, "muted", self.music_right_frame.cget("bg"))
        self._style_label(self.selected_video_meta_label, "muted", self.music_right_frame.cget("bg"))

        for button, variant in [
            (self.load_btn, "secondary"),
            (self.reset_video_profile_btn, "ghost"),
            (self.validate_video_btn, "primary"),
            (self.refresh_model_lists_btn, "secondary"),
            (self.import_image_btn, "secondary"),
            (self.add_image_prompt_btn, "secondary"),
            (self.sync_image_to_scene_btn, "secondary"),
            (self.run_image_queue_btn, "accent"),
            (self.reset_image_settings_btn, "ghost"),
            (self.validate_image_btn, "secondary"),
            (self.refresh_image_models_btn, "secondary"),
            (self.add_scene_btn, "secondary"),
            (self.sync_t2v_to_image_queue_btn, "secondary"),
            (self.auto_assign_scene_images_btn, "secondary"),
            (self.render_scene_timeline_btn, "primary"),
            (self.stitch_btn, "primary"),
            (self.clear_sel_btn, "ghost"),
            (self.select_all_btn, "secondary"),
            (self.gallery_import_image_btn, "secondary"),
            (self.gallery_import_btn, "secondary"),
            (self.gen_music_btn, "accent"),
            (self.import_audio_btn, "secondary"),
            (self.preview_music_btn, "secondary"),
            (self.preview_final_btn, "secondary"),
            (self.merge_music_btn, "primary"),
            (self.chatbot_setup_btn, "secondary"),
            (self.chatbot_download_btn, "accent"),
            (self.chatbot_runtime_btn, "secondary"),
            (self.chatbot_test_backend_btn, "secondary"),
            (self.chatbot_output_mode_btn, "ghost"),
            (self.chatbot_copy_output_btn, "secondary"),
            (self.chatbot_apply_btn, "accent"),
            (self.chatbot_apply_scene_btn, "accent"),
            (self.chatbot_send_btn, "secondary"),
            (self.chatbot_scene_plan_btn, "secondary"),
            (self.chatbot_new_chat_btn, "ghost"),
            (self.chatbot_clear_chat_btn, "ghost"),
            (self.chatbot_generate_btn, "primary")
        ]:
            self._style_button(button, variant)

        for compact_button, variant in [
            (self.load_btn, "secondary"),
            (self.reset_video_profile_btn, "ghost"),
            (self.validate_video_btn, "primary"),
            (self.refresh_model_lists_btn, "secondary"),
            (self.import_image_btn, "secondary"),
            (self.add_image_prompt_btn, "secondary"),
            (self.sync_image_to_scene_btn, "secondary"),
            (self.run_image_queue_btn, "accent"),
            (self.reset_image_settings_btn, "ghost"),
            (self.validate_image_btn, "secondary"),
            (self.refresh_image_models_btn, "secondary"),
            (self.add_scene_btn, "secondary"),
            (self.sync_t2v_to_image_queue_btn, "secondary"),
            (self.auto_assign_scene_images_btn, "secondary"),
            (self.render_scene_timeline_btn, "primary"),
            (self.stitch_btn, "primary"),
            (self.clear_sel_btn, "ghost"),
            (self.select_all_btn, "secondary"),
            (self.gallery_import_image_btn, "secondary"),
            (self.gallery_import_btn, "secondary"),
            (self.import_audio_btn, "secondary"),
            (self.chatbot_setup_btn, "secondary"),
            (self.chatbot_download_btn, "accent"),
            (self.chatbot_runtime_btn, "secondary"),
            (self.chatbot_test_backend_btn, "secondary"),
            (self.chatbot_output_mode_btn, "ghost"),
            (self.chatbot_copy_output_btn, "secondary"),
            (self.chatbot_send_btn, "secondary"),
            (self.chatbot_scene_plan_btn, "secondary"),
            (self.chatbot_new_chat_btn, "ghost"),
            (self.chatbot_clear_chat_btn, "ghost"),
            (self.chatbot_apply_btn, "accent"),
            (self.chatbot_apply_scene_btn, "accent")
        ]:
            self._style_button(compact_button, variant, compact=True)

        for checkbutton in [self.strip_audio_cb, self.video_output_include_project_cb, self.music_randomize_seed_cb, self.music_generate_codes_cb]:
            self._style_checkbutton(checkbutton)

        for entry_widget in [
            self.music_tags_text,
            self.music_lyrics_text,
            self.video_preflight_text,
            self.chatbot_briefing_text
        ]:
            self._style_text_input(entry_widget, multiline=True)

        for combobox in [
            self.video_profile_combo,
            self.video_checkpoint_combo,
            self.video_text_encoder_combo,
            self.video_lora_combo,
            self.video_upscaler_combo,
            self.image_clip_combo,
            self.image_vae_combo,
            self.image_unet_combo,
            self.music_timesignature_combo,
            self.music_language_combo,
            self.music_sampler_combo,
            self.music_scheduler_combo,
            self.music_quality_combo
        ]:
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
            
        self.current_project_dir = self._normalize_path(project_dir)
        
        # Setup project subdirectories
        self.scenes_dir = os.path.join(self.current_project_dir, "generated_scenes")
        self.stitched_dir = os.path.join(self.current_project_dir, "stitched_videos")
        self.thumbs_dir = os.path.join(self.current_project_dir, "thumbnails")
        self.audio_dir = os.path.join(self.current_project_dir, "generated_audio")
        self.imported_audio_dir = os.path.join(self.current_project_dir, "imported_audio")
        self.final_mv_dir = os.path.join(self.current_project_dir, "final_music_videos")
        self.imported_video_dir = os.path.join(self.current_project_dir, "imported_videos")
        self.generated_image_dir = os.path.join(self.current_project_dir, "generated_images")
        self.imported_image_dir = os.path.join(self.current_project_dir, "imported_images")
        self.debug_dir = os.path.join(self.current_project_dir, "debug")
        
        for d in [self.scenes_dir, self.stitched_dir, self.thumbs_dir, self.audio_dir, self.imported_audio_dir, self.final_mv_dir, self.imported_video_dir, self.generated_image_dir, self.imported_image_dir, self.debug_dir]:
            os.makedirs(d, exist_ok=True)

        self.debug_log_file = os.path.join(self.debug_dir, "wrapper_debug.log")
        self.log_debug("PROJECT_SET", project_dir=self.current_project_dir)
            
        project_name = os.path.basename(self.current_project_dir)
        project_drive = os.path.splitdrive(self.current_project_dir)[0] or ""
        self.project_label.config(text=f"Current Project: {project_name}  [{project_drive}]")
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
            self.set_project(project_dir)
            self.save_global_settings()

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
        self._cancel_comfyui_console_poll()
        if self._is_comfyui_running():
            self.comfyui_ready = True
            self.update_status("ComfyUI already running on port 8188.", "blue")
            self.comfyui_process = None
            self.comfyui_console_hwnd = None
            self.comfyui_console_visible = False
            self.comfyui_console_title = None
            self.comfyui_console_pending_visibility = None
            self._refresh_comfyui_terminal_button()
            return

        bat_path = self._normalize_path(self.comfyui_launcher_path)
        if bat_path and os.path.exists(bat_path):
            self.update_status("Launching ComfyUI...", "blue")
            try:
                console_title = f"{APP_NAME} ComfyUI {uuid.uuid4().hex[:8]}"
                launcher_expression = f'title {console_title} && "{bat_path}"'
                # Keep the console host alive so the Help-menu terminal toggle can show/hide it reliably.
                launcher_command = f'"{os.environ.get("COMSPEC", "cmd.exe")}" /k {launcher_expression}'
                startupinfo = None
                if sys.platform == "win32":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = WINDOWS_HIDE

                self.comfyui_process = subprocess.Popen(
                    launcher_command,
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    cwd=os.path.dirname(bat_path),
                    startupinfo=startupinfo,
                )
                self.comfyui_console_hwnd = None
                self.comfyui_console_visible = False
                self.comfyui_console_title = console_title
                self.comfyui_console_pending_visibility = False
                self.log_debug(
                    "COMFYUI_LAUNCH_REQUESTED",
                    pid=self.comfyui_process.pid,
                    console_title=self.comfyui_console_title,
                    launcher_path=bat_path
                )
                self._queue_comfyui_console_visibility(False, source="launch")
                self._refresh_comfyui_terminal_button()
                # Give it some time to start up
                self.root.after(5000, lambda: self.update_status("ComfyUI Launched. Waiting for connection...", "blue"))
            except Exception as e:
                self.update_status(f"Error launching ComfyUI: {e}", "red")
                self.comfyui_process = None
                self.comfyui_console_hwnd = None
                self.comfyui_console_visible = False
                self.comfyui_console_title = None
                self.comfyui_console_pending_visibility = None
                self._refresh_comfyui_terminal_button()
        else:
            self.update_status("ComfyUI launcher not configured. Use Project > Configure Runtime Paths.", "red")

    def _load_comfyui_readiness_history(self):
        history = {"samples": [], "average_seconds": 0.0}
        try:
            if os.path.exists(self.comfyui_readiness_history_file):
                with open(self.comfyui_readiness_history_file, "r", encoding="utf-8") as f:
                    payload = json.load(f)
                if isinstance(payload, dict):
                    raw_samples = payload.get("samples") if isinstance(payload.get("samples"), list) else []
                    samples = []
                    for sample in raw_samples:
                        if not isinstance(sample, dict):
                            continue
                        try:
                            elapsed = max(0.0, float(sample.get("elapsed_seconds") or 0.0))
                        except (TypeError, ValueError):
                            continue
                        if elapsed <= 0:
                            continue
                        samples.append({
                            "elapsed_seconds": elapsed,
                            "recorded_at": str(sample.get("recorded_at") or "").strip(),
                        })
                    samples = samples[-12:]
                    elapsed_values = [s["elapsed_seconds"] for s in samples]
                    history["samples"] = samples
                    history["average_seconds"] = (sum(elapsed_values) / len(elapsed_values)) if elapsed_values else 0.0
        except Exception as exc:
            print(f"Error loading ComfyUI readiness history: {exc}")
        self.comfyui_readiness_history = history

    def _save_comfyui_readiness_history(self):
        try:
            os.makedirs(os.path.dirname(self.comfyui_readiness_history_file), exist_ok=True)
            payload = {
                "samples": self.comfyui_readiness_history.get("samples", []),
                "average_seconds": self.comfyui_readiness_history.get("average_seconds", 0.0),
            }
            with open(self.comfyui_readiness_history_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=4)
        except Exception as exc:
            print(f"Error saving ComfyUI readiness history: {exc}")

    def _record_comfyui_readiness_timing(self, elapsed_seconds):
        try:
            elapsed = max(0.0, float(elapsed_seconds))
        except (TypeError, ValueError):
            return
        if elapsed <= 0:
            return
        samples = list(self.comfyui_readiness_history.get("samples") or [])
        samples.append({
            "elapsed_seconds": elapsed,
            "recorded_at": datetime.now().isoformat(timespec="seconds"),
        })
        samples = samples[-12:]
        elapsed_values = [s["elapsed_seconds"] for s in samples]
        self.comfyui_readiness_history = {
            "samples": samples,
            "average_seconds": (sum(elapsed_values) / len(elapsed_values)) if elapsed_values else 0.0,
        }
        self._save_comfyui_readiness_history()

    def _flash_autonomous_status(self):
        if not hasattr(self, "autonomous_status_label"):
            return
        if self.comfyui_readiness_flash_job is not None:
            return
        label = self.autonomous_status_label
        original_bg = label.cget("bg")
        flash_color = self.colors["danger"]
        cycle_count = 8

        def flash(index=0):
            if index >= cycle_count:
                label.config(bg=original_bg)
                self.comfyui_readiness_flash_job = None
                return
            label.config(bg=flash_color if index % 2 == 0 else original_bg)
            self.comfyui_readiness_flash_job = self.root.after(150, lambda: flash(index + 1))

        flash()

    def _update_comfyui_readiness_eta(self):
        if self.comfyui_ready:
            self.comfyui_readiness_eta_job = None
            return
        avg = self.comfyui_readiness_history.get("average_seconds", 0.0)
        if avg > 0 and self.comfyui_poll_started_at:
            elapsed = time.time() - self.comfyui_poll_started_at
            remaining = max(0, int(avg - elapsed))
            if remaining > 0:
                eta_text = f"⏳ Waiting for ComfyUI to become ready... (ETA: ~{remaining}s)"
            else:
                eta_text = "⏳ Waiting for ComfyUI to become ready... (any moment now)"
            if hasattr(self, "autonomous_status_label"):
                self.autonomous_status_label.config(text=eta_text)
        self.comfyui_readiness_eta_job = self.root.after(1000, self._update_comfyui_readiness_eta)

    def _start_comfyui_readiness_poll(self):
        """Begin polling ComfyUI until it responds, updating the autonomous panel status."""
        if self.comfyui_ready:
            return
        self.comfyui_poll_started_at = time.time()
        if hasattr(self, "autonomous_start_btn"):
            self.autonomous_start_btn.config(state=tk.DISABLED)
        if hasattr(self, "autonomous_status_label"):
            self.autonomous_status_label.config(text="⏳ Waiting for ComfyUI to become ready...")
        self._update_comfyui_readiness_eta()
        self._poll_comfyui_readiness()

    def _poll_comfyui_readiness(self):
        """Check if ComfyUI is reachable. Update autonomous panel and re-schedule if not."""
        try:
            req = urllib.request.Request("http://127.0.0.1:8188/queue")
            with urllib.request.urlopen(req, timeout=2) as resp:
                resp.read()
            reachable = True
        except Exception:
            reachable = False

        if reachable:
            self.comfyui_ready = True
            self.comfyui_ready_poll_id = None
            if self.comfyui_readiness_eta_job is not None:
                self.root.after_cancel(self.comfyui_readiness_eta_job)
                self.comfyui_readiness_eta_job = None
            if self.comfyui_poll_started_at:
                elapsed = time.time() - self.comfyui_poll_started_at
                self._record_comfyui_readiness_timing(elapsed)
                self.comfyui_poll_started_at = None
            if hasattr(self, "autonomous_status_label"):
                self.autonomous_status_label.config(text="✅ ComfyUI is ready. Enter a creative brief and click Start.")
            if hasattr(self, "autonomous_start_btn") and not getattr(self, "autonomous_active", False):
                self.autonomous_start_btn.config(state=tk.NORMAL)
            self.update_status("ComfyUI is online and ready.", "green")
        else:
            self.comfyui_ready_poll_id = self.root.after(3000, self._poll_comfyui_readiness)

    def setup_ui(self):
        # Top Menu Bar
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        self.project_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Project", menu=self.project_menu)
        self.project_menu.add_command(label="New Project", command=self.create_new_project)
        self.project_menu.add_command(label="Open Project", command=self.open_project)
        self.project_menu.add_command(label="Rename Current Project", command=self.rename_current_project)
        self.project_menu.add_command(label="Configure Runtime Paths", command=self.configure_runtime_paths)
        self.project_menu.add_command(label="Install Missing Models", command=self.install_missing_models)
        self.project_menu.add_command(label="Advanced Chatbot Runtime Settings", command=self.configure_chatbot_runtime)
        self.project_menu.add_command(label="Download Chatbot Model", command=self.prompt_and_download_chatbot_model)
        self.project_menu.add_separator()
        self.project_menu.add_command(label="Exit", command=self.on_closing)

        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="Open Debug Log", command=self.open_debug_log)
        self.help_menu_open_debug_index = self.help_menu.index("end")
        self.help_menu.add_command(label="Show ComfyUI Terminal", command=self.toggle_comfyui_terminal, state=tk.DISABLED)
        self.help_menu_toggle_terminal_index = self.help_menu.index("end")
        self.help_menu.add_separator()
        self.help_menu.add_command(label="Run Interactive Tutorial", command=self.run_interactive_tutorial)
        self.help_menu.add_command(label=f"About {APP_NAME}", command=self.show_about_dialog)

        # Project Status Bar
        self.status_frame = tk.Frame(self.root, pady=8)
        self.status_frame.pack(fill=tk.X)
        self.status_frame.grid_columnconfigure(0, weight=1)
        self.project_label = tk.Label(self.status_frame, text="Current Project: None")
        self.project_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.version_label = tk.Label(self.status_frame, text=f"{APP_NAME} {APP_VERSION}")
        self.version_label.pack(side=tk.RIGHT, padx=10)

        # ETA Progress Panel (hidden by default)
        self.eta_panel_frame = tk.Frame(self.root, relief=tk.GROOVE, borderwidth=1, padx=8, pady=4)
        eta_top_row = tk.Frame(self.eta_panel_frame)
        eta_top_row.pack(fill=tk.X)
        self.eta_phase_label = tk.Label(eta_top_row, text="", font=("", 9, "bold"), anchor=tk.W)
        self.eta_phase_label.pack(side=tk.LEFT)
        self.eta_item_label = tk.Label(eta_top_row, text="", anchor=tk.W, padx=12)
        self.eta_item_label.pack(side=tk.LEFT)
        self.eta_elapsed_label = tk.Label(eta_top_row, text="Elapsed: 0s", anchor=tk.W, padx=12)
        self.eta_elapsed_label.pack(side=tk.LEFT)
        self.eta_countdown_label = tk.Label(eta_top_row, text="ETA: Estimating...", anchor=tk.E, padx=12)
        self.eta_countdown_label.pack(side=tk.RIGHT)
        eta_bar_row = tk.Frame(self.eta_panel_frame)
        eta_bar_row.pack(fill=tk.X, pady=(2, 0))
        self.eta_progress_bar = ttk.Progressbar(eta_bar_row, mode="determinate", maximum=100)
        self.eta_progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.eta_percent_label = tk.Label(eta_bar_row, text="0%", width=5, anchor=tk.E)
        self.eta_percent_label.pack(side=tk.RIGHT, padx=(6, 0))
        
        # Create Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Chatbot
        self.chatbot_tab = tk.Frame(self.notebook)
        self.notebook.add(self.chatbot_tab, text="Chatbot")

        # Tab 2: Image Phase
        self.image_tab = tk.Frame(self.notebook)
        self.notebook.add(self.image_tab, text="Image Phase")
        
        # Tab 3: Video Generation
        self.video_tab = tk.Frame(self.notebook)
        self.notebook.add(self.video_tab, text="Video Generation")

        # Tab 4: Gallery
        self.gallery_tab = tk.Frame(self.notebook)
        self.notebook.add(self.gallery_tab, text="Gallery")

        # Tab 5: Music Studio
        self.music_tab = tk.Frame(self.notebook)
        self.notebook.add(self.music_tab, text="Music Studio")
        
        # --- Video Tab Content ---
        self.left_frame = tk.Frame(self.video_tab, padx=0, pady=0)
        self.left_frame.pack(fill=tk.BOTH, expand=True, padx=14, pady=(6, 14))
        
        self.video_config_row = tk.Frame(self.left_frame)
        self.video_config_row.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=18, pady=(0, 12))

        self.scene_timeline_section = self._create_collapsible_section(
            self.video_config_row,
            "scene_timeline",
            "Scene Timeline",
            meta_text="0 scenes",
            is_open=False,
            body_expand=True,
            group="video_left_support"
        )
        self.scene_timeline_section["container"].pack(fill=tk.BOTH, expand=True)

        self.video_settings_section = self._create_collapsible_section(
            self.video_config_row,
            "video_settings",
            "Workflow Settings",
            meta_text="Profile, models, output",
            is_open=False,
            body_expand=True,
            group="video_left_support"
        )
        self.video_settings_section["container"].pack(fill=tk.X, pady=(10, 0))

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
        self.image_negative_prompt_var = tk.StringVar()
        self.image_width_var = tk.StringVar()
        self.image_height_var = tk.StringVar()
        self.image_steps_var = tk.StringVar()
        self.image_cfg_var = tk.StringVar()
        self.image_sampler_var = tk.StringVar()
        self.image_scheduler_var = tk.StringVar()
        self.image_denoise_var = tk.StringVar()
        self.image_clip_name_var = tk.StringVar()
        self.image_vae_name_var = tk.StringVar()
        self.image_unet_name_var = tk.StringVar()

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

        self.preflight_action_frame = tk.Frame(self.preflight_frame)
        self.preflight_action_frame.pack(fill=tk.X, pady=(8, 0))
        self._style_panel(self.preflight_action_frame, self.colors["surface"])

        self.install_models_btn = tk.Button(self.preflight_action_frame, text="Install Missing Models", command=self.install_missing_models)
        self.install_models_btn.pack(side=tk.RIGHT, padx=(8, 0))
        self._style_button(self.install_models_btn, "accent", compact=True)

        self.recheck_preflight_btn = tk.Button(
            self.preflight_action_frame,
            text="Re-Run Startup Check",
            command=lambda: self.run_startup_preflight(interactive=True)
        )
        self.recheck_preflight_btn.pack(side=tk.RIGHT)
        self._style_button(self.recheck_preflight_btn, "secondary", compact=True)

        self._set_video_preflight_summary("Validation not run for current settings.", "Not validated", "gray")
        self._update_model_install_controls({"installable_missing": []})

        self.scene_timeline_frame = tk.Frame(self.scene_timeline_section["body"], padx=18, pady=16)
        self.scene_timeline_frame.pack(fill=tk.BOTH, expand=True)

        self.scene_timeline_header_frame = tk.Frame(self.scene_timeline_frame)
        self.scene_timeline_header_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        scene_intro = self._create_section_intro(
            self.scene_timeline_header_frame,
            "Scene Timeline",
            "Build scenes with one shared prompt box",
            "Use one scene prompt per row, then decide whether each scene renders as text-guided video or image-guided motion."
        )
        self.scene_section_eyebrow_label, self.scene_section_title_label, self.scene_section_copy_label = scene_intro

        self.scene_timeline_stats_frame = tk.Frame(self.scene_timeline_header_frame)
        self.scene_timeline_stats_frame.pack(side=tk.TOP, fill=tk.X, pady=(12, 0))
        _, self.scene_count_value_label = self._create_metric_chip(self.scene_timeline_stats_frame, "Scenes", "0 scenes")
        self.scene_count_value_label.master.pack(side=tk.LEFT, fill=tk.X, expand=True)
        _, self.scene_i2v_count_value_label = self._create_metric_chip(self.scene_timeline_stats_frame, "I2V", "0")
        self.scene_i2v_count_value_label.master.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))

        self.scene_timeline_actions_frame = tk.Frame(self.scene_timeline_frame)
        self.scene_timeline_actions_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        self.add_scene_btn = tk.Button(self.scene_timeline_actions_frame, text="Add Scene", command=self.add_scene_timeline_entry)
        self.add_scene_btn.pack(side=tk.LEFT)
        self.sync_t2v_to_image_queue_btn = tk.Button(self.scene_timeline_actions_frame, text="Send Scene Prompts to Image Phase", command=self.sync_t2v_prompts_to_image_queue)
        self.sync_t2v_to_image_queue_btn.pack(side=tk.LEFT, padx=(10, 0))
        self.auto_assign_scene_images_btn = tk.Button(self.scene_timeline_actions_frame, text="Auto-Assign I2V Images", command=self.auto_assign_i2v_scenes_by_asset_order)
        self.auto_assign_scene_images_btn.pack(side=tk.LEFT, padx=(10, 0))
        self.render_scene_timeline_btn = tk.Button(self.scene_timeline_actions_frame, text="Render Scene Timeline", command=self.start_scene_timeline_render)
        self.render_scene_timeline_btn.pack(side=tk.LEFT, padx=(10, 0))

        self.scene_canvas_shell = tk.Frame(self.scene_timeline_frame)
        self.scene_canvas_shell.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self._style_panel(self.scene_canvas_shell, self.colors["surface"], border=False)

        self.scene_canvas = tk.Canvas(self.scene_canvas_shell, bd=0, highlightthickness=0)
        self.scene_scrollbar = tk.Scrollbar(self.scene_canvas_shell, orient="vertical", command=self.scene_canvas.yview)
        self.scene_scrollable_frame = tk.Frame(self.scene_canvas)

        self.scene_canvas_window_id = self.scene_canvas.create_window((0, 0), window=self.scene_scrollable_frame, anchor="nw")
        self.scene_canvas.configure(yscrollcommand=self.scene_scrollbar.set)
        self.scene_scrollable_frame.bind(
            "<Configure>",
            lambda _event: self.scene_canvas.configure(scrollregion=self.scene_canvas.bbox("all"))
        )
        self.scene_canvas.bind(
            "<Configure>",
            lambda event: self.scene_canvas.itemconfig(self.scene_canvas_window_id, width=event.width)
        )

        self.scene_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(0, 8))
        self.scene_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

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

        self.video_utilities_section = self._create_collapsible_section(
            self.left_frame,
            "video_utilities",
            "Project Utilities",
            meta_text="workflow, status, stitch",
            is_open=False,
            body_expand=False
        )
        self.video_utilities_section["container"].pack(side=tk.BOTTOM, fill=tk.X, padx=18, pady=(0, 12))

        self.video_utilities_frame = tk.Frame(self.video_utilities_section["body"], padx=18, pady=12)
        self.video_utilities_frame.pack(fill=tk.BOTH, expand=True)

        self.video_header_frame = tk.Frame(self.video_utilities_frame, padx=0, pady=0)
        self.video_header_frame.pack(side=tk.TOP, fill=tk.X)

        self.video_header_text_frame = tk.Frame(self.video_header_frame)
        self.video_header_text_frame.pack(side=tk.TOP, fill=tk.X, expand=True)
        header_intro = self._create_section_intro(
            self.video_header_text_frame,
            "Video Studio",
            "Workflow context and delivery controls",
            "Use this drawer for workflow setup, delivery status, and stitch actions while keeping the Scene Timeline as the primary workspace above."
        )
        self.video_header_eyebrow_label, self.video_header_title_label, self.video_header_copy_label = header_intro

        self.video_header_stats_frame = tk.Frame(self.video_header_frame)
        self.video_header_stats_frame.pack(side=tk.TOP, fill=tk.X, pady=(12, 0))
        _, self.prompt_count_value_label = self._create_metric_chip(self.video_header_stats_frame, "Scenes", "0 scenes")
        self.prompt_count_value_label.master.pack(side=tk.LEFT, fill=tk.X, expand=True)
        _, self.selection_count_value_label = self._create_metric_chip(self.video_header_stats_frame, "Stitch", "0 selected")
        self.selection_count_value_label.master.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        self.workflow_toolbar_card = tk.Frame(self.video_utilities_frame, padx=18, pady=10)
        self.workflow_toolbar_card.pack(side=tk.TOP, fill=tk.X, pady=(10, 0))

        self.top_frame = tk.Frame(self.workflow_toolbar_card)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)
        self.top_frame.grid_columnconfigure(1, weight=1)

        self.load_btn = tk.Button(self.top_frame, text="Load Workflow JSON", command=self.load_json_dialog)
        self.load_btn.grid(row=0, column=0, sticky="w")

        self.json_label = tk.Label(self.workflow_toolbar_card, text="No JSON loaded", anchor="w", justify=tk.LEFT)
        self.json_label.pack(side=tk.TOP, fill=tk.X, expand=True, pady=(6, 0))

        self.left_frame.bind("<Configure>", self._on_left_panel_resize)

        self.separator = tk.Frame(self.video_utilities_frame, height=2, bd=1, relief=tk.SUNKEN)
        self.separator.pack(side=tk.TOP, fill=tk.X, pady=8)

        self.bottom_frame = tk.Frame(self.video_utilities_frame, padx=0, pady=0)
        self.bottom_frame.pack(side=tk.TOP, fill=tk.X)
        self.bottom_frame.grid_columnconfigure(1, weight=1)

        self.status_label = tk.Label(self.bottom_frame, text="Status: Idle", fg="blue")
        self.status_label.grid(row=0, column=0, sticky="w")

        self.post_process_frame = tk.Frame(self.video_utilities_frame, padx=0, pady=0)
        self.post_process_frame.pack(side=tk.TOP, fill=tk.X, pady=(10, 0))
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
        # --- Image and Music Tab Content ---
        self.setup_image_tab()
        self.setup_gallery_tab()
        self.setup_music_tab()
        self.setup_chatbot_tab()
        self._reflow_video_left_panel()
        self._apply_static_theme()
        self.notebook.bind("<<NotebookTabChanged>>", self._on_notebook_tab_changed)
        self.root.bind("<Configure>", self._on_window_resize)
        self.root.after(0, self._finalize_initial_layout)

    def _finalize_initial_layout(self):
        self._apply_responsive_section_defaults()
        if not self.remember_section_open_states:
            self._apply_collapsible_launch_defaults()
        self._protect_primary_workspaces()
        self._refresh_responsive_copy()

    def _on_left_panel_resize(self, event):
        available_width = max(320, event.width - 40)
        self.debug_prompt_label.config(wraplength=available_width)

    def setup_image_tab(self):
        self.image_scroll_shell = tk.Frame(self.image_tab, padx=0, pady=0)
        self.image_scroll_shell.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

        self.image_tab_canvas = tk.Canvas(self.image_scroll_shell, bd=0, highlightthickness=0)
        self.image_tab_scrollbar = tk.Scrollbar(self.image_scroll_shell, orient="vertical", command=self.image_tab_canvas.yview)
        self.image_main_frame = tk.Frame(self.image_tab_canvas, padx=0, pady=0)
        self.image_tab_canvas_window_id = self.image_tab_canvas.create_window((0, 0), window=self.image_main_frame, anchor="nw")
        self.image_tab_canvas.configure(yscrollcommand=self.image_tab_scrollbar.set)

        self.image_main_frame.bind(
            "<Configure>",
            lambda _event: self.image_tab_canvas.configure(scrollregion=self.image_tab_canvas.bbox("all"))
        )
        self.image_tab_canvas.bind(
            "<Configure>",
            lambda event: self.image_tab_canvas.itemconfig(self.image_tab_canvas_window_id, width=event.width)
        )

        self.image_tab_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.image_tab_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.image_utilities_section = self._create_collapsible_section(
            self.image_main_frame,
            "image_utilities",
            "Image Utilities",
            meta_text="0 queued • 0 assets",
            is_open=False,
            body_expand=False,
            body_background=self.colors["surface_alt"]
        )
        self.image_utilities_section["container"].pack(fill=tk.X)

        self.image_utilities_frame = tk.Frame(self.image_utilities_section["body"], padx=18, pady=14)
        self.image_utilities_frame.pack(fill=tk.BOTH, expand=True)

        self.image_header_frame = tk.Frame(self.image_utilities_frame)
        self.image_header_frame.pack(fill=tk.X)
        image_tab_intro = self._create_section_intro(
            self.image_header_frame,
            "Image Phase",
            "Create still assets before motion",
            "Generate still-image concepts, import reference frames, and keep assets ready for later image-to-video scenes."
        )
        self.image_header_eyebrow_label, self.image_header_title_label, self.image_header_copy_label = image_tab_intro

        self.image_header_stats_frame = tk.Frame(self.image_header_frame)
        self.image_header_stats_frame.pack(fill=tk.X, pady=(14, 0))
        _, self.image_queue_count_value_label = self._create_metric_chip(self.image_header_stats_frame, "Queue", "0 prompts")
        self.image_queue_count_value_label.master.pack(side=tk.LEFT, fill=tk.X, expand=True)
        _, self.image_asset_count_value_label = self._create_metric_chip(self.image_header_stats_frame, "Assets", "0 images")
        self.image_asset_count_value_label.master.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))

        self.image_settings_section = self._create_collapsible_section(
            self.image_utilities_frame,
            "image_workflow_settings",
            "Workflow Settings",
            meta_text="workflow defaults",
            is_open=False,
            body_expand=False
        )
        self.image_settings_section["container"].pack(side=tk.TOP, fill=tk.X, pady=(14, 0))

        self.image_settings_card = tk.Frame(self.image_settings_section["body"], padx=14, pady=14)
        self.image_settings_card.pack(fill=tk.BOTH, expand=True)
        self._style_panel(self.image_settings_card, self.colors["card"], border=True)

        self.image_settings_title_label = tk.Label(self.image_settings_card, text="Image Workflow Settings")
        self.image_settings_title_label.pack(anchor="w")
        self.image_settings_hint_label = tk.Label(
            self.image_settings_card,
            text="Adjust still-image resolution and sampler settings before running the image queue.",
            anchor="w",
            justify=tk.LEFT,
            wraplength=520
        )
        self.image_settings_hint_label.pack(anchor="w", pady=(4, 10), fill=tk.X)

        image_negative_prompt_frame = tk.Frame(self.image_settings_card)
        image_negative_prompt_frame.pack(fill=tk.X, pady=(0, 8))
        image_negative_prompt_frame.grid_columnconfigure(0, weight=1)
        self.image_negative_prompt_label = tk.Label(image_negative_prompt_frame, text="Negative Prompt")
        self.image_negative_prompt_label.grid(row=0, column=0, sticky="w")
        self.image_negative_prompt_entry = tk.Entry(image_negative_prompt_frame, textvariable=self.image_negative_prompt_var)
        self.image_negative_prompt_entry.grid(row=1, column=0, sticky="ew", pady=(2, 0))

        image_numeric_frame = tk.Frame(self.image_settings_card)
        image_numeric_frame.pack(fill=tk.X, pady=(0, 8))
        image_numeric_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        for index, (label_text, variable) in enumerate([
            ("Width", self.image_width_var),
            ("Height", self.image_height_var),
            ("Steps", self.image_steps_var),
            ("CFG", self.image_cfg_var)
        ]):
            field_frame = tk.Frame(image_numeric_frame)
            field_frame.grid(row=0, column=index, sticky="ew", padx=(0 if index == 0 else 8, 0))
            tk.Label(field_frame, text=label_text).pack(anchor="w")
            tk.Entry(field_frame, textvariable=variable, width=10).pack(fill=tk.X, pady=(2, 0))

        image_sampler_frame = tk.Frame(self.image_settings_card)
        image_sampler_frame.pack(fill=tk.X, pady=(0, 8))
        image_sampler_frame.grid_columnconfigure((0, 1, 2), weight=1)

        for index, (label_text, variable) in enumerate([
            ("Sampler", self.image_sampler_var),
            ("Scheduler", self.image_scheduler_var),
            ("Denoise", self.image_denoise_var)
        ]):
            field_frame = tk.Frame(image_sampler_frame)
            field_frame.grid(row=0, column=index, sticky="ew", padx=(0 if index == 0 else 8, 0))
            tk.Label(field_frame, text=label_text).pack(anchor="w")
            tk.Entry(field_frame, textvariable=variable).pack(fill=tk.X, pady=(2, 0))

        image_model_frame = tk.Frame(self.image_settings_card)
        image_model_frame.pack(fill=tk.X, pady=(0, 8))
        image_model_frame.grid_columnconfigure((0, 1, 2), weight=1)

        for index, (label_text, variable) in enumerate([
            ("CLIP", self.image_clip_name_var),
            ("VAE", self.image_vae_name_var),
            ("UNet", self.image_unet_name_var)
        ]):
            field_frame = tk.Frame(image_model_frame)
            field_frame.grid(row=0, column=index, sticky="ew", padx=(0 if index == 0 else 8, 0))
            tk.Label(field_frame, text=label_text).pack(anchor="w")
        self.image_clip_combo = ttk.Combobox(image_model_frame, textvariable=self.image_clip_name_var, state="readonly")
        self.image_clip_combo.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        self.image_vae_combo = ttk.Combobox(image_model_frame, textvariable=self.image_vae_name_var, state="readonly")
        self.image_vae_combo.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(2, 0))
        self.image_unet_combo = ttk.Combobox(image_model_frame, textvariable=self.image_unet_name_var, state="readonly")
        self.image_unet_combo.grid(row=1, column=2, sticky="ew", padx=(8, 0), pady=(2, 0))

        self.image_settings_actions_frame = tk.Frame(self.image_settings_card)
        self.image_settings_actions_frame.pack(fill=tk.X)
        self.image_settings_actions_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.reset_image_settings_btn = tk.Button(self.image_settings_actions_frame, text="Reset Image Defaults", command=self.reset_image_settings_defaults)
        self.reset_image_settings_btn.grid(row=0, column=0, sticky="ew")

        self.validate_image_btn = tk.Button(self.image_settings_actions_frame, text="Validate Image Settings", command=self.validate_image_setup)
        self.validate_image_btn.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self.refresh_image_models_btn = tk.Button(self.image_settings_actions_frame, text="Refresh Image Models", command=self.refresh_image_model_choices)
        self.refresh_image_models_btn.grid(row=0, column=2, sticky="ew", padx=(6, 0))

        self.image_queue_actions_frame = tk.Frame(self.image_utilities_frame)
        self.image_queue_actions_frame.pack(side=tk.TOP, fill=tk.X, pady=(14, 0))
        self.import_image_btn = tk.Button(self.image_queue_actions_frame, text="Import Images", command=self.import_images_dialog)
        self.import_image_btn.pack(side=tk.LEFT)
        self.add_image_prompt_btn = tk.Button(self.image_queue_actions_frame, text="Add Image Prompt", command=self.add_image_prompt_entry)
        self.add_image_prompt_btn.pack(side=tk.LEFT, padx=(10, 0))
        self.sync_image_to_scene_btn = tk.Button(self.image_queue_actions_frame, text="Send Image Prompts to Scene Timeline", command=self.sync_image_prompts_to_scene_timeline)
        self.sync_image_to_scene_btn.pack(side=tk.LEFT, padx=(10, 0))
        self.run_image_queue_btn = tk.Button(self.image_queue_actions_frame, text="Run Image Queue", command=self.start_image_queue)
        self.run_image_queue_btn.pack(side=tk.LEFT, padx=(10, 0))

        self.image_prompt_queue_section = self._create_collapsible_section(
            self.image_main_frame,
            "image_prompt_queue",
            "Image Prompt Queue",
            meta_text="0 queued",
            is_open=False,
            body_expand=True
        )
        self.image_prompt_queue_section["container"].pack(fill=tk.BOTH, expand=True, pady=(14, 0))

        self.image_prompt_section_frame = tk.Frame(self.image_prompt_queue_section["body"], padx=18, pady=14)
        self.image_prompt_section_frame.pack(fill=tk.BOTH, expand=True)

        self.image_canvas_shell = tk.Frame(self.image_prompt_section_frame)
        self.image_canvas_shell.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self._style_panel(self.image_canvas_shell, self.colors["surface"], border=False)

        self.image_canvas = tk.Canvas(self.image_canvas_shell, bd=0, highlightthickness=0)
        self.image_scrollbar = tk.Scrollbar(self.image_canvas_shell, orient="vertical", command=self.image_canvas.yview)
        self.image_scrollable_frame = tk.Frame(self.image_canvas)

        self.image_canvas_window_id = self.image_canvas.create_window((0, 0), window=self.image_scrollable_frame, anchor="nw")
        self.image_canvas.configure(yscrollcommand=self.image_scrollbar.set)

        def configure_image_scrollable_frame(_event):
            self.image_canvas.configure(scrollregion=self.image_canvas.bbox("all"))

        self.image_scrollable_frame.bind("<Configure>", configure_image_scrollable_frame)

        def configure_image_canvas(event):
            self.image_canvas.itemconfig(self.image_canvas_window_id, width=event.width)

        self.image_canvas.bind("<Configure>", configure_image_canvas)

        self.image_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(0, 8))
        self.image_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.refresh_image_model_choices(initial_load=True)
        self._register_image_persistence_hooks()
        self._update_image_workspace_balance()

    def setup_gallery_tab(self):
        self.right_frame = tk.Frame(self.gallery_tab, padx=0, pady=0)
        self.right_frame.pack(fill=tk.BOTH, expand=True, padx=14, pady=(6, 14))

        self.gallery_header_frame = tk.Frame(self.right_frame, padx=18, pady=14)
        self.gallery_header_frame.pack(side=tk.TOP, fill=tk.X)

        self.gallery_eyebrow_label = tk.Label(self.gallery_header_frame, text="Media Browser")
        self.gallery_eyebrow_label.pack(anchor="w")
        self.gallery_title_label = tk.Label(self.right_frame, text="Project Gallery")
        self.gallery_title_label.pack(in_=self.gallery_header_frame, anchor="w", pady=(4, 0))
        self.gallery_copy_label = tk.Label(
            self.gallery_header_frame,
            text="Review generated scenes, still images, imported media, stitched renders, and finished music videos in one dedicated browser.",
            anchor="w",
            justify=tk.LEFT,
            wraplength=920
        )
        self.gallery_copy_label.pack(anchor="w", pady=(6, 14), fill=tk.X)

        self.gallery_stats_frame = tk.Frame(self.gallery_header_frame)
        self.gallery_stats_frame.pack(fill=tk.X)
        _, self.gallery_scene_count_label = self._create_metric_chip(self.gallery_stats_frame, "Scenes", "0")
        self.gallery_scene_count_label.master.pack(side=tk.LEFT, fill=tk.X, expand=True)
        _, self.gallery_image_count_label = self._create_metric_chip(self.gallery_stats_frame, "Images", "0")
        self.gallery_image_count_label.master.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        _, self.gallery_imported_count_label = self._create_metric_chip(self.gallery_stats_frame, "Imports", "0")
        self.gallery_imported_count_label.master.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        _, self.gallery_stitched_count_label = self._create_metric_chip(self.gallery_stats_frame, "Stitched", "0")
        self.gallery_stitched_count_label.master.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        _, self.gallery_final_count_label = self._create_metric_chip(self.gallery_stats_frame, "Finals", "0")
        self.gallery_final_count_label.master.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.gallery_actions_frame = tk.Frame(self.gallery_header_frame)
        self.gallery_actions_frame.pack(fill=tk.X, pady=(12, 0))
        self.gallery_import_image_btn = tk.Button(self.gallery_actions_frame, text="Import Images", command=self.import_images_dialog)
        self.gallery_import_image_btn.pack(side=tk.LEFT)
        self.gallery_import_btn = tk.Button(self.gallery_actions_frame, text="Import Video", command=self.import_videos_dialog)
        self.gallery_import_btn.pack(side=tk.LEFT, padx=(8, 0))
        gallery_drop_text = "Drag video or image files here too." if self.drag_drop_enabled else "Import project-owned image and video assets here."
        self.gallery_drop_hint_label = tk.Label(self.gallery_actions_frame, text=gallery_drop_text, anchor="w", justify=tk.LEFT)
        self.gallery_drop_hint_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        self.gallery_section = self._create_collapsible_section(
            self.right_frame,
            "gallery_browser",
            "Gallery Browser",
            meta_text="Project media",
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

    def setup_music_tab(self):
        # Left side: Controls
        self.music_left_frame = tk.Frame(self.music_tab, padx=0, pady=0)
        self.music_left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(18, 10), pady=18)

        self.music_scroll_shell = tk.Frame(self.music_left_frame, padx=0, pady=0)
        self.music_scroll_shell.pack(fill=tk.BOTH, expand=True)

        self.music_canvas = tk.Canvas(self.music_scroll_shell, bd=0, highlightthickness=0)
        self.music_scrollbar = tk.Scrollbar(self.music_scroll_shell, orient="vertical", command=self.music_canvas.yview)
        self.music_main_frame = tk.Frame(self.music_canvas, padx=18, pady=14)
        self.music_canvas_window_id = self.music_canvas.create_window((0, 0), window=self.music_main_frame, anchor="nw")
        self.music_canvas.configure(yscrollcommand=self.music_scrollbar.set)

        self.music_main_frame.bind(
            "<Configure>",
            lambda _event: self.music_canvas.configure(scrollregion=self.music_canvas.bbox("all"))
        )
        self.music_canvas.bind(
            "<Configure>",
            lambda event: self.music_canvas.itemconfig(self.music_canvas_window_id, width=event.width)
        )

        self.music_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.music_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Right side: Selected Video Preview
        self.music_right_frame = tk.Frame(self.music_tab, padx=0, pady=0, width=360)
        self.music_right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 18), pady=18)
        self.music_right_frame.pack_propagate(False)

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
        self.music_key_value_label.master.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        _, self.music_sampling_value_label = self._create_metric_chip(self.music_header_stats_frame, "Sampling", "8 st | cfg 1 | euler")
        self.music_sampling_value_label.master.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.music_prompt_section = self._create_collapsible_section(
            self.music_main_frame,
            "music_prompt",
            "Style Direction",
            meta_text="Needs direction",
            is_open=False,
            body_expand=True
        )
        self.music_prompt_section["container"].pack(fill=tk.X, pady=(18, 12))

        self.music_prompt_card = tk.Frame(self.music_prompt_section["body"], padx=16, pady=16)
        self.music_prompt_card.pack(fill=tk.BOTH, expand=True)

        self.music_tags_label = tk.Label(self.music_prompt_card, text="Style Direction")
        self.music_tags_label.pack(anchor="w")
        self.music_tags_hint_label = tk.Label(self.music_prompt_card, text="Describe genre, texture, emotion, and instrumentation.", anchor="w", justify=tk.LEFT)
        self.music_tags_hint_label.pack(anchor="w", pady=(4, 10), fill=tk.X)
        self.music_tags_text = tk.Text(self.music_prompt_card, height=5, width=60)
        self.music_tags_text.pack(fill=tk.X)
        self.music_tags_text.bind("<KeyRelease>", self._on_music_text_changed)
        
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
        self.music_lyrics_text.bind("<KeyRelease>", self._on_music_text_changed)
        
        self.music_duration_var = tk.IntVar(value=120)
        self.music_duration_var.trace_add("write", self._update_music_config_summary)
        self.music_bpm_var = tk.IntVar(value=120)
        self.music_bpm_var.trace_add("write", self._update_music_config_summary)
        self.music_key_var = tk.StringVar(value="C major")
        self.music_key_var.trace_add("write", self._update_music_config_summary)
        self.music_model_variant_var = tk.StringVar(value=MUSIC_MODEL_VARIANT_DEFAULT)
        self.music_model_variant_var.trace_add("write", self._on_music_model_variant_changed)
        self.music_steps_var = tk.IntVar(value=8)
        self.music_steps_var.trace_add("write", self._update_music_config_summary)
        self.music_cfg_var = tk.DoubleVar(value=1.0)
        self.music_cfg_var.trace_add("write", self._update_music_config_summary)
        self.music_sampler_var = tk.StringVar(value="euler")
        self.music_sampler_var.trace_add("write", self._update_music_config_summary)
        self.music_scheduler_var = tk.StringVar(value="simple")
        self.music_denoise_var = tk.DoubleVar(value=1.0)
        self.music_seed_var = tk.IntVar(value=1)
        self.music_randomize_seed_var = tk.BooleanVar(value=True)
        self.music_randomize_seed_var.trace_add("write", self._update_music_seed_entry_state)
        self.music_timesignature_var = tk.StringVar(value="4")
        self.music_language_var = tk.StringVar(value="en")
        self.music_generate_audio_codes_var = tk.BooleanVar(value=True)
        self.music_cfg_scale_var = tk.DoubleVar(value=2.0)
        self.music_temperature_var = tk.DoubleVar(value=0.85)
        self.music_top_p_var = tk.DoubleVar(value=0.9)
        self.music_top_k_var = tk.IntVar(value=0)
        self.music_min_p_var = tk.DoubleVar(value=ACE_STEP_15_MIN_P_DEFAULT)
        self.music_quality_var = tk.StringVar(value="V0")

        model_variant_frame = tk.Frame(self.music_main_frame, padx=16)
        model_variant_frame.pack(fill=tk.X, pady=(0, 4))
        model_variant_label = tk.Label(model_variant_frame, text="Music Model")
        model_variant_label.pack(anchor="w")
        self.music_model_variant_combo = ttk.Combobox(model_variant_frame, textvariable=self.music_model_variant_var, values=MUSIC_MODEL_VARIANT_OPTIONS, state="readonly")
        self.music_model_variant_combo.pack(fill=tk.X, pady=(6, 0))
        self.music_vram_warning_label = tk.Label(model_variant_frame, text="\u26a0 XL models require \u226512 GB VRAM (\u226520 GB recommended)", anchor="w", justify=tk.LEFT, fg="#b8860b", font=("", 8, "italic"))
        self.music_vram_warning_label.pack(anchor="w", pady=(4, 0))

        self.music_playback_section = self._create_collapsible_section(
            self.music_main_frame,
            "music_playback",
            "Playback Parameters",
            meta_text="120s • 120 BPM",
            is_open=False,
            body_expand=True
        )
        self.music_playback_section["container"].pack(fill=tk.X, pady=(0, 12))

        self.music_playback_card = tk.Frame(self.music_playback_section["body"], padx=16, pady=16)
        self.music_playback_card.pack(fill=tk.BOTH, expand=True)

        self.music_settings_frame = tk.Frame(self.music_playback_card)
        self.music_settings_frame.pack(fill=tk.X)
        self.music_settings_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        duration_frame = tk.Frame(self.music_settings_frame)
        duration_frame.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        duration_label = tk.Label(duration_frame, text="Duration (s)")
        duration_label.pack(anchor="w")
        self.music_duration_entry = tk.Entry(duration_frame, textvariable=self.music_duration_var, width=8)
        self.music_duration_entry.pack(fill=tk.X, pady=(6, 0))
        
        bpm_frame = tk.Frame(self.music_settings_frame)
        bpm_frame.grid(row=0, column=1, sticky="ew", padx=8)
        bpm_label = tk.Label(bpm_frame, text="BPM")
        bpm_label.pack(anchor="w")
        self.music_bpm_entry = tk.Entry(bpm_frame, textvariable=self.music_bpm_var, width=8)
        self.music_bpm_entry.pack(fill=tk.X, pady=(6, 0))
        
        key_frame = tk.Frame(self.music_settings_frame)
        key_frame.grid(row=0, column=2, sticky="ew", padx=(8, 0))
        key_label = tk.Label(key_frame, text="Key / Scale")
        key_label.pack(anchor="w")
        self.music_key_entry = tk.Entry(key_frame, textvariable=self.music_key_var, width=15)
        self.music_key_entry.pack(fill=tk.X, pady=(6, 0))

        steps_frame = tk.Frame(self.music_settings_frame)
        steps_frame.grid(row=0, column=3, sticky="ew", padx=(8, 0))
        steps_label = tk.Label(steps_frame, text="Steps")
        steps_label.pack(anchor="w")
        self.music_steps_entry = tk.Entry(steps_frame, textvariable=self.music_steps_var, width=8)
        self.music_steps_entry.pack(fill=tk.X, pady=(6, 0))

        self.music_generation_section = self._create_collapsible_section(
            self.music_main_frame,
            "music_generation",
            "Generation Tuning",
            meta_text="8 st • euler",
            is_open=False,
            body_expand=True
        )
        self.music_generation_section["container"].pack(fill=tk.X, pady=(0, 12))

        self.music_generation_card = tk.Frame(self.music_generation_section["body"], padx=16, pady=16)
        self.music_generation_card.pack(fill=tk.BOTH, expand=True)

        self.music_generation_frame = tk.Frame(self.music_generation_card)
        self.music_generation_frame.pack(fill=tk.X, pady=(14, 0))
        self.music_generation_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        cfg_frame = tk.Frame(self.music_generation_frame)
        cfg_frame.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        cfg_label = tk.Label(cfg_frame, text="Sampler CFG")
        cfg_label.pack(anchor="w")
        self.music_cfg_entry = tk.Entry(cfg_frame, textvariable=self.music_cfg_var, width=8)
        self.music_cfg_entry.pack(fill=tk.X, pady=(6, 0))

        denoise_frame = tk.Frame(self.music_generation_frame)
        denoise_frame.grid(row=0, column=1, sticky="ew", padx=8)
        denoise_label = tk.Label(denoise_frame, text="Denoise")
        denoise_label.pack(anchor="w")
        self.music_denoise_entry = tk.Entry(denoise_frame, textvariable=self.music_denoise_var, width=8)
        self.music_denoise_entry.pack(fill=tk.X, pady=(6, 0))

        timesig_frame = tk.Frame(self.music_generation_frame)
        timesig_frame.grid(row=0, column=2, sticky="ew", padx=8)
        timesig_label = tk.Label(timesig_frame, text="Time Signature")
        timesig_label.pack(anchor="w")
        self.music_timesignature_combo = ttk.Combobox(timesig_frame, textvariable=self.music_timesignature_var, values=MUSIC_TIME_SIGNATURE_OPTIONS, state="readonly")
        self.music_timesignature_combo.pack(fill=tk.X, pady=(6, 0))

        language_frame = tk.Frame(self.music_generation_frame)
        language_frame.grid(row=0, column=3, sticky="ew", padx=(8, 0))
        language_label = tk.Label(language_frame, text="Language")
        language_label.pack(anchor="w")
        self.music_language_combo = ttk.Combobox(language_frame, textvariable=self.music_language_var, values=MUSIC_LANGUAGE_OPTIONS, state="readonly")
        self.music_language_combo.pack(fill=tk.X, pady=(6, 0))

        sampler_frame = tk.Frame(self.music_generation_frame)
        sampler_frame.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(12, 0))
        sampler_label = tk.Label(sampler_frame, text="Sampler")
        sampler_label.pack(anchor="w")
        self.music_sampler_combo = ttk.Combobox(sampler_frame, textvariable=self.music_sampler_var, values=MUSIC_SAMPLER_OPTIONS, state="readonly")
        self.music_sampler_combo.pack(fill=tk.X, pady=(6, 0))

        scheduler_frame = tk.Frame(self.music_generation_frame)
        scheduler_frame.grid(row=1, column=1, sticky="ew", padx=8, pady=(12, 0))
        scheduler_label = tk.Label(scheduler_frame, text="Scheduler")
        scheduler_label.pack(anchor="w")
        self.music_scheduler_combo = ttk.Combobox(scheduler_frame, textvariable=self.music_scheduler_var, values=MUSIC_SCHEDULER_OPTIONS, state="readonly")
        self.music_scheduler_combo.pack(fill=tk.X, pady=(6, 0))

        seed_frame = tk.Frame(self.music_generation_frame)
        seed_frame.grid(row=1, column=2, sticky="ew", padx=8, pady=(12, 0))
        seed_label = tk.Label(seed_frame, text="Seed")
        seed_label.pack(anchor="w")
        self.music_seed_entry = tk.Entry(seed_frame, textvariable=self.music_seed_var, width=12)
        self.music_seed_entry.pack(fill=tk.X, pady=(6, 0))

        quality_frame = tk.Frame(self.music_generation_frame)
        quality_frame.grid(row=1, column=3, sticky="ew", padx=(8, 0), pady=(12, 0))
        quality_label = tk.Label(quality_frame, text="MP3 Quality")
        quality_label.pack(anchor="w")
        self.music_quality_combo = ttk.Combobox(quality_frame, textvariable=self.music_quality_var, values=MUSIC_MP3_QUALITY_OPTIONS, state="readonly")
        self.music_quality_combo.pack(fill=tk.X, pady=(6, 0))

        self.music_toggle_frame = tk.Frame(self.music_generation_card)
        self.music_toggle_frame.pack(fill=tk.X, pady=(14, 0))
        self.music_randomize_seed_cb = tk.Checkbutton(self.music_toggle_frame, text="Randomize Seed Each Run", variable=self.music_randomize_seed_var)
        self.music_randomize_seed_cb.pack(side=tk.LEFT)
        self.music_generate_codes_cb = tk.Checkbutton(self.music_toggle_frame, text="Generate Audio Codes", variable=self.music_generate_audio_codes_var)
        self.music_generate_codes_cb.pack(side=tk.LEFT, padx=(16, 0))

        self.music_advanced_section = self._create_collapsible_section(
            self.music_main_frame,
            "music_advanced",
            "Advanced Sampling",
            meta_text="Top P 0.9 • Min P 0",
            is_open=False,
            body_expand=True
        )
        self.music_advanced_section["container"].pack(fill=tk.X, pady=(0, 12))

        self.music_advanced_card = tk.Frame(self.music_advanced_section["body"], padx=16, pady=16)
        self.music_advanced_card.pack(fill=tk.BOTH, expand=True)

        self.music_advanced_tuning_hint_label = tk.Label(self.music_advanced_card, text="Refine language-model guidance, token sampling, and probability cutoffs.", anchor="w", justify=tk.LEFT)
        self.music_advanced_tuning_hint_label.pack(anchor="w", pady=(4, 0), fill=tk.X)

        self.music_advanced_frame = tk.Frame(self.music_advanced_card)
        self.music_advanced_frame.pack(fill=tk.X, pady=(12, 0))
        self.music_advanced_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        cfg_scale_frame = tk.Frame(self.music_advanced_frame)
        cfg_scale_frame.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        cfg_scale_label = tk.Label(cfg_scale_frame, text="Code CFG")
        cfg_scale_label.pack(anchor="w")
        self.music_cfg_scale_entry = tk.Entry(cfg_scale_frame, textvariable=self.music_cfg_scale_var, width=8)
        self.music_cfg_scale_entry.pack(fill=tk.X, pady=(6, 0))

        temperature_frame = tk.Frame(self.music_advanced_frame)
        temperature_frame.grid(row=0, column=1, sticky="ew", padx=8)
        temperature_label = tk.Label(temperature_frame, text="Temperature")
        temperature_label.pack(anchor="w")
        self.music_temperature_entry = tk.Entry(temperature_frame, textvariable=self.music_temperature_var, width=8)
        self.music_temperature_entry.pack(fill=tk.X, pady=(6, 0))

        top_p_frame = tk.Frame(self.music_advanced_frame)
        top_p_frame.grid(row=0, column=2, sticky="ew", padx=8)
        top_p_label = tk.Label(top_p_frame, text="Top P")
        top_p_label.pack(anchor="w")
        self.music_top_p_entry = tk.Entry(top_p_frame, textvariable=self.music_top_p_var, width=8)
        self.music_top_p_entry.pack(fill=tk.X, pady=(6, 0))

        top_k_frame = tk.Frame(self.music_advanced_frame)
        top_k_frame.grid(row=0, column=3, sticky="ew", padx=8)
        top_k_label = tk.Label(top_k_frame, text="Top K")
        top_k_label.pack(anchor="w")
        self.music_top_k_entry = tk.Entry(top_k_frame, textvariable=self.music_top_k_var, width=8)
        self.music_top_k_entry.pack(fill=tk.X, pady=(6, 0))

        min_p_frame = tk.Frame(self.music_advanced_frame)
        min_p_frame.grid(row=0, column=4, sticky="ew", padx=(8, 0))
        min_p_label = tk.Label(min_p_frame, text="Min P")
        min_p_label.pack(anchor="w")
        self.music_min_p_entry = tk.Entry(min_p_frame, textvariable=self.music_min_p_var, width=8)
        self.music_min_p_entry.pack(fill=tk.X, pady=(6, 0))
        
        self.music_actions_section = self._create_collapsible_section(
            self.music_main_frame,
            "music_actions",
            "Run and Review",
            meta_text="Idle",
            is_open=False,
            body_expand=True
        )
        self.music_actions_section["container"].pack(fill=tk.X)

        self.music_actions_card = tk.Frame(self.music_actions_section["body"], padx=16, pady=16)
        self.music_actions_card.pack(fill=tk.BOTH, expand=True)

        self.music_action_frame = tk.Frame(self.music_actions_card)
        self.music_action_frame.pack(fill=tk.X, pady=(16, 0))
        self.music_action_frame.grid_columnconfigure((0, 1), weight=1)
        self.music_primary_actions_frame = tk.Frame(self.music_action_frame)
        self.music_primary_actions_frame.grid(row=0, column=0, sticky="w")
        self.music_secondary_actions_frame = tk.Frame(self.music_action_frame)
        self.music_secondary_actions_frame.grid(row=0, column=1, sticky="e")
        
        self.gen_music_btn = tk.Button(self.music_primary_actions_frame, text="Generate Music", command=self.generate_music)
        self.gen_music_btn.pack(side=tk.LEFT)

        self.import_audio_btn = tk.Button(self.music_primary_actions_frame, text="Import Audio", command=self.import_audio_dialog)
        self.import_audio_btn.pack(side=tk.LEFT, padx=(8, 0))
        
        self.preview_music_btn = tk.Button(self.music_primary_actions_frame, text="Preview Audio", command=self.preview_audio, state=tk.DISABLED)
        self.preview_music_btn.pack(side=tk.LEFT, padx=(8, 0))

        music_drop_text = "Drag an audio file here to link it instantly." if self.drag_drop_enabled else "Import your own audio if you want to skip generation."
        self.music_drop_hint_label = tk.Label(self.music_actions_card, text=music_drop_text, anchor="w", justify=tk.LEFT, wraplength=420)
        self.music_drop_hint_label.pack(anchor="w", pady=(10, 0), fill=tk.X)
        
        self.preview_final_btn = tk.Button(self.music_secondary_actions_frame, text="Preview Final Video", command=self.preview_final_video, state=tk.DISABLED)
        self.preview_final_btn.pack(side=tk.RIGHT)
        
        self.merge_music_btn = tk.Button(self.music_secondary_actions_frame, text="Approve & Merge with Video", command=self.merge_audio_video, state=tk.DISABLED)
        self.merge_music_btn.pack(side=tk.RIGHT, padx=(0, 8))
        
        self.music_status_label = tk.Label(self.music_actions_card, text="Status: Idle", fg="blue")
        self.music_status_label.pack(anchor="w", pady=(14, 0))
        
        # --- Selected Video Info ---
        self.music_media_state_section = self._create_collapsible_section(
            self.music_right_frame,
            "music_media_state",
            "Linked Media",
            meta_text="No clip linked",
            is_open=False,
            body_expand=True,
            body_background=self.colors["surface_alt"]
        )
        self.music_media_state_section["container"].pack(fill=tk.X)

        self.music_media_state_card = tk.Frame(self.music_media_state_section["body"], padx=16, pady=16)
        self.music_media_state_card.pack(fill=tk.BOTH, expand=True)

        self.music_sidebar_eyebrow_label = tk.Label(self.music_media_state_card, text="Linked Media")
        self.music_sidebar_eyebrow_label.pack(anchor="w")
        self.music_sidebar_title_label = tk.Label(self.music_media_state_card, text="Selected Video")
        self.music_sidebar_title_label.pack(anchor="w", pady=(4, 0))
        self.music_sidebar_copy_label = tk.Label(
            self.music_media_state_card,
            text="This panel tracks the source clip, active audio, and final export state for the current music pass.",
            anchor="w",
            justify=tk.LEFT,
            wraplength=320
        )
        self.music_sidebar_copy_label.pack(anchor="w", pady=(6, 14), fill=tk.X)

        self.music_sidebar_summary_frame = tk.Frame(self.music_media_state_card)
        self.music_sidebar_summary_frame.pack(fill=tk.X)
        _, self.music_selected_clip_value_label = self._create_metric_chip(self.music_sidebar_summary_frame, "Clip", "No clip linked")
        self.music_selected_clip_value_label.master.pack(fill=tk.X)
        _, self.music_audio_state_value_label = self._create_metric_chip(self.music_sidebar_summary_frame, "Audio", "No audio linked")
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
            text="Select a stitched or imported clip from the gallery to lock music direction to a specific cut.",
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

        self._register_music_persistence_hooks()
        self._update_music_workspace_balance()
        self._reset_music_settings_to_loaded_workflow()
        self._update_music_config_summary()
        self._refresh_music_sidebar_state()

    def setup_chatbot_tab(self):
        self.chatbot_shell = tk.Frame(self.chatbot_tab, padx=18, pady=18)
        self.chatbot_shell.pack(fill=tk.BOTH, expand=True)
        self._style_panel(self.chatbot_shell, self.colors["bg"])

        self.chatbot_header_frame = tk.Frame(self.chatbot_shell)
        self.chatbot_header_frame.pack(fill=tk.X)
        self._style_panel(self.chatbot_header_frame, self.colors["bg"])
        chatbot_intro = self._create_section_intro(
            self.chatbot_header_frame,
            "Creative Assistant",
            "Talk through the music video before generating prompts",
            "Use the assistant like a real conversation first. Chat naturally about concept, pacing, scenes, and visual direction, then create prompt drafts only when you are ready."
        )
        self.chatbot_header_eyebrow_label, self.chatbot_header_title_label, self.chatbot_header_copy_label = chatbot_intro

        self.chatbot_header_stats_frame = tk.Frame(self.chatbot_header_frame)
        self.chatbot_header_stats_frame.pack(fill=tk.X, pady=(14, 0))
        self._style_panel(self.chatbot_header_stats_frame, self.colors["bg"])
        _, self.chatbot_runtime_state_value_label = self._create_metric_chip(self.chatbot_header_stats_frame, "Readiness", self._get_chatbot_readiness_summary())
        self.chatbot_runtime_state_value_label.master.pack(side=tk.LEFT, fill=tk.X, expand=True)
        _, self.chatbot_backend_value_label = self._create_metric_chip(self.chatbot_header_stats_frame, "Backend", self._get_chatbot_backend_mode_label())
        self.chatbot_backend_value_label.master.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        _, self.chatbot_next_step_value_label = self._create_metric_chip(self.chatbot_header_stats_frame, "Next Step", self._get_chatbot_next_step_text())
        self.chatbot_next_step_value_label.master.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        _, self.chatbot_model_value_label = self._create_metric_chip(self.chatbot_header_stats_frame, "Model", "Not installed")
        self.chatbot_model_value_label.master.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        _, self.chatbot_destination_value_label = self._create_metric_chip(self.chatbot_header_stats_frame, "Storage", self.chatbot_model_root or "Unset")
        self.chatbot_destination_value_label.master.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.chatbot_workspace_frame = tk.Frame(self.chatbot_shell)
        self.chatbot_workspace_frame.pack(fill=tk.BOTH, expand=True)
        self._style_panel(self.chatbot_workspace_frame, self.colors["bg"])
        self.chatbot_workspace_frame.grid_columnconfigure(0, weight=1)
        self.chatbot_workspace_frame.grid_rowconfigure(0, weight=1)
        self.chatbot_workspace_frame.grid_rowconfigure(1, weight=0)

        self.chatbot_focus_workspace_section = self._create_collapsible_section(
            self.chatbot_workspace_frame,
            "chatbot_focus_workspace",
            "Creative Workspace",
            meta_text=self._get_chatbot_focus_section_meta(),
            is_open=True,
            body_expand=True,
            body_background=self.colors["surface"],
        )
        self.chatbot_focus_workspace_section["container"].grid(row=0, column=0, sticky="nsew", pady=(0, 12))
        self._style_panel(self.chatbot_focus_workspace_section["container"], self.colors["surface"], border=True)
        self._style_panel(self.chatbot_focus_workspace_section["header"], self.colors["surface"])
        self._style_panel(self.chatbot_focus_workspace_section["body"], self.colors["surface"])
        self._style_label(self.chatbot_focus_workspace_section["title"], "section", self.chatbot_focus_workspace_section["header"].cget("bg"))
        self._style_label(self.chatbot_focus_workspace_section["meta"], "muted", self.chatbot_focus_workspace_section["header"].cget("bg"))
        self._style_button(self.chatbot_focus_workspace_section["toggle"], "ghost", compact=True)

        self.chatbot_focus_workspace_frame = tk.Frame(self.chatbot_focus_workspace_section["body"])
        self.chatbot_focus_workspace_frame.pack(fill=tk.BOTH, expand=True)
        self._style_panel(self.chatbot_focus_workspace_frame, self.colors["surface"])
        self.chatbot_focus_workspace_frame.grid_columnconfigure(0, weight=5)
        self.chatbot_focus_workspace_frame.grid_columnconfigure(1, weight=6)
        self.chatbot_focus_workspace_frame.grid_rowconfigure(0, weight=1)

        self.chatbot_workflow_card = tk.Frame(self.chatbot_focus_workspace_frame, padx=18, pady=16)
        self.chatbot_workflow_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self._style_panel(self.chatbot_workflow_card, self.colors["surface"], border=True)

        self.chatbot_briefing_card = self.chatbot_workflow_card
        self._style_panel(self.chatbot_briefing_card, self.colors["surface"])

        self.chatbot_workflow_title_label = tk.Label(self.chatbot_briefing_card, text="Workflow")
        self.chatbot_workflow_title_label.pack(anchor="w")
        self._style_label(self.chatbot_workflow_title_label, "section", self.chatbot_briefing_card.cget("bg"))
        self.chatbot_workflow_hint_label = tk.Label(
            self.chatbot_briefing_card,
            text="Shape the request, choose the mode, and decide when to turn exploration into a structured result.",
            anchor="w",
            justify=tk.LEFT,
            wraplength=520,
        )
        self.chatbot_workflow_hint_label.pack(anchor="w", fill=tk.X, pady=(6, 10))
        self._style_label(self.chatbot_workflow_hint_label, "muted", self.chatbot_briefing_card.cget("bg"))

        self.chatbot_task_var = tk.StringVar(value=CHATBOT_TASK_CHAT)
        self.chatbot_mode_row = tk.Frame(self.chatbot_briefing_card)
        self.chatbot_mode_row.pack(fill=tk.X)
        self._style_panel(self.chatbot_mode_row, self.chatbot_briefing_card.cget("bg"))
        self.chatbot_mode_label = tk.Label(self.chatbot_mode_row, text="Mode")
        self.chatbot_mode_label.pack(side=tk.LEFT)
        self._style_label(self.chatbot_mode_label, "body_strong", self.chatbot_mode_row.cget("bg"))
        self.chatbot_task_combo = ttk.Combobox(
            self.chatbot_mode_row,
            textvariable=self.chatbot_task_var,
            values=self._get_chatbot_task_options(),
            state="readonly",
            width=28,
        )
        self.chatbot_task_combo.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
        self.chatbot_task_combo.configure(style="TCombobox")
        self.chatbot_task_combo.bind("<<ComboboxSelected>>", self._on_chatbot_task_changed)

        self.chatbot_model_family_var = tk.StringVar(value=self.chatbot_model_family or DEFAULT_CHATBOT_MODEL_FAMILY)
        self.chatbot_model_family_row = tk.Frame(self.chatbot_briefing_card)
        self.chatbot_model_family_row.pack(fill=tk.X, pady=(8, 0))
        self._style_panel(self.chatbot_model_family_row, self.chatbot_briefing_card.cget("bg"))
        self.chatbot_model_family_label = tk.Label(self.chatbot_model_family_row, text="Model")
        self.chatbot_model_family_label.pack(side=tk.LEFT)
        self._style_label(self.chatbot_model_family_label, "body_strong", self.chatbot_model_family_row.cget("bg"))
        self.chatbot_model_family_combo = ttk.Combobox(
            self.chatbot_model_family_row,
            textvariable=self.chatbot_model_family_var,
            values=[CHATBOT_MODEL_FAMILY_QWEN3, CHATBOT_MODEL_FAMILY_GEMMA4],
            state="readonly",
            width=28,
        )
        self.chatbot_model_family_combo.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
        self.chatbot_model_family_combo.configure(style="TCombobox")
        self.chatbot_model_family_combo.bind("<<ComboboxSelected>>", self._on_chatbot_model_family_changed)

        self.chatbot_gemma4_tag_var = tk.StringVar(value=self.chatbot_gemma4_ollama_tag or DEFAULT_GEMMA4_OLLAMA_TAG)
        self.chatbot_gemma4_tag_row = tk.Frame(self.chatbot_briefing_card)
        self.chatbot_gemma4_tag_row.pack(fill=tk.X, pady=(6, 0))
        self._style_panel(self.chatbot_gemma4_tag_row, self.chatbot_briefing_card.cget("bg"))
        self.chatbot_gemma4_tag_label = tk.Label(self.chatbot_gemma4_tag_row, text="Tag")
        self.chatbot_gemma4_tag_label.pack(side=tk.LEFT)
        self._style_label(self.chatbot_gemma4_tag_label, "body_strong", self.chatbot_gemma4_tag_row.cget("bg"))
        self.chatbot_gemma4_tag_combo = ttk.Combobox(
            self.chatbot_gemma4_tag_row,
            textvariable=self.chatbot_gemma4_tag_var,
            values=GEMMA4_OLLAMA_TAG_OPTIONS,
            state="readonly",
            width=28,
        )
        self.chatbot_gemma4_tag_combo.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
        self.chatbot_gemma4_tag_combo.configure(style="TCombobox")
        self.chatbot_gemma4_tag_combo.bind("<<ComboboxSelected>>", self._on_chatbot_gemma4_tag_changed)
        if self.chatbot_model_family != CHATBOT_MODEL_FAMILY_GEMMA4:
            self.chatbot_gemma4_tag_row.pack_forget()

        self.chatbot_mode_summary_label = tk.Label(self.chatbot_briefing_card, text=self._get_chatbot_task_primary_action_copy(CHATBOT_TASK_CHAT), anchor="w", justify=tk.LEFT, wraplength=860)
        self.chatbot_mode_summary_label.pack(anchor="w", fill=tk.X, pady=(8, 0))
        self._style_label(self.chatbot_mode_summary_label, "muted", self.chatbot_briefing_card.cget("bg"))

        self.chatbot_task_hint_label = tk.Label(self.chatbot_briefing_card, text=self._get_chatbot_task_description(CHATBOT_TASK_CHAT), anchor="w", justify=tk.LEFT, wraplength=860)
        self.chatbot_task_hint_label.pack(anchor="w", fill=tk.X, pady=(6, 10))
        self._style_label(self.chatbot_task_hint_label, "body", self.chatbot_briefing_card.cget("bg"))

        self.chatbot_briefing_title_label = tk.Label(self.chatbot_briefing_card, text="Message")
        self.chatbot_briefing_title_label.pack(anchor="w")
        self._style_label(self.chatbot_briefing_title_label, "body_strong", self.chatbot_briefing_card.cget("bg"))
        self.chatbot_briefing_hint_label = tk.Label(self.chatbot_briefing_card, text=self._get_chatbot_task_briefing_hint(CHATBOT_TASK_CHAT), anchor="w", justify=tk.LEFT, wraplength=860)
        self.chatbot_briefing_hint_label.pack(anchor="w", fill=tk.X, pady=(6, 10))
        self._style_label(self.chatbot_briefing_hint_label, "muted", self.chatbot_briefing_card.cget("bg"))

        self.chatbot_task_actions_frame = tk.Frame(self.chatbot_briefing_card)
        self.chatbot_task_actions_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(12, 0))
        self._style_panel(self.chatbot_task_actions_frame, self.chatbot_briefing_card.cget("bg"))
        self.chatbot_send_btn = tk.Button(self.chatbot_task_actions_frame, text="Send", command=self._handle_chatbot_send, state=tk.DISABLED)
        self.chatbot_send_btn.pack(side=tk.LEFT)
        self.chatbot_scene_plan_btn = tk.Button(self.chatbot_task_actions_frame, text="Plan Scenes", command=self._handle_chatbot_plan_scenes, state=tk.DISABLED)
        self.chatbot_scene_plan_btn.pack(side=tk.LEFT, padx=(10, 0))
        self.chatbot_generate_btn = tk.Button(self.chatbot_task_actions_frame, text="Generate Prompt Draft", command=self._handle_chatbot_generate, state=tk.DISABLED)
        self.chatbot_generate_btn.pack(side=tk.LEFT, padx=(10, 0))
        self.chatbot_finalize_song_btn = tk.Button(self.chatbot_task_actions_frame, text="Finalize Song", command=self._handle_chatbot_finalize_song, state=tk.DISABLED)
        self.chatbot_finalize_song_btn.pack(side=tk.LEFT, padx=(10, 0))
        self.chatbot_new_chat_btn = tk.Button(self.chatbot_task_actions_frame, text="New Chat", command=self._start_new_chatbot_conversation)
        self.chatbot_new_chat_btn.pack(side=tk.LEFT, padx=(10, 0))
        self.chatbot_clear_chat_btn = tk.Button(self.chatbot_task_actions_frame, text="Clear Chat", command=self._clear_chatbot_conversation)
        self.chatbot_clear_chat_btn.pack(side=tk.LEFT, padx=(10, 0))

        self.chatbot_briefing_text = tk.Text(self.chatbot_briefing_card, height=10, wrap="word")
        self.chatbot_briefing_text.pack(fill=tk.BOTH, expand=True)
        self._style_text_input(self.chatbot_briefing_text, multiline=True)

        self.chatbot_output_card = tk.Frame(self.chatbot_focus_workspace_frame, padx=18, pady=16)
        self.chatbot_output_card.grid(row=0, column=1, sticky="nsew")
        self._style_panel(self.chatbot_output_card, self.colors["surface"], border=True)
        self.chatbot_output_title_label = tk.Label(self.chatbot_output_card, text="Assistant Output")
        self.chatbot_output_title_label.pack(anchor="w")
        self._style_label(self.chatbot_output_title_label, "section", self.chatbot_output_card.cget("bg"))
        self.chatbot_output_hint_label = tk.Label(self.chatbot_output_card, text=self._get_chatbot_task_output_hint(CHATBOT_TASK_CHAT), anchor="w", justify=tk.LEFT, wraplength=620)
        self.chatbot_output_hint_label.pack(anchor="w", fill=tk.X, pady=(6, 10))
        self._style_label(self.chatbot_output_hint_label, "muted", self.chatbot_output_card.cget("bg"))
        self.chatbot_result_status_label = tk.Label(self.chatbot_output_card, text=self._get_chatbot_idle_status_text(CHATBOT_TASK_CHAT), anchor="w", justify=tk.LEFT, wraplength=620)
        self.chatbot_result_status_label.pack(anchor="w", fill=tk.X, pady=(0, 10))
        self._style_label(self.chatbot_result_status_label, "body", self.chatbot_output_card.cget("bg"))

        self.chatbot_artifact_review_card = tk.Frame(self.chatbot_output_card, padx=14, pady=12)
        self._style_panel(self.chatbot_artifact_review_card, self.colors["surface_soft"], border=True)
        self.chatbot_artifact_review_eyebrow_label = tk.Label(self.chatbot_artifact_review_card, text="Selected Result", anchor="w")
        self.chatbot_artifact_review_eyebrow_label.pack(anchor="w")
        self._style_label(self.chatbot_artifact_review_eyebrow_label, "muted", self.chatbot_artifact_review_card.cget("bg"))
        self.chatbot_artifact_review_eyebrow_label.configure(font=self.fonts["micro"])
        self.chatbot_artifact_review_title_label = tk.Label(self.chatbot_artifact_review_card, text="No saved result selected", anchor="w", justify=tk.LEFT, wraplength=620)
        self.chatbot_artifact_review_title_label.pack(anchor="w", fill=tk.X, pady=(4, 0))
        self._style_label(self.chatbot_artifact_review_title_label, "body_strong", self.chatbot_artifact_review_card.cget("bg"))
        self.chatbot_artifact_review_meta_label = tk.Label(self.chatbot_artifact_review_card, text="", anchor="w", justify=tk.LEFT, wraplength=620)
        self.chatbot_artifact_review_meta_label.pack(anchor="w", fill=tk.X, pady=(4, 0))
        self._style_label(self.chatbot_artifact_review_meta_label, "muted", self.chatbot_artifact_review_card.cget("bg"))
        self.chatbot_artifact_review_destination_label = tk.Label(self.chatbot_artifact_review_card, text="", anchor="w", justify=tk.LEFT, wraplength=620)
        self.chatbot_artifact_review_destination_label.pack(anchor="w", fill=tk.X, pady=(4, 0))
        self._style_label(self.chatbot_artifact_review_destination_label, "body", self.chatbot_artifact_review_card.cget("bg"))
        self.chatbot_artifact_review_brief_label = tk.Label(self.chatbot_artifact_review_card, text="", anchor="w", justify=tk.LEFT, wraplength=620)
        self.chatbot_artifact_review_brief_label.pack(anchor="w", fill=tk.X, pady=(8, 0))
        self._style_label(self.chatbot_artifact_review_brief_label, "muted", self.chatbot_artifact_review_card.cget("bg"))
        self.chatbot_artifact_review_preview_label = tk.Label(self.chatbot_artifact_review_card, text="", anchor="w", justify=tk.LEFT, wraplength=620)
        self.chatbot_artifact_review_preview_label.pack(anchor="w", fill=tk.X, pady=(8, 0))
        self._style_label(self.chatbot_artifact_review_preview_label, "body", self.chatbot_artifact_review_card.cget("bg"))

        self.chatbot_output_actions_frame = tk.Frame(self.chatbot_output_card)
        self.chatbot_output_actions_frame.pack(fill=tk.X, pady=(0, 10))
        self._style_panel(self.chatbot_output_actions_frame, self.chatbot_output_card.cget("bg"))
        self.chatbot_output_mode_btn = tk.Button(self.chatbot_output_actions_frame, text="Show Raw JSON", command=self._toggle_chatbot_output_view)
        self.chatbot_output_mode_btn.pack(side=tk.LEFT)
        self.chatbot_copy_output_btn = tk.Button(self.chatbot_output_actions_frame, text="Copy Result", command=self._copy_chatbot_output_to_clipboard, state=tk.DISABLED)
        self.chatbot_copy_output_btn.pack(side=tk.LEFT, padx=(10, 0))
        self.chatbot_apply_btn = tk.Button(self.chatbot_output_actions_frame, text="Add Prompt to Image Queue", command=self.apply_chatbot_result_to_image_queue, state=tk.DISABLED)
        self.chatbot_apply_btn.pack(side=tk.LEFT, padx=(10, 0))
        self.chatbot_apply_scene_btn = tk.Button(self.chatbot_output_actions_frame, text="Add Prompt to Scene Timeline", command=self.apply_chatbot_result_to_scene_timeline, state=tk.DISABLED)
        self.chatbot_apply_scene_btn.pack(side=tk.LEFT, padx=(10, 0))
        self.chatbot_apply_music_btn = tk.Button(self.chatbot_output_actions_frame, text="Send to Music Tab", command=self.apply_chatbot_result_to_music_tab, state=tk.DISABLED)
        self.chatbot_apply_music_btn.pack(side=tk.LEFT, padx=(10, 0))

        self.chatbot_transcript_shell = tk.Frame(self.chatbot_output_card)
        self.chatbot_transcript_shell.pack(fill=tk.BOTH, expand=True)
        self._style_panel(self.chatbot_transcript_shell, self.colors["card"])
        self.chatbot_transcript_last_signature = ()

        self.chatbot_transcript_canvas = tk.Canvas(self.chatbot_transcript_shell, bd=0, highlightthickness=0, bg=self.colors["card"])
        self.chatbot_transcript_scrollbar = tk.Scrollbar(self.chatbot_transcript_shell, orient="vertical", command=self._on_chatbot_transcript_scrollbar)
        self.chatbot_transcript_frame = tk.Frame(self.chatbot_transcript_canvas)
        self._style_panel(self.chatbot_transcript_frame, self.colors["card"])
        self.chatbot_transcript_window_id = self.chatbot_transcript_canvas.create_window((0, 0), window=self.chatbot_transcript_frame, anchor="nw")
        self.chatbot_transcript_canvas.configure(yscrollcommand=self.chatbot_transcript_scrollbar.set)
        self.chatbot_transcript_frame.bind(
            "<Configure>",
            lambda _event: self.chatbot_transcript_canvas.configure(scrollregion=self.chatbot_transcript_canvas.bbox("all"))
        )
        self.chatbot_transcript_canvas.bind(
            "<Configure>",
            lambda event: self.chatbot_transcript_canvas.itemconfig(self.chatbot_transcript_window_id, width=event.width)
        )
        self.chatbot_transcript_shell.bind("<MouseWheel>", self._on_chatbot_transcript_mousewheel)
        self.chatbot_transcript_shell.bind("<Button-4>", self._on_chatbot_transcript_mousewheel)
        self.chatbot_transcript_shell.bind("<Button-5>", self._on_chatbot_transcript_mousewheel)
        self.chatbot_transcript_frame.bind("<MouseWheel>", self._on_chatbot_transcript_mousewheel)
        self.chatbot_transcript_frame.bind("<Button-4>", self._on_chatbot_transcript_mousewheel)
        self.chatbot_transcript_frame.bind("<Button-5>", self._on_chatbot_transcript_mousewheel)
        self.chatbot_transcript_canvas.bind("<MouseWheel>", self._on_chatbot_transcript_mousewheel)
        self.chatbot_transcript_canvas.bind("<Button-4>", self._on_chatbot_transcript_mousewheel)
        self.chatbot_transcript_canvas.bind("<Button-5>", self._on_chatbot_transcript_mousewheel)
        self.chatbot_transcript_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.chatbot_transcript_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.chatbot_history_section = self._create_collapsible_section(
            self.chatbot_workspace_frame,
            "chatbot_history",
            "Saved Results",
            meta_text="No saved results",
            is_open=False,
            body_expand=False,
            body_background=self.colors["surface"],
        )
        self.chatbot_history_section["container"].grid(row=1, column=0, sticky="ew", pady=(0, 12))
        self._style_panel(self.chatbot_history_section["container"], self.colors["surface"], border=True)
        self._style_panel(self.chatbot_history_section["header"], self.colors["surface"])
        self._style_panel(self.chatbot_history_section["body"], self.colors["surface"])
        self._style_label(self.chatbot_history_section["title"], "section", self.chatbot_history_section["header"].cget("bg"))
        self._style_label(self.chatbot_history_section["meta"], "muted", self.chatbot_history_section["header"].cget("bg"))
        self._style_button(self.chatbot_history_section["toggle"], "ghost", compact=True)

        self.chatbot_history_card = self.chatbot_history_section["body"]
        self.chatbot_apply_hint_label = tk.Label(self.chatbot_history_card, text="Saved scene plans and prompt drafts stay here for quick compare-and-reload. Selecting one reloads it into the review surface above the transcript.", anchor="w", justify=tk.LEFT, wraplength=860)
        self.chatbot_apply_hint_label.pack(anchor="w", fill=tk.X, pady=(0, 10))
        self._style_label(self.chatbot_apply_hint_label, "muted", self.chatbot_history_card.cget("bg"))
        self.chatbot_history_shell = tk.Frame(self.chatbot_history_card)
        self.chatbot_history_shell.pack(fill=tk.BOTH, expand=True)
        self._style_panel(self.chatbot_history_shell, self.chatbot_history_card.cget("bg"))
        self.chatbot_history_canvas = tk.Canvas(self.chatbot_history_shell, bd=0, highlightthickness=0, bg=self.colors["surface"], height=220)
        self.chatbot_history_scrollbar = tk.Scrollbar(self.chatbot_history_shell, orient="vertical", command=self.chatbot_history_canvas.yview)
        self.chatbot_history_frame = tk.Frame(self.chatbot_history_canvas)
        self._style_panel(self.chatbot_history_frame, self.colors["surface"])
        self.chatbot_history_window_id = self.chatbot_history_canvas.create_window((0, 0), window=self.chatbot_history_frame, anchor="nw")
        self.chatbot_history_canvas.configure(yscrollcommand=self.chatbot_history_scrollbar.set)
        self.chatbot_history_frame.bind(
            "<Configure>",
            lambda _event: self.chatbot_history_canvas.configure(scrollregion=self.chatbot_history_canvas.bbox("all"))
        )
        self.chatbot_history_canvas.bind(
            "<Configure>",
            lambda event: self.chatbot_history_canvas.itemconfig(self.chatbot_history_window_id, width=event.width)
        )
        self.chatbot_history_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.chatbot_history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ── Autonomous Mode Panel ──
        self.chatbot_workspace_frame.grid_rowconfigure(2, weight=0)
        self.autonomous_section = self._create_collapsible_section(
            self.chatbot_workspace_frame,
            "autonomous_mode",
            "🚀 Autonomous Music Video",
            meta_text="One-click pipeline",
            is_open=False,
            body_expand=False,
            body_background=self.colors["surface"],
        )
        self.autonomous_section["container"].grid(row=2, column=0, sticky="ew", pady=(0, 12))
        self._style_panel(self.autonomous_section["container"], self.colors["surface"], border=True)
        self._style_panel(self.autonomous_section["header"], self.colors["surface"])
        self._style_panel(self.autonomous_section["body"], self.colors["surface"])
        self._style_label(self.autonomous_section["title"], "section", self.autonomous_section["header"].cget("bg"))
        self._style_label(self.autonomous_section["meta"], "muted", self.autonomous_section["header"].cget("bg"))
        self._style_button(self.autonomous_section["toggle"], "ghost", compact=True)

        auto_body = self.autonomous_section["body"]

        auto_desc = tk.Label(
            auto_body,
            text="Describe the vibe, theme, and mood of your music video below, set a target duration, then click Start. "
                 "The pipeline will automatically plan scenes, render video, generate music, and merge everything.",
            anchor="w", justify=tk.LEFT, wraplength=860,
        )
        auto_desc.pack(anchor="w", fill=tk.X, pady=(0, 8))
        self._style_label(auto_desc, "muted", auto_body.cget("bg"))

        auto_brief_label = tk.Label(auto_body, text="Creative Brief:", anchor="w")
        auto_brief_label.pack(anchor="w", pady=(0, 4))
        self._style_label(auto_brief_label, "body_strong", auto_body.cget("bg"))

        self.autonomous_brief_text = tk.Text(auto_body, height=4, wrap=tk.WORD)
        self.autonomous_brief_text.pack(fill=tk.X, pady=(0, 10))
        self.autonomous_brief_text.insert("1.0", "")
        self.autonomous_brief_text.configure(
            bg=self.colors["card"], fg=self.colors["text"],
            insertbackground=self.colors["text"], relief=tk.FLAT,
            highlightthickness=1, highlightcolor=self.colors["accent"],
            highlightbackground=self.colors["border"],
        )

        auto_controls = tk.Frame(auto_body)
        auto_controls.pack(fill=tk.X, pady=(0, 8))
        self._style_panel(auto_controls, auto_body.cget("bg"))

        dur_label = tk.Label(auto_controls, text="Target Duration (seconds):")
        dur_label.pack(side=tk.LEFT, padx=(0, 6))
        self._style_label(dur_label, "body_strong", auto_body.cget("bg"))

        self.autonomous_duration_var = tk.StringVar(value="120")
        self.autonomous_duration_entry = tk.Spinbox(
            auto_controls, from_=5, to=3600, increment=5,
            textvariable=self.autonomous_duration_var, width=8,
        )
        self.autonomous_duration_entry.pack(side=tk.LEFT, padx=(0, 12))
        self.autonomous_duration_var.trace_add("write", self._update_autonomous_scene_estimate)

        self.autonomous_estimate_label = tk.Label(auto_controls, text="", anchor="w")
        self.autonomous_estimate_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._style_label(self.autonomous_estimate_label, "muted", auto_body.cget("bg"))
        self._update_autonomous_scene_estimate()

        auto_btn_row = tk.Frame(auto_body)
        auto_btn_row.pack(fill=tk.X, pady=(0, 8))
        self._style_panel(auto_btn_row, auto_body.cget("bg"))

        self.autonomous_start_btn = tk.Button(
            auto_btn_row, text="🚀  Start Autonomous Generation",
            command=self._start_autonomous_pipeline,
        )
        self.autonomous_start_btn.pack(side=tk.LEFT, padx=(0, 8))
        self._style_button(self.autonomous_start_btn, "primary")

        self.autonomous_cancel_btn = tk.Button(
            auto_btn_row, text="Cancel",
            command=self._cancel_autonomous_pipeline, state=tk.DISABLED,
        )
        self.autonomous_cancel_btn.pack(side=tk.LEFT)
        self._style_button(self.autonomous_cancel_btn, "danger")

        auto_progress_frame = tk.Frame(auto_body)
        auto_progress_frame.pack(fill=tk.X, pady=(0, 4))
        self._style_panel(auto_progress_frame, auto_body.cget("bg"))

        self.autonomous_progress_var = tk.IntVar(value=0)
        self.autonomous_progressbar = ttk.Progressbar(
            auto_progress_frame, variable=self.autonomous_progress_var,
            maximum=100, mode="determinate",
        )
        self.autonomous_progressbar.pack(fill=tk.X, pady=(0, 6))

        self.autonomous_status_label = tk.Label(auto_progress_frame, text="Ready. Enter a creative brief and click Start.", anchor="w", justify=tk.LEFT)
        self.autonomous_status_label.pack(anchor="w", fill=tk.X)
        self._style_label(self.autonomous_status_label, "body", auto_body.cget("bg"))

        self.autonomous_phase_labels = {}
        for phase_key in AUTONOMOUS_PHASE_ORDER:
            plbl = tk.Label(auto_progress_frame, text=f"  ○  {AUTONOMOUS_PHASE_LABELS[phase_key]}", anchor="w")
            plbl.pack(anchor="w")
            self._style_label(plbl, "muted", auto_body.cget("bg"))
            self.autonomous_phase_labels[phase_key] = plbl

        self.chatbot_readiness_section = self._create_collapsible_section(
            self.chatbot_shell,
            "chatbot_readiness",
            "Preflight",
            meta_text=self._get_chatbot_readiness_summary(),
            is_open=False,
            body_expand=False,
            body_background=self.colors["surface"],
        )
        self.chatbot_readiness_section["container"].pack(fill=tk.X, pady=(0, 12))
        self._style_panel(self.chatbot_readiness_section["container"], self.colors["surface"], border=True)
        self._style_panel(self.chatbot_readiness_section["header"], self.colors["surface"])
        self._style_panel(self.chatbot_readiness_section["body"], self.colors["surface"])
        self._style_label(self.chatbot_readiness_section["title"], "section", self.chatbot_readiness_section["header"].cget("bg"))
        self._style_label(self.chatbot_readiness_section["meta"], "muted", self.chatbot_readiness_section["header"].cget("bg"))
        self._style_button(self.chatbot_readiness_section["toggle"], "ghost", compact=True)

        self.chatbot_runtime_card = self.chatbot_readiness_section["body"]
        self.chatbot_runtime_title_label = tk.Label(self.chatbot_runtime_card, text="Before you generate")
        self.chatbot_runtime_title_label.pack(anchor="w")
        self._style_label(self.chatbot_runtime_title_label, "section", self.chatbot_runtime_card.cget("bg"))
        self.chatbot_readiness_summary_label = tk.Label(self.chatbot_runtime_card, text=self._get_chatbot_readiness_summary(), anchor="w")
        self.chatbot_readiness_summary_label.pack(anchor="w", pady=(6, 0))
        self._style_label(self.chatbot_readiness_summary_label, "body_strong", self.chatbot_runtime_card.cget("bg"))
        self.chatbot_readiness_next_step_label = tk.Label(self.chatbot_runtime_card, text=self._get_chatbot_next_step_text(), anchor="w", justify=tk.LEFT, wraplength=860)
        self.chatbot_readiness_next_step_label.pack(anchor="w", fill=tk.X, pady=(6, 8))
        self._style_label(self.chatbot_readiness_next_step_label, "body", self.chatbot_runtime_card.cget("bg"))
        self.chatbot_runtime_status_label = tk.Label(self.chatbot_runtime_card, text=self._get_chatbot_runtime_state_text(), anchor="w", justify=tk.LEFT, wraplength=820)
        self.chatbot_runtime_status_label.pack(anchor="w", fill=tk.X, pady=(6, 10))
        self._style_label(self.chatbot_runtime_status_label, "muted", self.chatbot_runtime_card.cget("bg"))

        self.chatbot_runtime_actions_frame = tk.Frame(self.chatbot_runtime_card)
        self.chatbot_runtime_actions_frame.pack(fill=tk.X)
        self._style_panel(self.chatbot_runtime_actions_frame, self.chatbot_runtime_card.cget("bg"))
        self.chatbot_setup_btn = tk.Button(self.chatbot_runtime_actions_frame, text="Set Up Model", command=lambda: self.ensure_chatbot_model_ready(interactive=True))
        self.chatbot_setup_btn.pack(side=tk.LEFT)
        self._style_button(self.chatbot_setup_btn, "primary", compact=True)
        self.chatbot_download_btn = tk.Button(self.chatbot_runtime_actions_frame, text="Download Model", command=self.prompt_and_download_chatbot_model)
        self.chatbot_download_btn.pack(side=tk.LEFT, padx=(10, 0))
        self._style_button(self.chatbot_download_btn, "secondary", compact=True)
        self.chatbot_runtime_btn = tk.Button(self.chatbot_runtime_actions_frame, text="Runtime Details", command=self.configure_chatbot_runtime)
        self.chatbot_runtime_btn.pack(side=tk.LEFT, padx=(10, 0))
        self._style_button(self.chatbot_runtime_btn, "ghost", compact=True)
        self.chatbot_test_backend_btn = tk.Button(self.chatbot_runtime_actions_frame, text="Test Backend", command=self.test_chatbot_runtime_connection)
        self.chatbot_test_backend_btn.pack(side=tk.LEFT, padx=(10, 0))
        self._style_button(self.chatbot_test_backend_btn, "accent", compact=True)

        self.chatbot_readiness_health_label = tk.Label(self.chatbot_runtime_card, text=self.chatbot_backend_health_text, anchor="w", justify=tk.LEFT, wraplength=820)
        self.chatbot_readiness_health_label.pack(anchor="w", fill=tk.X, pady=(10, 0))
        self._style_label(self.chatbot_readiness_health_label, "muted", self.chatbot_runtime_card.cget("bg"))

        self._update_chatbot_workspace_balance()
        self._refresh_chatbot_runtime_ui()
        self._on_chatbot_task_changed()
        self._refresh_chatbot_history_list()

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
            return self._normalize_path(workflow_path)

        for base_dir in [self.resource_root_dir, self.app_root_dir]:
            candidate = os.path.join(base_dir, workflow_path)
            if os.path.exists(candidate):
                return self._normalize_path(candidate)

        return self._normalize_path(os.path.join(self.resource_root_dir, workflow_path))

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

    def _get_role_refs_from_roles(self, roles, role_name):
        role_ref = (roles or {}).get(role_name)
        if not role_ref:
            return []
        return self._iter_role_refs(role_ref)

    def _get_profile_role_refs(self, role_name, profile_key=None):
        profile = self._get_video_profile(profile_key)
        return self._get_role_refs_from_roles(profile.get("roles", {}), role_name)

    def _get_workflow_role_value_from_roles(self, workflow, roles, role_name, default=""):
        for role_ref in self._get_role_refs_from_roles(roles, role_name):
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

    def _set_workflow_role_value_from_roles(self, workflow, roles, role_name, value):
        updated_count = 0
        for role_ref in self._get_role_refs_from_roles(roles, role_name):
            node_id = str(role_ref["node_id"])
            node_data = workflow.get(node_id)
            if not node_data:
                continue
            node_inputs = node_data.setdefault("inputs", {})
            node_inputs[role_ref["input"]] = value
            updated_count += 1
        return updated_count

    def _get_workflow_role_value(self, workflow, role_name, default="", profile_key=None):
        profile = self._get_video_profile(profile_key)
        return self._get_workflow_role_value_from_roles(workflow, profile.get("roles", {}), role_name, default=default)

    def _set_workflow_role_value(self, workflow, role_name, value, profile_key=None):
        profile = self._get_video_profile(profile_key)
        return self._set_workflow_role_value_from_roles(workflow, profile.get("roles", {}), role_name, value)

    def _get_image_workflow_value(self, role_name, default=""):
        if not self.image_workflow:
            return default
        return self._get_workflow_role_value_from_roles(self.image_workflow, IMAGE_WORKFLOW_PROFILE["roles"], role_name, default=default)

    def _build_image_filename_prefix(self, mode, index=None):
        parts = ["z-image"]
        if self.current_project_dir:
            parts.append(self._sanitize_output_token(os.path.basename(self.current_project_dir), fallback="project"))

        if mode == "single":
            parts.extend(["Single", str(int(time.time()))])
        elif index is not None:
            parts.append(f"{index:02d}")
        else:
            parts.append(str(int(time.time())))

        return f"images/{'_'.join(parts)}"

    def _get_default_image_settings(self):
        return {
            "negative_prompt": str(self._get_image_workflow_value("negative_prompt", "") or ""),
            "width": int(self._get_image_workflow_value("width", 1920) or 1920),
            "height": int(self._get_image_workflow_value("height", 1088) or 1088),
            "clip_name": str(self._get_image_workflow_value("clip_name", "") or ""),
            "vae_name": str(self._get_image_workflow_value("vae_name", "") or ""),
            "unet_name": str(self._get_image_workflow_value("unet_name", "") or ""),
            "steps": int(self._get_image_workflow_value("steps", 33) or 33),
            "cfg": float(self._get_image_workflow_value("cfg", 4) or 4),
            "sampler_name": str(self._get_image_workflow_value("sampler_name", "res_multistep") or "res_multistep"),
            "scheduler": str(self._get_image_workflow_value("scheduler", "simple") or "simple"),
            "denoise": float(self._get_image_workflow_value("denoise", 1) or 1)
        }

    def _sync_image_settings_from_workflow(self, force=False):
        if not self.image_workflow:
            return

        resolved_defaults = self._get_default_image_settings()
        field_mapping = [
            (self.image_negative_prompt_var, "negative_prompt"),
            (self.image_width_var, "width"),
            (self.image_height_var, "height"),
            (self.image_steps_var, "steps"),
            (self.image_cfg_var, "cfg"),
            (self.image_sampler_var, "sampler_name"),
            (self.image_scheduler_var, "scheduler"),
            (self.image_denoise_var, "denoise"),
            (self.image_clip_name_var, "clip_name"),
            (self.image_vae_name_var, "vae_name"),
            (self.image_unet_name_var, "unet_name")
        ]

        for tk_var, field_name in field_mapping:
            current_value = tk_var.get().strip() if isinstance(tk_var.get(), str) else tk_var.get()
            if current_value and not force:
                continue
            tk_var.set(str(resolved_defaults.get(field_name, "") or ""))

    def _reset_image_settings_to_loaded_workflow(self):
        for tk_var in [
            self.image_negative_prompt_var,
            self.image_width_var,
            self.image_height_var,
            self.image_steps_var,
            self.image_cfg_var,
            self.image_sampler_var,
            self.image_scheduler_var,
            self.image_denoise_var,
            self.image_clip_name_var,
            self.image_vae_name_var,
            self.image_unet_name_var
        ]:
            tk_var.set("")
        self._sync_image_settings_from_workflow(force=True)

    def _get_image_settings_snapshot(self):
        return {
            "negative_prompt": self.image_negative_prompt_var.get().strip(),
            "width": self.image_width_var.get().strip(),
            "height": self.image_height_var.get().strip(),
            "steps": self.image_steps_var.get().strip(),
            "cfg": self.image_cfg_var.get().strip(),
            "sampler_name": self.image_sampler_var.get().strip(),
            "scheduler": self.image_scheduler_var.get().strip(),
            "denoise": self.image_denoise_var.get().strip(),
            "clip_name": self.image_clip_name_var.get().strip(),
            "vae_name": self.image_vae_name_var.get().strip(),
            "unet_name": self.image_unet_name_var.get().strip()
        }

    def _apply_saved_image_settings(self, saved_settings=None):
        if not hasattr(self, "image_width_var"):
            return

        resolved = self._get_default_image_settings()
        if saved_settings:
            resolved.update(saved_settings)

        self.image_negative_prompt_var.set(str(resolved.get("negative_prompt", "") or ""))
        self.image_width_var.set(str(resolved.get("width", "") or ""))
        self.image_height_var.set(str(resolved.get("height", "") or ""))
        self.image_steps_var.set(str(resolved.get("steps", "") or ""))
        self.image_cfg_var.set(str(resolved.get("cfg", "") or ""))
        self.image_sampler_var.set(str(resolved.get("sampler_name", "") or ""))
        self.image_scheduler_var.set(str(resolved.get("scheduler", "") or ""))
        self.image_denoise_var.set(str(resolved.get("denoise", "") or ""))
        self.image_clip_name_var.set(str(resolved.get("clip_name", "") or ""))
        self.image_vae_name_var.set(str(resolved.get("vae_name", "") or ""))
        self.image_unet_name_var.set(str(resolved.get("unet_name", "") or ""))
        self._update_prompt_collection_summary()

    def _validate_image_workflow_template(self, workflow=None):
        workflow_to_validate = workflow if workflow is not None else self.image_workflow
        if not workflow_to_validate:
            return False, "No image workflow is loaded."

        required_roles = [
            "prompt",
            "negative_prompt",
            "width",
            "height",
            "filename_prefix",
            "clip_name",
            "vae_name",
            "unet_name",
            "steps",
            "cfg",
            "sampler_name",
            "scheduler",
            "denoise",
            "seed"
        ]

        for role_name in required_roles:
            role_refs = self._get_role_refs_from_roles(IMAGE_WORKFLOW_PROFILE.get("roles", {}), role_name)
            if not role_refs:
                return False, f"Image workflow profile is missing the '{role_name}' mapping."
            for role_ref in role_refs:
                node_id = str(role_ref["node_id"])
                node_data = workflow_to_validate.get(node_id)
                if not node_data:
                    return False, f"Image workflow is missing node {node_id} for role '{role_name}'."
                if role_ref["input"] not in node_data.get("inputs", {}):
                    return False, f"Image workflow node {node_id} is missing input '{role_ref['input']}' for role '{role_name}'."

        return True, None

    def _collect_validated_image_settings(self):
        is_valid, validation_error = self._validate_image_workflow_template()
        if not is_valid:
            return None, validation_error

        parsed_settings = {
            "negative_prompt": self.image_negative_prompt_var.get().strip(),
            "clip_name": self.image_clip_name_var.get().strip(),
            "vae_name": self.image_vae_name_var.get().strip(),
            "unet_name": self.image_unet_name_var.get().strip(),
            "sampler_name": self.image_sampler_var.get().strip(),
            "scheduler": self.image_scheduler_var.get().strip()
        }

        numeric_fields = [
            ("width", self.image_width_var.get().strip(), int),
            ("height", self.image_height_var.get().strip(), int),
            ("steps", self.image_steps_var.get().strip(), int),
            ("cfg", self.image_cfg_var.get().strip(), float),
            ("denoise", self.image_denoise_var.get().strip(), float)
        ]
        for field_name, raw_value, caster in numeric_fields:
            if not raw_value:
                return None, f"Image {field_name.replace('_', ' ').title()} is required."
            try:
                parsed_value = caster(raw_value)
            except ValueError:
                expected_type = "an integer" if caster is int else "a number"
                return None, f"Image {field_name.replace('_', ' ').title()} must be {expected_type}."
            if parsed_value <= 0:
                return None, f"Image {field_name.replace('_', ' ').title()} must be greater than zero."
            parsed_settings[field_name] = parsed_value

        for field_name in ["clip_name", "vae_name", "unet_name", "sampler_name", "scheduler"]:
            if not parsed_settings[field_name]:
                return None, f"Image {field_name.replace('_', ' ').title()} is required."

        return parsed_settings, None

    def _get_image_settings_summary_text(self):
        width = self.image_width_var.get().strip() if hasattr(self, "image_width_var") else ""
        height = self.image_height_var.get().strip() if hasattr(self, "image_height_var") else ""
        steps = self.image_steps_var.get().strip() if hasattr(self, "image_steps_var") else ""
        if width and height and steps:
            return f"{width}x{height} • {steps} st"
        return "workflow defaults"

    def _on_image_setting_changed(self, *_args):
        self._update_prompt_collection_summary()
        self._schedule_project_state_save()

    def _register_image_persistence_hooks(self):
        for variable in [
            self.image_negative_prompt_var,
            self.image_width_var,
            self.image_height_var,
            self.image_steps_var,
            self.image_cfg_var,
            self.image_sampler_var,
            self.image_scheduler_var,
            self.image_denoise_var,
            self.image_clip_name_var,
            self.image_vae_name_var,
            self.image_unet_name_var
        ]:
            variable.trace_add("write", self._on_image_setting_changed)

    def reset_image_settings_defaults(self):
        self._reset_image_settings_to_loaded_workflow()
        self.save_global_settings()
        self.save_project_state()
        self.update_status("Image settings reset to workflow defaults.", "blue")

    def validate_image_setup(self):
        image_settings, validation_error = self._collect_validated_image_settings()
        if validation_error:
            self.update_status(validation_error, "red")
            messagebox.showerror("Image Setup Validation", validation_error)
            return

        details = [
            f"Workflow JSON: {self.image_json_path}",
            f"Dimensions: {image_settings['width']}x{image_settings['height']}",
            f"Steps: {image_settings['steps']}",
            f"CFG: {image_settings['cfg']:g}",
            f"Sampler: {image_settings['sampler_name']}",
            f"Scheduler: {image_settings['scheduler']}",
            f"Denoise: {image_settings['denoise']:g}",
            f"CLIP: {image_settings['clip_name']}",
            f"VAE: {image_settings['vae_name']}",
            f"UNet: {image_settings['unet_name']}"
        ]
        messagebox.showinfo("Image Setup Validation", "\n".join(details))
        self.update_status("Image settings validation passed.", "green")

    def _build_image_workflow_for_prompt(self, prompt_text, filename_prefix, image_settings=None):
        if not self.image_workflow:
            raise ValueError("No image workflow is loaded.")

        resolved_settings = dict(self._get_default_image_settings())
        if image_settings:
            resolved_settings.update(image_settings)

        workflow_to_submit = copy.deepcopy(self.image_workflow)
        self._set_workflow_role_value_from_roles(workflow_to_submit, IMAGE_WORKFLOW_PROFILE["roles"], "prompt", prompt_text)
        self._set_workflow_role_value_from_roles(workflow_to_submit, IMAGE_WORKFLOW_PROFILE["roles"], "negative_prompt", resolved_settings["negative_prompt"])
        self._set_workflow_role_value_from_roles(workflow_to_submit, IMAGE_WORKFLOW_PROFILE["roles"], "width", int(resolved_settings["width"]))
        self._set_workflow_role_value_from_roles(workflow_to_submit, IMAGE_WORKFLOW_PROFILE["roles"], "height", int(resolved_settings["height"]))
        self._set_workflow_role_value_from_roles(workflow_to_submit, IMAGE_WORKFLOW_PROFILE["roles"], "filename_prefix", filename_prefix)
        self._set_workflow_role_value_from_roles(workflow_to_submit, IMAGE_WORKFLOW_PROFILE["roles"], "clip_name", resolved_settings["clip_name"])
        self._set_workflow_role_value_from_roles(workflow_to_submit, IMAGE_WORKFLOW_PROFILE["roles"], "vae_name", resolved_settings["vae_name"])
        self._set_workflow_role_value_from_roles(workflow_to_submit, IMAGE_WORKFLOW_PROFILE["roles"], "unet_name", resolved_settings["unet_name"])
        self._set_workflow_role_value_from_roles(workflow_to_submit, IMAGE_WORKFLOW_PROFILE["roles"], "steps", int(resolved_settings["steps"]))
        self._set_workflow_role_value_from_roles(workflow_to_submit, IMAGE_WORKFLOW_PROFILE["roles"], "cfg", float(resolved_settings["cfg"]))
        self._set_workflow_role_value_from_roles(workflow_to_submit, IMAGE_WORKFLOW_PROFILE["roles"], "sampler_name", resolved_settings["sampler_name"])
        self._set_workflow_role_value_from_roles(workflow_to_submit, IMAGE_WORKFLOW_PROFILE["roles"], "scheduler", resolved_settings["scheduler"])
        self._set_workflow_role_value_from_roles(workflow_to_submit, IMAGE_WORKFLOW_PROFILE["roles"], "denoise", float(resolved_settings["denoise"]))
        self._set_workflow_role_value_from_roles(workflow_to_submit, IMAGE_WORKFLOW_PROFILE["roles"], "seed", random.randint(1, 999999999999999))

        self.log_debug(
            "IMAGE_WORKFLOW_PREPARED",
            prompt_preview=self._truncate_text(prompt_text, 120),
            filename_prefix=filename_prefix,
            width=resolved_settings["width"],
            height=resolved_settings["height"],
            clip_name=resolved_settings["clip_name"],
            vae_name=resolved_settings["vae_name"],
            unet_name=resolved_settings["unet_name"]
        )
        return workflow_to_submit

    def _normalize_music_workflow(self, workflow):
        if not isinstance(workflow, dict):
            return []

        normalized_node_ids = []
        for node_id, node_data in workflow.items():
            if not isinstance(node_data, dict):
                continue
            if node_data.get("class_type") != "TextEncodeAceStepAudio1.5":
                continue

            node_inputs = node_data.setdefault("inputs", {})
            if "min_p" in node_inputs:
                continue

            node_inputs["min_p"] = ACE_STEP_15_MIN_P_DEFAULT
            normalized_node_ids.append(str(node_id))

        if normalized_node_ids:
            self.log_debug(
                "MUSIC_WORKFLOW_NORMALIZED",
                updated_nodes=normalized_node_ids,
                min_p=ACE_STEP_15_MIN_P_DEFAULT
            )

        return normalized_node_ids

    def _get_music_workflow_input(self, node_id, input_name, default=None):
        if not self.music_workflow:
            return default

        node_inputs = self.music_workflow.get(str(node_id), {}).get("inputs", {})
        value = node_inputs.get(input_name, default)
        if isinstance(value, list):
            return default
        return value

    def _coerce_music_int(self, value, default=0):
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return default

    def _coerce_music_float(self, value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _get_music_workflow_defaults(self):
        if self.music_workflow:
            self._normalize_music_workflow(self.music_workflow)

        return {
            "duration": self._coerce_music_int(self._get_music_workflow_input("94", "duration", 120), 120),
            "bpm": self._coerce_music_int(self._get_music_workflow_input("94", "bpm", 120), 120),
            "keyscale": str(self._get_music_workflow_input("94", "keyscale", "C major") or "C major"),
            "steps": self._coerce_music_int(self._get_music_workflow_input("3", "steps", 8), 8),
            "cfg": self._coerce_music_float(self._get_music_workflow_input("3", "cfg", 1.0), 1.0),
            "sampler_name": str(self._get_music_workflow_input("3", "sampler_name", "euler") or "euler"),
            "scheduler": str(self._get_music_workflow_input("3", "scheduler", "simple") or "simple"),
            "denoise": self._coerce_music_float(self._get_music_workflow_input("3", "denoise", 1.0), 1.0),
            "seed": self._coerce_music_int(self._get_music_workflow_input("94", "seed", 1), 1),
            "randomize_seed": True,
            "timesignature": str(self._get_music_workflow_input("94", "timesignature", "4") or "4"),
            "language": str(self._get_music_workflow_input("94", "language", "en") or "en"),
            "generate_audio_codes": bool(self._get_music_workflow_input("94", "generate_audio_codes", True)),
            "cfg_scale": self._coerce_music_float(self._get_music_workflow_input("94", "cfg_scale", 2.0), 2.0),
            "temperature": self._coerce_music_float(self._get_music_workflow_input("94", "temperature", 0.85), 0.85),
            "top_p": self._coerce_music_float(self._get_music_workflow_input("94", "top_p", 0.9), 0.9),
            "top_k": self._coerce_music_int(self._get_music_workflow_input("94", "top_k", 0), 0),
            "min_p": self._coerce_music_float(self._get_music_workflow_input("94", "min_p", ACE_STEP_15_MIN_P_DEFAULT), ACE_STEP_15_MIN_P_DEFAULT),
            "quality": str(self._get_music_workflow_input("107", "quality", "V0") or "V0")
        }

    def _get_music_settings_snapshot(self):
        return {
            "duration": self.music_duration_var.get(),
            "bpm": self.music_bpm_var.get(),
            "keyscale": self.music_key_var.get().strip(),
            "steps": self.music_steps_var.get(),
            "cfg": self.music_cfg_var.get(),
            "sampler_name": self.music_sampler_var.get().strip(),
            "scheduler": self.music_scheduler_var.get().strip(),
            "denoise": self.music_denoise_var.get(),
            "seed": self.music_seed_var.get(),
            "randomize_seed": bool(self.music_randomize_seed_var.get()),
            "timesignature": self.music_timesignature_var.get().strip(),
            "language": self.music_language_var.get().strip(),
            "generate_audio_codes": bool(self.music_generate_audio_codes_var.get()),
            "cfg_scale": self.music_cfg_scale_var.get(),
            "temperature": self.music_temperature_var.get(),
            "top_p": self.music_top_p_var.get(),
            "top_k": self.music_top_k_var.get(),
            "min_p": self.music_min_p_var.get(),
            "quality": self.music_quality_var.get().strip(),
            "model_variant": self.music_model_variant_var.get().strip()
        }

    def _get_music_ui_state_snapshot(self):
        return {
            key: bool(self.collapsible_sections.get(key, {}).get("open"))
            for key in PERSISTED_MUSIC_SECTION_KEYS
            if key in self.collapsible_sections
        }

    def _apply_music_ui_state_snapshot(self, ui_state=None):
        if not isinstance(ui_state, dict):
            return

        for key in PERSISTED_MUSIC_SECTION_KEYS:
            if key not in ui_state or key not in self.collapsible_sections:
                continue
            self._set_collapsible_section_open(key, bool(ui_state[key]))

        self._update_music_workspace_balance()

    def _schedule_project_state_save(self, delay_ms=500):
        if not self.current_project_dir or self.project_state_restore_in_progress:
            return

        if self.project_state_save_after_id is not None:
            try:
                self.root.after_cancel(self.project_state_save_after_id)
            except tk.TclError:
                pass
            self.project_state_save_after_id = None

        try:
            self.project_state_save_after_id = self.root.after(delay_ms, self._flush_scheduled_project_state_save)
        except tk.TclError:
            self.project_state_save_after_id = None

    def _flush_scheduled_project_state_save(self):
        self.project_state_save_after_id = None
        if self.project_state_restore_in_progress:
            return
        self.save_project_state()

    def _on_music_text_changed(self, *_args):
        self._update_music_config_summary()
        self._schedule_project_state_save()

    def _on_music_setting_changed(self, *_args):
        self._schedule_project_state_save()

    def _register_music_persistence_hooks(self):
        for variable in [
            self.music_duration_var,
            self.music_bpm_var,
            self.music_key_var,
            self.music_steps_var,
            self.music_cfg_var,
            self.music_sampler_var,
            self.music_scheduler_var,
            self.music_denoise_var,
            self.music_seed_var,
            self.music_randomize_seed_var,
            self.music_timesignature_var,
            self.music_language_var,
            self.music_generate_audio_codes_var,
            self.music_cfg_scale_var,
            self.music_temperature_var,
            self.music_top_p_var,
            self.music_top_k_var,
            self.music_min_p_var,
            self.music_quality_var,
            self.music_model_variant_var
        ]:
            variable.trace_add("write", self._on_music_setting_changed)

    def _apply_music_settings_snapshot(self, settings=None, legacy_state=None):
        if not hasattr(self, "music_duration_var"):
            return

        resolved = self._get_music_workflow_defaults()

        if legacy_state:
            resolved.update({
                "duration": legacy_state.get("music_duration", resolved["duration"]),
                "bpm": legacy_state.get("music_bpm", resolved["bpm"]),
                "keyscale": legacy_state.get("music_key", resolved["keyscale"])
            })

        if settings:
            resolved.update(settings)

        self.music_duration_var.set(self._coerce_music_int(resolved.get("duration"), 120))
        self.music_bpm_var.set(self._coerce_music_int(resolved.get("bpm"), 120))
        self.music_key_var.set(str(resolved.get("keyscale", "C major") or "C major"))
        self.music_steps_var.set(self._coerce_music_int(resolved.get("steps"), 8))
        self.music_cfg_var.set(self._coerce_music_float(resolved.get("cfg"), 1.0))
        self.music_sampler_var.set(str(resolved.get("sampler_name", "euler") or "euler"))
        self.music_scheduler_var.set(str(resolved.get("scheduler", "simple") or "simple"))
        self.music_denoise_var.set(self._coerce_music_float(resolved.get("denoise"), 1.0))
        self.music_seed_var.set(self._coerce_music_int(resolved.get("seed"), 1))
        self.music_randomize_seed_var.set(bool(resolved.get("randomize_seed", True)))
        self.music_timesignature_var.set(str(resolved.get("timesignature", "4") or "4"))
        self.music_language_var.set(str(resolved.get("language", "en") or "en"))
        self.music_generate_audio_codes_var.set(bool(resolved.get("generate_audio_codes", True)))
        self.music_cfg_scale_var.set(self._coerce_music_float(resolved.get("cfg_scale"), 2.0))
        self.music_temperature_var.set(self._coerce_music_float(resolved.get("temperature"), 0.85))
        self.music_top_p_var.set(self._coerce_music_float(resolved.get("top_p"), 0.9))
        self.music_top_k_var.set(self._coerce_music_int(resolved.get("top_k"), 0))
        self.music_min_p_var.set(self._coerce_music_float(resolved.get("min_p"), ACE_STEP_15_MIN_P_DEFAULT))
        self.music_quality_var.set(str(resolved.get("quality", "V0") or "V0"))
        restored_variant = str(resolved.get("model_variant", MUSIC_MODEL_VARIANT_DEFAULT) or MUSIC_MODEL_VARIANT_DEFAULT)
        if restored_variant in MUSIC_MODEL_VARIANT_MAP:
            self.music_model_variant_var.set(restored_variant)
        else:
            self.music_model_variant_var.set(MUSIC_MODEL_VARIANT_DEFAULT)
        self._update_music_seed_entry_state()

    def _reset_music_settings_to_loaded_workflow(self):
        self._apply_music_settings_snapshot()

    def _update_music_seed_entry_state(self, *_args):
        if hasattr(self, "music_seed_entry"):
            self.music_seed_entry.configure(state=(tk.DISABLED if self.music_randomize_seed_var.get() else tk.NORMAL))

    def _build_music_seed(self):
        if self.music_randomize_seed_var.get():
            resolved_seed = random.randint(1, 999999999)
            self.music_seed_var.set(resolved_seed)
            return resolved_seed
        return self._coerce_music_int(self.music_seed_var.get(), 1)

    def _on_music_model_variant_changed(self, *_args):
        variant = self.music_model_variant_var.get()
        info = MUSIC_MODEL_VARIANT_MAP.get(variant)
        if info:
            self.music_steps_var.set(info["steps"])
        self._on_music_setting_changed()

    def _get_active_music_model_filename(self):
        variant = self.music_model_variant_var.get()
        info = MUSIC_MODEL_VARIANT_MAP.get(variant, MUSIC_MODEL_VARIANT_MAP[MUSIC_MODEL_VARIANT_DEFAULT])
        return info["filename"]

    def _get_active_music_manifest_id(self):
        variant = self.music_model_variant_var.get()
        info = MUSIC_MODEL_VARIANT_MAP.get(variant, MUSIC_MODEL_VARIANT_MAP[MUSIC_MODEL_VARIANT_DEFAULT])
        return info["manifest_id"]

    def _is_xl_music_variant(self, variant_name=None):
        if variant_name is None:
            variant_name = self.music_model_variant_var.get()
        info = MUSIC_MODEL_VARIANT_MAP.get(variant_name, {})
        return info.get("backend") == "acestep_api"

    def _check_acestep_api_health(self):
        try:
            req = urllib.request.Request(f"{ACESTEP_API_URL}/health")
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    self.acestep_api_healthy = True
                    return True
        except Exception:
            pass
        self.acestep_api_healthy = False
        return False

    def _launch_acestep_api_server(self):
        # Search for ACE-Step-1.5 in likely locations:
        #   1) Inside ComfyUI root (D:\ComfyUI\ACE-Step-1.5)
        #   2) Next to the app folder (sibling of LTX2_Custom_UI_Batch_Queue)
        #   3) Next to ComfyUI root (D:\ACE-Step-1.5)
        acestep_dir = None
        search_bases = []
        if self.comfyui_root:
            search_bases.append(self.comfyui_root)               # e.g. D:\ComfyUI
        search_bases.append(os.path.dirname(self.app_root_dir))  # e.g. D:\ComfyUI (parent of LTX2_Custom_UI_Batch_Queue)
        if self.comfyui_root:
            search_bases.append(os.path.dirname(self.comfyui_root))  # e.g. D:\
        for base in search_bases:
            candidate = os.path.join(base, "ACE-Step-1.5")
            if os.path.isdir(candidate):
                acestep_dir = candidate
                break
        if not acestep_dir:
            searched = [os.path.join(b, "ACE-Step-1.5") for b in search_bases]
            self.log_debug("ACESTEP_LAUNCH_SKIP", reason="repo_not_found", searched_paths=str(searched))
            return False

        if self._check_acestep_api_health():
            self.log_debug("ACESTEP_LAUNCH_SKIP", reason="already_running")
            return True

        # Launch via uv directly (not via bat file, which overrides our env vars)
        uv_exe = shutil.which("uv")
        if not uv_exe:
            # Fallback: try the bat file
            bat_path = os.path.join(acestep_dir, "start_api_server.bat")
            if not os.path.exists(bat_path):
                self.log_debug("ACESTEP_LAUNCH_SKIP", reason="no_uv_or_bat")
                return False
            cmd = ["cmd", "/c", bat_path]
        else:
            cmd = [uv_exe, "run", "--no-sync", "acestep-api", "--host", "127.0.0.1", "--port", "8001"]

        try:
            env = os.environ.copy()
            env["ACESTEP_INIT_LLM"] = "false"
            env["CHECK_UPDATE"] = "false"
            env["ACESTEP_NO_INIT"] = "true"
            self.acestep_model_loaded = False
            self.acestep_api_process = subprocess.Popen(
                cmd,
                cwd=acestep_dir,
                env=env,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
            self.log_debug("ACESTEP_API_SERVER_LAUNCHED", pid=self.acestep_api_process.pid, cwd=acestep_dir, cmd=str(cmd))
            return True
        except Exception as e:
            self.log_debug("ACESTEP_LAUNCH_ERROR", details=str(e))
            return False

    def _wait_for_acestep_api(self, timeout=120):
        start = time.time()
        while time.time() - start < timeout:
            if self._check_acestep_api_health():
                self.log_debug("ACESTEP_API_READY", elapsed=f"{time.time() - start:.1f}s")
                return True
            time.sleep(3)
        self.log_debug("ACESTEP_API_TIMEOUT", timeout=timeout)
        return False

    def _generate_music_xl(self, tags, lyrics, variant_info):
        api_model_id = variant_info.get("api_model_id", "acestep-v15-xl-turbo")
        music_seed = self._build_music_seed()
        duration = self.music_duration_var.get()
        try:
            duration = float(duration)
        except (TypeError, ValueError):
            duration = 60.0

        bpm_raw = self.music_bpm_var.get()
        try:
            bpm = int(bpm_raw)
        except (TypeError, ValueError):
            bpm = None

        payload = {
            "prompt": tags,
            "lyrics": lyrics,
            "model": api_model_id,
            "audio_duration": duration,
            "inference_steps": variant_info.get("steps", 8),
            "guidance_scale": float(self.music_cfg_var.get() or 7.0),
            "seed": music_seed,
            "use_random_seed": False,
            "audio_format": "wav",
            "batch_size": 1,
            "vocal_language": self.music_language_var.get() or "en",
            "key_scale": self.music_key_var.get() or "",
            "time_signature": self.music_timesignature_var.get() or "",
            "sampler_name": self.music_sampler_var.get() or "euler",
            "infer_method": "ode",
        }
        if bpm and bpm > 0:
            payload["bpm"] = bpm

        self.log_debug("ACESTEP_XL_REQUEST", model=api_model_id, duration=duration, steps=variant_info.get("steps"), seed=music_seed)

        # -- Phase: Submitting --
        is_cold = not self.acestep_model_loaded
        self.xl_gen_phase = "submitting"
        self.xl_gen_phase_start = time.time()
        self.xl_gen_progress = 0.0
        self.xl_gen_stage_text = ""

        # Submit task — first request triggers lazy model loading which can block
        # the server's event loop for several minutes while checkpoint shards load.
        # Use ACESTEP_API_TIMEOUT as the HTTP timeout so first-run model loading
        # (which can take 10+ minutes) doesn't cause a premature timeout.
        if is_cold:
            self.xl_gen_phase = "model_loading"
            self.update_music_status("Submitting to XL server (first run loads models, please wait)...", "blue")
        else:
            self.update_music_status("Submitting to XL server...", "blue")

        t_submit_start = time.time()
        result = None
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(f"{ACESTEP_API_URL}/release_task", data=data)
            req.add_header("Content-Type", "application/json")
            with urllib.request.urlopen(req, timeout=ACESTEP_API_TIMEOUT) as resp:
                result = json.loads(resp.read().decode())
        except Exception as e:
            self.log_debug("ACESTEP_XL_SUBMIT_ERROR", details=str(e))
            self.xl_gen_phase = None
            return None

        t_submit_done = time.time()
        submit_elapsed = t_submit_done - t_submit_start
        submit_phase_key = XL_PHASE_SUBMIT_COLD if is_cold else XL_PHASE_SUBMIT_WARM
        self.record_tutorial_phase_timing(submit_phase_key, submit_elapsed)
        self.log_debug("ACESTEP_XL_SUBMIT_PHASE", phase=submit_phase_key, elapsed=f"{submit_elapsed:.1f}s")

        task_id = None
        result_data = result.get("data")
        if isinstance(result_data, dict):
            task_id = result_data.get("task_id")
        elif isinstance(result_data, str):
            task_id = result_data
        if not task_id:
            self.log_debug("ACESTEP_XL_NO_TASK_ID", response=str(result)[:500])
            self.xl_gen_phase = None
            return None

        self.log_debug("ACESTEP_XL_TASK_SUBMITTED", task_id=task_id)

        # -- Phase: Generating (polling) --
        self.xl_gen_phase = "generating"
        self.xl_gen_phase_start = time.time()
        self.xl_gen_progress = 0.0
        self.xl_gen_stage_text = ""
        self.update_music_status("XL model generating...", "blue")

        # Poll for result
        t_gen_start = time.time()
        start_time = t_gen_start
        last_status_update = 0
        while time.time() - start_time < ACESTEP_API_TIMEOUT:
            time.sleep(ACESTEP_API_POLL_INTERVAL)
            elapsed = time.time() - start_time
            try:
                query_payload = json.dumps({"task_id_list": json.dumps([task_id])}).encode("utf-8")
                req = urllib.request.Request(f"{ACESTEP_API_URL}/query_result", data=query_payload)
                req.add_header("Content-Type", "application/json")
                with urllib.request.urlopen(req, timeout=15) as resp:
                    poll_result = json.loads(resp.read().decode())
            except Exception as e:
                self.log_debug("ACESTEP_XL_POLL_ERROR", elapsed=f"{elapsed:.0f}s", details=str(e))
                # Server might be busy loading models — show a helpful status
                if elapsed - last_status_update > 10:
                    self.update_music_status(
                        f"XL: Waiting for server (models may be downloading/loading)... {self._format_elapsed_display(elapsed)}",
                        "blue",
                    )
                    last_status_update = elapsed
                continue

            data_list = poll_result.get("data", [])
            if not data_list:
                # Server responded but no task data yet — models likely still loading
                if elapsed - last_status_update > 10:
                    self.update_music_status(
                        f"XL: Server is initializing models (first run downloads ~20GB)... {self._format_elapsed_display(elapsed)}",
                        "blue",
                    )
                    last_status_update = elapsed
                continue

            item = data_list[0] if isinstance(data_list, list) else data_list
            status = item.get("status")
            progress_text = item.get("progress_text", "")

            # Extract progress/stage from the result items when running
            try:
                result_json = json.loads(item.get("result", "[]")) if isinstance(item.get("result"), str) else (item.get("result") or [])
                if isinstance(result_json, list) and result_json and isinstance(result_json[0], dict):
                    server_progress = float(result_json[0].get("progress", 0.0))
                    server_stage = str(result_json[0].get("stage", ""))
                else:
                    server_progress = 0.0
                    server_stage = ""
            except (json.JSONDecodeError, TypeError, ValueError):
                server_progress = 0.0
                server_stage = ""

            # Update live phase state for the tick callback
            self.xl_gen_progress = server_progress
            self.xl_gen_stage_text = progress_text or server_stage

            if progress_text:
                last_status_update = elapsed
            elif status == 0 and elapsed - last_status_update > 10:
                last_status_update = elapsed

            self.log_debug("ACESTEP_XL_POLL", status=status, elapsed=f"{elapsed:.0f}s", progress=progress_text[:100] if progress_text else "", raw_item=str(item)[:300])

            # status 1 = succeeded, status 0 = running, status 2 = failed
            if status == 1:
                # Record generation phase timing
                gen_elapsed = time.time() - t_gen_start
                self.record_tutorial_phase_timing(XL_PHASE_GENERATION, gen_elapsed)
                self.log_debug("ACESTEP_XL_GEN_PHASE", elapsed=f"{gen_elapsed:.1f}s")
                self.acestep_model_loaded = True

                # Parse the result to get audio path
                result_str = item.get("result", "")
                try:
                    result_list = json.loads(result_str) if isinstance(result_str, str) else result_str
                except (json.JSONDecodeError, TypeError):
                    result_list = result_str

                audio_url = None
                if isinstance(result_list, list) and result_list:
                    first = result_list[0] if isinstance(result_list[0], dict) else {}
                    audio_url = first.get("file", "")

                self.log_debug("ACESTEP_XL_RESULT", audio_url=str(audio_url)[:200], result_sample=str(result_list)[:300])
                if audio_url:
                    # -- Phase: Downloading --
                    self.xl_gen_phase = "downloading"
                    self.xl_gen_phase_start = time.time()
                    self.xl_gen_progress = 0.0
                    t_dl_start = time.time()
                    result_path = self._download_acestep_audio(audio_url, task_id)
                    dl_elapsed = time.time() - t_dl_start
                    self.record_tutorial_phase_timing(XL_PHASE_DOWNLOAD, dl_elapsed)
                    self.log_debug("ACESTEP_XL_DL_PHASE", elapsed=f"{dl_elapsed:.1f}s")
                    self.xl_gen_phase = None
                    return result_path
                else:
                    self.log_debug("ACESTEP_XL_NO_AUDIO", result=str(result_list)[:500])
                    self.xl_gen_phase = None
                    return None
            elif status == 2:
                # During model loading, the cache can briefly return status=2 with empty data.
                # Only treat as a real failure if we've been running long enough for models to load.
                if elapsed < 60:
                    self.log_debug("ACESTEP_XL_STATUS2_EARLY", elapsed=f"{elapsed:.0f}s", item=str(item)[:300])
                    continue  # Keep polling — models may still be loading
                self.log_debug("ACESTEP_XL_FAILED", task_id=task_id, result=str(item)[:500])
                self.xl_gen_phase = None
                return None

        self.log_debug("ACESTEP_XL_TIMEOUT", task_id=task_id, elapsed=f"{time.time() - start_time:.0f}s")
        self.xl_gen_phase = None
        return None

    def _download_acestep_audio(self, audio_path_or_url, task_id):
        try:
            dest_filename = f"ACE_XL_{int(time.time())}_{task_id[:8]}.wav"
            dest_path = os.path.join(self.audio_dir, dest_filename)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            # The API result "file" field can be:
            #   1) A relative URL: /v1/audio?path=<encoded_path>
            #   2) A full URL: http://...
            #   3) A local filesystem path: D:\...\file.wav
            if audio_path_or_url.startswith("http://") or audio_path_or_url.startswith("https://"):
                download_url = audio_path_or_url
            elif audio_path_or_url.startswith("/v1/audio"):
                # Relative URL from API — prepend base URL
                download_url = f"{ACESTEP_API_URL}{audio_path_or_url}"
            elif os.path.isfile(audio_path_or_url):
                # Local filesystem path — just copy the file directly
                shutil.copy2(audio_path_or_url, dest_path)
                self.log_debug("ACESTEP_XL_AUDIO_COPIED", src=audio_path_or_url, dest=dest_path)
                return dest_path
            else:
                # Assume it's a path that needs URL-encoding for the /v1/audio endpoint
                encoded = urllib.parse.quote(audio_path_or_url, safe="")
                download_url = f"{ACESTEP_API_URL}/v1/audio?path={encoded}"

            self.log_debug("ACESTEP_XL_DOWNLOADING", url=download_url[:200])
            urllib.request.urlretrieve(download_url, dest_path)

            if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
                self.log_debug("ACESTEP_XL_AUDIO_DOWNLOADED", dest_path=dest_path, size=os.path.getsize(dest_path))
                return dest_path
            else:
                self.log_debug("ACESTEP_XL_DOWNLOAD_EMPTY", dest_path=dest_path)
                return None
        except Exception as e:
            self.log_debug("ACESTEP_XL_DOWNLOAD_ERROR", details=str(e))
            return None

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

    def refresh_image_model_choices(self, initial_load=False):
        combo_mapping = {
            "clip_name": self.image_clip_combo,
            "vae_name": self.image_vae_combo,
            "unet_name": self.image_unet_combo
        }
        variable_mapping = {
            "clip_name": self.image_clip_name_var,
            "vae_name": self.image_vae_name_var,
            "unet_name": self.image_unet_name_var
        }

        for field_name, combo in combo_mapping.items():
            current_value = variable_mapping[field_name].get().strip()
            discovered_choices = self._scan_model_choices_for_field(field_name)
            if current_value and current_value not in discovered_choices:
                discovered_choices = sorted({*discovered_choices, current_value}, key=str.lower)
            self.image_model_choices[field_name] = discovered_choices
            combo["values"] = discovered_choices
            if current_value:
                variable_mapping[field_name].set(current_value)

        if not initial_load:
            total_choices = sum(len(choices) for choices in self.image_model_choices.values())
            self.update_status(f"Refreshed image model lists ({total_choices} choices found).", "blue")
            self.log_debug("IMAGE_MODEL_LISTS_REFRESHED", counts={k: len(v) for k, v in self.image_model_choices.items()})

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

    def _load_image_workflow_template(self):
        self.image_json_path = self._make_workflow_path_absolute(self.image_json_path)
        print(f"[DEBUG-IMG] _load_image_workflow_template path={self.image_json_path}")
        print(f"[DEBUG-IMG] resource_root_dir={self.resource_root_dir}  app_root_dir={self.app_root_dir}")
        print(f"[DEBUG-IMG] exists={os.path.exists(self.image_json_path)}  frozen={getattr(sys, 'frozen', False)}")

        if not os.path.exists(self.image_json_path):
            print(f"[DEBUG-IMG] FILE NOT FOUND, setting image_workflow=None")
            self.image_workflow = None
            return

        try:
            with open(self.image_json_path, 'r', encoding='utf-8') as f:
                self.image_workflow = json.load(f)
            print(f"[DEBUG-IMG] Loaded OK, {len(self.image_workflow)} nodes")
        except Exception as e:
            print(f"[DEBUG-IMG] EXCEPTION: {type(e).__name__}: {e}")
            self.image_workflow = None

    def _load_i2v_workflow_template(self):
        self.i2v_json_path = self._make_workflow_path_absolute(self.i2v_json_path)

        if not os.path.exists(self.i2v_json_path):
            self.i2v_workflow = None
            return

        try:
            with open(self.i2v_json_path, 'r', encoding='utf-8') as f:
                self.i2v_workflow = json.load(f)
        except Exception:
            self.i2v_workflow = None

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
        self._load_image_workflow_template()
        self._load_i2v_workflow_template()
        if hasattr(self, "image_width_var"):
            self._reset_image_settings_to_loaded_workflow()
        self.music_json_path = self._make_workflow_path_absolute(self.music_json_path)
            
        if os.path.exists(self.music_json_path):
            try:
                with open(self.music_json_path, 'r', encoding='utf-8') as f:
                    self.music_workflow = json.load(f)
                self._normalize_music_workflow(self.music_workflow)
                if hasattr(self, "music_duration_var"):
                    self._reset_music_settings_to_loaded_workflow()
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

    def update_scene_scroll_region(self):
        if not hasattr(self, "scene_scrollable_frame"):
            return
        self.scene_scrollable_frame.update_idletasks()
        self.scene_canvas.configure(scrollregion=self.scene_canvas.bbox("all"))

    def _get_scene_mode_label(self, mode_value):
        return "Image to Video" if str(mode_value or "").strip().lower() == SCENE_MODE_I2V else "Text to Video"

    def _get_scene_mode_value(self, mode_label):
        return SCENE_MODE_I2V if str(mode_label or "").strip() == "Image to Video" else SCENE_MODE_T2V

    def _get_scene_asset_options(self):
        options = [("Unassigned", "")]
        for asset in self._normalize_image_assets(self.image_assets):
            project_path = self._normalize_path(asset.get("project_path"))
            if not project_path or not os.path.exists(project_path):
                continue
            options.append((self._get_image_asset_display_name(asset), str(asset.get("asset_id", "")).strip()))
        return options

    def _collect_scene_entry_frames(self):
        if not hasattr(self, "scene_scrollable_frame"):
            self.scene_entry_frames = []
            return []
        self.scene_entry_frames = [
            frame for frame in self.scene_scrollable_frame.winfo_children()
            if getattr(frame, "scene_id", None)
            and hasattr(frame, "image_asset_combo")
            and hasattr(frame, "image_asset_var")
            and hasattr(frame, "prompt_text")
        ]
        return self.scene_entry_frames

    def _apply_scene_mode_state(self, frame):
        is_i2v = self._get_scene_mode_value(frame.mode_var.get()) == SCENE_MODE_I2V
        frame.image_picker_label.config(text="Source Image" if is_i2v else "Optional Image")
        frame.image_asset_combo.configure(state="readonly")

    def _refresh_scene_asset_choices(self):
        options = self._get_scene_asset_options()
        option_labels = [label for label, _asset_id in options]

        for frame in self._collect_scene_entry_frames():
            selected_asset_id = getattr(frame, "selected_asset_id", None) or ""
            frame.asset_option_map = {label: asset_id for label, asset_id in options}
            frame.asset_option_reverse_map = {asset_id: label for label, asset_id in options}
            frame.image_asset_combo["values"] = option_labels

            resolved_label = frame.asset_option_reverse_map.get(selected_asset_id, "Unassigned")
            frame.image_asset_var.set(resolved_label)
        self._refresh_scene_asset_summaries()

    def _refresh_scene_entry_rows(self):
        for index, frame in enumerate(self._collect_scene_entry_frames(), start=1):
            frame.order_label.config(text=f"Scene {index:02d}")
            self._apply_scene_mode_state(frame)
        self._refresh_scene_asset_choices()
        self.update_scene_scroll_region()
        self._update_prompt_collection_summary()

    def _clear_all_scene_timeline_entries(self):
        if not hasattr(self, "scene_scrollable_frame"):
            self.scene_entry_frames = []
            return

        for frame in list(self.scene_scrollable_frame.winfo_children()):
            frame.destroy()
        self.scene_entry_frames = []
        self.update_scene_scroll_region()
        self._update_prompt_collection_summary()

    def add_scene_timeline_entry(self, scene_data=None):
        scene_data = scene_data or self._create_scene_entry(
            len(self._collect_scene_entry_frames()) + 1,
            mode=SCENE_MODE_T2V,
            prompt=""
        )

        frame = tk.Frame(self.scene_scrollable_frame, pady=6)
        frame.pack(fill=tk.X, expand=True)
        self._style_panel(frame, self.colors["card"], border=True)
        frame.scene_id = scene_data.get("scene_id") or self._generate_entity_id("scene")
        frame.output_path = self._normalize_path(scene_data.get("output_path"))
        frame.render_status = str(scene_data.get("render_status", "pending")).strip().lower() or "pending"

        header_row = tk.Frame(frame, padx=10, pady=8)
        header_row.pack(fill=tk.X)
        self._style_panel(header_row, self.colors["card"])

        frame.order_label = tk.Label(header_row, text="Scene")
        frame.order_label.pack(side=tk.LEFT)
        self._style_label(frame.order_label, "section", self.colors["card"])

        frame.mode_var = tk.StringVar(value=self._get_scene_mode_label(scene_data.get("mode", SCENE_MODE_T2V)))
        mode_combo = ttk.Combobox(header_row, textvariable=frame.mode_var, state="readonly", values=["Text to Video", "Image to Video"], width=18)
        mode_combo.pack(side=tk.LEFT, padx=(12, 0))
        frame.mode_combo = mode_combo

        frame.status_label = tk.Label(header_row, text=f"Status: {frame.render_status.title()}")
        frame.status_label.pack(side=tk.LEFT, padx=(12, 0))
        self._style_label(frame.status_label, "muted", self.colors["card"])

        btn_frame = tk.Frame(header_row)
        btn_frame.pack(side=tk.RIGHT)
        self._style_panel(btn_frame, self.colors["card"])

        move_up_btn = tk.Button(btn_frame, text="Up", command=lambda f=frame: self.move_scene_timeline_entry(f, -1))
        move_up_btn.pack(side=tk.LEFT)
        self._style_button(move_up_btn, "ghost", compact=True)

        move_down_btn = tk.Button(btn_frame, text="Down", command=lambda f=frame: self.move_scene_timeline_entry(f, 1))
        move_down_btn.pack(side=tk.LEFT, padx=(6, 0))
        self._style_button(move_down_btn, "ghost", compact=True)

        remove_btn = tk.Button(btn_frame, text="Remove", command=lambda f=frame: self.remove_scene_timeline_entry(f))
        remove_btn.pack(side=tk.LEFT, padx=(6, 0))
        self._style_button(remove_btn, "ghost", compact=True)

        body_row = tk.Frame(frame, padx=10, pady=10)
        body_row.pack(fill=tk.X)
        self._style_panel(body_row, self.colors["card"])
        body_row.grid_columnconfigure(1, weight=1)

        prompt_label = tk.Label(body_row, text="Scene Prompt")
        prompt_label.grid(row=0, column=0, sticky="nw", pady=(0, 6))
        self._style_label(prompt_label, "muted", self.colors["card"])

        frame.prompt_text = tk.Text(body_row, height=3, width=50)
        frame.prompt_text.grid(row=0, column=1, sticky="ew", pady=(0, 6))
        self._style_text_input(frame.prompt_text, multiline=True)
        scene_prompt_text = self._get_scene_prompt_text(scene_data)
        if scene_prompt_text:
            frame.prompt_text.insert("1.0", scene_prompt_text)

        frame.image_picker_label = tk.Label(body_row, text="Source Image")
        frame.image_picker_label.grid(row=1, column=0, sticky="w", pady=(0, 6))
        self._style_label(frame.image_picker_label, "muted", self.colors["card"])

        frame.image_asset_var = tk.StringVar(value="Unassigned")
        frame.image_asset_combo = ttk.Combobox(body_row, textvariable=frame.image_asset_var, state="readonly", width=48)
        frame.image_asset_combo.grid(row=1, column=1, sticky="ew", pady=(0, 6))
        frame.selected_asset_id = str(scene_data.get("image_asset_id") or "").strip()

        frame.asset_summary_label = tk.Label(body_row, text="No source image assigned.", anchor="w", justify=tk.LEFT, wraplength=680)
        frame.asset_summary_label.grid(row=2, column=1, sticky="ew", pady=(0, 6))
        self._style_label(frame.asset_summary_label, "muted", self.colors["card"])

        output_text = os.path.basename(frame.output_path) if frame.output_path and os.path.exists(frame.output_path) else "No render yet"
        frame.output_label = tk.Label(frame, text=output_text, anchor="w")
        frame.output_label.pack(fill=tk.X, padx=10, pady=(0, 10))
        self._style_label(frame.output_label, "muted", self.colors["card"])

        mode_combo.bind("<<ComboboxSelected>>", lambda _event, f=frame: self._refresh_scene_entry_rows())
        frame.image_asset_combo.bind(
            "<<ComboboxSelected>>",
            lambda _event, f=frame: self._handle_scene_asset_selection(f)
        )

        self.scene_entry_frames.append(frame)
        self._refresh_scene_entry_rows()

    def _handle_scene_asset_selection(self, frame):
        frame.selected_asset_id = frame.asset_option_map.get(frame.image_asset_var.get(), "")
        self._refresh_scene_asset_summaries()
        self._update_prompt_collection_summary()

    def remove_scene_timeline_entry(self, frame):
        frame.destroy()
        self._collect_scene_entry_frames()
        self._refresh_scene_entry_rows()

    def move_scene_timeline_entry(self, frame, direction):
        frames = self._collect_scene_entry_frames()
        if frame not in frames:
            return

        current_index = frames.index(frame)
        target_index = current_index + direction
        if target_index < 0 or target_index >= len(frames):
            return

        scene_state = self._collect_scene_timeline_from_widgets()
        scene_state[current_index], scene_state[target_index] = scene_state[target_index], scene_state[current_index]
        self._rebuild_scene_timeline_from_state(scene_state)

    def _collect_scene_timeline_from_widgets(self):
        scene_entries = []
        for index, frame in enumerate(self._collect_scene_entry_frames(), start=1):
            selected_asset_id = frame.asset_option_map.get(frame.image_asset_var.get(), "") if hasattr(frame, "asset_option_map") else getattr(frame, "selected_asset_id", "")
            frame.selected_asset_id = selected_asset_id
            scene_entries.append(
                self._create_scene_entry(
                    index,
                    mode=self._get_scene_mode_value(frame.mode_var.get()),
                    prompt=frame.prompt_text.get("1.0", tk.END).strip(),
                    image_asset_id=selected_asset_id,
                    scene_id=frame.scene_id,
                    output_path=getattr(frame, "output_path", None),
                    render_status=getattr(frame, "render_status", "pending")
                )
            )
        return self._reindex_ordered_entries(scene_entries)

    def _rebuild_scene_timeline_from_state(self, scene_timeline=None):
        self._clear_all_scene_timeline_entries()
        for scene_entry in self._normalize_scene_timeline(scene_timeline or []):
            self.add_scene_timeline_entry(scene_entry)
        self._refresh_scene_entry_rows()

    def _rebuild_image_prompt_queue_from_texts(self, prompts_text=None):
        normalized_prompts = self._normalize_string_list(prompts_text or [])
        self._clear_all_image_prompt_entries()
        self.image_prompt_queue = list(normalized_prompts)
        for prompt_text in normalized_prompts:
            self.add_image_prompt_entry()
            self.image_prompts[-1].insert(tk.END, prompt_text)
        self._update_prompt_collection_summary()

    def sync_scene_timeline_from_prompt_queue(self):
        prompts_text = self._collect_prompt_texts()
        self.scene_timeline = self._build_scene_timeline_from_prompts(prompts_text)
        self._rebuild_scene_timeline_from_state(self.scene_timeline)
        self.update_status("Scene timeline synced from prompt queue.", "blue")

    def sync_t2v_prompts_to_image_queue(self):
        scene_timeline = self._collect_scene_timeline_from_widgets()
        labeled_prompts = self._build_image_prompt_queue_from_scene_timeline(scene_timeline)
        if not labeled_prompts:
            messagebox.showwarning("Image Phase", "No non-empty scene prompts from Text to Video scenes are available to send to the Image Phase.")
            return

        self.scene_timeline = self._normalize_scene_timeline(scene_timeline)
        self._rebuild_image_prompt_queue_from_texts(labeled_prompts)
        self.save_project_state()
        self.update_status(f"Image Phase rebuilt from {len(labeled_prompts)} scene prompt{'s' if len(labeled_prompts) != 1 else ''}.", "blue")

    def sync_image_prompts_to_scene_timeline(self):
        prompts_text = self._collect_image_prompt_texts()
        if not prompts_text:
            messagebox.showwarning("Scene Timeline", "No non-empty image prompts are available to send to the Scene Timeline.")
            return

        scene_timeline = self._collect_scene_timeline_from_widgets()
        updated_timeline, sync_summary = self._apply_image_prompts_to_scene_timeline(scene_timeline, prompts_text)
        if not (sync_summary["updated"] or sync_summary["created"]):
            messagebox.showwarning("Scene Timeline", "No image prompts could be applied to the Scene Timeline.")
            return

        self.scene_timeline = self._normalize_scene_timeline(updated_timeline)
        self._rebuild_scene_timeline_from_state(self.scene_timeline)
        self.save_project_state()

        status_parts = [
            f"{sync_summary['updated']} updated",
            f"{sync_summary['created']} created",
            f"{sync_summary['preserved_i2v']} I2V preserved"
        ]
        if sync_summary["malformed_labels"]:
            status_parts.append(f"{sync_summary['malformed_labels']} malformed label{'s' if sync_summary['malformed_labels'] != 1 else ''} treated as unlabeled")
        self.update_status(f"Scene Timeline synced from Image Phase: {', '.join(status_parts)}.", "blue")

    def _set_scene_entry_render_state(self, scene_id, render_status, output_path=None):
        normalized_status = str(render_status or "pending").strip().lower() or "pending"
        normalized_output_path = self._normalize_path(output_path)
        for frame in self._collect_scene_entry_frames():
            if frame.scene_id != scene_id:
                continue
            frame.render_status = normalized_status
            frame.output_path = normalized_output_path
            frame.status_label.config(text=f"Status: {normalized_status.title()}")
            display_text = os.path.basename(normalized_output_path) if normalized_output_path and os.path.exists(normalized_output_path) else "No render yet"
            frame.output_label.config(text=display_text)
            break
        self._update_prompt_collection_summary()

    def _build_i2v_workflow_for_scene(self, prompt_text, image_path, filename_prefix, video_settings):
        workflow_to_submit = copy.deepcopy(self.i2v_workflow)

        self._set_workflow_role_value_from_roles(workflow_to_submit, I2V_WORKFLOW_PROFILE["roles"], "prompt", prompt_text)
        self._set_workflow_role_value_from_roles(workflow_to_submit, I2V_WORKFLOW_PROFILE["roles"], "negative_prompt", video_settings["negative_prompt"])
        self._set_workflow_role_value_from_roles(workflow_to_submit, I2V_WORKFLOW_PROFILE["roles"], "width", video_settings["width"])
        self._set_workflow_role_value_from_roles(workflow_to_submit, I2V_WORKFLOW_PROFILE["roles"], "height", video_settings["height"])
        self._set_workflow_role_value_from_roles(workflow_to_submit, I2V_WORKFLOW_PROFILE["roles"], "fps", video_settings["fps"])
        self._set_workflow_role_value_from_roles(workflow_to_submit, I2V_WORKFLOW_PROFILE["roles"], "length", video_settings["length"])
        self._set_workflow_role_value_from_roles(workflow_to_submit, I2V_WORKFLOW_PROFILE["roles"], "t2v_enabled", False)
        self._set_workflow_role_value_from_roles(workflow_to_submit, I2V_WORKFLOW_PROFILE["roles"], "filename_prefix", filename_prefix)
        self._set_workflow_role_value_from_roles(workflow_to_submit, I2V_WORKFLOW_PROFILE["roles"], "checkpoint_name", video_settings["checkpoint_name"])
        self._set_workflow_role_value_from_roles(workflow_to_submit, I2V_WORKFLOW_PROFILE["roles"], "text_encoder_name", video_settings["text_encoder_name"])
        self._set_workflow_role_value_from_roles(workflow_to_submit, I2V_WORKFLOW_PROFILE["roles"], "lora_name", video_settings["lora_name"])
        self._set_workflow_role_value_from_roles(workflow_to_submit, I2V_WORKFLOW_PROFILE["roles"], "upscaler_name", video_settings["upscaler_name"])
        self._set_workflow_role_value_from_roles(workflow_to_submit, I2V_WORKFLOW_PROFILE["roles"], "image_path", image_path)

        for role_ref in self._get_role_refs_from_roles(I2V_WORKFLOW_PROFILE["roles"], "noise_seed"):
            node_id = str(role_ref["node_id"])
            workflow_to_submit[node_id]["inputs"][role_ref["input"]] = random.randint(1, 999999999999999)

        return workflow_to_submit

    def start_scene_timeline_render(self):
        self.save_project_state()
        scene_timeline = self._collect_scene_timeline_from_widgets()
        if not scene_timeline:
            messagebox.showwarning("Warning", "Add at least one scene to the timeline.")
            return

        video_settings, validation_error = self._collect_validated_video_settings()
        if validation_error:
            messagebox.showerror("Workflow Settings Error", validation_error)
            self.update_status(validation_error, "red")
            return

        has_i2v_scene = any(entry.get("mode") == SCENE_MODE_I2V for entry in scene_timeline)
        if has_i2v_scene and not self.i2v_workflow:
            messagebox.showerror("Workflow Missing", "The image-to-video workflow JSON could not be loaded.")
            return

        for entry in scene_timeline:
            scene_prompt = self._get_scene_prompt_text(entry)
            if not scene_prompt:
                messagebox.showwarning("Scene Timeline", f"Scene {entry['order_index']} needs a scene prompt.")
                return
            if entry.get("mode") == SCENE_MODE_I2V:
                asset = self._get_image_asset_by_id(entry.get("image_asset_id"))
                if not asset or not os.path.exists(asset.get("project_path", "")):
                    messagebox.showwarning("Scene Timeline", f"Scene {entry['order_index']} needs a valid source image.")
                    return

        self.scene_timeline = scene_timeline
        self.render_scene_timeline_btn.config(state=tk.DISABLED)
        self.add_scene_btn.config(state=tk.DISABLED)
        if hasattr(self, "sync_t2v_to_image_queue_btn"):
            self.sync_t2v_to_image_queue_btn.config(state=tk.DISABLED)
        if hasattr(self, "sync_image_to_scene_btn"):
            self.sync_image_to_scene_btn.config(state=tk.DISABLED)
        if hasattr(self, "auto_assign_scene_images_btn"):
            self.auto_assign_scene_images_btn.config(state=tk.DISABLED)

        thread = threading.Thread(target=self._run_scene_timeline_thread, args=(scene_timeline, video_settings))
        thread.daemon = True
        thread.start()

    def _run_scene_timeline_thread(self, scene_timeline, video_settings):
        total = len(scene_timeline)
        self._set_tutorial_runtime_progress(
            "video_render",
            reset=True,
            status="Preparing scene timeline render...",
            current=0,
            total=total,
            item_label="Scene timeline",
            stage="preparing",
        )
        for index, scene_entry in enumerate(scene_timeline, start=1):
            scene_id = scene_entry.get("scene_id")
            scene_mode = scene_entry.get("mode", SCENE_MODE_T2V)
            prompt_text = self._get_scene_prompt_text(scene_entry)
            self.root.after(0, lambda sid=scene_id: self._set_scene_entry_render_state(sid, "rendering"))
            self.update_status(f"Rendering scene {index} of {total}...", "blue")
            self.update_debug_prompt_status(prompt_text, current=index, total=total)
            self._set_tutorial_runtime_progress(
                "video_render",
                status=f"Submitting scene {index} of {total}...",
                current=index,
                total=total,
                item_label=f"Scene {index}",
                stage="submitting",
            )

            before_files = self._snapshot_media_files(self.scenes_dir, SUPPORTED_VIDEO_EXTENSIONS)
            filename_prefix = self._build_video_filename_prefix(video_settings, "timeline", index)

            if scene_mode == SCENE_MODE_I2V:
                asset = self._get_image_asset_by_id(scene_entry.get("image_asset_id"))
                workflow_to_submit = self._build_i2v_workflow_for_scene(
                    prompt_text,
                    asset.get("project_path"),
                    filename_prefix,
                    video_settings
                )
            else:
                workflow_to_submit = self._build_video_workflow_for_prompt(
                    prompt_text,
                    filename_prefix,
                    video_settings
                )

            prompt_id = self.queue_prompt(workflow_to_submit)
            if not prompt_id:
                self.root.after(0, lambda sid=scene_id: self._set_scene_entry_render_state(sid, "failed"))
                self._set_tutorial_runtime_progress("video_render", status=f"Scene {index} failed to submit.", current=index, total=total, item_label=f"Scene {index}", stage="failed")
                break

            item_start = time.time()
            self.eta_item_start_time = item_start
            success = self.wait_for_completion(
                prompt_id,
                tutorial_progress_phase="video_render",
                tutorial_progress_current=index,
                tutorial_progress_total=total,
                tutorial_progress_label=f"Scene {index}",
            )
            if not success:
                self.root.after(0, lambda sid=scene_id: self._set_scene_entry_render_state(sid, "failed"))
                break

            self.record_tutorial_phase_timing("video_render", time.time() - item_start)
            rendered_output = self._get_newest_rendered_media(before_files, self.scenes_dir, SUPPORTED_VIDEO_EXTENSIONS)
            scene_entry["output_path"] = rendered_output
            scene_entry["render_status"] = "ready"
            self.root.after(0, lambda sid=scene_id, output_path=rendered_output: self._set_scene_entry_render_state(sid, "ready", output_path))
            self.root.after(0, self.refresh_gallery)
            self._set_tutorial_runtime_progress(
                "video_render",
                status=f"Rendered scene {index} of {total}.",
                current=index,
                total=total,
                item_label=f"Scene {index}",
                stage="item_complete",
                output_path=rendered_output,
            )
        else:
            self.update_status("Scene timeline render complete.", "green")
            self._set_tutorial_runtime_progress("video_render", status="Scene timeline render complete.", current=total, total=total, item_label="Scene timeline", stage="complete")

        self.scene_timeline = self._normalize_scene_timeline(scene_timeline)
        self.root.after(0, self.save_project_state)
        self.root.after(0, lambda: self.render_scene_timeline_btn.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.add_scene_btn.config(state=tk.NORMAL))
        if hasattr(self, "sync_t2v_to_image_queue_btn"):
            self.root.after(0, lambda: self.sync_t2v_to_image_queue_btn.config(state=tk.NORMAL))
        if hasattr(self, "sync_image_to_scene_btn"):
            self.root.after(0, lambda: self.sync_image_to_scene_btn.config(state=tk.NORMAL))
        if hasattr(self, "auto_assign_scene_images_btn"):
            self.root.after(0, lambda: self.auto_assign_scene_images_btn.config(state=tk.NORMAL))

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

    def add_image_prompt_entry(self):
        frame = tk.Frame(self.image_scrollable_frame, pady=6)
        frame.pack(fill=tk.X, expand=True)
        self._style_panel(frame, self.colors["card"], border=True)

        text_widget = tk.Text(frame, height=4, width=50)
        text_widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._style_text_input(text_widget, multiline=True)
        frame.prompt_text_widget = text_widget

        btn_frame = tk.Frame(frame)
        btn_frame.pack(side=tk.RIGHT, padx=5)
        self._style_panel(btn_frame, self.colors["card"])

        generate_btn = tk.Button(btn_frame, text="Generate", command=lambda t=text_widget: self.generate_single_image_prompt(t))
        generate_btn.pack(side=tk.TOP, fill=tk.X, pady=(0, 2))
        self._style_button(generate_btn, "accent", compact=True)

        remove_btn = tk.Button(btn_frame, text="Remove", command=lambda f=frame, t=text_widget: self.remove_image_prompt_entry(f, t))
        remove_btn.pack(side=tk.TOP, fill=tk.X)
        self._style_button(remove_btn, "ghost", compact=True)

        self.image_prompts.append(text_widget)
        self.log_debug("IMAGE_PROMPT_ADDED", widget_id=id(text_widget), total_widgets=len(self.image_prompts))
        self.update_image_scroll_region()
        self._update_prompt_collection_summary()

    def _clear_all_prompt_entries(self):
        cleared_count = len(self.scrollable_frame.winfo_children())
        for frame in list(self.scrollable_frame.winfo_children()):
            frame.destroy()
        self.prompts.clear()
        self.log_debug("PROMPTS_CLEARED", cleared_count=cleared_count)
        self.update_scroll_region()
        self._update_prompt_collection_summary()

    def _clear_all_image_prompt_entries(self):
        if not hasattr(self, "image_scrollable_frame"):
            self.image_prompts.clear()
            return

        cleared_count = len(self.image_scrollable_frame.winfo_children())
        for frame in list(self.image_scrollable_frame.winfo_children()):
            frame.destroy()
        self.image_prompts.clear()
        self.log_debug("IMAGE_PROMPTS_CLEARED", cleared_count=cleared_count)
        self.update_image_scroll_region()
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

    def _collect_image_prompt_widgets(self):
        widgets = []
        for frame in self.image_scrollable_frame.winfo_children():
            text_widget = getattr(frame, "prompt_text_widget", None)
            if text_widget is None:
                continue
            try:
                if int(text_widget.winfo_exists()) == 1:
                    widgets.append(text_widget)
            except tk.TclError:
                continue
        self.image_prompts = widgets
        return widgets

    def _collect_prompt_texts(self):
        prompts_text = [w.get("1.0", tk.END).strip() for w in self._collect_prompt_widgets() if w.get("1.0", tk.END).strip()]
        previews = [self._truncate_text(p, 120) for p in prompts_text]
        self.log_debug("PROMPTS_COLLECTED", count=len(prompts_text), previews=previews)
        return prompts_text

    def _collect_image_prompt_texts(self):
        prompts_text = [w.get("1.0", tk.END).strip() for w in self._collect_image_prompt_widgets() if w.get("1.0", tk.END).strip()]
        previews = [self._truncate_text(p, 120) for p in prompts_text]
        self.log_debug("IMAGE_PROMPTS_COLLECTED", count=len(prompts_text), previews=previews)
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

    def remove_image_prompt_entry(self, frame, text_widget):
        try:
            removed_text = text_widget.get("1.0", tk.END).strip()
        except Exception:
            removed_text = ""

        frame.destroy()
        if text_widget in self.image_prompts:
            self.image_prompts.remove(text_widget)

        if not self.image_scrollable_frame.winfo_children():
            self.add_image_prompt_entry()
        else:
            self._collect_image_prompt_widgets()

        self.log_debug(
            "IMAGE_PROMPT_REMOVED",
            widget_id=id(text_widget),
            removed_preview=self._truncate_text(removed_text, 120),
            remaining_widgets=len(self.image_scrollable_frame.winfo_children())
        )

        self.update_image_scroll_region()
        self._update_prompt_collection_summary()

    def update_image_scroll_region(self):
        if not hasattr(self, "image_scrollable_frame"):
            return
        self.image_scrollable_frame.update_idletasks()
        self.image_canvas.configure(scrollregion=self.image_canvas.bbox("all"))

    def clear_ui_fields(self):
        self._clear_all_image_prompt_entries()
        self.add_image_prompt_entry()
        self._clear_all_scene_timeline_entries()
        self.add_scene_timeline_entry()
        self._reset_chatbot_creative_state(refresh_ui=False)
        self.update_debug_prompt_status("(none)")
        self._reset_video_settings_to_loaded_workflow()
        self._reset_image_settings_to_loaded_workflow()
        if getattr(self, "global_image_settings_defaults", None):
            self._apply_saved_image_settings(self.global_image_settings_defaults)
        self.prompts = []
        self.image_prompt_queue = []
        self.image_assets = []
        self.scene_timeline = []
        self.selected_videos.clear()
        self._update_video_selection_summary()
        
        # Clear Music Settings
        self.music_tags_text.delete("1.0", tk.END)
        self.music_lyrics_text.delete("1.0", tk.END)
        self._reset_music_settings_to_loaded_workflow()
        self.strip_audio_var.set(True)
        
        self.current_generated_audio = None
        self.current_audio_source = None
        self.selected_video_for_music = None
        self.current_final_video = None
        self._reset_selected_video_preview()

        if hasattr(self, "chatbot_briefing_text"):
            self.chatbot_briefing_text.delete("1.0", tk.END)
        self._refresh_chatbot_history_list()
        self._refresh_chatbot_output_preview()
        self._refresh_chatbot_runtime_ui()
        
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
            "image_settings": self._get_image_settings_snapshot(),
            "remember_section_open_states": self.remember_section_open_states,
            "last_project_dir": self.current_project_dir,
            "output_root": self.base_output_dir,
            "comfyui_root": self.comfyui_root,
            "comfyui_launcher_path": self.comfyui_launcher_path,
            "model_search_roots": self.model_search_roots,
            "chatbot_model_url": self.chatbot_model_url,
            "chatbot_model_filename": self.chatbot_model_filename,
            "chatbot_model_root": self.chatbot_model_root,
            "chatbot_model_path": self.chatbot_model_path,
            "chatbot_preferred_drive": self.chatbot_preferred_drive,
            "chatbot_backend_mode": self.chatbot_backend_mode,
            "chatbot_server_url": self.chatbot_server_url,
            "chatbot_server_executable_path": self.chatbot_server_executable_path,
            "chatbot_context_size": self.chatbot_context_size,
            "chatbot_request_timeout": self.chatbot_request_timeout,
            "chatbot_temperature": self.chatbot_temperature,
            "chatbot_top_p": self.chatbot_top_p,
            "chatbot_top_k": self.chatbot_top_k,
            "chatbot_min_p": self.chatbot_min_p,
            "chatbot_repeat_penalty": self.chatbot_repeat_penalty,
            "chatbot_default_to_non_thinking": self.chatbot_default_to_non_thinking,
            "chatbot_auto_launch_server": self.chatbot_auto_launch_server,
            "chatbot_model_family": self.chatbot_model_family,
            "chatbot_gemma4_ollama_tag": self.chatbot_gemma4_ollama_tag
        }
        try:
            os.makedirs(os.path.dirname(self.global_settings_file), exist_ok=True)
            with open(self.global_settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"Error saving global settings: {e}")

    def load_global_settings(self):
        try:
            settings, loaded_from = self._read_global_settings_payload()
            self.is_first_launch = loaded_from is None
            self._sync_runtime_paths(settings)
            chatbot_settings_dirty = False

            self._load_video_profile_state(
                settings.get("video_profile", DEFAULT_VIDEO_PROFILE),
                settings.get("api_json_path"),
                settings.get("video_settings", {})
            )
            self.global_image_settings_defaults = settings.get("image_settings", {})
            self.remember_section_open_states = bool(settings.get("remember_section_open_states", False))
            self._apply_saved_image_settings(self.global_image_settings_defaults)
            self.chatbot_model_url = str(settings.get("chatbot_model_url", CHATBOT_MODEL_URL)).strip() or CHATBOT_MODEL_URL
            self.chatbot_model_filename = str(settings.get("chatbot_model_filename", CHATBOT_MODEL_FILENAME)).strip() or CHATBOT_MODEL_FILENAME
            self.chatbot_model_root = self._normalize_path(settings.get("chatbot_model_root")) or self._get_recommended_chatbot_model_root()
            self.chatbot_model_path = self._normalize_path(settings.get("chatbot_model_path")) or self._get_chatbot_model_path_from_root(self.chatbot_model_root)
            self.chatbot_preferred_drive = str(settings.get("chatbot_preferred_drive", "M")).strip().upper().rstrip(":") or "M"
            saved_backend_mode = str(settings.get("chatbot_backend_mode", CHATBOT_BACKEND_MODE_CONNECT)).strip().lower()
            self.chatbot_backend_mode = saved_backend_mode if saved_backend_mode in {CHATBOT_BACKEND_MODE_CONNECT, CHATBOT_BACKEND_MODE_MANAGED, CHATBOT_BACKEND_MODE_OLLAMA} else CHATBOT_BACKEND_MODE_CONNECT
            self.chatbot_server_url = str(settings.get("chatbot_server_url", self._get_default_chatbot_server_url(self.chatbot_backend_mode))).strip() or self._get_default_chatbot_server_url(self.chatbot_backend_mode)
            raw_server_executable_path = self._normalize_path(settings.get("chatbot_server_executable_path")) or ""
            self.chatbot_server_executable_path = self._sanitize_chatbot_server_executable_path(raw_server_executable_path, backend_mode=self.chatbot_backend_mode) or ""
            if self.chatbot_server_executable_path != raw_server_executable_path:
                chatbot_settings_dirty = True
            try:
                self.chatbot_context_size = max(1024, int(settings.get("chatbot_context_size", DEFAULT_CHATBOT_CONTEXT_SIZE)))
            except (TypeError, ValueError):
                self.chatbot_context_size = DEFAULT_CHATBOT_CONTEXT_SIZE
            try:
                self.chatbot_request_timeout = max(15, int(settings.get("chatbot_request_timeout", DEFAULT_CHATBOT_REQUEST_TIMEOUT)))
            except (TypeError, ValueError):
                self.chatbot_request_timeout = DEFAULT_CHATBOT_REQUEST_TIMEOUT
            try:
                self.chatbot_temperature = max(0.0, float(settings.get("chatbot_temperature", DEFAULT_CHATBOT_TEMPERATURE)))
            except (TypeError, ValueError):
                self.chatbot_temperature = DEFAULT_CHATBOT_TEMPERATURE
            try:
                self.chatbot_top_p = min(1.0, max(0.0, float(settings.get("chatbot_top_p", DEFAULT_CHATBOT_TOP_P))))
            except (TypeError, ValueError):
                self.chatbot_top_p = DEFAULT_CHATBOT_TOP_P
            try:
                self.chatbot_top_k = max(1, int(settings.get("chatbot_top_k", DEFAULT_CHATBOT_TOP_K)))
            except (TypeError, ValueError):
                self.chatbot_top_k = DEFAULT_CHATBOT_TOP_K
            try:
                self.chatbot_min_p = min(1.0, max(0.0, float(settings.get("chatbot_min_p", DEFAULT_CHATBOT_MIN_P))))
            except (TypeError, ValueError):
                self.chatbot_min_p = DEFAULT_CHATBOT_MIN_P
            try:
                self.chatbot_repeat_penalty = max(0.0, float(settings.get("chatbot_repeat_penalty", DEFAULT_CHATBOT_REPEAT_PENALTY)))
            except (TypeError, ValueError):
                self.chatbot_repeat_penalty = DEFAULT_CHATBOT_REPEAT_PENALTY
            self.chatbot_default_to_non_thinking = bool(settings.get("chatbot_default_to_non_thinking", DEFAULT_CHATBOT_DEFAULT_TO_NON_THINKING))
            self.chatbot_auto_launch_server = bool(settings.get("chatbot_auto_launch_server", False))
            saved_model_family = str(settings.get("chatbot_model_family", DEFAULT_CHATBOT_MODEL_FAMILY)).strip().lower()
            self.chatbot_model_family = saved_model_family if saved_model_family in {CHATBOT_MODEL_FAMILY_QWEN3, CHATBOT_MODEL_FAMILY_GEMMA4} else DEFAULT_CHATBOT_MODEL_FAMILY
            saved_gemma4_tag = str(settings.get("chatbot_gemma4_ollama_tag", DEFAULT_GEMMA4_OLLAMA_TAG)).strip()
            self.chatbot_gemma4_ollama_tag = saved_gemma4_tag if saved_gemma4_tag in GEMMA4_OLLAMA_TAG_OPTIONS else DEFAULT_GEMMA4_OLLAMA_TAG
            if (
                self.chatbot_backend_mode == CHATBOT_BACKEND_MODE_CONNECT
                and (self.chatbot_server_url or "").rstrip("/") == DEFAULT_CHATBOT_SERVER_URL
                and not self.chatbot_server_executable_path
            ):
                detected_ollama_path = self._detect_ollama_executable()
                if detected_ollama_path:
                    self.chatbot_backend_mode = CHATBOT_BACKEND_MODE_OLLAMA
                    self.chatbot_server_url = DEFAULT_OLLAMA_SERVER_URL
                    self.chatbot_server_executable_path = detected_ollama_path
                    self.chatbot_auto_launch_server = True
                    chatbot_settings_dirty = True
            self._refresh_chatbot_runtime_ui()
            self.load_tutorial_phase_history()
            self._load_comfyui_readiness_history()

            # On first launch, let the user choose where to store projects
            if self.is_first_launch and not settings.get("output_root"):
                chosen = filedialog.askdirectory(
                    title="Choose Output Folder — Where should Prompt2MTV store your projects?",
                    initialdir=self.base_output_dir,
                )
                if chosen:
                    self.base_output_dir = self._normalize_path(chosen)
                    os.makedirs(self.base_output_dir, exist_ok=True)

            last_project = self._normalize_path(settings.get("last_project_dir"))
            if last_project and os.path.exists(last_project):
                self.set_project(last_project)
            else:
                default_project = os.path.join(self.base_output_dir, f"Project_{int(time.time())}")
                self.set_project(default_project)

            if loaded_from == self.legacy_global_settings_file and not os.path.exists(self.global_settings_file):
                self.save_global_settings()
            elif chatbot_settings_dirty:
                self.save_global_settings()
        except Exception as e:
            print(f"Error loading global settings: {e}")
            self.is_first_launch = True
            self.global_image_settings_defaults = {}
            self._sync_runtime_paths({})
            self.chatbot_model_url = CHATBOT_MODEL_URL
            self.chatbot_model_filename = CHATBOT_MODEL_FILENAME
            self.chatbot_model_root = self._get_recommended_chatbot_model_root()
            self.chatbot_model_path = self._get_chatbot_model_path_from_root(self.chatbot_model_root)
            self.chatbot_preferred_drive = "M"
            self.chatbot_backend_mode = CHATBOT_BACKEND_MODE_CONNECT
            self.chatbot_server_url = self._get_default_chatbot_server_url(CHATBOT_BACKEND_MODE_CONNECT)
            self.chatbot_server_executable_path = ""
            self.chatbot_context_size = DEFAULT_CHATBOT_CONTEXT_SIZE
            self.chatbot_request_timeout = DEFAULT_CHATBOT_REQUEST_TIMEOUT
            self.chatbot_temperature = DEFAULT_CHATBOT_TEMPERATURE
            self.chatbot_top_p = DEFAULT_CHATBOT_TOP_P
            self.chatbot_top_k = DEFAULT_CHATBOT_TOP_K
            self.chatbot_min_p = DEFAULT_CHATBOT_MIN_P
            self.chatbot_repeat_penalty = DEFAULT_CHATBOT_REPEAT_PENALTY
            self.chatbot_default_to_non_thinking = DEFAULT_CHATBOT_DEFAULT_TO_NON_THINKING
            self.chatbot_auto_launch_server = False
            self.remember_section_open_states = False
            self.chatbot_backend_health_text = "Backend check: Not tested yet."
            self.tutorial_phase_history = self._create_empty_tutorial_phase_history()
            self._refresh_chatbot_runtime_ui()
            default_project = os.path.join(self.base_output_dir, f"Project_{int(time.time())}")
            self.set_project(default_project)

    def _create_empty_tutorial_phase_history(self):
        return {
            "schema_version": TUTORIAL_PHASE_HISTORY_SCHEMA_VERSION,
            "phases": {},
            "metadata": {
                "updated_at": "",
                "total_recorded_samples": 0,
            },
        }

    def load_tutorial_phase_history(self):
        history_state = self._create_empty_tutorial_phase_history()
        try:
            if os.path.exists(self.tutorial_phase_history_file):
                with open(self.tutorial_phase_history_file, "r", encoding="utf-8") as history_file:
                    payload = json.load(history_file)
                if isinstance(payload, dict):
                    history_state["schema_version"] = int(payload.get("schema_version") or TUTORIAL_PHASE_HISTORY_SCHEMA_VERSION)
                    history_state["metadata"] = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else history_state["metadata"]
                    phase_map = payload.get("phases") if isinstance(payload.get("phases"), dict) else {}
                    normalized_phases = {}
                    for phase_key, phase_state in phase_map.items():
                        normalized_key = str(phase_key or "").strip()
                        if not normalized_key or not isinstance(phase_state, dict):
                            continue
                        samples = []
                        for sample in phase_state.get("samples") or []:
                            if not isinstance(sample, dict):
                                continue
                            try:
                                elapsed_seconds = max(0.0, float(sample.get("elapsed_seconds") or 0.0))
                            except (TypeError, ValueError):
                                continue
                            if elapsed_seconds <= 0:
                                continue
                            samples.append(
                                {
                                    "elapsed_seconds": elapsed_seconds,
                                    "completed_at": str(sample.get("completed_at") or "").strip(),
                                    "status": str(sample.get("status") or "complete").strip() or "complete",
                                }
                            )
                        if not samples:
                            continue
                        trimmed_samples = samples[-TUTORIAL_PHASE_HISTORY_MAX_SAMPLES:]
                        normalized_phases[normalized_key] = self._build_tutorial_phase_history_entry(normalized_key, trimmed_samples)
                    history_state["phases"] = normalized_phases
                    history_state["metadata"] = self._build_tutorial_phase_history_metadata(normalized_phases)
        except Exception as exc:
            print(f"Error loading tutorial phase history: {exc}")
        self.tutorial_phase_history = history_state
        return history_state

    def _build_tutorial_phase_history_entry(self, phase_key, samples):
        trimmed_samples = list(samples or [])[-TUTORIAL_PHASE_HISTORY_MAX_SAMPLES:]
        elapsed_values = [max(0.0, float(sample.get("elapsed_seconds") or 0.0)) for sample in trimmed_samples]
        elapsed_values = [value for value in elapsed_values if value > 0]
        average_seconds = (sum(elapsed_values) / len(elapsed_values)) if elapsed_values else 0.0
        last_completed_at = str(trimmed_samples[-1].get("completed_at") or "").strip() if trimmed_samples else ""
        return {
            "phase_key": str(phase_key or "").strip(),
            "samples": trimmed_samples,
            "sample_count": len(trimmed_samples),
            "average_seconds": average_seconds,
            "last_completed_at": last_completed_at,
        }

    def _build_tutorial_phase_history_metadata(self, phase_map):
        phase_map = phase_map if isinstance(phase_map, dict) else {}
        total_samples = sum(int((phase_state or {}).get("sample_count") or 0) for phase_state in phase_map.values())
        return {
            "updated_at": datetime.now().isoformat(timespec="seconds"),
            "total_recorded_samples": total_samples,
        }

    def save_tutorial_phase_history(self):
        try:
            os.makedirs(os.path.dirname(self.tutorial_phase_history_file), exist_ok=True)
            phase_map = self.tutorial_phase_history.get("phases") if isinstance(self.tutorial_phase_history, dict) else {}
            normalized_phases = {}
            for phase_key, phase_state in (phase_map or {}).items():
                if not isinstance(phase_state, dict):
                    continue
                normalized_entry = self._build_tutorial_phase_history_entry(phase_key, phase_state.get("samples") or [])
                if normalized_entry.get("sample_count"):
                    normalized_phases[str(phase_key)] = normalized_entry
            payload = {
                "schema_version": TUTORIAL_PHASE_HISTORY_SCHEMA_VERSION,
                "phases": normalized_phases,
                "metadata": self._build_tutorial_phase_history_metadata(normalized_phases),
            }
            with open(self.tutorial_phase_history_file, "w", encoding="utf-8") as history_file:
                json.dump(payload, history_file, indent=4)
            self.tutorial_phase_history = payload
        except Exception as exc:
            print(f"Error saving tutorial phase history: {exc}")

    def record_tutorial_phase_timing(self, phase_key, elapsed_seconds, status="complete"):
        normalized_key = str(phase_key or "").strip()
        normalized_status = str(status or "complete").strip().lower() or "complete"
        try:
            normalized_elapsed = max(0.0, float(elapsed_seconds or 0.0))
        except (TypeError, ValueError):
            return None
        if not normalized_key or normalized_status != "complete" or normalized_elapsed <= 0:
            return None

        history_state = self.tutorial_phase_history if isinstance(self.tutorial_phase_history, dict) else self._create_empty_tutorial_phase_history()
        phase_map = history_state.setdefault("phases", {})
        phase_entry = phase_map.get(normalized_key) if isinstance(phase_map.get(normalized_key), dict) else {"samples": []}
        samples = list(phase_entry.get("samples") or [])
        samples.append(
            {
                "elapsed_seconds": normalized_elapsed,
                "completed_at": datetime.now().isoformat(timespec="seconds"),
                "status": normalized_status,
            }
        )
        phase_map[normalized_key] = self._build_tutorial_phase_history_entry(normalized_key, samples)
        history_state["metadata"] = self._build_tutorial_phase_history_metadata(phase_map)
        self.tutorial_phase_history = history_state
        self.save_tutorial_phase_history()
        return phase_map.get(normalized_key)

    def get_tutorial_phase_average_seconds(self, phase_key, fallback_seconds=None):
        normalized_key = str(phase_key or "").strip()
        if not normalized_key:
            return fallback_seconds
        phase_map = self.tutorial_phase_history.get("phases") if isinstance(self.tutorial_phase_history, dict) else {}
        phase_entry = phase_map.get(normalized_key) if isinstance(phase_map, dict) else None
        if not isinstance(phase_entry, dict):
            return fallback_seconds
        try:
            average_seconds = float(phase_entry.get("average_seconds") or 0.0)
        except (TypeError, ValueError):
            return fallback_seconds
        return average_seconds if average_seconds > 0 else fallback_seconds

    def _format_eta_display(self, eta_seconds):
        if eta_seconds is None or eta_seconds < 0:
            return "Estimating..."
        eta_seconds = int(eta_seconds)
        if eta_seconds < 10:
            return "< 10s"
        if eta_seconds < 60:
            return f"~{eta_seconds}s"
        minutes, seconds = divmod(eta_seconds, 60)
        if minutes < 60:
            return f"~{minutes}m {seconds:02d}s"
        hours, minutes = divmod(minutes, 60)
        return f"~{hours}h {minutes:02d}m"

    def _format_elapsed_display(self, elapsed_seconds):
        if elapsed_seconds is None or elapsed_seconds < 0:
            return "0s"
        elapsed_seconds = int(elapsed_seconds)
        if elapsed_seconds < 60:
            return f"{elapsed_seconds}s"
        minutes, seconds = divmod(elapsed_seconds, 60)
        if minutes < 60:
            return f"{minutes}m {seconds:02d}s"
        hours, minutes = divmod(minutes, 60)
        return f"{hours}h {minutes:02d}m"

    def _calculate_phase_eta(self, phase_key, current_item, total_items):
        avg = self.get_tutorial_phase_average_seconds(phase_key)
        if avg is None or total_items <= 0:
            return None
        remaining_items = max(0, total_items - current_item)
        current_elapsed = 0.0
        if self.eta_item_start_time:
            current_elapsed = time.time() - self.eta_item_start_time
        if current_item < total_items:
            remaining_on_current = max(0.0, avg - current_elapsed)
        else:
            remaining_on_current = 0.0
        eta_seconds = (remaining_items * avg) + remaining_on_current
        return max(0.0, eta_seconds)

    def _show_eta_panel(self, phase_key, total, current=0):
        self.eta_active_phase = phase_key
        self.eta_phase_start_time = time.time()
        self.eta_item_start_time = time.time()
        display_name = PHASE_DISPLAY_NAMES.get(phase_key, phase_key)
        try:
            self.eta_phase_label.config(text=display_name)
            self.eta_item_label.config(text=f"Item {current} of {total}" if total > 1 else "Processing...")
            self.eta_elapsed_label.config(text="Elapsed: 0s")
            self.eta_countdown_label.config(text="ETA: Estimating...")
            self.eta_progress_bar["value"] = 0
            self.eta_percent_label.config(text="0%")
            self.eta_panel_frame.pack(fill=tk.X, padx=10, pady=(0, 2))
        except tk.TclError:
            return
        self._start_eta_tick()

    def _hide_eta_panel(self, delay_ms=3000):
        def do_hide():
            self.eta_active_phase = None
            self.eta_item_start_time = None
            self.eta_phase_start_time = None
            self.eta_variant_timing_key = None
            self._stop_eta_tick()
            try:
                self.eta_panel_frame.pack_forget()
            except tk.TclError:
                pass
        if delay_ms > 0:
            self.root.after(delay_ms, do_hide)
        else:
            do_hide()

    def _update_eta_display(self, phase_key, current, total, stage=None):
        if not hasattr(self, "eta_panel_frame"):
            return
        if stage in ("complete", "failed"):
            elapsed = time.time() - self.eta_phase_start_time if self.eta_phase_start_time else 0
            pct = 100 if stage == "complete" else int((current / max(total, 1)) * 100)
            try:
                self.eta_progress_bar["value"] = pct
                self.eta_percent_label.config(text=f"{pct}%")
                self.eta_elapsed_label.config(text=f"Elapsed: {self._format_elapsed_display(elapsed)}")
                status_text = "Complete!" if stage == "complete" else "Failed"
                self.eta_countdown_label.config(text=status_text)
                self.eta_item_label.config(text=f"Done — {current} of {total}" if stage == "complete" else f"Failed at {current} of {total}")
            except tk.TclError:
                pass
            self._hide_eta_panel(delay_ms=5000)
            return
        if stage == "item_complete":
            self.eta_item_start_time = time.time()
        pct = int((max(current - 1, 0) / max(total, 1)) * 100) if stage != "item_complete" else int((current / max(total, 1)) * 100)
        eta_seconds = self._calculate_phase_eta(phase_key, current if stage == "item_complete" else current - 1, total)
        elapsed = time.time() - self.eta_phase_start_time if self.eta_phase_start_time else 0
        try:
            self.eta_progress_bar["value"] = pct
            self.eta_percent_label.config(text=f"{pct}%")
            self.eta_elapsed_label.config(text=f"Elapsed: {self._format_elapsed_display(elapsed)}")
            self.eta_countdown_label.config(text=f"ETA: {self._format_eta_display(eta_seconds)}")
            if total > 1:
                self.eta_item_label.config(text=f"Item {current} of {total}")
            elif self.ws_progress.get("total", 0) > 0:
                ws_step = self.ws_progress.get("step", 0)
                ws_total = self.ws_progress["total"]
                self.eta_item_label.config(text=f"Step {ws_step} of {ws_total}")
            else:
                self.eta_item_label.config(text="Processing...")
        except tk.TclError:
            pass

    def _tick_eta_display(self):
        if not self.eta_active_phase or not self.eta_phase_start_time:
            return
        elapsed = time.time() - self.eta_phase_start_time
        progress_state = self.tutorial_runtime_progress.get(self.eta_active_phase, {})
        current = progress_state.get("current", 0)
        total = progress_state.get("total", 1)
        stage = progress_state.get("stage", "")
        if stage in ("complete", "failed"):
            return

        # XL generation: phase-aware ETA using server progress and historical averages
        if self.eta_active_phase == "music_generate_xl" and self.xl_gen_phase:
            phase = self.xl_gen_phase
            phase_elapsed = (time.time() - self.xl_gen_phase_start) if self.xl_gen_phase_start else elapsed
            server_progress = self.xl_gen_progress
            stage_text = self.xl_gen_stage_text

            if phase in ("submitting", "model_loading"):
                # Use historical cold/warm submit average for ETA
                if phase == "model_loading" or not self.acestep_model_loaded:
                    avg = self.get_tutorial_phase_average_seconds(XL_PHASE_SUBMIT_COLD, fallback_seconds=XL_COLD_START_DEFAULT_SECONDS)
                    phase_label = "Loading XL model (first run ~7 min)..."
                else:
                    avg = self.get_tutorial_phase_average_seconds(XL_PHASE_SUBMIT_WARM, fallback_seconds=XL_WARM_SUBMIT_DEFAULT_SECONDS)
                    phase_label = "Submitting..."
                eta_seconds = max(0.0, avg - phase_elapsed) if avg else None
                pct = min(95, int((phase_elapsed / avg) * 100)) if avg and avg > 0 else 0
                try:
                    self.eta_progress_bar["value"] = pct
                    self.eta_percent_label.config(text=f"{pct}%")
                    self.eta_elapsed_label.config(text=f"Elapsed: {self._format_elapsed_display(elapsed)}")
                    self.eta_countdown_label.config(text=f"ETA: {self._format_eta_display(eta_seconds)}")
                    self.eta_item_label.config(text=phase_label)
                    self.music_status_label.config(
                        text=f"Status: {phase_label} ({self._format_elapsed_display(elapsed)}, ETA: {self._format_eta_display(eta_seconds)})",
                        fg="blue",
                    )
                    self._update_collapsible_section_meta("music_actions", f"XL: {phase_label}")
                except tk.TclError:
                    pass
            elif phase == "generating":
                # Use server progress for real-time ETA when available
                if server_progress > 0.01 and phase_elapsed > 0:
                    eta_seconds = (phase_elapsed / server_progress) * (1.0 - server_progress)
                    pct = int(server_progress * 100)
                else:
                    avg = self.get_tutorial_phase_average_seconds(XL_PHASE_GENERATION, fallback_seconds=XL_GENERATION_DEFAULT_SECONDS)
                    eta_seconds = max(0.0, avg - phase_elapsed) if avg else None
                    pct = min(95, int((phase_elapsed / avg) * 100)) if avg and avg > 0 else 0
                progress_label = f"Generating audio — {pct}%"
                if stage_text:
                    progress_label = f"Generating — {stage_text}"
                try:
                    self.eta_progress_bar["value"] = pct
                    self.eta_percent_label.config(text=f"{pct}%")
                    self.eta_elapsed_label.config(text=f"Elapsed: {self._format_elapsed_display(elapsed)}")
                    self.eta_countdown_label.config(text=f"ETA: {self._format_eta_display(eta_seconds)}")
                    self.eta_item_label.config(text=progress_label)
                    self.music_status_label.config(
                        text=f"Status: {progress_label} ({self._format_elapsed_display(elapsed)}, ETA: {self._format_eta_display(eta_seconds)})",
                        fg="blue",
                    )
                    self._update_collapsible_section_meta("music_actions", f"XL: {progress_label}")
                except tk.TclError:
                    pass
            elif phase == "downloading":
                avg = self.get_tutorial_phase_average_seconds(XL_PHASE_DOWNLOAD, fallback_seconds=XL_DOWNLOAD_DEFAULT_SECONDS)
                eta_seconds = max(0.0, avg - phase_elapsed) if avg else None
                try:
                    self.eta_progress_bar["value"] = 95
                    self.eta_percent_label.config(text="95%")
                    self.eta_elapsed_label.config(text=f"Elapsed: {self._format_elapsed_display(elapsed)}")
                    self.eta_countdown_label.config(text=f"ETA: {self._format_eta_display(eta_seconds)}")
                    self.eta_item_label.config(text="Downloading audio...")
                    self.music_status_label.config(
                        text=f"Status: Downloading audio... ({self._format_elapsed_display(elapsed)})",
                        fg="blue",
                    )
                except tk.TclError:
                    pass
            self.eta_tick_id = self.root.after(1000, self._tick_eta_display)
            return

        # Chatbot phases: use historical cold/warm averages for ETA
        if str(self.eta_active_phase or "").startswith("chatbot_"):
            is_cold = str(self.eta_active_phase or "").endswith("_cold")
            fallback = CHATBOT_COLD_START_DEFAULT_SECONDS if is_cold else CHATBOT_WARM_DEFAULT_SECONDS
            avg = self.get_tutorial_phase_average_seconds(self.eta_active_phase, fallback_seconds=fallback)
            eta_seconds = max(0.0, avg - elapsed) if avg else None
            pct = min(95, int((elapsed / avg) * 100)) if avg and avg > 0 else 0
            status_text = progress_state.get("status", "")
            display_name = PHASE_DISPLAY_NAMES.get(self.eta_active_phase, "Chatbot")
            elapsed_str = self._format_elapsed_display(elapsed)
            eta_str = self._format_eta_display(eta_seconds) if eta_seconds is not None else "Estimating..."
            try:
                self.eta_progress_bar["value"] = pct
                self.eta_percent_label.config(text=f"{pct}%")
                self.eta_elapsed_label.config(text=f"Elapsed: {elapsed_str}")
                self.eta_countdown_label.config(text=f"ETA: {eta_str}")
                self.eta_item_label.config(text=status_text or display_name)
                # Update chatbot in-tab status label with live elapsed/ETA
                if hasattr(self, "chatbot_result_status_label") and self.chatbot_generation_in_progress:
                    inline_text = f"{status_text or display_name}  ({elapsed_str}, ETA: {eta_str})"
                    self.chatbot_result_status_label.config(text=inline_text)
            except tk.TclError:
                pass
            self.eta_tick_id = self.root.after(1000, self._tick_eta_display)
            return

        # Use WebSocket step-level progress when available
        ws_step = self.ws_progress.get("step", 0)
        ws_total = self.ws_progress.get("total", 0)
        if ws_total > 0 and ws_step > 0:
            pct = int((ws_step / ws_total) * 100)
            if elapsed > 0 and ws_step > 0:
                secs_per_step = elapsed / ws_step
                remaining_steps = ws_total - ws_step
                eta_seconds = remaining_steps * secs_per_step
            else:
                eta_seconds = self._calculate_phase_eta(self.eta_active_phase, max(current - 1, 0), total)
            step_label = f"Step {ws_step} of {ws_total}"
            try:
                self.eta_progress_bar["value"] = pct
                self.eta_percent_label.config(text=f"{pct}%")
                self.eta_elapsed_label.config(text=f"Elapsed: {self._format_elapsed_display(elapsed)}")
                self.eta_countdown_label.config(text=f"ETA: {self._format_eta_display(eta_seconds)}")
                self.eta_item_label.config(text=step_label)
                # Update music status label with step progress
                if self.eta_active_phase == "music_generate":
                    self.music_status_label.config(text=f"Status: Generating Music... {step_label} ({pct}%)", fg="blue")
                    self._update_collapsible_section_meta("music_actions", f"Generating... {step_label} ({pct}%)")
            except tk.TclError:
                pass
        else:
            # Fallback to historical ETA when no WS data
            # Prefer variant-specific timing key for music generation
            eta_phase_key = self.eta_variant_timing_key or self.eta_active_phase
            completed = current - 1 if stage not in ("item_complete",) else current
            eta_seconds = self._calculate_phase_eta(eta_phase_key, max(completed, 0), total)
            try:
                self.eta_elapsed_label.config(text=f"Elapsed: {self._format_elapsed_display(elapsed)}")
                self.eta_countdown_label.config(text=f"ETA: {self._format_eta_display(eta_seconds)}")
                # Show elapsed time in music status even without WS step data
                if self.eta_active_phase == "music_generate" and stage in ("running", "queued", "submitting"):
                    elapsed_str = self._format_elapsed_display(elapsed)
                    eta_str = self._format_eta_display(eta_seconds) if eta_seconds is not None else "Estimating..."
                    self.music_status_label.config(text=f"Status: Generating Music... ({elapsed_str}, ETA: {eta_str})", fg="blue")
                    self._update_collapsible_section_meta("music_actions", f"Generating... ({elapsed_str})")
            except tk.TclError:
                pass
        self.eta_tick_id = self.root.after(1000, self._tick_eta_display)

    def _start_eta_tick(self):
        self._stop_eta_tick()
        self.eta_tick_id = self.root.after(1000, self._tick_eta_display)

    def _stop_eta_tick(self):
        if self.eta_tick_id is not None:
            try:
                self.root.after_cancel(self.eta_tick_id)
            except tk.TclError:
                pass
            self.eta_tick_id = None

    def save_project_state(self):
        if not self.current_project_dir:
            return

        if self.project_state_save_after_id is not None:
            try:
                self.root.after_cancel(self.project_state_save_after_id)
            except tk.TclError:
                pass
            self.project_state_save_after_id = None
            
        project_data_file = os.path.join(self.current_project_dir, "project_data.json")
        image_prompts_text = self._collect_image_prompt_texts()
        collected_scene_timeline = self._collect_scene_timeline_from_widgets() if hasattr(self, "scene_scrollable_frame") else []
        self.scene_timeline = self._normalize_scene_timeline(collected_scene_timeline)
        self.image_assets = self._normalize_image_assets(self.image_assets)
        self.image_prompt_queue = image_prompts_text
        legacy_prompts = self._get_t2v_prompts_from_scene_timeline(self.scene_timeline)
        state = {
            "schema_version": PROJECT_STATE_SCHEMA_VERSION,
            "prompts": legacy_prompts,
            "image_prompt_queue": image_prompts_text,
            "image_settings": self._get_image_settings_snapshot(),
            "image_assets": self.image_assets,
            "scene_timeline": self.scene_timeline,
            "collapsible_ui_state": self._get_collapsible_ui_state_snapshot(),
            "chatbot_state": self._serialize_chatbot_creative_state(),
            "video_profile": self._get_selected_video_profile_key(),
            "api_json_path": self.api_json_path,
            "video_settings": self._get_video_settings_snapshot(),
            "music_tags": self.music_tags_text.get("1.0", tk.END).strip(),
            "music_lyrics": self.music_lyrics_text.get("1.0", tk.END).strip(),
            "music_settings": self._get_music_settings_snapshot(),
            "music_ui_state": self._get_music_ui_state_snapshot(),
            "music_duration": self.music_duration_var.get(),
            "music_bpm": self.music_bpm_var.get(),
            "music_key": self.music_key_var.get(),
            "strip_audio": self.strip_audio_var.get(),
            "current_generated_audio": self.current_generated_audio,
            "current_audio_source": self.current_audio_source,
            "selected_video_for_music": self.selected_video_for_music,
            "current_final_video": getattr(self, 'current_final_video', None),
            "autonomous_target_duration": self.autonomous_target_duration,
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
        self.project_state_restore_in_progress = True
        
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
                self._apply_saved_image_settings(state.get("image_settings") or self.global_image_settings_defaults)
                
                # Load Video Prompts
                saved_prompts = state.get("prompts", [])
                self.image_prompt_queue = self._normalize_string_list(state.get("image_prompt_queue", []))
                self.image_assets = self._normalize_image_assets(state.get("image_assets", []))
                self.scene_timeline = self._normalize_scene_timeline(state.get("scene_timeline", []), fallback_prompts=saved_prompts)
                self._update_prompt_collection_summary()

                saved_image_prompts = self.image_prompt_queue
                if saved_image_prompts:
                    self._clear_all_image_prompt_entries()
                    for prompt_text in saved_image_prompts:
                        self.add_image_prompt_entry()
                        self.image_prompts[-1].insert(tk.END, prompt_text)
                self._update_prompt_collection_summary()

                if self.scene_timeline:
                    self._rebuild_scene_timeline_from_state(self.scene_timeline)
                else:
                    self.add_scene_timeline_entry()

                self._load_chatbot_creative_state(state.get("chatbot_state"))
                self._apply_chatbot_view_state_to_widgets()
                self._refresh_chatbot_history_list()
                self._refresh_chatbot_output_preview()
                
                # Load Music Settings
                self.music_tags_text.insert(tk.END, state.get("music_tags", ""))
                self.music_lyrics_text.insert(tk.END, state.get("music_lyrics", ""))
                self._apply_music_settings_snapshot(state.get("music_settings"), legacy_state=state)
                self.strip_audio_var.set(state.get("strip_audio", True))
                
                # Load Music State
                self.current_generated_audio = state.get("current_generated_audio")
                self.current_audio_source = state.get("current_audio_source") or self._infer_audio_source(self.current_generated_audio)
                self.selected_video_for_music = state.get("selected_video_for_music")
                self.current_final_video = state.get("current_final_video")

                # Load Autonomous Mode State
                saved_auto_dur = state.get("autonomous_target_duration")
                if saved_auto_dur is not None:
                    self.autonomous_target_duration = int(saved_auto_dur)
                    if hasattr(self, "autonomous_duration_var"):
                        self.autonomous_duration_var.set(str(self.autonomous_target_duration))

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
                    self.current_audio_source = None
                    self.preview_music_btn.config(state=tk.DISABLED)
                    self.merge_music_btn.config(state=tk.DISABLED)
                    
                if self.current_final_video and os.path.exists(self.current_final_video):
                    if hasattr(self, 'preview_final_btn'):
                        self.preview_final_btn.config(state=tk.NORMAL)
                else:
                    self.current_final_video = None
                    if hasattr(self, 'preview_final_btn'):
                        self.preview_final_btn.config(state=tk.DISABLED)

                if self.remember_section_open_states:
                    restored_ui_state = state.get("collapsible_ui_state")
                    if not isinstance(restored_ui_state, dict):
                        restored_ui_state = state.get("music_ui_state")
                    self._apply_collapsible_ui_state_snapshot(restored_ui_state)
                self._refresh_music_sidebar_state()

            except Exception as e:
                print(f"Error loading project state: {e}")
            finally:
                self.project_state_restore_in_progress = False
        else:
            self.project_state_restore_in_progress = False

    def refresh_gallery(self):
        # Clear existing
        for widget in self.gallery_inner_frame.winfo_children():
            widget.destroy()
        self.thumbnail_images.clear()
        self.video_checkbox_vars.clear()
        self.gallery_video_cards.clear()
        final_files = self._get_gallery_video_files(self.final_mv_dir)
        stitched_files = self._get_gallery_video_files(self.stitched_dir)
        scene_files = self._get_gallery_video_files(self.scenes_dir)
        imported_files = self._get_gallery_video_files(self.imported_video_dir)
        generated_image_files = self._get_gallery_image_files(self.generated_image_dir)
        imported_image_files = self._get_gallery_image_files(self.imported_image_dir)
        current_project_videos = {
            os.path.join(self.final_mv_dir, filename) for filename in final_files
        } | {
            os.path.join(self.stitched_dir, filename) for filename in stitched_files
        } | {
            os.path.join(self.scenes_dir, filename) for filename in scene_files
        } | {
            os.path.join(self.imported_video_dir, filename) for filename in imported_files
        }
        self.selected_videos = {path for path in self.selected_videos if path in current_project_videos}

        self._update_gallery_overview(len(final_files), len(stitched_files), len(scene_files), len(generated_image_files) + len(imported_image_files))
        self._refresh_scene_asset_choices()

        self._populate_image_gallery_section(
            "Imported Images",
            "Project-owned stills brought in manually for later image-to-video use.",
            self.imported_image_dir,
            imported_image_files
        )

        self._populate_image_gallery_section(
            "Generated Images",
            "Still frames generated from the image phase queue.",
            self.generated_image_dir,
            generated_image_files
        )

        self._populate_gallery_section(
            "Imported Clips",
            "Project-owned clips you brought in manually or by drag and drop.",
            self.imported_video_dir,
            imported_files,
            show_add_music=True
        )

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
            [f for f in os.listdir(folder_path) if self._is_supported_video_file(f)],
            key=lambda x: os.path.getmtime(os.path.join(folder_path, x)),
            reverse=True
        )

    def _get_gallery_image_files(self, folder_path):
        if not os.path.exists(folder_path):
            return []
        return sorted(
            [f for f in os.listdir(folder_path) if self._is_supported_image_file(f)],
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

    def _populate_image_gallery_section(self, title, description, folder_path, files):
        section_frame = tk.Frame(self.gallery_inner_frame, padx=14, pady=14)
        section_frame.pack(fill=tk.X, padx=4, pady=(0, 12))
        self._style_panel(section_frame, self.colors["surface"], border=True)

        usage_map = self._get_image_asset_usage_map()
        section_assets = []
        for filename in files:
            image_path = os.path.join(folder_path, filename)
            section_assets.append((filename, self._get_image_asset_by_path(image_path)))

        section_assets.sort(
            key=lambda item: (
                int(item[1].get("order_index") or 10 ** 6) if item[1] else 10 ** 6,
                -os.path.getmtime(os.path.join(folder_path, item[0])) if os.path.exists(os.path.join(folder_path, item[0])) else 0,
                item[0].lower()
            )
        )
        used_count = sum(
            1 for _filename, asset in section_assets
            if asset and usage_map.get(str(asset.get("asset_id") or "").strip())
        )
        unused_count = max(len(section_assets) - used_count, 0)

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

        _, unused_label = self._create_metric_chip(header_row, "Unused", str(unused_count))
        unused_label.master.pack(side=tk.RIGHT, padx=(12, 0))
        _, used_label = self._create_metric_chip(header_row, "Used", str(used_count))
        used_label.master.pack(side=tk.RIGHT, padx=(12, 0))
        _, count_label = self._create_metric_chip(header_row, "Items", str(len(files)))
        count_label.master.pack(side=tk.RIGHT, padx=(12, 0))

        if not files:
            empty_label = tk.Label(section_frame, text="No images in this section yet.", anchor="w")
            empty_label.pack(fill=tk.X, pady=(14, 0))
            self._style_label(empty_label, "muted", self.colors["surface"])
            return

        for filename, asset in section_assets:
            image_path = os.path.join(folder_path, filename)
            self.add_gallery_image_item(section_frame, image_path, filename, image_asset=asset, usage_map=usage_map)

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
        add_music_btn = None
        if show_add_music:
            add_music_btn = tk.Button(btn_frame, text="Add Music", command=lambda p=video_path, t=thumb_path: self.select_video_for_music(p, t))
            add_music_btn.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
            self._style_button(add_music_btn, "accent", compact=True)

        self.gallery_video_cards[os.path.normcase(video_path)] = {
            "frame": frame,
            "thumbnail_button": btn,
            "title_label": lbl,
            "checkbox": chk,
            "checkbox_var": var,
            "add_music_btn": add_music_btn,
            "open_folder_btn": open_folder_btn,
            "delete_btn": delete_btn,
            "thumb_path": thumb_path,
            "video_path": video_path,
        }

    def add_gallery_image_item(self, parent, image_path, title, image_asset=None, usage_map=None):
        frame = tk.Frame(parent, bd=0, relief=tk.FLAT)
        frame.pack(fill=tk.X, pady=(12, 0))
        self._style_panel(frame, self.colors["card"], border=True)

        image_asset = image_asset or self._get_image_asset_by_path(image_path)
        usage_map = usage_map or self._get_image_asset_usage_map()
        asset_id = str(image_asset.get("asset_id") or "").strip() if image_asset else ""
        usage_entries = usage_map.get(asset_id, []) if asset_id else []
        scene_numbers = sorted({int(entry.get("order_index") or 0) for entry in usage_entries if int(entry.get("order_index") or 0) > 0})
        order_index = int(image_asset.get("order_index") or 0) if image_asset else 0
        label_text = str(image_asset.get("label") or "").strip() if image_asset else ""
        if not label_text:
            label_text = os.path.splitext(os.path.basename(image_path))[0]
        source_text = str(image_asset.get("source") or self._infer_image_source(image_path) or "linked").strip().title() or "Linked"
        usage_text = f"Used in scenes {', '.join(str(number) for number in scene_numbers)}" if scene_numbers else "Unused in scene timeline"
        prompt_text = str(image_asset.get("prompt_text") or "").strip() if image_asset else ""

        thumb_shell = tk.Frame(frame, padx=8, pady=8)
        thumb_shell.pack(side=tk.LEFT, padx=(0, 6), pady=0)
        self._style_panel(thumb_shell, self.colors["surface_soft"])

        try:
            img = Image.open(image_path)
            img.thumbnail((160, 90))
            photo = ImageTk.PhotoImage(img)
            self.thumbnail_images.append(photo)

            btn = tk.Button(thumb_shell, image=photo, command=lambda p=image_path: self.play_video(p), bg=self.colors["black"], cursor="hand2")
            btn.pack(side=tk.LEFT)
            btn.configure(relief=tk.FLAT, bd=0, highlightthickness=0, activebackground=self.colors["black"], activeforeground=self.colors["text"])
        except Exception as e:
            print(f"Error loading image thumbnail: {e}")
            btn = tk.Button(thumb_shell, text="Open", width=15, height=5, command=lambda p=image_path: self.play_video(p), bg=self.colors["black"], fg=self.colors["text"], cursor="hand2")
            btn.pack(side=tk.LEFT)
            btn.configure(relief=tk.FLAT, bd=0, highlightthickness=0, activebackground=self.colors["black"], activeforeground=self.colors["text"])

        info_frame = tk.Frame(frame)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=10)
        self._style_panel(info_frame, self.colors["card"])

        title_prefix = f"{order_index:02d} | " if order_index > 0 else ""
        lbl = tk.Label(info_frame, text=f"{title_prefix}{label_text}", wraplength=260, justify=tk.LEFT)
        lbl.pack(anchor="nw")
        self._style_label(lbl, "body_strong", self.colors["card"])

        modified_text = datetime.fromtimestamp(os.path.getmtime(image_path)).strftime("%b %d, %Y %I:%M %p")
        meta_label = tk.Label(info_frame, text=f"{source_text} image | {os.path.basename(image_path)} | Updated {modified_text}", anchor="w", wraplength=420, justify=tk.LEFT)
        meta_label.pack(anchor="w", pady=(4, 6))
        self._style_label(meta_label, "muted", self.colors["card"])

        usage_label = tk.Label(info_frame, text=usage_text, anchor="w", wraplength=420, justify=tk.LEFT)
        usage_label.pack(anchor="w")
        self._style_label(usage_label, "body", self.colors["card"])

        if prompt_text:
            prompt_label = tk.Label(info_frame, text=f"Prompt: {self._truncate_text(prompt_text, 140)}", anchor="w", wraplength=420, justify=tk.LEFT)
            prompt_label.pack(anchor="w", pady=(4, 0))
            self._style_label(prompt_label, "muted", self.colors["card"])

        btn_frame = tk.Frame(info_frame)
        btn_frame.pack(fill=tk.X, pady=(8, 0))
        self._style_panel(btn_frame, self.colors["card"])
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

        rename_btn = tk.Button(
            btn_frame,
            text="Rename",
            command=lambda asset_id=asset_id, image_path=image_path: self.prompt_rename_image_asset(asset_id, image_path)
        )
        rename_btn.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self._style_button(rename_btn, "ghost", compact=True)

        move_up_btn = tk.Button(
            btn_frame,
            text="Move Up",
            command=lambda asset_id=asset_id: self.move_image_asset(asset_id, -1)
        )
        move_up_btn.grid(row=0, column=1, sticky="ew", padx=4)
        self._style_button(move_up_btn, "ghost", compact=True)

        move_down_btn = tk.Button(
            btn_frame,
            text="Move Down",
            command=lambda asset_id=asset_id: self.move_image_asset(asset_id, 1)
        )
        move_down_btn.grid(row=0, column=2, sticky="ew", padx=(4, 0))
        self._style_button(move_down_btn, "ghost", compact=True)

        if not asset_id:
            rename_btn.configure(state=tk.DISABLED)
            move_up_btn.configure(state=tk.DISABLED)
            move_down_btn.configure(state=tk.DISABLED)
        elif order_index <= 1:
            move_up_btn.configure(state=tk.DISABLED)
        if asset_id and order_index >= len(self.image_assets):
            move_down_btn.configure(state=tk.DISABLED)

        open_folder_btn = tk.Button(btn_frame, text="Open Folder", command=lambda p=image_path: self.open_folder(p))
        open_folder_btn.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(0, 4), pady=(8, 0))
        self._style_button(open_folder_btn, "secondary", compact=True)

        delete_btn = tk.Button(btn_frame, text="Delete", fg="red", command=lambda p=image_path, asset_id=asset_id: self.delete_image(p, asset_id=asset_id))
        delete_btn.grid(row=1, column=2, sticky="ew", padx=(4, 0), pady=(8, 0))
        self._style_button(delete_btn, "danger", compact=True)

    def move_image_asset(self, asset_id, direction):
        normalized_asset_id = str(asset_id or "").strip()
        if not normalized_asset_id or not direction:
            return

        assets = list(self._normalize_image_assets(self.image_assets))
        current_index = next((index for index, asset in enumerate(assets) if str(asset.get("asset_id") or "").strip() == normalized_asset_id), None)
        if current_index is None:
            return

        target_index = current_index + int(direction)
        if target_index < 0 or target_index >= len(assets):
            return

        assets[current_index], assets[target_index] = assets[target_index], assets[current_index]
        self.image_assets = self._reindex_ordered_entries(assets)
        self.save_project_state()
        self.refresh_gallery()

    def prompt_rename_image_asset(self, asset_id, image_path=None):
        asset = self._get_image_asset_by_id(asset_id) if asset_id else self._get_image_asset_by_path(image_path)
        if not asset:
            return

        current_label = str(asset.get("label") or "").strip() or os.path.splitext(os.path.basename(asset.get("project_path") or image_path or "image"))[0]
        new_label = simpledialog.askstring(
            "Rename Image Asset",
            "Enter a storyboard label for this image:",
            initialvalue=current_label,
            parent=self.root
        )
        if new_label is None:
            return

        cleaned_label = str(new_label).strip() or os.path.splitext(os.path.basename(asset.get("project_path") or image_path or "image"))[0]
        asset["label"] = cleaned_label
        asset["updated_at"] = datetime.now().isoformat(timespec="seconds")
        self.save_project_state()
        self.refresh_gallery()

    def _clear_image_asset_references(self, asset_id):
        normalized_asset_id = str(asset_id or "").strip()
        if not normalized_asset_id:
            return []

        scene_timeline = self._collect_scene_timeline_from_widgets() if hasattr(self, "scene_scrollable_frame") else self.scene_timeline
        updated_scene_timeline = []
        cleared_scene_numbers = []
        for entry in self._normalize_scene_timeline(scene_timeline):
            entry_copy = dict(entry)
            if str(entry_copy.get("image_asset_id") or "").strip() == normalized_asset_id:
                entry_copy["image_asset_id"] = ""
                cleared_scene_numbers.append(int(entry_copy.get("order_index") or 0))
            updated_scene_timeline.append(entry_copy)

        self.scene_timeline = self._normalize_scene_timeline(updated_scene_timeline)
        for frame in self._collect_scene_entry_frames():
            if str(getattr(frame, "selected_asset_id", "") or "").strip() == normalized_asset_id:
                frame.selected_asset_id = ""
                frame.image_asset_var.set("Unassigned")
        return sorted(number for number in cleared_scene_numbers if number > 0)

    def delete_image(self, image_path, asset_id=None):
        resolved_asset = self._get_image_asset_by_id(asset_id) if asset_id else self._get_image_asset_by_path(image_path)
        scene_numbers = self._get_image_asset_scene_numbers(resolved_asset.get("asset_id")) if resolved_asset else []
        prompt_lines = [f"Are you sure you want to delete {os.path.basename(image_path)}?"]
        if scene_numbers:
            prompt_lines.extend([
                "",
                f"This image is assigned to scenes {', '.join(str(number) for number in scene_numbers)}.",
                "Deleting it will clear those scene assignments."
            ])
        if not messagebox.askyesno("Confirm Delete", "\n".join(prompt_lines)):
            return

        try:
            if os.path.exists(image_path):
                os.remove(image_path)

            normalized_target = os.path.normcase(self._normalize_path(image_path) or image_path)
            resolved_asset_id = str((resolved_asset or {}).get("asset_id") or asset_id or "").strip()
            if resolved_asset_id:
                self._clear_image_asset_references(resolved_asset_id)
            self.image_assets = [
                asset for asset in self.image_assets
                if os.path.normcase(asset.get("project_path", "")) != normalized_target
            ]
            self.image_assets = self._normalize_image_assets(self.image_assets)
            self.save_project_state()
            self.refresh_gallery()
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete image:\n{e}")

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
        self.update_music_status("Video selected. Ready to generate music or import audio.", "blue")

    def toggle_video_selection(self, video_path, var):
        if var.get():
            self.selected_videos.add(video_path)
        else:
            self.selected_videos.discard(video_path)
        self._update_video_selection_summary()

    def select_all_videos(self):
        for var, path in self.video_checkbox_vars:
            video_dir = os.path.dirname(path)
            if video_dir in {self.scenes_dir, self.imported_video_dir}:
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
        def apply_status():
            self.music_status_label.config(text=f"Status: {message}", fg=color)
            self._update_collapsible_section_meta("music_actions", message)

        self.root.after(0, apply_status)

    def _set_tutorial_runtime_progress(self, phase, reset=False, **kwargs):
        if not phase:
            return

        if reset or phase not in self.tutorial_runtime_progress:
            progress_state = {"phase": phase, "started_at": time.time()}
        else:
            progress_state = dict(self.tutorial_runtime_progress.get(phase, {}))

        progress_state.update(kwargs)
        progress_state["phase"] = phase
        progress_state["updated_at"] = time.time()
        self.tutorial_runtime_progress[phase] = progress_state

        stage = kwargs.get("stage")
        current = progress_state.get("current", 0)
        total = progress_state.get("total", 1)

        if stage == "preparing" and reset:
            self.root.after(0, lambda p=phase, t=total, c=current: self._show_eta_panel(p, t, c))
        elif stage in ("submitting", "running", "item_complete", "complete", "failed"):
            self.root.after(0, lambda p=phase, c=current, t=total, s=stage: self._update_eta_display(p, c, t, s))

    def _clear_tutorial_runtime_progress(self, phase=None):
        if phase is None:
            self.tutorial_runtime_progress.clear()
            return
        self.tutorial_runtime_progress.pop(phase, None)

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
        self._set_tutorial_runtime_progress(
            "stitch",
            reset=True,
            status="Preparing stitched render...",
            current=0,
            total=len(filepaths),
            item_label="Selected clips",
            stage="preparing",
        )
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
            self._set_tutorial_runtime_progress(
                "stitch",
                status=f"Stitching {len(filepaths)} selected clip{'s' if len(filepaths) != 1 else ''}...",
                current=len(filepaths),
                total=len(filepaths),
                item_label="Selected clips",
                stage="running",
                output_path=output_file,
            )
            
            stitch_start = time.time()
            subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW, capture_output=True, text=True, check=True)
            self.record_tutorial_phase_timing("stitch", time.time() - stitch_start)
            
            self.update_status(f"Stitching Complete! Saved as {os.path.basename(output_file)}", "green")
            self._set_tutorial_runtime_progress(
                "stitch",
                status=f"Stitching complete: {os.path.basename(output_file)}",
                current=len(filepaths),
                total=len(filepaths),
                item_label="Selected clips",
                stage="complete",
                output_path=output_file,
            )
            
            # Clear selection after successful stitch
            self.selected_videos.clear()
            
            self.root.after(0, self.refresh_gallery)
            
        except FileNotFoundError:
            self.update_status("Error: FFmpeg not found. Please install FFmpeg or imageio-ffmpeg.", "red")
            self._set_tutorial_runtime_progress("stitch", status="FFmpeg not found for stitching.", stage="failed")
        except subprocess.CalledProcessError as e:
            self.update_status(f"FFmpeg Error: {e.stderr}", "red")
            self._set_tutorial_runtime_progress("stitch", status="FFmpeg reported a stitching error.", stage="failed", detail=e.stderr)
        except Exception as e:
            self.update_status(f"Stitching Error: {str(e)}", "red")
            self._set_tutorial_runtime_progress("stitch", status=f"Stitching error: {str(e)}", stage="failed")
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

        if hasattr(self, "run_queue_btn"):
            self.run_queue_btn.config(state=tk.DISABLED)
        if hasattr(self, "add_prompt_btn"):
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

        self._set_tutorial_runtime_progress("video_single", reset=True, status="Generating video clip...", current=0, total=1, item_label="Single clip", stage="preparing")
        prompt_id = self.queue_prompt(workflow_to_submit)
        if prompt_id:
            self.log_debug("SINGLE_PROMPT_QUEUED", prompt_id=prompt_id)
            item_start = time.time()
            self.eta_item_start_time = item_start
            self._set_tutorial_runtime_progress("video_single", status="Rendering video clip...", current=1, total=1, item_label="Single clip", stage="submitting")
            success = self.wait_for_completion(prompt_id)
            if success:
                self.record_tutorial_phase_timing("video_single", time.time() - item_start)
                self.update_status("Single clip generated successfully!", "green")
                self.log_debug("SINGLE_PROMPT_COMPLETE", prompt_id=prompt_id, success=True)
                self._set_tutorial_runtime_progress("video_single", status="Single clip generated.", current=1, total=1, item_label="Single clip", stage="complete")
            else:
                self.update_status("Failed to generate single clip.", "red")
                self.log_debug("SINGLE_PROMPT_COMPLETE", prompt_id=prompt_id, success=False)
                self._set_tutorial_runtime_progress("video_single", status="Single clip failed.", current=1, total=1, item_label="Single clip", stage="failed")
                
        if hasattr(self, "run_queue_btn"):
            self.root.after(0, lambda: self.run_queue_btn.config(state=tk.NORMAL))
        if hasattr(self, "add_prompt_btn"):
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

        if hasattr(self, "run_queue_btn"):
            self.run_queue_btn.config(state=tk.DISABLED)
        if hasattr(self, "add_prompt_btn"):
            self.add_prompt_btn.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self.run_queue, args=(prompts_text, video_settings))
        thread.daemon = True
        thread.start()

    def run_queue(self, prompts_text, video_settings):
        total = len(prompts_text)
        self._set_tutorial_runtime_progress(
            "video_queue",
            reset=True,
            status="Preparing video queue...",
            current=0,
            total=total,
            item_label="Prompt queue",
            stage="preparing",
        )
        
        for i, prompt_text in enumerate(prompts_text, start=1):
            self.update_status(f"Generating {i} of {total}...", "blue")
            self.update_debug_prompt_status(prompt_text, current=i, total=total)
            self.log_debug("QUEUE_ITEM_START", index=i, total=total, prompt_preview=self._truncate_text(prompt_text, 140))
            self._set_tutorial_runtime_progress(
                "video_queue",
                status=f"Submitting video prompt {i} of {total}...",
                current=i,
                total=total,
                item_label=f"Prompt {i}",
                stage="submitting",
            )

            filename_prefix = self._build_video_filename_prefix(video_settings, "queue", i)

            workflow_to_submit = self._build_video_workflow_for_prompt(
                prompt_text,
                filename_prefix,
                video_settings
            )
                
            # Send POST request
            item_start = time.time()
            self.eta_item_start_time = item_start
            prompt_id = self.queue_prompt(workflow_to_submit)
            if not prompt_id:
                self.log_debug("QUEUE_ITEM_ABORTED", index=i, reason="queue_prompt_failed")
                self._set_tutorial_runtime_progress("video_queue", status=f"Video prompt {i} failed to submit.", current=i, total=total, item_label=f"Prompt {i}", stage="failed")
                break
            self.log_debug("QUEUE_ITEM_QUEUED", index=i, prompt_id=prompt_id)
                
            # Polling Loop
            success = self.wait_for_completion(
                prompt_id,
                tutorial_progress_phase="video_queue",
                tutorial_progress_current=i,
                tutorial_progress_total=total,
                tutorial_progress_label=f"Prompt {i}",
            )
            if not success:
                self.log_debug("QUEUE_ITEM_FAILED", index=i, prompt_id=prompt_id)
                break
            self.record_tutorial_phase_timing("video_queue", time.time() - item_start)
            self.log_debug("QUEUE_ITEM_COMPLETE", index=i, prompt_id=prompt_id)
            self._set_tutorial_runtime_progress(
                "video_queue",
                status=f"Completed video prompt {i} of {total}.",
                current=i,
                total=total,
                item_label=f"Prompt {i}",
                stage="item_complete",
            )
                
        else:
            self.update_status("Finished all prompts!", "green")
            self.log_debug("QUEUE_COMPLETE", total=total)
            self._set_tutorial_runtime_progress("video_queue", status="Finished all video prompts.", current=total, total=total, item_label="Prompt queue", stage="complete")
            
        if hasattr(self, "run_queue_btn"):
            self.root.after(0, lambda: self.run_queue_btn.config(state=tk.NORMAL))
        if hasattr(self, "add_prompt_btn"):
            self.root.after(0, lambda: self.add_prompt_btn.config(state=tk.NORMAL))

    def run_image_queue(self, prompts_text, image_settings=None):
        total = len(prompts_text)
        self._set_tutorial_runtime_progress(
            "image_generate",
            reset=True,
            status="Preparing image queue...",
            current=0,
            total=total,
            item_label="Image queue",
            stage="preparing",
        )

        for i, prompt_text in enumerate(prompts_text, start=1):
            self.update_status(f"Generating image {i} of {total}...", "blue")
            self.update_debug_prompt_status(prompt_text, current=i, total=total)
            self.log_debug("IMAGE_QUEUE_ITEM_START", index=i, total=total, prompt_preview=self._truncate_text(prompt_text, 140))
            self._set_tutorial_runtime_progress(
                "image_generate",
                status=f"Submitting image prompt {i} of {total}...",
                current=i,
                total=total,
                item_label=f"Image {i}",
                stage="submitting",
            )

            filename_prefix = self._build_image_filename_prefix("queue", i)
            workflow_to_submit = self._build_image_workflow_for_prompt(prompt_text, filename_prefix, image_settings=image_settings)

            item_start = time.time()
            self.eta_item_start_time = item_start
            prompt_id = self.queue_prompt(workflow_to_submit)
            if not prompt_id:
                self.log_debug("IMAGE_QUEUE_ITEM_ABORTED", index=i, reason="queue_prompt_failed")
                self._set_tutorial_runtime_progress("image_generate", status=f"Image prompt {i} failed to submit.", current=i, total=total, item_label=f"Image {i}", stage="failed")
                break

            success = self.wait_for_completion(
                prompt_id,
                output_kind="image",
                destination_dir=self.generated_image_dir,
                prompt_text=prompt_text,
                tutorial_progress_phase="image_generate",
                tutorial_progress_current=i,
                tutorial_progress_total=total,
                tutorial_progress_label=f"Image {i}",
            )
            if not success:
                self.log_debug("IMAGE_QUEUE_ITEM_FAILED", index=i, prompt_id=prompt_id)
                break

            self.record_tutorial_phase_timing("image_generate", time.time() - item_start)
            self.log_debug("IMAGE_QUEUE_ITEM_COMPLETE", index=i, prompt_id=prompt_id)
            self._set_tutorial_runtime_progress(
                "image_generate",
                status=f"Completed image {i} of {total}.",
                current=i,
                total=total,
                item_label=f"Image {i}",
                stage="item_complete",
            )
        else:
            self.update_status("Finished all image prompts!", "green")
            self.log_debug("IMAGE_QUEUE_COMPLETE", total=total)
            self._set_tutorial_runtime_progress("image_generate", status="Finished all image prompts.", current=total, total=total, item_label="Image queue", stage="complete")

    def run_single_image_prompt_thread(self, prompt_text, image_settings=None):
        self.update_status("Generating single image...", "blue")
        self.update_debug_prompt_status(prompt_text)
        self.log_debug("SINGLE_IMAGE_PROMPT_THREAD_START", prompt_preview=self._truncate_text(prompt_text, 140))

        filename_prefix = self._build_image_filename_prefix("single")
        workflow_to_submit = self._build_image_workflow_for_prompt(prompt_text, filename_prefix, image_settings=image_settings)

        self._set_tutorial_runtime_progress("image_single", reset=True, status="Generating image...", current=0, total=1, item_label="Single image", stage="preparing")
        prompt_id = self.queue_prompt(workflow_to_submit)
        if prompt_id:
            item_start = time.time()
            self.eta_item_start_time = item_start
            self._set_tutorial_runtime_progress("image_single", status="Rendering image...", current=1, total=1, item_label="Single image", stage="submitting")
            success = self.wait_for_completion(
                prompt_id,
                output_kind="image",
                destination_dir=self.generated_image_dir,
                prompt_text=prompt_text
            )
            if success:
                self.record_tutorial_phase_timing("image_single", time.time() - item_start)
                self.update_status("Single image generated successfully!", "green")
                self.log_debug("SINGLE_IMAGE_PROMPT_COMPLETE", prompt_id=prompt_id, success=True)
                self._set_tutorial_runtime_progress("image_single", status="Single image generated.", current=1, total=1, item_label="Single image", stage="complete")
            else:
                self.update_status("Failed to generate single image.", "red")
                self.log_debug("SINGLE_IMAGE_PROMPT_COMPLETE", prompt_id=prompt_id, success=False)
                self._set_tutorial_runtime_progress("image_single", status="Single image failed.", current=1, total=1, item_label="Single image", stage="failed")

        self.root.after(0, lambda: self.run_image_queue_btn.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.add_image_prompt_btn.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.import_image_btn.config(state=tk.NORMAL))
        if hasattr(self, "sync_image_to_scene_btn"):
            self.root.after(0, lambda: self.sync_image_to_scene_btn.config(state=tk.NORMAL))

    def _get_prompt_preview_from_workflow(self, workflow):
        prompt_preview = self._get_workflow_role_value(workflow, "prompt", default="")
        if prompt_preview:
            return prompt_preview
        return self._get_workflow_role_value_from_roles(workflow, IMAGE_WORKFLOW_PROFILE["roles"], "prompt", default="")

    def generate_single_image_prompt(self, text_widget):
        self.save_project_state()
        if not self.image_workflow:
            messagebox.showwarning("Warning", "Please load the image workflow JSON first.")
            return

        prompt_text = text_widget.get("1.0", tk.END).strip()
        if not prompt_text:
            messagebox.showwarning("Warning", "Image prompt is empty.")
            return

        image_settings, validation_error = self._collect_validated_image_settings()
        if validation_error:
            messagebox.showerror("Image Workflow Settings Error", validation_error)
            self.update_status(validation_error, "red")
            return

        self.log_debug("SINGLE_IMAGE_PROMPT_REQUESTED", prompt_preview=self._truncate_text(prompt_text, 140))

        self.run_image_queue_btn.config(state=tk.DISABLED)
        self.add_image_prompt_btn.config(state=tk.DISABLED)
        self.import_image_btn.config(state=tk.DISABLED)
        if hasattr(self, "sync_image_to_scene_btn"):
            self.sync_image_to_scene_btn.config(state=tk.DISABLED)

        thread = threading.Thread(target=self.run_single_image_prompt_thread, args=(prompt_text, image_settings))
        thread.daemon = True
        thread.start()

    def start_image_queue(self):
        self.save_project_state()
        if not self.image_workflow:
            messagebox.showwarning("Warning", "Please load the image workflow JSON first.")
            return

        prompts_text = self._collect_image_prompt_texts()
        if not prompts_text:
            messagebox.showwarning("Warning", "Please add at least one image prompt.")
            return

        image_settings, validation_error = self._collect_validated_image_settings()
        if validation_error:
            messagebox.showerror("Image Workflow Settings Error", validation_error)
            self.update_status(validation_error, "red")
            return

        self.log_debug("IMAGE_QUEUE_START", prompt_count=len(prompts_text), previews=[self._truncate_text(p, 120) for p in prompts_text])

        self.run_image_queue_btn.config(state=tk.DISABLED)
        self.add_image_prompt_btn.config(state=tk.DISABLED)
        self.import_image_btn.config(state=tk.DISABLED)
        if hasattr(self, "sync_image_to_scene_btn"):
            self.sync_image_to_scene_btn.config(state=tk.DISABLED)

        thread = threading.Thread(target=self._run_image_queue_thread, args=(prompts_text, image_settings))
        thread.daemon = True
        thread.start()

    def _run_image_queue_thread(self, prompts_text, image_settings):
        try:
            self.run_image_queue(prompts_text, image_settings=image_settings)
        finally:
            self.root.after(0, lambda: self.run_image_queue_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.add_image_prompt_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.import_image_btn.config(state=tk.NORMAL))
            if hasattr(self, "sync_image_to_scene_btn"):
                self.root.after(0, lambda: self.sync_image_to_scene_btn.config(state=tk.NORMAL))

    def queue_prompt(self, workflow):
        prompt_preview = self._get_prompt_preview_from_workflow(workflow)

        self.log_debug(
            "QUEUE_PROMPT_POST",
            prompt_preview=self._truncate_text(prompt_preview, 160)
        )

        p = {"prompt": workflow, "client_id": self.comfyui_client_id}
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
                    error_body = ""
                    try:
                        error_body = e.read().decode('utf-8', errors='replace')
                        error_detail = json.loads(error_body)
                        node_errors = error_detail.get("node_errors", {})
                        error_msg = error_detail.get("error", {}).get("message", "")
                        if node_errors:
                            first_node_id = next(iter(node_errors), "")
                            first_node = node_errors[first_node_id]
                            node_errors_list = first_node.get("errors", [])
                            if node_errors_list:
                                raw_msg = node_errors_list[0].get("message", error_msg)
                                # Provide a human-readable message for common errors
                                if raw_msg == "Value not in list" and first_node.get("class_type") == "UNETLoader":
                                    bad_value = node_errors_list[0].get("details", "")
                                    error_msg = f"Model file not found in ComfyUI: {bad_value}" if bad_value else "Selected model file not found in ComfyUI. Download it or switch variants."
                                else:
                                    error_msg = raw_msg
                        if error_msg:
                            self.update_status(f"ComfyUI Error: {error_msg}", "red")
                        else:
                            self.update_status("Error: 400 Bad Request (Invalid JSON workflow).", "red")
                    except Exception:
                        self.update_status("Error: 400 Bad Request (Invalid JSON workflow).", "red")
                    self.log_debug("QUEUE_PROMPT_ERROR", reason="http_400", details=str(e), body=error_body[:500])
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

    def _get_output_directory_for_kind(self, output_kind):
        if output_kind == "audio":
            return self.audio_dir
        if output_kind == "image":
            return self.generated_image_dir
        return self.scenes_dir

    def _filename_matches_output_kind(self, filename, output_kind):
        lower_filename = str(filename or "").lower()
        if output_kind == "audio":
            return lower_filename.endswith(SUPPORTED_AUDIO_EXTENSIONS)
        if output_kind == "image":
            return lower_filename.endswith(SUPPORTED_IMAGE_EXTENSIONS)
        return lower_filename.endswith(SUPPORTED_VIDEO_EXTENSIONS)

    def download_comfyui_media(self, filename, subfolder, folder_type, dest_path):
        try:
            url = f"http://127.0.0.1:8188/view?filename={urllib.parse.quote(filename)}&subfolder={urllib.parse.quote(subfolder)}&type={urllib.parse.quote(folder_type)}"
            urllib.request.urlretrieve(url, dest_path)
            return True
        except Exception as e:
            print(f"Error downloading file: {e}")
            return False

    def download_comfyui_video(self, filename, subfolder, folder_type, dest_path):
        return self.download_comfyui_media(filename, subfolder, folder_type, dest_path)

    def _start_ws_progress_listener(self, prompt_id):
        """Start a background WebSocket listener that captures per-step KSampler progress from ComfyUI."""
        if not WS_AVAILABLE:
            return
        self.ws_progress = {"step": 0, "total": 0, "active": False}

        def _ws_listener():
            ws = None
            try:
                ws_url = f"ws://127.0.0.1:8188/ws?clientId={self.comfyui_client_id}"
                ws = _ws_mod.create_connection(ws_url, timeout=10)
                ws.settimeout(2.0)
                self.ws_progress["active"] = True
                while self.ws_progress.get("active", False):
                    try:
                        raw = ws.recv()
                    except _ws_mod.WebSocketTimeoutException:
                        continue
                    except Exception:
                        break
                    if isinstance(raw, bytes):
                        continue
                    try:
                        msg = json.loads(raw)
                    except (json.JSONDecodeError, ValueError):
                        continue
                    msg_type = msg.get("type", "")
                    data = msg.get("data", {})
                    if msg_type == "progress":
                        self.ws_progress["step"] = data.get("value", 0)
                        self.ws_progress["total"] = data.get("max", 0)
                    elif msg_type == "executing" and data.get("node") is None:
                        # Execution finished for this prompt
                        if data.get("prompt_id") == prompt_id:
                            break
                    elif msg_type == "execution_complete":
                        if data.get("prompt_id") == prompt_id:
                            break
            except Exception as e:
                self.log_debug("WS_PROGRESS_LISTENER_ERROR", details=str(e))
            finally:
                self.ws_progress["active"] = False
                if ws is not None:
                    try:
                        ws.close()
                    except Exception:
                        pass

        self.ws_thread = threading.Thread(target=_ws_listener, daemon=True)
        self.ws_thread.start()

    def _stop_ws_progress_listener(self):
        """Signal the WebSocket listener to stop."""
        self.ws_progress["active"] = False
        self.ws_thread = None

    def wait_for_completion(self, prompt_id, is_music=False, output_kind=None, destination_dir=None, prompt_text="", tutorial_progress_phase=None, tutorial_progress_current=None, tutorial_progress_total=None, tutorial_progress_label=""):
        resolved_output_kind = output_kind or ("audio" if is_music else "video")
        resolved_destination_dir = destination_dir or self._get_output_directory_for_kind(resolved_output_kind)
        progress_label = tutorial_progress_label or resolved_output_kind.title()
        progress_current = tutorial_progress_current if tutorial_progress_current is not None else 1
        progress_total = tutorial_progress_total if tutorial_progress_total is not None else 1
        error_count = 0
        self._start_ws_progress_listener(prompt_id)
        try:
            return self._poll_for_completion(prompt_id, is_music, resolved_output_kind, resolved_destination_dir, prompt_text, tutorial_progress_phase, progress_current, progress_total, progress_label)
        finally:
            self._stop_ws_progress_listener()

    def _poll_for_completion(self, prompt_id, is_music, resolved_output_kind, resolved_destination_dir, prompt_text, tutorial_progress_phase, progress_current, progress_total, progress_label):
        error_count = 0
        if tutorial_progress_phase:
            self._set_tutorial_runtime_progress(
                tutorial_progress_phase,
                status=f"Queued {progress_label} in ComfyUI...",
                current=progress_current,
                total=progress_total,
                item_label=progress_label,
                stage="queued",
                prompt_id=prompt_id,
            )
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
                        self.log_debug("PROMPT_HISTORY_FOUND", prompt_id=prompt_id, is_music=is_music, output_kind=resolved_output_kind)
                        if tutorial_progress_phase:
                            self._set_tutorial_runtime_progress(
                                tutorial_progress_phase,
                                status=f"Downloading {progress_label} output...",
                                current=progress_current,
                                total=progress_total,
                                item_label=progress_label,
                                stage="downloading",
                                prompt_id=prompt_id,
                            )
                        # Extract output filename and download
                        try:
                            outputs = history[prompt_id].get('outputs', {})
                            downloaded_output = False
                            for node_id, node_output in outputs.items():
                                media_list = node_output.get('gifs', []) + node_output.get('images', []) + node_output.get('audio', [])
                                for media in media_list:
                                    filename = media.get('filename', '')
                                    if not self._filename_matches_output_kind(filename, resolved_output_kind):
                                        continue

                                    subfolder = media.get('subfolder', '')
                                    folder_type = media.get('type', 'output')
                                    dest_path = os.path.join(resolved_destination_dir, filename)
                                    if self.download_comfyui_media(filename, subfolder, folder_type, dest_path):
                                        downloaded_output = True
                                        if resolved_output_kind == "video":
                                            self.root.after(0, self.refresh_gallery)
                                        elif resolved_output_kind == "audio":
                                            self.current_generated_audio = dest_path
                                            self.current_audio_source = "generated"
                                        elif resolved_output_kind == "image":
                                            self._upsert_image_asset(dest_path, source="generated", prompt_text=prompt_text, status="ready")
                                            self.root.after(0, self.refresh_gallery)
                                            self.root.after(0, self.save_project_state)

                                        self.log_debug("PROMPT_OUTPUT_DOWNLOADED", prompt_id=prompt_id, media_type=resolved_output_kind, filename=filename, dest_path=dest_path)
                                        break
                                if downloaded_output:
                                    break
                        except Exception as e:
                            print(f"Error parsing history for output: {e}")
                            self.log_debug("PROMPT_HISTORY_PARSE_ERROR", prompt_id=prompt_id, details=str(e))
                        if tutorial_progress_phase:
                            self._set_tutorial_runtime_progress(
                                tutorial_progress_phase,
                                status=f"{progress_label} complete.",
                                current=progress_current,
                                total=progress_total,
                                item_label=progress_label,
                                stage="complete",
                                prompt_id=prompt_id,
                            )
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
                    queue_stage = None
                    for q_list in [queue_data.get("queue_running", []), queue_data.get("queue_pending", [])]:
                        for item in q_list:
                            if item[1] == prompt_id:
                                in_queue = True
                                queue_stage = "running" if q_list is queue_data.get("queue_running", []) else "pending"
                                break
                        if in_queue:
                            break

                    if in_queue and tutorial_progress_phase:
                        queue_status = "Running in ComfyUI..." if queue_stage == "running" else "Waiting in ComfyUI queue..."
                        self._set_tutorial_runtime_progress(
                            tutorial_progress_phase,
                            status=f"{progress_label}: {queue_status}",
                            current=progress_current,
                            total=progress_total,
                            item_label=progress_label,
                            stage=queue_stage,
                            prompt_id=prompt_id,
                        )
                            
                    if not in_queue:
                        # Final race-condition check
                        req_history_check = urllib.request.Request(f"http://127.0.0.1:8188/history/{prompt_id}")
                        with urllib.request.urlopen(req_history_check, timeout=5) as response:
                            try:
                                history_check = json.loads(response.read())
                                if prompt_id in history_check:
                                    self.log_debug("PROMPT_HISTORY_FOUND_FINAL_CHECK", prompt_id=prompt_id)
                                    if tutorial_progress_phase:
                                        self._set_tutorial_runtime_progress(
                                            tutorial_progress_phase,
                                            status=f"{progress_label} complete.",
                                            current=progress_current,
                                            total=progress_total,
                                            item_label=progress_label,
                                            stage="complete",
                                            prompt_id=prompt_id,
                                        )
                                    return True
                            except json.JSONDecodeError:
                                pass
                        
                        self.update_status(f"Error: Prompt {prompt_id} failed or was cancelled in ComfyUI", "red")
                        self.update_music_status(f"Error: Prompt {prompt_id} failed or was cancelled in ComfyUI", "red")
                        self.log_debug("PROMPT_FAILED_OR_CANCELLED", prompt_id=prompt_id)
                        if tutorial_progress_phase:
                            self._set_tutorial_runtime_progress(
                                tutorial_progress_phase,
                                status=f"{progress_label} failed or was cancelled in ComfyUI.",
                                current=progress_current,
                                total=progress_total,
                                item_label=progress_label,
                                stage="failed",
                                prompt_id=prompt_id,
                            )
                        return False

            except urllib.error.URLError as e:
                error_count += 1
                if error_count >= 10:
                    self.update_status("Fatal Error: Server unresponsive. Aborting.", "red")
                    self.update_music_status("Fatal Error: Server unresponsive. Aborting.", "red")
                    if tutorial_progress_phase:
                        self._set_tutorial_runtime_progress(tutorial_progress_phase, status=f"{progress_label} aborted: ComfyUI became unresponsive.", current=progress_current, total=progress_total, item_label=progress_label, stage="failed", prompt_id=prompt_id)
                    return False
                # Don't abort on timeouts or temporary connection refusals under heavy GPU load
                error_reason = getattr(e, 'reason', str(e))
                self.update_status(f"Server busy or timeout ({error_reason}). Waiting...", "orange")
                self.update_music_status(f"Server busy or timeout ({error_reason}). Waiting...", "orange")
                self.log_debug("PROMPT_POLL_RETRY", prompt_id=prompt_id, error=str(error_reason), error_count=error_count)
                if tutorial_progress_phase:
                    self._set_tutorial_runtime_progress(tutorial_progress_phase, status=f"{progress_label}: waiting for ComfyUI ({error_reason}).", current=progress_current, total=progress_total, item_label=progress_label, stage="retrying", prompt_id=prompt_id)
                pass # Let it fall through to time.sleep(3) and try again
            except Exception as e:
                error_count += 1
                if error_count >= 10:
                    self.update_status("Fatal Error: Server unresponsive. Aborting.", "red")
                    self.update_music_status("Fatal Error: Server unresponsive. Aborting.", "red")
                    if tutorial_progress_phase:
                        self._set_tutorial_runtime_progress(tutorial_progress_phase, status=f"{progress_label} aborted after repeated polling errors.", current=progress_current, total=progress_total, item_label=progress_label, stage="failed", prompt_id=prompt_id)
                    return False
                self.update_status(f"Polling error: {str(e)}. Retrying...", "orange")
                self.update_music_status(f"Polling error: {str(e)}. Retrying...", "orange")
                self.log_debug("PROMPT_POLL_EXCEPTION", prompt_id=prompt_id, error=str(e), error_count=error_count)
                if tutorial_progress_phase:
                    self._set_tutorial_runtime_progress(tutorial_progress_phase, status=f"{progress_label}: polling retry after error.", current=progress_current, total=progress_total, item_label=progress_label, stage="retrying", prompt_id=prompt_id, detail=str(e))
                pass # Let it fall through to time.sleep(3) and try again
                
            time.sleep(3)

    def generate_music(self):
        self.save_project_state()
        if not self.music_workflow:
            messagebox.showwarning("Warning", "Music workflow JSON not loaded.")
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
        # Determine variant-specific timing key for accurate ETA
        variant_info = MUSIC_MODEL_VARIANT_MAP.get(self.music_model_variant_var.get(), MUSIC_MODEL_VARIANT_MAP[MUSIC_MODEL_VARIANT_DEFAULT])
        variant_suffix = variant_info.get("filename", "").replace("acestep_v1.5_", "").replace("_bf16", "").replace(".safetensors", "")
        if not variant_suffix:
            variant_suffix = "turbo"
        timing_key = f"music_generate_{variant_suffix}"
        # Reset WS progress state
        self.ws_progress = {"step": 0, "total": 0, "active": False}
        self.eta_variant_timing_key = timing_key

        # Route XL variants to ACE-Step REST API instead of ComfyUI
        if self._is_xl_music_variant():
            self._run_music_generation_xl(tags, lyrics, variant_info, timing_key)
            return

        # Pre-flight: verify the selected model file exists in ComfyUI
        model_filename = variant_info["filename"]
        try:
            req = urllib.request.Request(f"http://127.0.0.1:8188/object_info/UNETLoader")
            with urllib.request.urlopen(req, timeout=5) as resp:
                info = json.loads(resp.read().decode())
            available_models = info.get("UNETLoader", {}).get("input", {}).get("required", {}).get("unet_name", [[]])[0]
            if model_filename not in available_models:
                display_name = self.music_model_variant_var.get()
                self.update_music_status(
                    f"Model '{model_filename}' not found in ComfyUI. "
                    f"Download it via 'Install Missing Models' or switch to a different variant.",
                    "red",
                )
                self.log_debug("MUSIC_MODEL_MISSING", model=model_filename, variant=display_name, available=str(available_models))
                self.root.after(0, lambda: self.gen_music_btn.config(state=tk.NORMAL))
                return
        except Exception:
            pass  # If the check fails, proceed anyway and let ComfyUI report the error

        self._set_tutorial_runtime_progress(
            "music_generate",
            reset=True,
            status="Preparing music workflow...",
            current=0,
            total=1,
            item_label="Soundtrack",
            stage="preparing",
        )
        self.update_music_status("Generating Music...", "blue")
        
        try:
            self._normalize_music_workflow(self.music_workflow)
            music_seed = self._build_music_seed()
            # Set the selected XL model variant on the UNETLoader node
            variant_info = MUSIC_MODEL_VARIANT_MAP.get(self.music_model_variant_var.get(), MUSIC_MODEL_VARIANT_MAP[MUSIC_MODEL_VARIANT_DEFAULT])
            self.music_workflow["104"]["inputs"]["unet_name"] = variant_info["filename"]
            # Update workflow
            self.music_workflow["94"]["inputs"]["tags"] = tags
            self.music_workflow["94"]["inputs"]["lyrics"] = lyrics
            self.music_workflow["94"]["inputs"]["duration"] = self.music_duration_var.get()
            self.music_workflow["94"]["inputs"]["bpm"] = self.music_bpm_var.get()
            self.music_workflow["94"]["inputs"]["keyscale"] = self.music_key_var.get()
            self.music_workflow["94"]["inputs"]["timesignature"] = self.music_timesignature_var.get()
            self.music_workflow["94"]["inputs"]["language"] = self.music_language_var.get()
            self.music_workflow["94"]["inputs"]["generate_audio_codes"] = bool(self.music_generate_audio_codes_var.get())
            self.music_workflow["94"]["inputs"]["cfg_scale"] = self.music_cfg_scale_var.get()
            self.music_workflow["94"]["inputs"]["temperature"] = self.music_temperature_var.get()
            self.music_workflow["94"]["inputs"]["top_p"] = self.music_top_p_var.get()
            self.music_workflow["94"]["inputs"]["top_k"] = self.music_top_k_var.get()
            self.music_workflow["94"]["inputs"]["min_p"] = self.music_min_p_var.get()
            self.music_workflow["94"]["inputs"]["seed"] = music_seed
            self.music_workflow["3"]["inputs"]["seed"] = music_seed
            self.music_workflow["3"]["inputs"]["steps"] = self.music_steps_var.get()
            self.music_workflow["3"]["inputs"]["cfg"] = self.music_cfg_var.get()
            self.music_workflow["3"]["inputs"]["sampler_name"] = self.music_sampler_var.get()
            self.music_workflow["3"]["inputs"]["scheduler"] = self.music_scheduler_var.get()
            self.music_workflow["3"]["inputs"]["denoise"] = self.music_denoise_var.get()
            self.music_workflow["98"]["inputs"]["seconds"] = self.music_duration_var.get()
            self.music_workflow["107"]["inputs"]["filename_prefix"] = f"ACE_Music_{int(time.time())}"
            self.music_workflow["107"]["inputs"]["quality"] = self.music_quality_var.get()
            self._set_tutorial_runtime_progress("music_generate", status="Submitting soundtrack workflow to ComfyUI...", current=1, total=1, item_label="Soundtrack", stage="submitting")
        except KeyError as e:
            self.update_music_status(f"Error: Missing node in JSON ({e})", "red")
            self._set_tutorial_runtime_progress("music_generate", status=f"Music workflow is missing node {e}.", current=1, total=1, item_label="Soundtrack", stage="failed")
            self.root.after(0, lambda: self.gen_music_btn.config(state=tk.NORMAL))
            return
            
        prompt_id = self.queue_prompt(self.music_workflow)
        if not prompt_id:
            self.update_music_status("Failed to submit workflow to ComfyUI.", "red")
            self._set_tutorial_runtime_progress("music_generate", status="Failed to submit soundtrack workflow.", current=1, total=1, item_label="Soundtrack", stage="failed")
            self.root.after(0, lambda: self.gen_music_btn.config(state=tk.NORMAL))
            return

        item_start = time.time()
        self.eta_item_start_time = item_start
        success = self.wait_for_completion(
            prompt_id,
            is_music=True,
            tutorial_progress_phase="music_generate",
            tutorial_progress_current=1,
            tutorial_progress_total=1,
            tutorial_progress_label="Soundtrack",
        )
        
        if success and self.current_generated_audio:
            elapsed = time.time() - item_start
            self.record_tutorial_phase_timing(timing_key, elapsed)
            # Also record under the generic key for fallback ETA
            self.record_tutorial_phase_timing("music_generate", elapsed)
            self.update_music_status("Music Generation Complete! Ready to preview or merge.", "green")
            self._set_tutorial_runtime_progress("music_generate", status="Soundtrack generation complete.", current=1, total=1, item_label="Soundtrack", stage="complete", output_path=self.current_generated_audio)
            self.root.after(0, lambda: self.preview_music_btn.config(state=tk.NORMAL))
            if self.selected_video_for_music:
                self.root.after(0, lambda: self.merge_music_btn.config(state=tk.NORMAL))
            self.root.after(0, self._refresh_music_sidebar_state)
        else:
            self.update_music_status("Music Generation Failed.", "red")
            self._set_tutorial_runtime_progress("music_generate", status="Soundtrack generation failed.", current=1, total=1, item_label="Soundtrack", stage="failed")
            self.root.after(0, self._refresh_music_sidebar_state)
            
        self.root.after(0, lambda: self.gen_music_btn.config(state=tk.NORMAL))

    def _run_music_generation_xl(self, tags, lyrics, variant_info, timing_key):
        self._set_tutorial_runtime_progress(
            "music_generate",
            reset=True,
            status="Checking ACE-Step API server...",
            current=0,
            total=1,
            item_label="Soundtrack (XL)",
            stage="preparing",
        )

        # Check API health; try to launch if not running
        if not self._check_acestep_api_health():
            self.update_music_status("ACE-Step API not running. Attempting to launch...", "orange")
            launched = self._launch_acestep_api_server()
            if launched:
                self.update_music_status("Waiting for ACE-Step API server to start...", "blue")
                if not self._wait_for_acestep_api(timeout=180):
                    self.update_music_status(
                        "ACE-Step API server did not become ready. "
                        "Start it manually with start_api_server.bat in ACE-Step-1.5, or switch to the Turbo variant.",
                        "red",
                    )
                    self._set_tutorial_runtime_progress("music_generate", status="ACE-Step API server not available.", current=1, total=1, item_label="Soundtrack (XL)", stage="failed")
                    self.root.after(0, lambda: self.gen_music_btn.config(state=tk.NORMAL))
                    return
            else:
                self.update_music_status(
                    "ACE-Step API server not found. Install ACE-Step-1.5 next to your ComfyUI folder, "
                    "or start the API server manually, then retry.",
                    "red",
                )
                self._set_tutorial_runtime_progress("music_generate", status="ACE-Step API not available.", current=1, total=1, item_label="Soundtrack (XL)", stage="failed")
                self.root.after(0, lambda: self.gen_music_btn.config(state=tk.NORMAL))
                return

        self.update_music_status("Generating Music (XL model via ACE-Step API)...", "blue")
        self._set_tutorial_runtime_progress("music_generate", status="Submitting XL generation to ACE-Step API...", current=1, total=1, item_label="Soundtrack (XL)", stage="submitting")

        # Show the ETA panel for XL generation
        self.root.after(0, lambda: self._show_eta_panel("music_generate_xl", total=1, current=0))

        item_start = time.time()
        self.eta_item_start_time = item_start

        audio_path = self._generate_music_xl(tags, lyrics, variant_info)

        if audio_path and os.path.exists(audio_path):
            self.current_generated_audio = audio_path
            self.current_audio_source = "generated"
            elapsed = time.time() - item_start
            self.record_tutorial_phase_timing(timing_key, elapsed)
            self.record_tutorial_phase_timing("music_generate", elapsed)
            self.update_music_status("XL Music Generation Complete! Ready to preview or merge.", "green")
            self._set_tutorial_runtime_progress("music_generate", status="Soundtrack generation complete (XL).", current=1, total=1, item_label="Soundtrack (XL)", stage="complete", output_path=audio_path)
            self.root.after(0, lambda: self._update_eta_display("music_generate_xl", 1, 1, stage="complete"))
            self.root.after(0, lambda: self.preview_music_btn.config(state=tk.NORMAL))
            if self.selected_video_for_music:
                self.root.after(0, lambda: self.merge_music_btn.config(state=tk.NORMAL))
            self.root.after(0, self._refresh_music_sidebar_state)
        else:
            self.update_music_status("XL Music Generation Failed. Check the ACE-Step API server console for details.", "red")
            self._set_tutorial_runtime_progress("music_generate", status="Soundtrack generation failed (XL).", current=1, total=1, item_label="Soundtrack (XL)", stage="failed")
            self.root.after(0, lambda: self._update_eta_display("music_generate_xl", 0, 1, stage="failed"))
            self.root.after(0, self._refresh_music_sidebar_state)

        # Clean up XL phase state
        self.xl_gen_phase = None
        self.xl_gen_phase_start = None
        self.xl_gen_progress = 0.0
        self.xl_gen_stage_text = ""
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
        self._set_tutorial_runtime_progress(
            "merge",
            reset=True,
            status="Preparing final audio and video merge...",
            current=0,
            total=1,
            item_label="Final video",
            stage="preparing",
        )
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
            self._set_tutorial_runtime_progress("merge", status="Running FFmpeg final merge...", current=1, total=1, item_label="Final video", stage="running", output_path=output_file)
            
            merge_start = time.time()
            subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW, capture_output=True, text=True, check=True)
            self.record_tutorial_phase_timing("merge", time.time() - merge_start)
            
            self.current_final_video = output_file
            self.update_music_status(f"Merge Complete! Saved as {os.path.basename(output_file)}", "green")
            self._set_tutorial_runtime_progress("merge", status=f"Final merge complete: {os.path.basename(output_file)}", current=1, total=1, item_label="Final video", stage="complete", output_path=output_file)
            self.root.after(0, self.refresh_gallery)
            self.root.after(0, lambda: self.preview_final_btn.config(state=tk.NORMAL))
            self.root.after(0, self._refresh_music_sidebar_state)
            
        except FileNotFoundError:
            self.update_music_status("Error: FFmpeg not found.", "red")
            self._set_tutorial_runtime_progress("merge", status="FFmpeg not found for final merge.", current=1, total=1, item_label="Final video", stage="failed")
        except subprocess.CalledProcessError as e:
            self.update_music_status(f"FFmpeg Error: {e.stderr}", "red")
            self._set_tutorial_runtime_progress("merge", status="FFmpeg reported a final merge error.", current=1, total=1, item_label="Final video", stage="failed", detail=e.stderr)
        except Exception as e:
            self.update_music_status(f"Merge Error: {str(e)}", "red")
            self._set_tutorial_runtime_progress("merge", status=f"Final merge error: {str(e)}", current=1, total=1, item_label="Final video", stage="failed")
        finally:
            self.root.after(0, lambda: self.merge_music_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.gen_music_btn.config(state=tk.NORMAL))
            self.root.after(0, self._refresh_music_sidebar_state)

    # ── Autonomous Music Video Pipeline ──────────────────────────────────

    def _calculate_autonomous_scene_count(self, target_duration_seconds):
        try:
            frames = int(self.video_length_var.get())
        except (ValueError, tk.TclError):
            frames = 121
        try:
            fps = int(self.video_fps_var.get())
        except (ValueError, tk.TclError):
            fps = 24
        if fps <= 0:
            fps = 24
        if frames <= 0:
            frames = 121
        seconds_per_scene = frames / fps
        scene_count = max(1, math.ceil(target_duration_seconds / seconds_per_scene))
        actual_duration = round(scene_count * seconds_per_scene, 2)
        return scene_count, actual_duration, seconds_per_scene

    def _update_autonomous_scene_estimate(self, *_args):
        try:
            dur = int(self.autonomous_duration_var.get())
        except (ValueError, tk.TclError):
            dur = 0
        if dur <= 0:
            if hasattr(self, "autonomous_estimate_label"):
                self.autonomous_estimate_label.config(text="Enter a duration above 0.")
            return
        scene_count, actual_dur, sps = self._calculate_autonomous_scene_count(dur)
        if hasattr(self, "autonomous_estimate_label"):
            self.autonomous_estimate_label.config(text=f"{scene_count} scenes × ~{sps:.1f}s = ~{actual_dur:.0f}s total video")

    def _autonomous_preflight(self):
        errors = []
        try:
            req = urllib.request.Request("http://127.0.0.1:8188/queue")
            with urllib.request.urlopen(req, timeout=5) as resp:
                resp.read()
        except Exception:
            errors.append("ComfyUI is not reachable at http://127.0.0.1:8188. Start it first.")
        if not self.current_project_dir:
            errors.append("No project is open. Create or open a project first.")
        if not self.workflow:
            errors.append("No video workflow loaded. Load a workflow first.")
        if not self.image_workflow:
            errors.append("No image workflow loaded. Load a Z-Image workflow for image generation.")
        if not self.music_workflow:
            errors.append("No music workflow loaded.")
        return errors

    def _start_autonomous_pipeline(self):
        if not self.comfyui_ready:
            self._flash_autonomous_status()
            return
        brief = self.autonomous_brief_text.get("1.0", tk.END).strip() if hasattr(self, "autonomous_brief_text") else ""
        if not brief:
            messagebox.showwarning("Autonomous Mode", "Enter a creative brief in the Autonomous Mode panel.\n\nDescribe the music video concept, mood, style, or any visual ideas.")
            return
        try:
            target_dur = int(self.autonomous_duration_var.get())
        except (ValueError, tk.TclError):
            target_dur = 0
        if target_dur <= 0:
            messagebox.showwarning("Autonomous Mode", "Set a target duration greater than 0 seconds.")
            return

        preflight_errors = self._autonomous_preflight()
        if preflight_errors:
            messagebox.showerror("Autonomous Mode – Pre-flight Failed", "\n\n".join(preflight_errors))
            return

        if not self.ensure_chatbot_model_ready(interactive=True):
            return

        self.autonomous_active = True
        self.autonomous_cancel_requested = False
        self.autonomous_state = AUTONOMOUS_STATE_IDLE
        self.autonomous_target_duration = target_dur
        self.autonomous_creative_brief = brief
        self.autonomous_completed_phases = set()
        self.autonomous_rendered_scene_paths = []
        self.autonomous_expanded_concept = ""
        self.autonomous_image_prompts = []
        self.autonomous_video_prompts = []
        self.autonomous_i2v_prompts = []
        self.autonomous_image_asset_map = {}
        self.autonomous_scene_outline = []
        scene_count, actual_dur, _ = self._calculate_autonomous_scene_count(target_dur)
        self.autonomous_scene_count = scene_count
        self.autonomous_actual_duration = actual_dur

        self._set_autonomous_ui_running(True)
        self._update_autonomous_progress(AUTONOMOUS_STATE_EXPANDING_CONCEPT, "Starting autonomous pipeline...", 0.0)

        thread = threading.Thread(target=self._run_autonomous_pipeline, daemon=True)
        thread.start()

    def _cancel_autonomous_pipeline(self):
        self.autonomous_cancel_requested = True
        self.update_status("Autonomous pipeline cancellation requested...", "orange")

    def _set_autonomous_ui_running(self, is_running):
        def apply():
            state = tk.DISABLED if is_running else tk.NORMAL
            if hasattr(self, "autonomous_start_btn"):
                self.autonomous_start_btn.config(state=state)
            if hasattr(self, "autonomous_cancel_btn"):
                self.autonomous_cancel_btn.config(state=tk.NORMAL if is_running else tk.DISABLED)
            if hasattr(self, "autonomous_duration_entry"):
                self.autonomous_duration_entry.config(state="readonly" if is_running else tk.NORMAL)
            if hasattr(self, "autonomous_brief_text"):
                self.autonomous_brief_text.config(state=tk.DISABLED if is_running else tk.NORMAL)
            if hasattr(self, "chatbot_send_btn"):
                self.chatbot_send_btn.config(state=state)
            if hasattr(self, "chatbot_scene_plan_btn"):
                self.chatbot_scene_plan_btn.config(state=state)
            if hasattr(self, "chatbot_generate_btn"):
                self.chatbot_generate_btn.config(state=state)
            if hasattr(self, "chatbot_finalize_song_btn"):
                self.chatbot_finalize_song_btn.config(state=state)
        self.root.after(0, apply)

    def _update_autonomous_progress(self, current_phase, message, phase_progress=0.0):
        def apply():
            if hasattr(self, "autonomous_status_label"):
                self.autonomous_status_label.config(text=message)
            if hasattr(self, "autonomous_phase_labels"):
                for phase_key, label_widget in self.autonomous_phase_labels.items():
                    if phase_key in self.autonomous_completed_phases:
                        label_widget.config(text=f"  ✓  {AUTONOMOUS_PHASE_LABELS[phase_key]}", fg=self.colors["success"])
                    elif phase_key == current_phase:
                        label_widget.config(text=f"  ⟳  {AUTONOMOUS_PHASE_LABELS[phase_key]}", fg=self.colors["accent"])
                    else:
                        label_widget.config(text=f"  ○  {AUTONOMOUS_PHASE_LABELS[phase_key]}", fg=self.colors["text_muted"])
            overall = 0.0
            for p in AUTONOMOUS_PHASE_ORDER:
                w = AUTONOMOUS_PHASE_WEIGHTS.get(p, 0)
                if p in self.autonomous_completed_phases:
                    overall += w
                elif p == current_phase:
                    overall += w * max(0.0, min(1.0, phase_progress))
            if hasattr(self, "autonomous_progress_var"):
                self.autonomous_progress_var.set(int(overall * 100))
        self.root.after(0, apply)

    def _run_autonomous_pipeline(self):
        brief = self.autonomous_creative_brief
        scene_count = self.autonomous_scene_count
        actual_duration = self.autonomous_actual_duration

        try:
            # ═══════════════════════════════════════════════════════════════
            # LLM BLOCK — All chatbot work runs while the model is warm.
            # The model stays loaded with keep_alive="30m" between calls,
            # then is explicitly unloaded before GPU-heavy ComfyUI phases.
            # ═══════════════════════════════════════════════════════════════

            # ── Phase 1: Expand Concept ──
            self.autonomous_state = AUTONOMOUS_STATE_EXPANDING_CONCEPT
            self._update_autonomous_progress(AUTONOMOUS_STATE_EXPANDING_CONCEPT, "Expanding creative concept...", 0.1)

            if self.autonomous_cancel_requested:
                raise InterruptedError("Cancelled by user.")
            concept_result = self._autonomous_expand_concept(brief)
            if self.autonomous_cancel_requested:
                raise InterruptedError("Cancelled by user.")
            self.autonomous_completed_phases.add(AUTONOMOUS_STATE_EXPANDING_CONCEPT)

            # ── Phase 2: Plan Scene Outline ──
            self.autonomous_state = AUTONOMOUS_STATE_PLANNING_SCENES
            self._update_autonomous_progress(AUTONOMOUS_STATE_PLANNING_SCENES, f"Outlining {scene_count} scenes...", 0.1)

            outline_result = self._autonomous_plan_scene_outline(brief, scene_count)
            if self.autonomous_cancel_requested:
                raise InterruptedError("Cancelled by user.")
            if not outline_result:
                raise RuntimeError("Scene outline failed — no scenes were generated.")
            self.autonomous_completed_phases.add(AUTONOMOUS_STATE_PLANNING_SCENES)

            # ── Phase 3: Plan Song ──
            self.autonomous_state = AUTONOMOUS_STATE_PLANNING_SONG
            self._update_autonomous_progress(AUTONOMOUS_STATE_PLANNING_SONG, "Writing song lyrics and style tags...", 0.1)

            if self.autonomous_cancel_requested:
                raise InterruptedError("Cancelled by user.")
            song_result = self._autonomous_plan_song(brief, actual_duration, outline_result)
            if self.autonomous_cancel_requested:
                raise InterruptedError("Cancelled by user.")
            if not song_result:
                raise RuntimeError("Song planning failed — no lyrics or style tags were generated.")

            song_apply_done = threading.Event()
            self.root.after(0, lambda: (self._autonomous_apply_song(song_result, actual_duration), song_apply_done.set()))
            song_apply_done.wait()
            self.autonomous_completed_phases.add(AUTONOMOUS_STATE_PLANNING_SONG)

            # ── Phase 3b: Batch-generate ALL image + video prompts ──
            self._update_autonomous_progress(AUTONOMOUS_STATE_PLANNING_SCENES, "Generating all scene prompts...", 0.0)

            if self.autonomous_cancel_requested:
                raise InterruptedError("Cancelled by user.")
            self._autonomous_generate_all_prompts()
            if self.autonomous_cancel_requested:
                raise InterruptedError("Cancelled by user.")

            # ── Unload LLM to free VRAM for ComfyUI ──
            self._unload_chatbot_model()

            # ═══════════════════════════════════════════════════════════════
            # IMAGE BLOCK — ComfyUI renders all images with models staying
            # loaded across the entire batch.
            # ═══════════════════════════════════════════════════════════════

            # ── Phase 4: Generate Images (pure ComfyUI, no LLM) ──
            self.autonomous_state = AUTONOMOUS_STATE_GENERATING_IMAGES
            self._update_autonomous_progress(AUTONOMOUS_STATE_GENERATING_IMAGES, "Rendering scene images...", 0.0)

            if self.autonomous_cancel_requested:
                raise InterruptedError("Cancelled by user.")
            images_ok = self._autonomous_generate_images()
            if self.autonomous_cancel_requested:
                raise InterruptedError("Cancelled by user.")
            if not images_ok:
                raise RuntimeError("Image generation failed — no images were produced.")
            self.autonomous_completed_phases.add(AUTONOMOUS_STATE_GENERATING_IMAGES)

            # ── Free image models so video models can load cleanly ──
            self._free_comfyui_vram()

            # ═══════════════════════════════════════════════════════════════
            # VIDEO BLOCK — Build timeline from images, then render all
            # video scenes with LTX models staying loaded for the batch.
            # ═══════════════════════════════════════════════════════════════

            # ── Phase 5: Build I2V Timeline ──
            self.autonomous_state = AUTONOMOUS_STATE_BUILDING_TIMELINE
            self._update_autonomous_progress(AUTONOMOUS_STATE_BUILDING_TIMELINE, "Building I2V scene timeline...", 0.5)

            if self.autonomous_cancel_requested:
                raise InterruptedError("Cancelled by user.")
            self._autonomous_build_i2v_timeline()
            rebuild_done = threading.Event()
            self.root.after(0, lambda: (self._autonomous_rebuild_timeline_ui(), rebuild_done.set()))
            rebuild_done.wait()
            self.autonomous_completed_phases.add(AUTONOMOUS_STATE_BUILDING_TIMELINE)

            # ── Phase 6: Render All Scenes (pure ComfyUI, no LLM) ──
            self.autonomous_state = AUTONOMOUS_STATE_RENDERING
            self._update_autonomous_progress(AUTONOMOUS_STATE_RENDERING, "Rendering video scenes...", 0.0)

            if self.autonomous_cancel_requested:
                raise InterruptedError("Cancelled by user.")
            render_ok = self._autonomous_render_scenes()
            if self.autonomous_cancel_requested:
                raise InterruptedError("Cancelled by user.")
            if not render_ok:
                raise RuntimeError("Scene rendering failed or produced no output files.")
            self.autonomous_completed_phases.add(AUTONOMOUS_STATE_RENDERING)

            # ── Phase 7: Stitch ──
            self.autonomous_state = AUTONOMOUS_STATE_STITCHING
            self._update_autonomous_progress(AUTONOMOUS_STATE_STITCHING, "Stitching rendered clips...", 0.1)

            if self.autonomous_cancel_requested:
                raise InterruptedError("Cancelled by user.")
            stitch_ok = self._autonomous_stitch_scenes()
            if not stitch_ok:
                raise RuntimeError("Stitching failed — no stitched video was produced.")
            self.autonomous_completed_phases.add(AUTONOMOUS_STATE_STITCHING)

            # ── Free video models before music generation ──
            self._free_comfyui_vram()

            # ═══════════════════════════════════════════════════════════════
            # MUSIC BLOCK — ACE-Step loads its own model.
            # ═══════════════════════════════════════════════════════════════

            # ── Phase 8: Generate Music ──
            self.autonomous_state = AUTONOMOUS_STATE_GENERATING_MUSIC
            self._update_autonomous_progress(AUTONOMOUS_STATE_GENERATING_MUSIC, "Generating soundtrack...", 0.1)

            if self.autonomous_cancel_requested:
                raise InterruptedError("Cancelled by user.")
            music_ok = self._autonomous_generate_music()
            if self.autonomous_cancel_requested:
                raise InterruptedError("Cancelled by user.")
            if not music_ok:
                raise RuntimeError("Music generation failed — no audio was produced.")
            self.autonomous_completed_phases.add(AUTONOMOUS_STATE_GENERATING_MUSIC)

            # ── Phase 9: Final Merge ──
            self.autonomous_state = AUTONOMOUS_STATE_MERGING
            self._update_autonomous_progress(AUTONOMOUS_STATE_MERGING, "Merging video and audio...", 0.1)

            if self.autonomous_cancel_requested:
                raise InterruptedError("Cancelled by user.")
            self._autonomous_final_merge()
            self.autonomous_completed_phases.add(AUTONOMOUS_STATE_MERGING)

            # ── Complete ──
            self.autonomous_state = AUTONOMOUS_STATE_COMPLETE
            self._update_autonomous_progress(AUTONOMOUS_STATE_MERGING, "Autonomous music video complete!", 1.0)
            self.root.after(0, lambda: self.update_status("Autonomous music video pipeline complete!", "green"))
            self.root.after(0, self.refresh_gallery)
            self.root.after(0, self.save_project_state)
            if hasattr(self, "notebook") and hasattr(self, "gallery_tab"):
                self.root.after(0, lambda: self.notebook.select(self.gallery_tab))

        except InterruptedError:
            self.autonomous_state = AUTONOMOUS_STATE_FAILED
            self._update_autonomous_progress(self.autonomous_state, "Pipeline cancelled by user.", 0.0)
            self.root.after(0, lambda: self.update_status("Autonomous pipeline cancelled.", "orange"))
        except Exception as exc:
            self.autonomous_state = AUTONOMOUS_STATE_FAILED
            error_msg = str(exc)
            self._update_autonomous_progress(self.autonomous_state, f"Pipeline failed: {error_msg[:120]}", 0.0)
            self.root.after(0, lambda: self.update_status(f"Autonomous pipeline failed: {error_msg[:120]}", "red"))
            self.root.after(0, lambda: messagebox.showerror("Autonomous Mode", f"Pipeline failed:\n\n{error_msg}"))
        finally:
            self.autonomous_active = False
            self._set_autonomous_ui_running(False)
            self.root.after(0, self.save_project_state)

    # ── Autonomous sub-phase implementations ──

    def _unload_chatbot_model(self):
        """Explicitly unload the LLM from VRAM to free memory for ComfyUI."""
        try:
            if self.chatbot_backend_mode == CHATBOT_BACKEND_MODE_OLLAMA:
                model_id = None
                try:
                    model_id = self._resolve_chatbot_generation_model_id(timeout_seconds=5)
                except Exception:
                    pass
                if model_id:
                    self._chatbot_http_json(
                        f"{self._chatbot_base_url()}/api/generate",
                        method="POST",
                        payload={"model": model_id, "keep_alive": 0},
                        timeout_seconds=10,
                    )
                    self.log_debug("CHATBOT_MODEL_UNLOADED", model_id=model_id, backend="ollama")
            self.chatbot_model_warm = False
        except Exception as exc:
            self.log_debug("CHATBOT_MODEL_UNLOAD_FAILED", error=str(exc))

    def _free_comfyui_vram(self):
        """Ask ComfyUI to unload cached models and free GPU memory."""
        try:
            req_body = json.dumps({"unload_models": True, "free_memory": True}).encode("utf-8")
            req = urllib.request.Request(
                "http://127.0.0.1:8188/free",
                data=req_body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp.read()
            self.log_debug("COMFYUI_VRAM_FREED")
        except Exception as exc:
            self.log_debug("COMFYUI_VRAM_FREE_FAILED", error=str(exc))

    def _autonomous_expand_concept(self, brief):
        backend_result = self._ensure_chatbot_backend_ready_for_use(action_label="autonomous concept expansion")
        if not backend_result.get("ok"):
            raise RuntimeError(f"Chatbot backend not ready: {backend_result.get('detail') or backend_result.get('status')}")
        self.chatbot_model_warm = True

        result = self._request_chatbot_structured_output(CHATBOT_TASK_CONCEPT_EXPAND, brief, keep_alive="30m")
        expanded_brief = str(result.get("expanded_brief") or "").strip()
        if not expanded_brief:
            raise RuntimeError("Concept expansion failed — no expanded brief was generated.")

        self.autonomous_expanded_concept = expanded_brief

        conversation_id = self._ensure_active_chatbot_conversation()
        self._append_chatbot_turn("user", f"[Autonomous] Expand concept: {brief[:200]}", kind="chat", conversation_id=conversation_id)
        display_text = result.get("raw_content") or json.dumps(result, indent=2)
        self._append_chatbot_turn("assistant", display_text, kind="artifact", conversation_id=conversation_id)
        self.chatbot_last_result = result
        self._record_chatbot_history_entry(CHATBOT_TASK_CONCEPT_EXPAND, brief, result)
        return result

    def _autonomous_plan_scenes(self, brief, scene_count):
        """Legacy wrapper — delegates to outline-based planning."""
        return self._autonomous_plan_scene_outline(brief, scene_count)

    def _autonomous_plan_scene_outline(self, brief, scene_count):
        backend_result = self._ensure_chatbot_backend_ready_for_use(action_label="autonomous scene outline")
        if not backend_result.get("ok"):
            raise RuntimeError(f"Chatbot backend not ready: {backend_result.get('detail') or backend_result.get('status')}")
        self.chatbot_model_warm = True

        concept = self.autonomous_expanded_concept or brief
        augmented_brief = (
            f"Create exactly {scene_count} scenes for a music video.\n"
            f"The video will be approximately {self.autonomous_actual_duration:.0f} seconds long "
            f"({scene_count} clips of ~{self.autonomous_actual_duration / max(scene_count, 1):.1f}s each).\n\n"
            f"Creative concept:\n{concept}"
        )
        result = self._request_chatbot_structured_output(CHATBOT_TASK_SCENE_OUTLINE, augmented_brief, keep_alive="30m")
        scenes = result.get("scenes") if isinstance(result.get("scenes"), list) else []
        if not scenes:
            return None

        # Cap to requested scene_count — LLM may return more scenes than asked for
        scenes = scenes[:scene_count]
        self.autonomous_scene_outline = scenes

        conversation_id = self._ensure_active_chatbot_conversation()
        self._append_chatbot_turn("user", f"[Autonomous] Outline {scene_count} scenes", kind="chat", conversation_id=conversation_id)
        display_text = result.get("raw_content") or json.dumps(result, indent=2)
        self._append_chatbot_turn("assistant", display_text, kind="artifact", conversation_id=conversation_id)
        self.chatbot_last_result = result
        self._record_chatbot_history_entry(CHATBOT_TASK_SCENE_OUTLINE, augmented_brief, result)
        return result

    def _autonomous_generate_single_image_prompt(self, outline_entry, scene_index, total_scenes, previous_image_prompt="", keep_alive=None):
        concept = self.autonomous_expanded_concept or self.autonomous_creative_brief
        title = str(outline_entry.get("title") or "").strip()
        shot_type = str(outline_entry.get("shot_type") or "").strip()
        mood = str(outline_entry.get("mood") or "").strip()
        visual_hook = str(outline_entry.get("visual_hook") or "").strip()
        notes = str(outline_entry.get("notes") or "").strip()

        briefing = (
            f"Scene {scene_index} of {total_scenes} in a music video.\n\n"
            f"Overall concept: {concept[:300]}\n\n"
            f"This scene:\n"
            f"- Title: {title}\n"
            f"- Shot type: {shot_type}\n"
            f"- Mood: {mood}\n"
            f"- Visual hook: {visual_hook}\n"
        )
        if notes:
            briefing += f"- Notes: {notes}\n"
        if previous_image_prompt:
            briefing += f"\nPrevious scene's image direction (for visual continuity):\n{previous_image_prompt[:200]}\n"

        result = self._request_chatbot_structured_output(CHATBOT_TASK_JIT_IMAGE_PROMPT, briefing, keep_alive=keep_alive)
        return str(result.get("image_prompt") or "").strip()

    def _autonomous_generate_single_video_prompt(self, outline_entry, image_prompt_used, scene_index, total_scenes, keep_alive=None):
        title = str(outline_entry.get("title") or "").strip()
        shot_type = str(outline_entry.get("shot_type") or "").strip()
        mood = str(outline_entry.get("mood") or "").strip()
        visual_hook = str(outline_entry.get("visual_hook") or "").strip()

        briefing = (
            f"Scene {scene_index} of {total_scenes}.\n\n"
            f"Scene outline:\n"
            f"- Title: {title}\n"
            f"- Shot type: {shot_type}\n"
            f"- Mood: {mood}\n"
            f"- Visual hook: {visual_hook}\n\n"
            f"The still image that will be animated shows:\n{image_prompt_used[:300]}\n"
        )

        result = self._request_chatbot_structured_output(CHATBOT_TASK_JIT_VIDEO_PROMPT, briefing, keep_alive=keep_alive)
        return str(result.get("video_prompt") or "").strip()

    def _autonomous_apply_scene_plan(self, result):
        scenes = result.get("scenes") if isinstance(result.get("scenes"), list) else []
        normalized_timeline = []
        for index, scene in enumerate(scenes, start=1):
            if not isinstance(scene, dict):
                continue
            prompt_text = str(scene.get("prompt") or "").strip()
            if not prompt_text:
                continue
            scene_number = int(scene.get("scene_number") or index)
            normalized_timeline.append(self._create_scene_entry(scene_number, mode=SCENE_MODE_T2V, prompt=prompt_text))
        if normalized_timeline:
            self.scene_timeline = self._normalize_scene_timeline(normalized_timeline)
            if hasattr(self, "scene_scrollable_frame"):
                self._rebuild_scene_timeline_from_state(self.scene_timeline)

    def _autonomous_plan_song(self, brief, actual_duration, outline_result):
        concept = self.autonomous_expanded_concept or brief
        scene_descriptions = ""
        scenes = outline_result.get("scenes") if isinstance(outline_result.get("scenes"), list) else []
        for s in scenes:
            title = str(s.get("title") or "").strip()
            mood = str(s.get("mood") or "").strip()
            notes = str(s.get("notes") or "").strip()
            if title:
                scene_descriptions += f"- {title}"
                if mood:
                    scene_descriptions += f" [{mood}]"
                if notes:
                    scene_descriptions += f" ({notes})"
                scene_descriptions += "\n"

        augmented_brief = (
            f"Write lyrics and style tags for a song to accompany this music video.\n"
            f"Target song duration: {actual_duration:.0f} seconds.\n\n"
            f"Creative concept:\n{concept}\n\n"
        )
        if scene_descriptions:
            augmented_brief += f"Visual narrative (scene by scene):\n{scene_descriptions}\n"
        augmented_brief += "The song should match the visual mood, pacing, and emotional arc of the scenes."

        result = self._request_chatbot_structured_output(CHATBOT_TASK_SONG_BRAINSTORM, augmented_brief, keep_alive="30m")
        lyrics = str(result.get("lyrics") or "").strip()
        style_tags = str(result.get("style_tags") or "").strip()
        if not lyrics and not style_tags:
            return None

        conversation_id = self._ensure_active_chatbot_conversation()
        self._append_chatbot_turn("user", f"[Autonomous] Write song for ~{actual_duration:.0f}s video", kind="chat", conversation_id=conversation_id)
        display_text = result.get("raw_content") or json.dumps(result, indent=2)
        self._append_chatbot_turn("assistant", display_text, kind="artifact", conversation_id=conversation_id)
        self.chatbot_last_result = result
        self._record_chatbot_history_entry(CHATBOT_TASK_SONG_BRAINSTORM, augmented_brief, result)
        return result

    def _autonomous_generate_all_prompts(self):
        """Batch-generate ALL image and video prompts while the LLM model is warm.

        Generates prompts one-at-a-time (to stay within context limits) but
        back-to-back so the model is never idle long enough to trigger Ollama's
        unload timeout.  Results are stored in self.autonomous_image_prompts
        and self.autonomous_video_prompts for later use by the ComfyUI render
        phases.
        """
        scene_outline = getattr(self, "autonomous_scene_outline", None) or []
        if not scene_outline:
            raise RuntimeError("No scene outline available for prompt generation.")

        scene_outline = scene_outline[:self.autonomous_scene_count]
        total = len(scene_outline)
        keep_alive = "30m"

        # ── Generate all image prompts ──
        self.autonomous_image_prompts = []
        previous_image_prompt = ""

        for index, outline_entry in enumerate(scene_outline, start=1):
            if self.autonomous_cancel_requested:
                raise InterruptedError("Cancelled by user.")

            phase_progress = (index - 1) / (total * 2)  # first half of prompt gen
            self._update_autonomous_progress(
                AUTONOMOUS_STATE_PLANNING_SCENES,
                f"Generating image prompt {index} of {total}...",
                phase_progress,
            )
            self.root.after(0, lambda i=index, t=total: self.update_status(
                f"[Autonomous] Writing image prompt {i} of {t}...", "blue"))

            prompt_text = ""
            for attempt in range(2):
                try:
                    prompt_text = self._autonomous_generate_single_image_prompt(
                        outline_entry, index, total, previous_image_prompt, keep_alive=keep_alive
                    )
                    if prompt_text:
                        break
                except Exception:
                    if attempt >= 1:
                        pass  # Give up on this scene's prompt

            self.autonomous_image_prompts.append(prompt_text)
            if prompt_text:
                previous_image_prompt = prompt_text

        # ── Generate all video prompts ──
        self.autonomous_video_prompts = []

        for index, outline_entry in enumerate(scene_outline, start=1):
            if self.autonomous_cancel_requested:
                raise InterruptedError("Cancelled by user.")

            phase_progress = 0.5 + (index - 1) / (total * 2)  # second half
            self._update_autonomous_progress(
                AUTONOMOUS_STATE_PLANNING_SCENES,
                f"Generating video prompt {index} of {total}...",
                phase_progress,
            )
            self.root.after(0, lambda i=index, t=total: self.update_status(
                f"[Autonomous] Writing video prompt {i} of {t}...", "blue"))

            image_prompt_used = self.autonomous_image_prompts[index - 1] if index <= len(self.autonomous_image_prompts) else ""

            prompt_text = ""
            for attempt in range(2):
                try:
                    prompt_text = self._autonomous_generate_single_video_prompt(
                        outline_entry, image_prompt_used, index, total, keep_alive=keep_alive
                    )
                    if prompt_text:
                        break
                except Exception:
                    if attempt >= 1:
                        pass

            self.autonomous_video_prompts.append(prompt_text)

        image_count = sum(1 for p in self.autonomous_image_prompts if p)
        video_count = sum(1 for p in self.autonomous_video_prompts if p)
        self.log_debug(
            "AUTONOMOUS_ALL_PROMPTS_GENERATED",
            image_prompts=image_count,
            video_prompts=video_count,
            total_scenes=total,
        )
        self._update_autonomous_progress(
            AUTONOMOUS_STATE_PLANNING_SCENES,
            f"Generated {image_count} image + {video_count} video prompts.",
            1.0,
        )

    def _autonomous_apply_song(self, result, actual_duration):
        lyrics = str(result.get("lyrics") or "").strip()
        style_tags = str(result.get("style_tags") or "").strip()
        self.autonomous_music_lyrics = lyrics
        self.autonomous_music_tags = style_tags
        if hasattr(self, "music_lyrics_text") and lyrics:
            self.music_lyrics_text.delete("1.0", tk.END)
            self.music_lyrics_text.insert("1.0", lyrics)
        if hasattr(self, "music_tags_text") and style_tags:
            self.music_tags_text.delete("1.0", tk.END)
            self.music_tags_text.insert("1.0", style_tags)
        try:
            self.music_duration_var.set(int(round(actual_duration)))
        except (ValueError, tk.TclError):
            pass

    def _autonomous_generate_images(self):
        """Render all scene images using pre-planned prompts (no LLM calls)."""
        image_prompts = getattr(self, "autonomous_image_prompts", None) or []
        if not image_prompts:
            raise RuntimeError("No pre-planned image prompts available. Run prompt generation first.")

        image_prompts = image_prompts[:self.autonomous_scene_count]

        if not self.image_workflow:
            raise RuntimeError("No image workflow loaded. Load a Z-Image workflow first.")

        image_settings = self._get_default_image_settings()
        total = len(image_prompts)
        self.autonomous_image_asset_map = {}

        for index, prompt_text in enumerate(image_prompts, start=1):
            if self.autonomous_cancel_requested:
                return False

            phase_progress = (index - 1) / total
            self._update_autonomous_progress(
                AUTONOMOUS_STATE_GENERATING_IMAGES,
                f"Rendering image {index} of {total}...",
                phase_progress,
            )
            self.root.after(0, lambda i=index, t=total: self.update_status(f"[Autonomous] Rendering image {i} of {t}...", "blue"))

            if not prompt_text:
                continue  # Skip scenes where prompt generation failed

            # ── Submit to ComfyUI ──
            filename_prefix = self._build_image_filename_prefix("auto", index=index)
            workflow_to_submit = self._build_image_workflow_for_prompt(prompt_text, filename_prefix, image_settings)

            before_files = self._snapshot_media_files(self.generated_image_dir, SUPPORTED_IMAGE_EXTENSIONS)

            success = False
            for attempt in range(2):
                prompt_id = self.queue_prompt(workflow_to_submit)
                if not prompt_id:
                    continue
                self.eta_item_start_time = time.time()
                success = self.wait_for_completion(prompt_id, output_kind="image", prompt_text=prompt_text)
                if success:
                    break

            if not success:
                continue

            new_file = self._get_newest_rendered_media(before_files, self.generated_image_dir, SUPPORTED_IMAGE_EXTENSIONS)
            if new_file:
                asset = self._get_image_asset_by_path(new_file)
                if asset:
                    self.autonomous_image_asset_map[index] = asset.get("asset_id")

        self._update_autonomous_progress(
            AUTONOMOUS_STATE_GENERATING_IMAGES,
            f"Generated {len(self.autonomous_image_asset_map)} of {total} images.",
            1.0,
        )
        return len(self.autonomous_image_asset_map) > 0

    def _autonomous_build_i2v_timeline(self):
        scene_outline = getattr(self, "autonomous_scene_outline", None) or []
        asset_map = self.autonomous_image_asset_map
        if not scene_outline or not asset_map:
            raise RuntimeError("No scene outline or image assets available to build timeline.")

        normalized_timeline = []
        for index in range(1, len(scene_outline) + 1):
            asset_id = asset_map.get(index)
            if not asset_id:
                continue
            asset = self._get_image_asset_by_id(asset_id)
            if not asset or not os.path.exists(asset.get("project_path", "")):
                continue
            # Use a placeholder prompt — the actual video prompt will be generated JIT during rendering
            normalized_timeline.append(
                self._create_scene_entry(
                    order_index=index,
                    mode=SCENE_MODE_I2V,
                    prompt="(JIT — will be generated before render)",
                    image_asset_id=asset_id,
                )
            )

        if not normalized_timeline:
            raise RuntimeError("Failed to build I2V timeline — no valid scene entries created.")

        self.scene_timeline = self._normalize_scene_timeline(normalized_timeline)

    def _autonomous_rebuild_timeline_ui(self):
        if hasattr(self, "scene_scrollable_frame"):
            self._rebuild_scene_timeline_from_state(self.scene_timeline)

    def _autonomous_render_scenes(self):
        """Render all video scenes using pre-planned prompts (no LLM calls)."""
        scene_timeline = list(self.scene_timeline)
        if not scene_timeline:
            return False

        video_settings, validation_error = self._collect_validated_video_settings()
        if validation_error:
            raise RuntimeError(f"Video settings validation error: {validation_error}")

        video_prompts = getattr(self, "autonomous_video_prompts", None) or []
        total = len(scene_timeline)
        rendered_paths = []

        for index, scene_entry in enumerate(scene_timeline, start=1):
            if self.autonomous_cancel_requested:
                return False

            phase_progress = (index - 1) / total
            self._update_autonomous_progress(
                AUTONOMOUS_STATE_RENDERING,
                f"Rendering scene {index} of {total}...",
                phase_progress,
            )

            scene_id = scene_entry.get("scene_id")
            self.root.after(0, lambda sid=scene_id: self._set_scene_entry_render_state(sid, "rendering"))
            self.root.after(0, lambda i=index, t=total: self.update_status(f"[Autonomous] Rendering scene {i} of {t}...", "blue"))

            # ── Use pre-planned video prompt ──
            prompt_text = video_prompts[index - 1] if index <= len(video_prompts) else ""

            if not prompt_text:
                self.root.after(0, lambda sid=scene_id: self._set_scene_entry_render_state(sid, "failed"))
                continue

            # Update the scene entry with the actual prompt
            scene_entry["prompt"] = prompt_text

            before_files = self._snapshot_media_files(self.scenes_dir, SUPPORTED_VIDEO_EXTENSIONS)
            filename_prefix = self._build_video_filename_prefix(video_settings, "timeline", index)

            scene_mode = scene_entry.get("mode", SCENE_MODE_T2V)
            if scene_mode == SCENE_MODE_I2V:
                asset = self._get_image_asset_by_id(scene_entry.get("image_asset_id"))
                if not asset or not os.path.exists(asset.get("project_path", "")):
                    self.root.after(0, lambda sid=scene_id: self._set_scene_entry_render_state(sid, "failed"))
                    continue
                workflow_to_submit = self._build_i2v_workflow_for_scene(prompt_text, asset.get("project_path"), filename_prefix, video_settings)
            else:
                workflow_to_submit = self._build_video_workflow_for_prompt(prompt_text, filename_prefix, video_settings)

            # ── Submit to ComfyUI with retry ──
            success = False
            for attempt in range(2):
                prompt_id = self.queue_prompt(workflow_to_submit)
                if not prompt_id:
                    continue
                self.eta_item_start_time = time.time()
                success = self.wait_for_completion(prompt_id)
                if success:
                    break

            if not success:
                self.root.after(0, lambda sid=scene_id: self._set_scene_entry_render_state(sid, "failed"))
                continue

            rendered_output = self._get_newest_rendered_media(before_files, self.scenes_dir, SUPPORTED_VIDEO_EXTENSIONS)
            if rendered_output:
                rendered_paths.append(rendered_output)
                scene_entry["output_path"] = rendered_output
                scene_entry["render_status"] = "ready"
                self.root.after(0, lambda sid=scene_id, op=rendered_output: self._set_scene_entry_render_state(sid, "ready", op))

        self.autonomous_rendered_scene_paths = rendered_paths
        self.scene_timeline = self._normalize_scene_timeline(scene_timeline)
        self.root.after(0, self.refresh_gallery)
        self.root.after(0, self.save_project_state)

        self._update_autonomous_progress(AUTONOMOUS_STATE_RENDERING, f"Rendered {len(rendered_paths)} of {total} scenes.", 1.0)
        return len(rendered_paths) > 0

    def _autonomous_stitch_scenes(self):
        # Use rendered paths in timeline order (not mtime) to preserve scene sequence
        paths = self.autonomous_rendered_scene_paths
        if not paths:
            scene_files = []
            if hasattr(self, "scenes_dir") and os.path.isdir(self.scenes_dir):
                for f in sorted(os.listdir(self.scenes_dir)):
                    full = os.path.join(self.scenes_dir, f)
                    if os.path.isfile(full) and os.path.splitext(f)[1].lower() in SUPPORTED_VIDEO_EXTENSIONS:
                        scene_files.append(full)
            paths = scene_files
        if not paths:
            return False

        # Preserve timeline order — paths are already in scene sequence from the render loop
        filepaths = list(paths)

        timestamp = int(time.time())
        list_file = os.path.join(self.stitched_dir, f"concat_auto_{timestamp}.txt")
        output_file = os.path.join(self.stitched_dir, f"final_master_render_{timestamp}.mp4")
        try:
            with open(list_file, 'w', encoding='utf-8') as f:
                for path in filepaths:
                    formatted_path = path.replace('\\', '/')
                    f.write(f"file '{formatted_path}'\n")
            cmd = [FFMPEG_PATH, '-y', '-f', 'concat', '-safe', '0', '-i', list_file, '-c:v', 'copy', '-an', output_file]
            subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW, capture_output=True, text=True, check=True)
        except Exception as exc:
            raise RuntimeError(f"Stitching failed: {exc}")
        finally:
            if os.path.exists(list_file):
                try:
                    os.remove(list_file)
                except Exception:
                    pass

        if not os.path.exists(output_file):
            return False

        self.selected_video_for_music = output_file
        self._update_autonomous_progress(AUTONOMOUS_STATE_STITCHING, f"Stitched {len(filepaths)} clips.", 1.0)
        self.root.after(0, self.refresh_gallery)
        return True

    def _autonomous_generate_music(self):
        tags = self.autonomous_music_tags
        lyrics = self.autonomous_music_lyrics
        if not tags and not lyrics:
            raise RuntimeError("No music tags or lyrics available for music generation.")

        self.current_generated_audio = None
        self.run_music_generation(tags, lyrics)

        if self.current_generated_audio and os.path.exists(self.current_generated_audio):
            self._update_autonomous_progress(AUTONOMOUS_STATE_GENERATING_MUSIC, "Soundtrack generated.", 1.0)
            return True

        return False

    def _autonomous_final_merge(self):
        if not self.selected_video_for_music or not os.path.exists(self.selected_video_for_music):
            raise RuntimeError("No stitched video available for final merge.")
        if not self.current_generated_audio or not os.path.exists(self.current_generated_audio):
            raise RuntimeError("No generated audio available for final merge.")

        timestamp = int(time.time())
        output_file = os.path.join(self.final_mv_dir, f"Final_Music_Video_{timestamp}.mp4")
        cmd = [
            FFMPEG_PATH, '-y',
            '-i', self.selected_video_for_music,
            '-i', self.current_generated_audio,
            '-map', '0:v:0', '-map', '1:a:0',
            '-c:v', 'copy', '-c:a', 'aac',
            '-shortest', output_file
        ]
        try:
            subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"Final merge FFmpeg error: {exc.stderr}")
        except FileNotFoundError:
            raise RuntimeError("FFmpeg not found. Install FFmpeg or imageio-ffmpeg.")

        if not os.path.exists(output_file):
            raise RuntimeError("Final merge produced no output file.")

        self.current_final_video = output_file
        self._update_autonomous_progress(AUTONOMOUS_STATE_MERGING, f"Music video complete: {os.path.basename(output_file)}", 1.0)
        self.root.after(0, self.refresh_gallery)

    def on_closing(self):
        self._cancel_comfyui_console_poll()
        self.save_global_settings()
        self.save_project_state()
        if self.chatbot_server_managed_by_app:
            self._stop_managed_chatbot_server()
        if self.comfyui_process:
            try:
                subprocess.run(['TASKKILL', '/F', '/T', '/PID', str(self.comfyui_process.pid)], creationflags=subprocess.CREATE_NO_WINDOW)
            except Exception:
                pass
        self.comfyui_process = None
        self.comfyui_console_hwnd = None
        self.comfyui_console_visible = False
        self.comfyui_console_title = None
        self.comfyui_console_pending_visibility = None
        self.root.destroy()

if __name__ == "__main__":
    root = Prompt2MTVWindow(themename=THEME_NAME)
    app = LTXQueueManager(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
