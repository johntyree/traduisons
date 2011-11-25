; traduisons_installer.nsi
;

;--------------------------------

; The name of the installer
Name "Traduisons!"

; The file to write
OutFile "traduisons_installer.exe"

; The default installation directory
InstallDir $PROGRAMFILES\Traduisons

; The license file to be read
LicenseData LICENSE


;--------------------------------

; Pages

Page license
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
SectionEnd

Section "Uninstall"
  MessageBox MB_OKCANCEL "Uninstall Traduisons!?" IDOK do_uninstall IDCANCEL QuitNow
  do_uninstall:
	  Delete $INSTDIR\*
	  RMDir  $INSTDIR
	  Delete "$SMPROGRAMS\Traduisons!\*"
	  RMDir  "$SMPROGRAMS\Traduisons!"
  QuitNow:
      Quit
SectionEnd
