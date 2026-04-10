#!/usr/bin/env python3
"""
Automated screenshot capture for Prompt2MTV README.

Launches the app headlessly (no mainloop), navigates each tab,
injects sample data where needed, and captures screenshots using
Pillow's ImageGrab.

Usage:
    python tools/capture_screenshots.py
"""

import ctypes
import os
import sys
import time

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

# Target width for README images (screenshots will be resized proportionally)
TARGET_WIDTH = 1280

# ── Sample data ─────────────────────────────────────────────────────────────
CHATBOT_SAMPLE_TURNS = [
    ("user", "I want to create a cinematic music video about a lone astronaut drifting through a neon-lit nebula. Can you help brainstorm ideas?"),
    ("assistant", "Great concept! Here are a few directions we could take:\n\n"
     "1. **Solitude & Wonder** — slow, sweeping shots of the astronaut silhouetted against swirling violet and teal gas clouds.\n"
     "2. **Retro-Futurism** — 80s-inspired synthwave palette with glowing grid lines overlaid on deep-space vistas.\n"
     "3. **Emotional Arc** — start in cold darkness, gradually introduce warm neon hues as the music builds.\n\n"
     "Which vibe resonates with you, or shall I combine elements?"),
    ("user", "I love the Retro-Futurism angle with the emotional arc! Let's combine those."),
    ("assistant", "Perfect combo! I'll draft scene prompts that start in dark deep-space with subtle cyan edges, "
     "then gradually introduce hot-pink and gold neon grids as the track reaches its crescendo. "
     "The astronaut's visor will reflect the growing light — a nice metaphor for discovery. "
     "Ready to generate the scene breakdown when you are!"),
]


def _grab_window(root):
    """Capture the Tk root window region and return a PIL Image."""
    root.update_idletasks()
    root.update()
    time.sleep(0.4)  # let the compositor finish rendering

    x = root.winfo_rootx()
    y = root.winfo_rooty()
    w = root.winfo_width()
    h = root.winfo_height()
    img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    return img


def _save(img, name):
    """Resize to TARGET_WIDTH and save as PNG."""
    ratio = TARGET_WIDTH / img.width
    new_size = (TARGET_WIDTH, int(img.height * ratio))
    img = img.resize(new_size, resample=3)  # LANCZOS
    path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    img.save(path, "PNG", optimize=True)
    print(f"  ✓ saved {path}  ({new_size[0]}×{new_size[1]})")
    return path


def main():
    print("Launching Prompt2MTV for screenshot capture …")

    # Import app classes
    import ltx_queue_manager as mod

    root = mod.Prompt2MTVWindow(themename=mod.THEME_NAME)
    app = mod.LTXQueueManager(root)

    # Let the UI fully render
    root.update_idletasks()
    root.update()
    time.sleep(1.5)

    saved = []

    # ── 1. Chatbot tab (Chat mode with sample conversation) ─────────────
    print("[1/5] Chatbot tab …")
    app.notebook.select(app.chatbot_tab)
    app.chatbot_task_var.set(mod.CHATBOT_TASK_CHAT)
    conv_id = app._ensure_active_chatbot_conversation(title="Neon Nebula Music Video")
    for role, content in CHATBOT_SAMPLE_TURNS:
        app._append_chatbot_turn(role, content, kind="chat", conversation_id=conv_id)
    app._refresh_chatbot_transcript()
    root.update_idletasks()
    root.update()
    time.sleep(0.5)
    saved.append(_save(_grab_window(root), "01_chatbot"))

    # ── 2. Image Phase tab ──────────────────────────────────────────────
    print("[2/5] Image Phase tab …")
    app.notebook.select(app.image_tab)
    root.update_idletasks()
    root.update()
    time.sleep(0.3)
    saved.append(_save(_grab_window(root), "02_image_phase"))

    # ── 3. Video Generation tab ─────────────────────────────────────────
    print("[3/5] Video Generation tab …")
    app.notebook.select(app.video_tab)
    root.update_idletasks()
    root.update()
    time.sleep(0.3)
    saved.append(_save(_grab_window(root), "03_video_generation"))

    # ── 4. Gallery tab ──────────────────────────────────────────────────
    print("[4/5] Gallery tab …")
    app.notebook.select(app.gallery_tab)
    root.update_idletasks()
    root.update()
    time.sleep(0.3)
    saved.append(_save(_grab_window(root), "04_gallery"))

    # ── 5. Music Studio tab ─────────────────────────────────────────────
    print("[5/5] Music Studio tab …")
    app.notebook.select(app.music_tab)
    root.update_idletasks()
    root.update()
    time.sleep(0.3)
    saved.append(_save(_grab_window(root), "05_music_studio"))

    root.destroy()

    print(f"\nDone — {len(saved)} screenshots saved to {SCREENSHOT_DIR}")
    for p in saved:
        print(f"  {p}")


if __name__ == "__main__":
    main()
