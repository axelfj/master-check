; Inno Setup script for the Windows installer. CI passes the version:
;   iscc /DAppVersion=0.1.0 installer\windows.iss
#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
AppId={{6F1E2B0A-4C3D-4E8A-9B61-2D7C5A1F3E01}
AppName=Master Check
AppVersion={#AppVersion}
AppPublisher=ROMMUSER
AppPublisherURL=https://github.com/axelfj/master-check
DefaultDirName={autopf}\Master Check
DefaultGroupName=Master Check
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
LicenseFile=..\LICENSE
OutputDir=Output
OutputBaseFilename=MasterCheck-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\MasterCheck.exe

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\MasterCheck\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Master Check"; Filename: "{app}\MasterCheck.exe"
Name: "{group}\Uninstall Master Check"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Master Check"; Filename: "{app}\MasterCheck.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\MasterCheck.exe"; Description: "{cm:LaunchProgram,Master Check}"; Flags: nowait postinstall skipifsilent
