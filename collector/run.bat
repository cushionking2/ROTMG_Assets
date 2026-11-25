@echo off
rem Run the map collector. Npcap must be installed. Start this BEFORE you enter the game world.
setlocal
set ROOT=%~dp0..
for /d %%J in ("%ROOT%\work\jdk\jdk-*") do set JDK=%%J
cd /d "%~dp0"
"%JDK%\bin\java" -cp "build\MapCollector.jar;lib\*" MapCollector captures
pause
