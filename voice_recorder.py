import os
import sys
import time
import queue
import tempfile
import shutil
import threading
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk

# Optional dependencies for audio capture/file writing
try:
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False

class AudioRecorder:
    def __init__(self):
        self.recording = False
        self.audio_data = []
        self.stream = None
        self.sample_rate = 24000
        self.volume_queue = queue.Queue()

    def start_recording(self, device_index=None, samplerate=24000):
        if not AUDIO_LIBS_AVAILABLE:
            raise ImportError("Audio libraries (sounddevice, soundfile, numpy) are not installed.")
        
        self.sample_rate = samplerate
        self.audio_data = []
        self.recording = True
        
        def callback(indata, frames, time_info, status):
            if self.recording:
                self.audio_data.append(indata.copy())
                # Calculate peak/RMS volume for the meter
                rms = np.sqrt(np.mean(indata**2))
                self.volume_queue.put(rms)

        self.stream = sd.InputStream(
            device=device_index,
            samplerate=samplerate,
            channels=1,
            callback=callback
        )
        self.stream.start()

    def stop_recording(self, output_path):
        if not self.recording:
            return False
            
        self.recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            
        if self.audio_data:
            merged = np.concatenate(self.audio_data, axis=0)
            sf.write(output_path, merged, self.sample_rate)
            return True
        return False


class VoiceCloningSetupWizard(tk.Toplevel):
    def __init__(self, parent, vibevoice_dir, python_exe, active_speaker="user", on_success_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.vibevoice_dir = vibevoice_dir
        self.python_exe = python_exe
        self.active_speaker = active_speaker or "user"
        self.on_success_callback = on_success_callback
        
        self.title("Voice Cloning Setup Wizard")
        self.geometry("700x820")
        self.resizable(False, False)
        self.grab_set()  # Make dialog modal
        
        self.profile_var = tk.StringVar()
        self.speaker_name_var = tk.StringVar(value="user")
        self.recorder = AudioRecorder()
        self.recording_thread = None
        self.verification_thread = None
        self.test_output_dir = os.path.join(tempfile.gettempdir(), "prompt2mtv_test")
        os.makedirs(self.test_output_dir, exist_ok=True)
        self.test_script_path = os.path.join(self.test_output_dir, "test_verification.txt")
        self.test_audio_path = os.path.join(self.test_output_dir, "test_verification_generated.wav")
        
        # Scan profiles
        self.profiles = self._scan_existing_profiles()
        
        self.mic_devices = []
        self.selected_device_var = tk.StringVar()
        
        self._init_ui()
        self._load_devices()

    def _init_ui(self):
        # Header banner
        header_frame = tk.Frame(self, bg="#1e293b", height=80)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        header_lbl = tk.Label(
            header_frame,
            text="🎙️ VibeVoice Voice Cloning Setup",
            font=("Segoe UI", 16, "bold"),
            fg="white",
            bg="#1e293b"
        )
        header_lbl.pack(pady=(12, 2), padx=20, anchor="w")
        
        sub_lbl = tk.Label(
            header_frame,
            text="Record or import a short sample of your voice to train the local model.",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#1e293b"
        )
        sub_lbl.pack(padx=20, anchor="w")

        # Footer Actions (PACK THIS FIRST BEFORE main_frame SO IT CLAIMS THE BOTTOM SPACE!)
        footer = tk.Frame(self, bg="#f8fafc", height=60, bd=1, relief=tk.SUNKEN)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)

        self.cancel_btn = tk.Button(footer, text="Cancel", command=self.destroy, font=("Segoe UI", 10))
        self.cancel_btn.pack(side=tk.RIGHT, padx=15, pady=15)

        self.done_btn = tk.Button(
            footer,
            text="Save and Complete",
            font=("Segoe UI", 10, "bold"),
            bg="#22c55e",
            fg="white",
            state=tk.DISABLED,
            command=self._save_and_complete
        )
        self.done_btn.pack(side=tk.RIGHT, pady=15)

        # Main Scrollable / Form Frame
        main_frame = tk.Frame(self, padx=20, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        if not AUDIO_LIBS_AVAILABLE:
            err_lbl = tk.Label(
                main_frame,
                text="❌ Required audio dependencies (sounddevice, soundfile, numpy) are missing!\n"
                     "Please run the pip install step in the settings tab first.",
                fg="#ef4444",
                font=("Segoe UI", 11, "bold"),
                justify=tk.LEFT
            )
            err_lbl.pack(pady=20)
            return

        # Voice Profile Selection
        profile_lbl = tk.Label(main_frame, text="Select Voice Profile:", font=("Segoe UI", 10, "bold"))
        profile_lbl.pack(anchor="w", pady=(0, 5))
        
        self.profile_combo = ttk.Combobox(main_frame, textvariable=self.profile_var, state="readonly", width=70)
        self.profile_combo.pack(anchor="w", pady=(0, 8))
        
        combo_vals = self.profiles + ["Create New Profile..."]
        self.profile_combo.config(values=combo_vals)
        self.profile_combo.bind("<<ComboboxSelected>>", self._on_profile_selected)
        
        if self.active_speaker in self.profiles:
            self.profile_var.set(self.active_speaker)
            self.speaker_name_var.set(self.active_speaker)
        else:
            self.profile_var.set("Create New Profile...")
            self.speaker_name_var.set(self.active_speaker or "")

        # Device Selection
        device_lbl = tk.Label(main_frame, text="Select Recording Microphone:", font=("Segoe UI", 10, "bold"))
        device_lbl.pack(anchor="w", pady=(0, 5))
        
        self.device_combo = ttk.Combobox(main_frame, textvariable=self.selected_device_var, state="readonly", width=70)
        self.device_combo.pack(anchor="w", pady=(0, 8))

        # Speaker Name Input
        spk_lbl = tk.Label(main_frame, text="Speaker Name (Custom voice identifier):", font=("Segoe UI", 10, "bold"))
        spk_lbl.pack(anchor="w", pady=(0, 5))
        
        self.speaker_name_entry = tk.Entry(main_frame, textvariable=self.speaker_name_var, font=("Segoe UI", 10))
        self.speaker_name_entry.pack(anchor="w", fill=tk.X, pady=(0, 8))

        # Reading Passage Card
        passage_card = tk.LabelFrame(main_frame, text=" Reading Passage (Speak clearly for 10-15 seconds) ", padx=15, pady=8, font=("Segoe UI", 9, "bold"))
        passage_card.pack(fill=tk.X, pady=(0, 8))
        
        passage_text = (
            "\"Antigravity is a powerful AI coding assistant designed by Google DeepMind. "
            "We are pair programming to create amazing tools, generating videos, music, and voiceovers. "
            "This cloned voice sounds clear and natural, perfect for video production!\""
        )
        passage_lbl = tk.Label(
            passage_card,
            text=passage_text,
            font=("Segoe UI", 10, "italic"),
            fg="#0f172a",
            wraplength=600,
            justify=tk.LEFT
        )
        passage_lbl.pack(anchor="w")

        # Recording Section (Controls & Visualizer)
        record_section = tk.Frame(main_frame)
        record_section.pack(fill=tk.X, pady=(0, 8))
        
        self.record_btn = tk.Button(
            record_section,
            text="🔴 Start Recording",
            font=("Segoe UI", 11, "bold"),
            bg="#ef4444",
            fg="white",
            padx=15,
            pady=5,
            command=self._toggle_recording
        )
        self.record_btn.pack(side=tk.LEFT, padx=(0, 15))

        self.play_btn = tk.Button(
            record_section,
            text="▶️ Play Sample",
            font=("Segoe UI", 10),
            state=tk.DISABLED,
            command=self._play_recorded_sample
        )
        self.play_btn.pack(side=tk.LEFT, padx=(0, 15))

        self.import_btn = tk.Button(
            record_section,
            text="📂 Import WAV File",
            font=("Segoe UI", 10),
            command=self._import_wav_file
        )
        self.import_btn.pack(side=tk.LEFT)

        # Volume Meter & Timer
        self.meter_canvas = tk.Canvas(main_frame, height=15, bg="#e2e8f0", bd=0, highlightthickness=0)
        self.meter_canvas.pack(fill=tk.X, pady=(0, 6))
        
        self.timer_lbl = tk.Label(main_frame, text="Duration: 0.0s", font=("Segoe UI", 9, "bold"), fg="#64748b")
        self.timer_lbl.pack(anchor="w")

        # Divider
        divider = ttk.Separator(main_frame, orient="horizontal")
        divider.pack(fill=tk.X, pady=8)

        # Verification Section
        verify_lbl = tk.Label(main_frame, text="Step 2: Model Verification Test", font=("Segoe UI", 10, "bold"))
        verify_lbl.pack(anchor="w", pady=(0, 4))

        # Custom verification text area
        custom_txt_lbl = tk.Label(main_frame, text="Test Script (Type custom text to test the cloned voice):", font=("Segoe UI", 9))
        custom_txt_lbl.pack(anchor="w", pady=(0, 2))
        
        self.custom_verify_entry = tk.Entry(main_frame, font=("Segoe UI", 10))
        self.custom_verify_entry.pack(anchor="w", fill=tk.X, pady=(0, 6))
        self.custom_verify_entry.insert(0, "Hello! Verification test of my cloned voice is successful!")

        self.verify_btn = tk.Button(
            main_frame,
            text="⚙️ Run Verification (Generates Cloned Speech)",
            font=("Segoe UI", 10, "bold"),
            bg="#3b82f6",
            fg="white",
            state=tk.DISABLED,
            command=self._run_verification
        )
        self.verify_btn.pack(anchor="w", pady=(0, 6))

        self.verify_progress = ttk.Progressbar(main_frame, mode="determinate", length=600)
        self.verify_progress.pack(anchor="w", fill=tk.X, pady=(0, 6))

        self.status_lbl = tk.Label(main_frame, text="Status: Ready to record.", font=("Segoe UI", 9), fg="#475569")
        self.status_lbl.pack(anchor="w", pady=(0, 8))

        self.test_play_btn = tk.Button(
            main_frame,
            text="🔊 Listen to Cloned Test Voice",
            font=("Segoe UI", 10),
            state=tk.DISABLED,
            command=self._play_test_voice
        )
        self.test_play_btn.pack(anchor="w")
        
        # Initialize widget states based on loaded active speaker
        self._on_profile_selected()

    def _scan_existing_profiles(self):
        voices_dir = os.path.normpath(os.path.join(self.vibevoice_dir, "demo", "voices"))
        if not os.path.exists(voices_dir):
            return ["user"]
            
        profiles = []
        try:
            for f in os.listdir(voices_dir):
                if f.lower().endswith(".wav") and f.startswith("en-") and f.endswith("_voice.wav"):
                    name = f[3:-10]
                    if name:
                        profiles.append(name)
        except Exception as e:
            print(f"Error scanning voice profiles: {e}")
            
        if "user" not in profiles:
            profiles.insert(0, "user")
        return sorted(list(set(profiles)))

    def _on_profile_selected(self, _event=None):
        selection = self.profile_var.get()
        if selection == "Create New Profile...":
            self.speaker_name_entry.config(state=tk.NORMAL)
            self.speaker_name_var.set("")
            
            # Disable testing / complete actions until recorded/imported
            self.play_btn.config(state=tk.DISABLED)
            self.verify_btn.config(state=tk.DISABLED)
            self.test_play_btn.config(state=tk.DISABLED)
            self.done_btn.config(state=tk.DISABLED)
            self.status_lbl.config(text="Status: Enter a Speaker Name and record or import your voice.")
        else:
            self.speaker_name_var.set(selection)
            self.speaker_name_entry.config(state=tk.DISABLED)
            
            # If the reference WAV file exists, enable actions
            if os.path.exists(self.recorded_path):
                self.play_btn.config(state=tk.NORMAL)
                self.verify_btn.config(state=tk.NORMAL)
                self.done_btn.config(state=tk.NORMAL)
                
                # Enable playback if test generated audio exists
                if os.path.exists(self.test_audio_path):
                    self.test_play_btn.config(state=tk.NORMAL)
                else:
                    self.test_play_btn.config(state=tk.DISABLED)
                    
                self.status_lbl.config(text=f"Status: Profile '{selection}' loaded. Ready to test or save.")
            else:
                self.play_btn.config(state=tk.DISABLED)
                self.verify_btn.config(state=tk.DISABLED)
                self.test_play_btn.config(state=tk.DISABLED)
                self.done_btn.config(state=tk.DISABLED)
                self.status_lbl.config(text=f"Status: Profile '{selection}' reference file missing. Please record or import.")

    def _load_devices(self):
        if not AUDIO_LIBS_AVAILABLE:
            return
        
        try:
            devices = sd.query_devices()
            self.mic_devices = []
            default_index = -1
            
            for i, dev in enumerate(devices):
                if dev.get("max_input_channels", 0) > 0:
                    device_name = f"{i}: {dev.get('name')}"
                    self.mic_devices.append((i, device_name))
            
            combo_vals = [d[1] for d in self.mic_devices]
            self.device_combo.config(values=combo_vals)
            
            default_device = sd.default.device[0]
            for index, (i, name) in enumerate(self.mic_devices):
                if i == default_device:
                    self.device_combo.current(index)
                    break
            else:
                if combo_vals:
                    self.device_combo.current(0)
        except Exception as e:
            print(f"Error listing audio input devices: {e}")

    def _toggle_recording(self):
        if self.recorder.recording:
            # Stop recording
            self.recorder.stop_recording(self.recorded_path)
            self.record_btn.config(text="🔴 Start Recording", bg="#ef4444")
            self.play_btn.config(state=tk.NORMAL)
            self.verify_btn.config(state=tk.NORMAL)
            self.done_btn.config(state=tk.NORMAL)
            self.status_lbl.config(text="Status: Recording saved. Ready for verification.")
            self._update_volume_meter(0.0)
        else:
            # Get selected device index
            selected = self.selected_device_var.get()
            device_index = None
            if selected:
                try:
                    device_index = int(selected.split(":")[0])
                except ValueError:
                    pass
            
            # Start recording
            try:
                # Ensure parent directory exists
                os.makedirs(os.path.dirname(self.recorded_path), exist_ok=True)
                
                self.recorder.start_recording(device_index=device_index)
                self.record_btn.config(text="⏹️ Stop Recording", bg="#1e293b")
                self.play_btn.config(state=tk.DISABLED)
                self.verify_btn.config(state=tk.DISABLED)
                self.done_btn.config(state=tk.DISABLED)
                self.status_lbl.config(text="Status: Recording voice clip...")
                
                self.timer_start = time.time()
                self._update_recording_ui()
            except Exception as e:
                messagebox.showerror("Error", f"Could not start recording: {e}")

    def _update_recording_ui(self):
        if not self.recorder.recording:
            return
            
        elapsed = time.time() - self.timer_start
        self.timer_lbl.config(text=f"Duration: {elapsed:.1f}s (Click Stop Recording when finished reading)")
        
        # Pull volume levels
        vol = 0.0
        while not self.recorder.volume_queue.empty():
            vol = self.recorder.volume_queue.get()
        
        self._update_volume_meter(vol)
        
        self._recording_after_id = self.after(100, self._update_recording_ui)

    def _update_volume_meter(self, level):
        self.meter_canvas.delete("all")
        # level is RMS, typically between 0.0 and 0.5. Normalize to width
        width = self.meter_canvas.winfo_width()
        meter_width = min(int((level * 4.0) * width), width)
        
        # Draw gradient block
        color = "#22c55e" # Green
        if level > 0.15:
            color = "#eab308" # Yellow
        if level > 0.25:
            color = "#ef4444" # Red
            
        self.meter_canvas.create_rectangle(0, 0, meter_width, 15, fill=color, outline="")

    def _play_recorded_sample(self):
        if not AUDIO_LIBS_AVAILABLE or not os.path.exists(self.recorded_path):
            return
        
        def play_thread():
            try:
                data, fs = sf.read(self.recorded_path)
                sd.play(data, fs)
                sd.wait()
            except Exception as e:
                print(f"Error during playback: {e}")
                
        threading.Thread(target=play_thread, daemon=True).start()

    def _import_wav_file(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select Reference Voice WAV File",
            filetypes=[("WAV files", "*.wav")]
        )
        if file_path:
            try:
                os.makedirs(os.path.dirname(self.recorded_path), exist_ok=True)
                shutil.copy(file_path, self.recorded_path)
                self.play_btn.config(state=tk.NORMAL)
                self.verify_btn.config(state=tk.NORMAL)
                self.done_btn.config(state=tk.NORMAL)
                self.status_lbl.config(text="Status: Reference voice imported. Ready for verification.")
                messagebox.showinfo("Success", f"Imported voice sample: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy file: {e}")

    def _run_verification(self):
        if self.verification_thread and self.verification_thread.is_alive():
            return
            
        # Evaluate speaker name on main thread to avoid Tkinter thread safety issues
        speaker = self.speaker_name_var.get().strip() or "user"
        speaker = "".join(c for c in speaker if c.isalnum() or c in ("_", "-"))
        if not speaker:
            speaker = "user"

        # Create a tiny verification test script
        custom_text = self.custom_verify_entry.get().strip()
        if not custom_text:
            custom_text = "Hello! Verification test of my cloned voice is successful!"
        try:
            with open(self.test_script_path, 'w', encoding='utf-8') as f:
                f.write(f"Speaker 1: {custom_text}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write verification script: {e}")
            return
            
        self.verify_progress.config(value=0)
        self.status_lbl.config(text="Status: Launching VibeVoice test inference... (This may take a moment)")
        self.verify_btn.config(state=tk.DISABLED)
        
        self.verify_result = {"status": "running", "error": ""}
        
        def run_thread():
            cmd = [
                self.python_exe,
                os.path.join(self.vibevoice_dir, "demo", "inference_from_file.py"),
                "--model_path", "microsoft/VibeVoice-1.5b",
                "--txt_path", self.test_script_path,
                "--speaker_names", speaker,
                "--output_dir", self.test_output_dir,
                "--cfg_scale", "1.3"
            ]
            
            try:
                # Execute subprocess
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=self.vibevoice_dir,
                    text=True
                )
                
                stdout, stderr = process.communicate()
                
                if process.returncode == 0 and os.path.exists(self.test_audio_path):
                    self.verify_result["status"] = "success"
                else:
                    self.verify_result["status"] = "failure"
                    self.verify_result["error"] = stderr or stdout
            except Exception as ex:
                self.verify_result["status"] = "failure"
                self.verify_result["error"] = str(ex)
                
        self.verification_thread = threading.Thread(target=run_thread, daemon=True)
        self.verification_thread.start()
        self._poll_verification_thread()

    def _poll_verification_thread(self):
        if not self.verification_thread or not self.verification_thread.is_alive():
            status = self.verify_result["status"]
            if status == "success":
                self._on_verification_success()
            else:
                self._on_verification_failure(self.verify_result["error"])
            return
            
        # Increment progress bar slightly to show activity
        val = self.verify_progress["value"]
        if val < 90:
            self.verify_progress.config(value=val + 2)
            
        self._poll_after_id = self.after(200, self._poll_verification_thread)

    def _on_verification_success(self):
        self.verify_progress.config(value=100)
        self.status_lbl.config(text="Status: Verification successful! Cloned speech generated.")
        self.test_play_btn.config(state=tk.NORMAL)
        self.done_btn.config(state=tk.NORMAL)
        self.verify_btn.config(state=tk.NORMAL)
        messagebox.showinfo("Verification Success", "Model successfully cloned your voice and generated a test greeting!")

    def _on_verification_failure(self, error_message):
        self.verify_progress.config(value=0)
        self.status_lbl.config(text="Status: Verification failed. Review errors.")
        self.verify_btn.config(state=tk.NORMAL)
        
        # Show detailed error dialog
        err_win = tk.Toplevel(self)
        err_win.title("VibeVoice Verification Error")
        err_win.geometry("500x400")
        
        lbl = tk.Label(err_win, text="VibeVoice process failed with the following traceback:", font=("Segoe UI", 10, "bold"), fg="#ef4444")
        lbl.pack(anchor="w", padx=15, pady=(15, 5))
        
        txt = tk.Text(err_win, wrap=tk.WORD, font=("Consolas", 9))
        txt.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        txt.insert(tk.END, error_message)
        txt.config(state=tk.DISABLED)

    def _play_test_voice(self):
        if not AUDIO_LIBS_AVAILABLE or not os.path.exists(self.test_audio_path):
            return
        
        def play_thread():
            try:
                data, fs = sf.read(self.test_audio_path)
                sd.play(data, fs)
                sd.wait()
            except Exception as e:
                print(f"Error playing verification test wav: {e}")
                
        threading.Thread(target=play_thread, daemon=True).start()

    def _save_and_complete(self):
        if self.on_success_callback:
            self.on_success_callback(self.recorded_path)
        self.destroy()

    def destroy(self):
        if hasattr(self, "_poll_after_id") and self._poll_after_id:
            try:
                self.after_cancel(self._poll_after_id)
            except Exception:
                pass
            self._poll_after_id = None
        if hasattr(self, "_recording_after_id") and self._recording_after_id:
            try:
                self.after_cancel(self._recording_after_id)
            except Exception:
                pass
            self._recording_after_id = None
        super().destroy()

    @property
    def recorded_path(self):
        speaker = self.speaker_name_var.get().strip() or "user"
        speaker = "".join(c for c in speaker if c.isalnum() or c in ("_", "-"))
        if not speaker:
            speaker = "user"
        return os.path.normpath(os.path.join(self.vibevoice_dir, "demo", "voices", f"en-{speaker}_voice.wav"))
