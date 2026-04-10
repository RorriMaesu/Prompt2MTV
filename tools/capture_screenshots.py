#!/usr/bin/env python3
"""
Automated screenshot capture for Prompt2MTV README.

Launches the app, navigates each tab, injects sample data, expands
collapsible sections, and captures screenshots using Pillow ImageGrab.

Usage:
    python tools/capture_screenshots.py
"""

import ctypes
import os
import sys
import time
import tkinter as tk

# ── DPI awareness (must be set before any Tk import) ────────────────────────
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI aware
except Exception:
    pass

# ── Ensure project root is on sys.path ──────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from PIL import ImageGrab  # noqa: E402

SCREENSHOT_DIR = os.path.join(PROJECT_ROOT, "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Target width for README images
TARGET_WIDTH = 1280

# ── Sample data ─────────────────────────────────────────────────────────────
CHATBOT_SAMPLE_TURNS = [
    ("user", "I want to create a cinematic music video about a lone astronaut drifting "
     "through a neon-lit nebula. Can you help brainstorm ideas?"),
    ("assistant",
     "Great concept! Here are a few directions we could take:\n\n"
     "1. Solitude & Wonder — slow, sweeping shots of the astronaut silhouetted "
     "against swirling violet and teal gas clouds.\n"
     "2. Retro-Futurism — 80s-inspired synthwave palette with glowing grid lines "
     "overlaid on deep-space vistas.\n"
     "3. Emotional Arc — start in cold darkness, gradually introduce warm neon "
     "hues as the music builds.\n\n"
     "Which vibe resonates with you, or shall I combine elements?"),
    ("user", "I love the Retro-Futurism angle with the emotional arc! Let's combine those."),
    ("assistant",
     "Perfect combo! I'll draft scene prompts that start in dark deep-space with "
     "subtle cyan edges, then gradually introduce hot-pink and gold neon grids as "
     "the track reaches its crescendo. The astronaut's visor will reflect the "
     "growing light — a nice metaphor for discovery. Ready to generate the scene "
     "breakdown when you are!"),
]

SCENE_PROMPTS = [
    "A lone astronaut floats in silence through the void of deep space. Faint cyan light "
    "edges the suit's visor. Stars drift slowly. Cold, dark, cinematic wide shot.",
    "The camera slowly pushes in as a neon-purple nebula emerges behind the astronaut. "
    "Synthwave grid lines begin to materialize in the gas clouds, glowing faintly.",
    "Hot-pink and gold neon light floods the frame as the nebula erupts in color. "
    "The astronaut's visor reflects swirling patterns. Music crescendo, euphoric.",
]

IMAGE_PROMPTS = [
    "Deep-space void, lone astronaut silhouette, faint cyan rim light on helmet visor, "
    "ultra-wide cinematic still, 8K, photorealistic",
    "Retro-futurism nebula swirl, synthwave grid overlay, violet and teal gas clouds, "
    "astronaut mid-frame, digital painting, concept art",
    "Neon explosion nebula, hot-pink and gold light rays, astronaut visor reflection, "
    "dramatic close-up portrait, hyper-detailed",
]

MUSIC_TAGS = (
    "synthwave, retro-futurism, cinematic, atmospheric, electronic, "
    "80s nostalgia, dreamy pads, arpeggiated synths, deep bass, "
    "emotional build, neon-lit, space exploration, euphoric crescendo"
)

MUSIC_LYRICS = """[Verse 1]
Drifting through the silence of a thousand suns
Cold and weightless, counting stars that never come
A flicker on the visor, cyan edge of light
The universe is waking from an endless night

[Chorus]
Neon rising, colors bleeding through the dark
Every photon carries fire, every wave a spark
Hold your breath and feel the grid beneath your skin
The nebula is calling — let the light begin

[Verse 2]
Pink and gold erupting where the void once stood
Synthwave pulses echoing like heart and blood
Reflections in the glass of everything I've found
A universe of color where there was no sound

[Chorus]
Neon rising, colors bleeding through the dark
Every photon carries fire, every wave a spark
Hold your breath and feel the grid beneath your skin
The nebula is calling — let the light begin"""


# ── Helpers ─────────────────────────────────────────────────────────────────

def _settle(root, delay=0.5):
    """Force TK to update and wait for the compositor."""
    root.update_idletasks()
    root.update()
    time.sleep(delay)


def _grab_window(root):
    """Capture the Tk root window region and return a PIL Image."""
    _settle(root, 0.5)
    x = root.winfo_rootx()
    y = root.winfo_rooty()
    w = root.winfo_width()
    h = root.winfo_height()
    return ImageGrab.grab(bbox=(x, y, x + w, y + h))


def _save(img, name):
    """Resize to TARGET_WIDTH and save as PNG."""
    ratio = TARGET_WIDTH / img.width
    new_size = (TARGET_WIDTH, int(img.height * ratio))
    img = img.resize(new_size, resample=3)  # LANCZOS
    path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    img.save(path, "PNG", optimize=True)
    print(f"  ✓ saved {path}  ({new_size[0]}×{new_size[1]})")
    return path


def _open_section(app, key):
    """Open a collapsible section by key (close siblings in its group)."""
    app._set_collapsible_section_open(key, True)


def main():
    print("Launching Prompt2MTV for screenshot capture …")

    # ── Monkey-patch to prevent ComfyUI from launching ──────────────────
    import ltx_queue_manager as mod
    _original_launch = mod.LTXQueueManager.launch_comfyui
    mod.LTXQueueManager.launch_comfyui = lambda self: None

    root = mod.Prompt2MTVWindow(themename=mod.THEME_NAME)
    app = mod.LTXQueueManager(root)

    # Restore in case we need it later
    mod.LTXQueueManager.launch_comfyui = _original_launch

    # Let the UI fully render
    _settle(root, 1.5)

    saved = []

    # ════════════════════════════════════════════════════════════════════
    # 1. CHATBOT TAB  — conversation + expanded workspace
    # ════════════════════════════════════════════════════════════════════
    print("[1/5] Chatbot tab …")
    app.notebook.select(app.chatbot_tab)
    _settle(root, 0.3)

    # Set mode to Chat / Explore
    app.chatbot_task_var.set(mod.CHATBOT_TASK_CHAT)

    # Inject sample conversation
    conv_id = app._ensure_active_chatbot_conversation(title="Neon Nebula Music Video")
    for role, content in CHATBOT_SAMPLE_TURNS:
        app._append_chatbot_turn(role, content, kind="chat", conversation_id=conv_id)
    app._refresh_chatbot_transcript()

    # Expand the Creative Workspace section
    _open_section(app, "chatbot_focus_workspace")

    _settle(root, 0.6)
    saved.append(_save(_grab_window(root), "01_chatbot"))

    # ════════════════════════════════════════════════════════════════════
    # 2. IMAGE PHASE TAB  — expanded with prompts filled in
    # ════════════════════════════════════════════════════════════════════
    print("[2/5] Image Phase tab …")
    app.notebook.select(app.image_tab)
    _settle(root, 0.3)

    # Expand Image Utilities (header area with stats + settings)
    _open_section(app, "image_utilities")
    _settle(root, 0.2)

    # Expand Image Prompt Queue section
    _open_section(app, "image_prompt_queue")
    _settle(root, 0.2)

    # Add sample image prompts
    for prompt_text in IMAGE_PROMPTS:
        app.add_image_prompt_entry()
        # The last added widget is at the end of app.image_prompts
        app.image_prompts[-1].insert("1.0", prompt_text)

    # Update the meta text
    app._update_prompt_collection_summary()
    app._update_image_workspace_balance()
    _settle(root, 0.5)
    saved.append(_save(_grab_window(root), "02_image_phase"))

    # ════════════════════════════════════════════════════════════════════
    # 3. VIDEO GENERATION TAB  — scene timeline expanded with scenes
    # ════════════════════════════════════════════════════════════════════
    print("[3/5] Video Generation tab …")
    app.notebook.select(app.video_tab)
    _settle(root, 0.3)

    # Expand Scene Timeline section
    _open_section(app, "scene_timeline")
    _settle(root, 0.2)

    # Add sample scene entries
    for i, prompt in enumerate(SCENE_PROMPTS):
        scene_data = app._create_scene_entry(
            order_index=i + 1,
            mode=mod.SCENE_MODE_T2V,
            prompt=prompt,
        )
        app.add_scene_timeline_entry(scene_data)

    app._update_prompt_collection_summary()
    app._update_video_workspace_balance()
    _settle(root, 0.5)
    saved.append(_save(_grab_window(root), "03_video_generation"))

    # ════════════════════════════════════════════════════════════════════
    # 4. GALLERY TAB  — expanded browser section
    # ════════════════════════════════════════════════════════════════════
    print("[4/5] Gallery tab …")
    app.notebook.select(app.gallery_tab)
    _settle(root, 0.3)

    # Expand Gallery Browser section
    _open_section(app, "gallery_browser")
    _settle(root, 0.5)
    saved.append(_save(_grab_window(root), "04_gallery"))

    # ════════════════════════════════════════════════════════════════════
    # 5. MUSIC STUDIO TAB  — expanded with tags, lyrics, and controls
    # ════════════════════════════════════════════════════════════════════
    print("[5/5] Music Studio tab …")
    app.notebook.select(app.music_tab)
    _settle(root, 0.3)

    # Fill in music style tags
    app.music_tags_text.insert("1.0", MUSIC_TAGS)

    # Fill in lyrics
    app.music_lyrics_text.insert("1.0", MUSIC_LYRICS)

    # Set richer music config values
    app.music_duration_var.set(180)
    app.music_bpm_var.set(128)
    app.music_key_var.set("A minor")

    # Update the summary chips
    app._update_music_config_summary()

    # Expand Style Direction section to show tags
    _open_section(app, "music_prompt")
    _settle(root, 0.2)

    # Expand Lyrics section
    _open_section(app, "music_lyrics")
    _settle(root, 0.2)

    # Expand Run and Review section
    _open_section(app, "music_actions")
    _settle(root, 0.5)

    saved.append(_save(_grab_window(root), "05_music_studio"))

    # ── Cleanup ─────────────────────────────────────────────────────────
    root.destroy()

    print(f"\nDone — {len(saved)} screenshots saved to {SCREENSHOT_DIR}")
    for p in saved:
        print(f"  {p}")


if __name__ == "__main__":
    main()
