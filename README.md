![Prompt2MTV Logo](prompt2MTV_logo.jpg)

# Prompt2MTV

Prompt2MTV is a polished desktop control center for turning text prompts into music videos with ComfyUI, LTX 2.3 video workflows, and ACE-Step music generation. It combines prompt queueing, project management, render validation, gallery review, soundtrack generation, and final video assembly in a single Windows-friendly interface.

The application is built around a local ComfyUI pipeline and is designed to reduce friction when moving from idea to finished music video. Instead of manually juggling workflow JSON files, output folders, model selections, scene stitching, and music passes, Prompt2MTV keeps the full process in one place.

## Key Features

- Modern desktop UI built with Tkinter and ttkbootstrap.
- Integrated LTX 2.3 text-to-video workflow support.
- Prompt queue for drafting and submitting multiple scene prompts in sequence.
- Project-based output organization under dedicated project folders.
- Workflow validation and model selection for checkpoints, text encoders, LoRAs, and upscalers.
- Built-in gallery for reviewing scenes, stitched renders, and final music videos.
- ACE-Step AI music workflow integration for soundtrack generation.
- Audio/video merge flow for producing a final music video export.
- Debug logging and preflight feedback to help diagnose local workflow issues.
- Fullscreen-friendly responsive layout with collapsible workspace sections.

## Project Structure

Key files in this repository:

- `ltx_queue_manager.py`: Main desktop application.
- `video_ltx2_3_t2v.json`: Primary LTX 2.3 video workflow.
- `ACE_Step_AI_Music_Generator_Workflow.json`: Music generation workflow.
- `LTX_T2V_Low_VRAM_GGUF.json`: Legacy or alternate workflow reference.
- `prompt2MTV_logo.jpg`: Project logo used in this repository and documentation.

Generated media and working project data are stored under `outputs/` during runtime and are intentionally excluded from version control.

## Prerequisites

Before running Prompt2MTV, make sure you have:

- Windows with Python 3.11+ available.
- A local ComfyUI installation configured for your workflows.
- The required LTX 2.3 model files in your ComfyUI model directories.
- The required ACE-Step music workflow dependencies.
- FFmpeg installed or available through `imageio-ffmpeg` for audio/video merge operations.

By default, the app looks for ComfyUI models in:

- `D:\ComfyUI\ComfyUI\models`
- `D:\ComfyUI\models`

If your environment differs, adjust your local setup accordingly before use.

## Installation

### 1. Clone the repository

```powershell
git clone https://github.com/RorriMaesu/Prompt2MTV.git
cd Prompt2MTV
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Python dependencies

This project currently uses direct script dependencies rather than a packaged installer. Install the libraries used by the application:

```powershell
pip install pillow ttkbootstrap imageio-ffmpeg
```

### 4. Confirm your ComfyUI workflows and models are in place

Ensure the following local workflow files are present in the project root:

- `video_ltx2_3_t2v.json`
- `ACE_Step_AI_Music_Generator_Workflow.json`

Also verify your LTX 2.3 and music-generation models are available to ComfyUI.

## Basic Usage

### Launch the app

```powershell
python ltx_queue_manager.py
```

### Typical workflow

1. Start Prompt2MTV.
2. Let the app load the default LTX 2.3 workflow and your most recent project, or create/select a project folder.
3. Review Workflow Settings and validate your video setup.
4. Add one or more prompts to the Prompt Queue.
5. Run the queue to generate scene clips through ComfyUI.
6. Review results in the gallery and select clips to stitch.
7. Generate music with the ACE-Step workflow.
8. Merge the generated audio with the selected video render.
9. Export and review the final music video from the gallery.

## Notes

- The application launches and communicates with a local ComfyUI instance.
- Generated assets are written into project folders inside `outputs/`.
- Local settings and runtime state are machine-specific and are not intended to be shared through Git.
- If FFmpeg is missing, merging and some media-processing steps may fail until it is installed.

## Support / Donate

If Prompt2MTV saves you time, helps unblock your workflow, or simply makes late-night iteration easier, consider supporting development. Contributions help fund more polish, faster fixes, and continued updates to keep the tool aligned with evolving LTX and ComfyUI workflows.

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Support-FFDD00?logo=buymeacoffee&logoColor=000000)](https://buymeacoffee.com/rorrimaesu)

## License

No license file is currently included in this repository.

Until a license is added, treat the project as all rights reserved by default. If you plan to share or redistribute Prompt2MTV, add an explicit license file first.