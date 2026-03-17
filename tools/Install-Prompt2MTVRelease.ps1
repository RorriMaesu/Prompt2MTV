param(
    [string]$InstallerPath = (Join-Path $PSScriptRoot '..\dist_installer\Prompt2MTV-Setup-0.3.0.exe'),
    [string]$InstallDir = "$env:LOCALAPPDATA\Programs\Prompt2MTV"
)

$ErrorActionPreference = 'Stop'

function Get-Prompt2MTVUninstallEntry {
    $roots = @(
        'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
        'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
        'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*'
    )

    foreach ($root in $roots) {
        $entry = Get-ItemProperty -Path $root -ErrorAction SilentlyContinue |
            Where-Object { $_.DisplayName -eq 'Prompt2MTV' } |
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
        Start-Process -FilePath $exePath -ArgumentList $silentArgs -Wait
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