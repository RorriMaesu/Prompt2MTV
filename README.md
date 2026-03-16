![Prompt2MTV Logo](prompt2MTV_logo.jpg)

# Prompt2MTV

Prompt2MTV is a Windows desktop app for building end-to-end AI music videos with a local ComfyUI pipeline. It combines LTX 2.3 text-to-video generation, prompt queue management, project organization, gallery review, ACE-Step music generation, and final audio/video merging in one interface.

Current packaged release: `0.2.0`

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
- Built-in first-launch guidance and startup preflight feedback.
- Runtime path configuration for ComfyUI root, launcher, model search paths, and output location.
- Responsive desktop UI with collapsible work areas for queueing, settings, diagnostics, and media review.
- Media gallery for scene clips, stitched outputs, and final music videos.
- ACE-Step music generation workflow support.
- Final merge flow for combining generated audio with selected video renders.
- Packaged Windows `.exe` and Inno Setup installer workflow.
- In-app About dialog and visible version label for installed builds.
- Debug logging to help troubleshoot local ComfyUI or workflow issues.

## Repository Contents

- `ltx_queue_manager.py`: Main application entry point and UI logic.
- `video_ltx2_3_t2v.json`: Primary LTX 2.3 text-to-video workflow.
- `ACE_Step_AI_Music_Generator_Workflow.json`: Music-generation workflow.
- `LTX_T2V_Low_VRAM_GGUF.json`: Alternate or legacy reference workflow.
- `requirements.txt`: Python dependencies for local development and packaging.
- `Prompt2MTV.spec`: Versioned PyInstaller build definition.
- `Prompt2MTV.iss`: Versioned Inno Setup installer definition.
- `build_exe.bat`: Helper script for building the Windows app bundle.
- `build_installer.bat`: Helper script for rebuilding the app and compiling the installer.
- `Prompt2MTV.ico`: Windows application and installer icon.
- `Prompt2MTV_version_info.txt`: Windows executable version metadata.
- `prompt2MTV_logo.jpg`: Logo used in the project documentation.

Generated project data and media outputs are written to `outputs/` at runtime and are excluded from source control.

## Prerequisites

Before launching Prompt2MTV, make sure your local environment is ready:

- Windows system.
- Python 3.11 or newer.
- A working local ComfyUI installation.
- The required LTX 2.3 workflow models.
- The required ACE-Step music workflow dependencies.
- FFmpeg available either from your system install or via bundled `imageio-ffmpeg` support.

The app can auto-discover common ComfyUI layouts and also lets you configure paths inside the UI. Default discovery looks at common locations rooted around your ComfyUI install, including setups like:

- `D:\ComfyUI\ComfyUI\models`
- `D:\ComfyUI\models`

If your ComfyUI environment uses a different layout, use `Project > Configure Runtime Paths` after launch.

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
pip install -r requirements.txt
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

On first launch, Prompt2MTV runs a setup/preflight check and explains missing ComfyUI, model, launcher, or FFmpeg requirements in plain language.

### Build a Windows executable

After the virtual environment is created and dependencies are installed, you can build a Windows GUI executable with:

```powershell
.\build_exe.bat
```

The packaged app is written to `dist\Prompt2MTV\Prompt2MTV.exe`.

The build uses the checked-in `Prompt2MTV.spec` file so packaging settings stay versioned with the project.
The executable icon is sourced from `Prompt2MTV.ico`.

The executable still expects a local ComfyUI installation and models, but it now stores app settings in a per-user Windows app-data folder and can prompt for ComfyUI runtime paths on first launch.

Packaged builds store their per-user data in:

- `%LOCALAPPDATA%\Prompt2MTV\app_settings.json`
- `%LOCALAPPDATA%\Prompt2MTV\outputs\`

### Build a Windows installer

If you want a setup wizard that installs Prompt2MTV and creates shortcuts, install Inno Setup 6 and run:

```powershell
.\build_installer.bat
```

That script rebuilds the packaged app, then compiles the checked-in `Prompt2MTV.iss` installer script into the `dist_installer` folder.

The current installer output name is versioned, for example:

- `dist_installer\Prompt2MTV-Setup-0.2.0.exe`

The installer is designed for non-technical Windows users and creates Start Menu and desktop shortcuts.

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
- Source checkouts keep local runtime files such as `app_settings.json` and `app_state.json` outside version control.
- Packaged builds keep user settings and outputs in `%LOCALAPPDATA%\Prompt2MTV`.
- If Prompt2MTV cannot find your ComfyUI launcher, root folder, or model directories, open `Project > Configure Runtime Paths`.
- The Help menu includes an About dialog so users can confirm the installed version without opening Windows file properties.
- The installer and packaged app do not bundle ComfyUI itself or the required models.

## Support / Donate

If Prompt2MTV has made your workflow faster, cleaner, or just less painful, consider supporting development. It helps cover the boring but necessary parts of keeping a project like this alive: testing new workflow changes, polishing the UI, fixing breakages, and funding the late-night sessions that turn rough tools into reliable ones.

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Support-FFDD00?logo=buymeacoffee&logoColor=000000)](https://buymeacoffee.com/rorrimaesu)