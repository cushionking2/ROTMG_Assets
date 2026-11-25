@echo off
rem Build the map collector. Uses the JDK in work\jdk and the RealmShark source in research.
setlocal
set ROOT=%~dp0..
for /d %%J in ("%ROOT%\work\jdk\jdk-*") do set JDK=%%J
set LIBS=%~dp0lib\*
if exist "%~dp0build" rmdir /s /q "%~dp0build"
mkdir "%~dp0build\classes"
"%JDK%\bin\javac" -nowarn -encoding UTF-8 --release 8 -cp "%LIBS%" -sourcepath "%ROOT%\research\X-com_RealmShark\src\main\java" -d "%~dp0build\classes" "%~dp0src\MapCollector.java"
if errorlevel 1 exit /b 1
"%JDK%\bin\jar" cfe "%~dp0build\MapCollector.jar" MapCollector -C "%~dp0build\classes" .
echo Built %~dp0build\MapCollector.jar
