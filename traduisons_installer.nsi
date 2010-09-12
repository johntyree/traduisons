; traduisons_install.nsi
;

;--------------------------------

; The name of the installer
Name "Traduisons!"

; The file to write
OutFile "traduisons_installer.exe"

; The default installation directory
InstallDir $PROGRAMFILES\Traduisons

;--------------------------------

; Pages

Page directory
Page instfiles

;--------------------------------


Section "Install"
  ; Set output path to the installation directory.
  SetOutPath $INSTDIR
  
  ; Put files there
  File /r dist\*
  WriteUninstaller Uninst.exe

  ; Add startmenu links
  CreateDirectory "$SMPROGRAMS\Traduisons!"
  CreateShortCut  "$SMPROGRAMS\Traduisons!\Traduisons!.lnk" "$INSTDIR\traduisons.exe"
  CreateShortCut  "$SMPROGRAMS\Traduisons!\Uninstall.lnk" "$INSTDIR\Uninst.exe"
SectionEnd ; end the section

Section "Uninstall"
  Delete $INSTDIR\*
  RMDir  $INSTDIR
  Delete "$SMPROGRAMS\Traduisons!\*"
  RMDir  "$SMPROGRAMS\Traduisons!"
SectionEnd
