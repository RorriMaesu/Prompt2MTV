![Prompt2MTV Logo](prompt2MTV_logo.jpg)

# Prompt2MTV

Prompt2MTV is a Windows desktop app for building end-to-end AI music videos with a local ComfyUI pipeline. It combines LTX 2.3 text-to-video generation, prompt queue management, project organization, gallery review, ACE-Step music generation, and final audio/video merging in one interface.

Projects can also store user-imported video clips and audio tracks, so you can bring in your own media instead of relying only on generated outputs. The music workspace now exposes more of the original ACE-Step workflow tuning controls, keeps those settings per project, and can start ComfyUI with its terminal hidden until you explicitly reveal it.

Current packaged release: `0.3.0`

## Start Here

If you just want to use Prompt2MTV on Windows:

1. Install ComfyUI portable.
2. Install Prompt2MTV from the Windows setup `.exe`.
3. Launch Prompt2MTV and let it guide you through missing paths or models.

Prompt2MTV is installable as a normal Windows app.
Prompt2MTV is **not** a cloud service and does **not** include ComfyUI or the large model files.

## Step 1: Install ComfyUI Portable

Prompt2MTV depends on a local ComfyUI installation.

Use one of these official Windows portable downloads:

- NVIDIA: [ComfyUI Windows Portable NVIDIA](https://github.com/comfyanonymous/ComfyUI/releases/latest/download/ComfyUI_windows_portable_nvidia.7z)
- AMD: [ComfyUI Windows Portable AMD](https://github.com/comfyanonymous/ComfyUI/releases/latest/download/ComfyUI_windows_portable_amd.7z)
- Official releases page: [ComfyUI Releases](https://github.com/Comfy-Org/ComfyUI/releases)

Install it like this:

1. Download the portable archive that matches your GPU.
2. Extract the `.7z` file.
3. Put the extracted folder somewhere simple, for example `D:\ComfyUI`.
4. Start ComfyUI once to confirm it opens correctly.
5. Close ComfyUI.

If Windows blocks the archive, open its file properties and click `Unblock` before extracting.

If the NVIDIA portable build does not start, update your NVIDIA drivers first.

## Step 2: Install Prompt2MTV

Download the Windows installer from GitHub Releases:

- [Prompt2MTV Releases](https://github.com/RorriMaesu/Prompt2MTV/releases)

Then:

1. Download the latest `Prompt2MTV-Setup-<version>.exe` file.
2. Double-click it.
3. Finish the setup wizard.
4. Launch Prompt2MTV from the desktop shortcut or Start Menu.

Expected installer filename example:

- `Prompt2MTV-Setup-0.3.0.exe`

The installer already includes the packaged app and its Python/runtime dependencies.

You do **not** need to install manually:

- Python
- `pip`
- virtual environments
- `requirements.txt`
- PyInstaller
- Inno Setup

## What Prompt2MTV Installs

The Windows installer includes:

- Prompt2MTV desktop app
- packaged Python runtime for the app
- bundled app dependencies
- desktop and Start Menu shortcuts
- per-user settings and output folders under `%LOCALAPPDATA%\Prompt2MTV`

The Windows installer does **not** include:

- ComfyUI itself
- LTX models
- ACE-Step models
- other large checkpoints, LoRAs, or model assets

## What Happens On First Launch

On first launch, Prompt2MTV runs startup checks and tells you what is missing in plain language.

It can help with:

- locating your ComfyUI root folder
- locating your ComfyUI launcher `.bat` file
- locating your ComfyUI model folders
- detecting missing workflow models

If `model_manifest.json` contains valid download URLs, Prompt2MTV can offer to download missing workflow models directly into the correct ComfyUI folders automatically.

If your ComfyUI install lives in a non-default location, use `Project > Configure Runtime Paths` inside the app.

Typical example ComfyUI root folder:

- `D:\ComfyUI`

## Before You Render Anything

Before Prompt2MTV can actually generate scenes or music, you still need:

- Windows
- a working local ComfyUI installation
- the required LTX 2.3 workflow models
- the required ACE-Step workflow dependencies

Prompt2MTV can use bundled `imageio-ffmpeg` support inside the packaged build, so normal users do not need to manually install FFmpeg just to get the app running.

## Typical Workflow

1. Launch Prompt2MTV.
2. Create or open a project.
3. Confirm runtime paths and workflow settings.
4. Let Prompt2MTV detect or download missing models if needed.
5. Add prompts to the prompt queue.
6. Run scene generation through ComfyUI.
7. Review clips in the gallery.
8. Import your own video clips into the gallery if needed.
9. Stitch selected renders.
10. Generate music with ACE-Step or import your own audio track.
11. Merge the final soundtrack and video.

## Key Features

- LTX 2.3 text-to-video workflow integration
- prompt queue for batching multiple scenes
- project-based organization for repeatable work
- startup preflight and first-launch guidance
- runtime path configuration for ComfyUI root, launcher, model paths, and output location
- missing-model detection for video and music workflows
- automatic model download support through `model_manifest.json`
- media gallery for generated scenes, stitched outputs, and final music videos
- imported clip support with project-owned storage in the gallery
- imported audio support for merging without running music generation
- drag-and-drop video and audio import support in supported builds
- ACE-Step music generation workflow support
- expanded ACE-Step music controls for sampling, language, timing, seed, and advanced token settings
- per-project music settings and collapsible music workspace state persistence
- Windows ComfyUI launcher integration with hidden-by-default terminal and in-app show or hide toggle
- packaged Windows `.exe` and Inno Setup installer workflow
- About dialog and visible app version for installed builds

## Music Workspace Notes

- You can either generate music with the bundled ACE-Step workflow or import a finished audio file directly into the active project.
- Imported clips appear in their own gallery section so they can be stitched or used as the music reference clip.
- Music settings such as duration, BPM, sampler, scheduler, seed behavior, and advanced sampling values are saved with each project.
- On Windows, Prompt2MTV can launch ComfyUI with its terminal hidden. Use the `Show ComfyUI Terminal` button in the top toolbar on the Video tab if you want to inspect the live console.

## Important Reality Check

Prompt2MTV can remove most of the manual app setup.

Prompt2MTV cannot currently make the whole workflow zero-setup, because the overall system still depends on:

- a local ComfyUI install
- large external model files
- enough disk space for those model files
- maintenance of those external assets over time

So the intended user path is:

- install ComfyUI portable
- install Prompt2MTV with the setup `.exe`
- let Prompt2MTV detect and download missing workflow models where possible

## Developer Setup

Use this section only if you want to modify the code, build the app yourself, or contribute to the project.

### Clone the repository

```powershell
git clone https://github.com/RorriMaesu/Prompt2MTV.git
cd Prompt2MTV
```

### Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
pip install -r requirements.txt
```

### Run from source

```powershell
python ltx_queue_manager.py
```

## Build the Windows App

Build the packaged executable with:

```powershell
.\build_exe.bat
```

Output:

- `dist\Prompt2MTV\Prompt2MTV.exe`

Build the Windows installer with:

```powershell
.\build_installer.bat
```

Output:

- `dist_installer\Prompt2MTV-Setup-0.3.0.exe`

If `model_manifest.json` contains valid model sources, installed builds can download missing workflow models directly into the detected ComfyUI model folders.

## Repository Contents

- `ltx_queue_manager.py`: Main application entry point and UI logic
- `model_downloader.py`: Streamed model download helper with progress, resume support, and SHA-256 verification
- `video_ltx2_3_t2v.json`: Primary LTX 2.3 text-to-video workflow
- `ACE_Step_AI_Music_Generator_Workflow.json`: Music-generation workflow
- `model_manifest.json`: Required-model manifest for workflow auditing and automatic installation
- `requirements.txt`: Python dependencies for local development and packaging
- `Prompt2MTV.spec`: PyInstaller build definition
- `Prompt2MTV.iss`: Inno Setup installer definition
- `build_exe.bat`: Windows app build helper
- `build_installer.bat`: Windows installer build helper
- `Prompt2MTV.ico`: App and installer icon
- `Prompt2MTV_version_info.txt`: Windows executable version metadata

Generated media and project outputs are written to `outputs/` at runtime and are excluded from source control.

## Operational Notes

- Prompt2MTV communicates with a local ComfyUI instance, not a hosted backend
- packaged builds keep user settings and outputs in `%LOCALAPPDATA%\Prompt2MTV`
- source checkouts keep local runtime files such as `app_settings.json` and `app_state.json` out of version control
- if Prompt2MTV cannot find your ComfyUI root, launcher, or model directories, use `Project > Configure Runtime Paths`
- the installer and packaged app do not bundle ComfyUI itself or the required models

## Support / Donate

If Prompt2MTV has made your workflow faster, cleaner, or just less painful, consider supporting development.

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Support-FFDD00?logo=buymeacoffee&logoColor=000000)](https://buymeacoffee.com/rorrimaesu)
