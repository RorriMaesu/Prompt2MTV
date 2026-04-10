#define MyAppName "Prompt2MTV"
#define MyAppVersion "1.2.0"
#define MyAppPublisher "Prompt2MTV"
#define MyAppTagline "Local AI Music Video Studio"
#define MyAppURL "https://buymeacoffee.com/rorrimaesu"
#define MyAppExeName "Prompt2MTV.exe"
#ifndef MyAppDistDir
#define MyAppDistDir "dist\\Prompt2MTV"
#endif
#ifndef MyAppOutputDir
#define MyAppOutputDir "dist_installer"
#endif

[Setup]
AppId={{8F6A8C07-EB70-4F5E-AF2F-0C7AA0F11CF1}
AppName={#MyAppName}
AppVerName={#MyAppName} {#MyAppVersion}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppComments={#MyAppTagline}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
Compression=lzma
SolidCompression=yes
WizardStyle=modern
OutputDir={#MyAppOutputDir}
OutputBaseFilename=Prompt2MTV-Setup-{#MyAppVersion}
SetupIconFile=Prompt2MTV.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Setup Wizard
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
VersionInfoTextVersion={#MyAppVersion}
WizardImageStretch=no
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[InstallDelete]
Type: filesandordirs; Name: "{app}\*"

[Files]
Source: "{#MyAppDistDir}\*"; DestDir: "{app}"; Excludes: "_internal\\bundled_models\\*"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Messages]
WelcomeLabel1=Welcome to the [name] Setup Wizard
WelcomeLabel2=This installer sets up Prompt2MTV, a local AI music video studio for ComfyUI-based scene generation, music generation, and final merge workflows.
FinishedHeadingLabel=Prompt2MTV setup is complete
FinishedLabel=Prompt2MTV has been installed successfully. Launch it now to review runtime paths and confirm your local ComfyUI environment.

[Code]
function GetUninstallString(): String;
var
  sUnInstPath: String;
  sUnInstallString: String;
begin
  sUnInstPath := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{8F6A8C07-EB70-4F5E-AF2F-0C7AA0F11CF1}_is1';
  sUnInstallString := '';
  if not RegQueryStringValue(HKLM, sUnInstPath, 'UninstallString', sUnInstallString) then
    RegQueryStringValue(HKCU, sUnInstPath, 'UninstallString', sUnInstallString);
  Result := sUnInstallString;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  sUnInstallString: String;
  iResultCode: Integer;
begin
  Result := '';
  sUnInstallString := GetUninstallString();
  if sUnInstallString <> '' then
  begin
    sUnInstallString := RemoveQuotes(sUnInstallString);
    Exec(sUnInstallString, '/VERYSILENT /NORESTART /SUPPRESSMSGBOXES', '', SW_HIDE, ewWaitUntilTerminated, iResultCode);
  end;
end;