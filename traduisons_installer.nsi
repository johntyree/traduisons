; traduisons_install.nsi
;
; This script is perhaps one of the simplest NSIs you can make. All of the
; optional settings are left to their default settings. The installer simply 
; prompts the user asking them where to install, and drops a copy of example1.nsi
; there. 

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
; SEE for what is supposed to happen here
; http://nsis.sourceforge.net/Docs/Chapter4.html#4.9.4
  MB_OKCANCEL "Uninstall Traduisons!?" IDOK do_uninstall IDCANCEL Quit
  do_uninstall:
	  Delete $INSTDIR\*
	  RMDir  $INSTDIR
	  Delete "$SMPROGRAMS\Traduisons!\*"
	  RMDir  "$SMPROGRAMS\Traduisons!"
SectionEnd
