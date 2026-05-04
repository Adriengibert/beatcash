; ============================================================
;  Beat Cash — Installateur Windows (Inno Setup 6+)
;  Génère : dist_installer\BeatCash_Setup.exe
; ============================================================

#define AppName     "Beat Cash"
#define AppVersion  "1.0"
#define AppExe      "BeatCash.exe"
#define AppPublisher "Beat Cash"
#define AppURL      ""

[Setup]
AppId={{E7A3C2D1-4F8B-4A2E-9C6D-B1F3A7E8D204}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
OutputDir=dist_installer
OutputBaseFilename=BeatCash_Setup
SetupIconFile=beat_cash.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardSizePercent=120
DisableWelcomePage=no
LicenseFile=
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\{#AppExe}
UninstallDisplayName={#AppName}
MinVersion=10.0
ArchitecturesInstallIn64BitMode=x64

; Splash / bannière
WizardImageFile=compiler:WizModernImage.bmp
WizardSmallImageFile=compiler:WizModernSmallImage.bmp

[Languages]
Name: "french";  MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
french.AppDescription=Publie tes vidéos sur YouTube et Instagram en un clic.
english.AppDescription=Publish your videos to YouTube and Instagram in one click.
french.SecretsNote=Important : pour utiliser YouTube, copie ton fichier client_secrets.json dans le dossier d'installation après l'installation.
english.SecretsNote=Important: to use YouTube, copy your client_secrets.json file into the installation folder after setup.

[Tasks]
Name: "desktopicon";    Description: "{cm:CreateDesktopIcon}";    GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
; Tous les fichiers de l'application compilée
Source: "dist\BeatCash\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; client_secrets.json si présent à côté du script de build
Source: "client_secrets.json"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
; Menu Démarrer
Name: "{group}\{#AppName}";               Filename: "{app}\{#AppExe}"; IconFilename: "{app}\{#AppExe}"
Name: "{group}\Désinstaller {#AppName}";  Filename: "{uninstallexe}"

; Bureau (si coché)
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon; IconFilename: "{app}\{#AppExe}"

; Barre de lancement rapide
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: quicklaunchicon

[Run]
; Proposer de lancer l'app à la fin de l'installation
Filename: "{app}\{#AppExe}"; \
  Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; \
  Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Supprimer aussi les fichiers générés à l'exécution
Type: files;        Name: "{app}\token.pickle"
Type: files;        Name: "{app}\seo_config.json"
Type: files;        Name: "{app}\instagram_session.json"
Type: filesandordirs; Name: "{app}"

[Code]
// ── Message de bienvenue personnalisé ────────────────────────────────
procedure InitializeWizard;
begin
  WizardForm.WelcomeLabel2.Caption :=
    'Beat Cash va être installé sur votre ordinateur.' + #13#10 + #13#10 +
    'Cette application vous permet de publier vos vidéos et' + #13#10 +
    'beats sur YouTube et Instagram en quelques clics.' + #13#10 + #13#10 +
    'Cliquez sur Suivant pour continuer.';
end;

// ── Message post-installation (client_secrets) ───────────────────────
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssDone then
  begin
    if not FileExists(ExpandConstant('{app}\client_secrets.json')) then
      MsgBox(
        'Installation terminée !' + #13#10 + #13#10 +
        'Pour activer l''upload YouTube :' + #13#10 +
        '1. Va sur console.cloud.google.com' + #13#10 +
        '2. Crée un projet et active l''API YouTube Data v3' + #13#10 +
        '3. Télécharge client_secrets.json' + #13#10 +
        '4. Copie-le dans : ' + ExpandConstant('{app}'),
        mbInformation, MB_OK
      );
  end;
end;
