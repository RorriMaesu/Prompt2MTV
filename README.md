![Prompt2MTV Logo](prompt2MTV_logo.jpg)

# Prompt2MTV

Prompt2MTV is a Windows desktop app for building end-to-end AI music videos with a local ComfyUI pipeline. It combines LTX 2.3 text-to-video generation, prompt queue management, project organization, gallery review, ACE-Step music generation, and final audio/video merging in one interface.

The goal is simple: keep the entire prompt-to-music-video workflow in a single workspace so you can spend less time managing JSON files, output folders, and render handoffs, and more time iterating on actual creative direction.

## What It Does

Prompt2MTV is built for creators who want a more practical production workflow around ComfyUI-based video generation. Instead of treating each render, stitch, and music pass as a separate manual process, the app gives you a project-centered pipeline:

1. Draft and queue prompts.
2. Generate scenes through an LTX 2.3 workflow.
3. Review clips in a gallery.
4. Stitch selected renders.
5. Generate music with ACE-Step.
6. Merge the final soundtrack and video.

## Key Features

- LTX 2.3 text-to-video workflow integration.
- Prompt queue for batching multiple scenes.
- Project-based organization for repeatable creative work.
- Workflow settings panel with model selection and validation.
- Built-in preflight feedback for catching setup problems earlier.
- Responsive desktop UI with collapsible work areas for queueing, settings, diagnostics, and media review.
- Media gallery for scene clips, stitched outputs, and final music videos.
- ACE-Step music generation workflow support.
- Final merge flow for combining generated audio with selected video renders.
- Debug logging to help troubleshoot local ComfyUI or workflow issues.

## Repository Contents

- `ltx_queue_manager.py`: Main application entry point and UI logic.
- `video_ltx2_3_t2v.json`: Primary LTX 2.3 text-to-video workflow.
- `ACE_Step_AI_Music_Generator_Workflow.json`: Music-generation workflow.
- `LTX_T2V_Low_VRAM_GGUF.json`: Alternate or legacy reference workflow.
- `prompt2MTV_logo.jpg`: Logo used in the project documentation.

Generated project data and media outputs are written to `outputs/` at runtime and are excluded from source control.

## Prerequisites

Before launching Prompt2MTV, make sure your local environment is ready:

- Windows system.
- Python 3.11 or newer.
- A working local ComfyUI installation.
- The required LTX 2.3 workflow models.
- The required ACE-Step music workflow dependencies.
- FFmpeg installed locally, or available through `imageio-ffmpeg`, for merging audio and video.

The app currently looks for ComfyUI models in these default locations:

- `D:\ComfyUI\ComfyUI\models`
- `D:\ComfyUI\models`

If your ComfyUI environment uses a different layout, update your local setup before running the app.

## Installation

### 1. Clone the repository

```powershell
git clone https://github.com/RorriMaesu/Prompt2MTV.git
cd Prompt2MTV
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
pip install pillow ttkbootstrap imageio-ffmpeg
```

### 5. Verify workflow files and models

Make sure these workflow files remain in the project root:

- `video_ltx2_3_t2v.json`
- `ACE_Step_AI_Music_Generator_Workflow.json`

Then confirm that your local ComfyUI install can access the corresponding models referenced by those workflows.

## Basic Usage

### Start the application

```powershell
python ltx_queue_manager.py
```

### Typical workflow

1. Launch Prompt2MTV.
2. Load or create a project folder.
3. Open Workflow Settings and confirm your model selections.
4. Run validation before starting a new render batch.
5. Add prompts to the Prompt Queue.
6. Run the queue to send jobs to ComfyUI.
7. Review generated scenes in the gallery.
8. Stitch the clips you want to keep.
9. Generate music from the ACE-Step workflow.
10. Merge the generated soundtrack with the selected video render.

## Operational Notes

- Prompt2MTV communicates with a local ComfyUI instance rather than a hosted backend.
- Generated files are stored inside project folders under `outputs/`.
- Local runtime files such as `app_settings.json` and `app_state.json` are intentionally kept out of version control.
- If FFmpeg is unavailable, merge-related features may not work until it is installed or exposed through `imageio-ffmpeg`.

## Support / Donate

If Prompt2MTV has made your workflow faster, cleaner, or just less painful, consider supporting development. It helps cover the boring but necessary parts of keeping a project like this alive: testing new workflow changes, polishing the UI, fixing breakages, and funding the late-night sessions that turn rough tools into reliable ones.

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Support-FFDD00?logo=buymeacoffee&logoColor=000000)](https://buymeacoffee.com/rorrimaesu)