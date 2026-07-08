param(
    [string]$InstallerPath,
    [string]$InstallDir = "$env:LOCALAPPDATA\Programs\Prompt2MTV"
)

$ErrorActionPreference = 'Stop'

if (-not $InstallerPath) {
    $searchDir = Join-Path $PSScriptRoot '..\dist_installer'
    if (Test-Path $searchDir) {
        $latestInstaller = Get-ChildItem (Join-Path $searchDir 'Prompt2MTV-Setup-*.exe') -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1
        if ($latestInstaller) {
            $InstallerPath = $latestInstaller.FullName
        }
    }
}

if (-not $InstallerPath) {
    $InstallerPath = Join-Path $PSScriptRoot '..\dist_installer\Prompt2MTV-Setup-4.0.0.exe'
}

function Get-Prompt2MTVUninstallEntry {
    $roots = @(
        'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
        'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
        'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*'
    )

    foreach ($root in $roots) {
        $entry = Get-ItemProperty -Path $root -ErrorAction SilentlyContinue |
            Where-Object { $_.PSChildName -eq '{8F6A8C07-EB70-4F5E-AF2F-0C7AA0F11CF1}_is1' } |
            Select-Object -First 1
        if ($entry) {
            return $entry
        }
    }

    return $null
}

function Invoke-Prompt2MTVManagedUninstall {
    param([Parameter(Mandatory = $true)]$Entry)

    $uninstallString = $Entry.UninstallString
    if (-not $uninstallString) {
        return
    }

    if ($uninstallString -match '^("(?<exe>[^"]+)"|(?<exe>\S+))(\s+(?<args>.*))?$') {
        $exePath = if ($Matches.exe) { $Matches.exe } else { $Matches['exe'] }
        $args = $Matches.args
        $silentArgs = if ($args) { "$args /VERYSILENT /SUPPRESSMSGBOXES /NORESTART" } else { '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART' }
        if (Test-Path $exePath) {
            Start-Process -FilePath $exePath -ArgumentList $silentArgs -Wait
        } else {
            Write-Output "Orphaned registry uninstall entry found at $($Entry.PSPath)."
            Write-Output "Attempting to clean up orphaned registry entry..."
            try {
                Remove-Item -Path $Entry.PSPath -Force -ErrorAction Stop
                Write-Output "Successfully removed orphaned registry entry."
            } catch {
                Write-Warning "Could not remove registry entry. If the installer fails, please run PowerShell as Administrator and run the script again."
            }
        }
    }
}

function Remove-Prompt2MTVUnmanagedInstall {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (Test-Path $Path) {
        Remove-Item $Path -Recurse -Force
    }
}

if (-not (Test-Path $InstallerPath)) {
    throw "Installer not found: $InstallerPath"
}

Get-Process Prompt2MTV -ErrorAction SilentlyContinue | Stop-Process -Force

$uninstallEntry = Get-Prompt2MTVUninstallEntry
if ($uninstallEntry) {
    Invoke-Prompt2MTVManagedUninstall -Entry $uninstallEntry
} else {
    Remove-Prompt2MTVUnmanagedInstall -Path $InstallDir
}

Start-Process -FilePath $InstallerPath -ArgumentList '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', '/SP-' -Wait

$installedExe = Join-Path $InstallDir 'Prompt2MTV.exe'
if (-not (Test-Path $installedExe)) {
    throw "Prompt2MTV install did not produce expected executable: $installedExe"
}

$desktop = [Environment]::GetFolderPath('Desktop')
$shortcutPath = Join-Path $desktop 'Prompt2MTV.lnk'
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $installedExe
$shortcut.WorkingDirectory = Split-Path $installedExe
$shortcut.IconLocation = "$installedExe,0"
$shortcut.Description = 'Prompt2MTV'
$shortcut.Save()

Write-Output "Installed: $installedExe"
Write-Output "Shortcut:  $shortcutPath"