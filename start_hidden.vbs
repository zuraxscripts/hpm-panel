' HMP Panel - Hidden startup script
' Runs the panel in the background without a visible console window

Dim objShell, strScriptPath
Set objShell = CreateObject("WScript.Shell")

' Get the directory where this script is located
strScriptPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Run start.bat hidden (0 = hidden window)
objShell.Run chr(34) & strScriptPath & "\start.bat" & chr(34), 0, False

Set objShell = Nothing
