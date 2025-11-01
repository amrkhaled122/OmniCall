; OmniCall Installer Script for Inno Setup
; Download Inno Setup from: https://jrsoftware.org/isdl.php
; To build: Right-click this file and select "Compile"

#define MyAppName "OmniCall"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Amr Khaled Abdelbaky"
#define MyAppURL "https://github.com/amrkhaled122/OmniCall"
#define MyAppExeName "OmniCall.exe"

[Setup]
AppId={{8A5F3C2D-9B4E-4F1A-8D2C-6E7F8A9B0C1D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
; Remove next line to allow installation to other folders
DisableProgramGroupPage=yes
; License file (will be shown during install)
LicenseFile=LICENSE
; Output settings
OutputDir=installer_output
OutputBaseFilename=OmniCall-Setup-v{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
; Windows version requirement
MinVersion=10.0
; Icon
SetupIconFile=pc_app\omnicall.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
; Privileges
PrivilegesRequired=lowest
; Styling
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkablealone
Name: "quicklaunchicon"; Description: "Pin to Taskbar"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkablealone

[Files]
; Main executable
Source: "dist\OmniCall\OmniCall.exe"; DestDir: "{app}"; Flags: ignoreversion
; Internal folder (hidden from user) - includes Accept.png and all dependencies
Source: "dist\OmniCall\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
; Documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu shortcut
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
; Desktop shortcut (optional)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
; Taskbar pin (Windows 10/11)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\User Pinned\TaskBar\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Option to run after install
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Optional: Check if already installed and offer to uninstall old version
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
  UninstallPath: String;
begin
  Result := True;
  
  // Check if app is already installed
  if RegQueryStringValue(HKLM, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{8A5F3C2D-9B4E-4F1A-8D2C-6E7F8A9B0C1D}_is1', 'UninstallString', UninstallPath) then
  begin
    if MsgBox('OmniCall is already installed. Do you want to uninstall the old version first?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      Exec(RemoveQuotes(UninstallPath), '/SILENT', '', SW_SHOW, ewWaitUntilTerminated, ResultCode);
    end;
  end;
end;
