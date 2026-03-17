![Prompt2MTV Logo](prompt2MTV_logo.jpg)

# Prompt2MTV

Prompt2MTV is a Windows desktop app for building end-to-end AI music videos with a local ComfyUI pipeline. It combines LTX 2.3 text-to-video generation, prompt queue management, project organization, gallery review, ACE-Step music generation, and final audio/video merging in one interface.

Current packaged release: `0.2.0`

The goal is simple: keep the entire prompt-to-music-video workflow in a single workspace so you can spend less time managing JSON files, output folders, and render handoffs, and more time iterating on actual creative direction.

## Start Here

If you just want to use Prompt2MTV, do **not** clone the repo and do **not** install Python.

For most Windows users, the easiest path is:

1. Install the official ComfyUI Windows portable build.
2. Install Prompt2MTV with the Prompt2MTV setup `.exe`.
3. Launch Prompt2MTV and point it at your ComfyUI folder if needed.

## Step 0: Install ComfyUI Portable First

Prompt2MTV depends on a local ComfyUI installation.

If you already have the Windows portable version of ComfyUI installed and working, skip to the next section.

If you do **not** have ComfyUI yet, install it first:

1. Open the official ComfyUI releases page:
	[https://github.com/Comfy-Org/ComfyUI/releases](https://github.com/Comfy-Org/ComfyUI/releases)
2. Download the Windows portable build that matches your hardware:
	- NVIDIA: [ComfyUI_windows_portable_nvidia.7z](https://github.com/comfyanonymous/ComfyUI/releases/latest/download/ComfyUI_windows_portable_nvidia.7z)
	- AMD: [ComfyUI_windows_portable_amd.7z](https://github.com/comfyanonymous/ComfyUI/releases/latest/download/ComfyUI_windows_portable_amd.7z)
3. Extract the `.7z` file.
	- Use [7-Zip](https://7-zip.org/) if Windows does not open it directly.
4. Put the extracted folder somewhere easy to find.
	- Example: `D:\ComfyUI`
5. Start ComfyUI once to confirm it opens correctly.
6. Close ComfyUI.

If Windows blocks the downloaded archive, right-click it, open `Properties`, and click `Unblock` before extracting.

If the portable NVIDIA build does not start, update your NVIDIA drivers first.

Use the Windows installer instead:

1. Open the [GitHub Releases page](https://github.com/RorriMaesu/Prompt2MTV/releases).
2. Download the latest `Prompt2MTV-Setup-<version>.exe` file.
3. Double-click the installer.
4. Finish the setup wizard.
5. Launch `Prompt2MTV` from your desktop or Start Menu.

The installer already includes the packaged app and its Python/runtime dependencies.

You do **not** need to manually install:

- Python
- `pip`
- virtual environments
- `requirements.txt`
- PyInstaller
- Inno Setup

You **do still need** a working local ComfyUI setup and the required models/workflows, because Prompt2MTV is a frontend for a local ComfyUI pipeline, not a cloud service.

## What Is Included

The Windows installer includes:

- Prompt2MTV desktop app
- packaged Python runtime for the app
- app dependencies bundled into the packaged build
- desktop and Start Menu shortcuts
- per-user settings/output folders under `%LOCALAPPDATA%\Prompt2MTV`

The Windows installer does **not** include:

- ComfyUI itself
- LTX models
- ACE-Step models or their external requirements
- custom checkpoints, LoRAs, or other large model assets

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

## What You Need Before First Launch

Before Prompt2MTV can actually render anything, make sure you have:

- Windows
- a working local ComfyUI installation, ideally the official Windows portable build
- the required LTX 2.3 workflow models
- the required ACE-Step music workflow dependencies

Prompt2MTV can use bundled `imageio-ffmpeg` support inside the packaged build, so normal users do not need to manually install FFmpeg just to get the app running.

On first launch, Prompt2MTV runs startup checks and tells you what is missing in plain language.

If `model_manifest.json` includes valid download URLs, Prompt2MTV can offer to download missing workflow models directly into the correct ComfyUI folders automatically.

If ComfyUI, model folders, or your launcher batch file live in a non-default location, open `Project > Configure Runtime Paths` inside the app.

## Repository Contents

- `ltx_queue_manager.py`: Main application entry point and UI logic.
- `model_downloader.py`: Streamed model download helper with progress, resume support, and SHA-256 verification.
- `video_ltx2_3_t2v.json`: Primary LTX 2.3 text-to-video workflow.
- `ACE_Step_AI_Music_Generator_Workflow.json`: Music-generation workflow.
- `model_manifest.json`: Required-model manifest for workflow auditing and optional automatic installation.
- `requirements.txt`: Python dependencies for local development and packaging.
- `Prompt2MTV.spec`: Versioned PyInstaller build definition.
- `Prompt2MTV.iss`: Versioned Inno Setup installer definition.
- `build_exe.bat`: Helper script for building the Windows app bundle.
- `build_installer.bat`: Helper script for rebuilding the app and compiling the installer.
- `Prompt2MTV.ico`: Windows application and installer icon.
- `Prompt2MTV_version_info.txt`: Windows executable version metadata.
- `prompt2MTV_logo.jpg`: Logo used in the project documentation.

Generated project data and media outputs are written to `outputs/` at runtime and are excluded from source control.

## Default Path Discovery

The app can auto-discover common ComfyUI layouts and also lets you configure paths inside the UI. Default discovery looks at common locations rooted around your ComfyUI install, including setups like:

- `D:\ComfyUI\ComfyUI\models`
- `D:\ComfyUI\models`

If your ComfyUI environment uses a different layout, use `Project > Configure Runtime Paths` after launch.

## Easiest Install For Normal Users

1. Install ComfyUI portable first if you do not already have it.
2. Open the [GitHub Releases page](https://github.com/RorriMaesu/Prompt2MTV/releases).
3. Download the newest `Prompt2MTV-Setup-<version>.exe`.
4. Run it.
5. Accept the default install options unless you have a reason not to.
6. Open Prompt2MTV from the created shortcut.

Expected installer filename example:

- `Prompt2MTV-Setup-0.2.0.exe`

After installation, Prompt2MTV stores user data in:

- `%LOCALAPPDATA%\Prompt2MTV\app_settings.json`
- `%LOCALAPPDATA%\Prompt2MTV\outputs\`

## First-Run Checklist

After launching Prompt2MTV for the first time:

1. Let the startup guidance finish.
2. If the app says it cannot find ComfyUI or your model folders, open `Project > Configure Runtime Paths`.
3. Point Prompt2MTV at your ComfyUI root folder if needed.
4. Point Prompt2MTV at your ComfyUI launcher `.bat` file if you want the app to start ComfyUI for you.
5. Confirm your model search paths.
6. Create or open a project and run validation before your first queue.

Typical example ComfyUI root folder:

- `D:\ComfyUI`

## Typical Workflow

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

## Developer Setup

Only use this section if you want to modify the code, build the executable yourself, or contribute to the project.

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

## Run From Source

### Start the Python version

```powershell
python ltx_queue_manager.py
```

### Build a Windows executable

After the virtual environment is created and dependencies are installed, you can build a Windows GUI executable with:

```powershell
.\build_exe.bat
```

The packaged app is written to `dist\Prompt2MTV\Prompt2MTV.exe`.

The build uses the checked-in `Prompt2MTV.spec` file so packaging settings stay versioned with the project.
The executable icon is sourced from `Prompt2MTV.ico`.

The executable still expects a local ComfyUI installation and models, but it now stores app settings in a per-user Windows app-data folder and can prompt for ComfyUI runtime paths on first launch.

If `model_manifest.json` contains valid model sources, installed builds can download missing workflow models directly into the detected ComfyUI model folders.

### Build a Windows installer

If you want a setup wizard that installs Prompt2MTV and creates shortcuts, install Inno Setup 6 and run:

```powershell
.\build_installer.bat
```

That script rebuilds the packaged app, then compiles the checked-in `Prompt2MTV.iss` installer script into the `dist_installer` folder.

The current installer output name is versioned, for example:

- `dist_installer\Prompt2MTV-Setup-0.2.0.exe`

The installer is designed for non-technical Windows users and creates Start Menu and desktop shortcuts.

## Operational Notes

- Prompt2MTV communicates with a local ComfyUI instance rather than a hosted backend.
- Generated files are stored inside project folders under `outputs/`.
- Source checkouts keep local runtime files such as `app_settings.json` and `app_state.json` outside version control.
- Packaged builds keep user settings and outputs in `%LOCALAPPDATA%\Prompt2MTV`.
- If Prompt2MTV cannot find your ComfyUI launcher, root folder, or model directories, open `Project > Configure Runtime Paths`.
- The Help menu includes an About dialog so users can confirm the installed version without opening Windows file properties.
- The installer and packaged app do not bundle ComfyUI itself or the required models.

## Important Reality Check

Prompt2MTV can be made "no manual app install" for users, and the installer now covers that part.

Prompt2MTV cannot currently be made "zero setup at all" unless you also ship and support:

- a full ComfyUI installation
- the required model files
- enough disk space for those assets
- a documented way to keep those external assets updated

So the README now separates these two ideas clearly:

- normal users should install Prompt2MTV with the setup `.exe`
- Prompt2MTV still depends on a local ComfyUI environment and models

## Support / Donate

If Prompt2MTV has made your workflow faster, cleaner, or just less painful, consider supporting development. It helps cover the boring but necessary parts of keeping a project like this alive: testing new workflow changes, polishing the UI, fixing breakages, and funding the late-night sessions that turn rough tools into reliable ones.

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Support-FFDD00?logo=buymeacoffee&logoColor=000000)](https://buymeacoffee.com/rorrimaesu)