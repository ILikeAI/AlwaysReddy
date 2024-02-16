@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

:: Set the FFmpeg download URL
SET "FFMPEG_URL=https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

:: Set the installation directory
SET "INSTALL_DIR=%ProgramFiles%\FFmpeg"

:: Create the installation directory
IF NOT EXIST "!INSTALL_DIR!" (
    mkdir "!INSTALL_DIR!"
)

:: Download FFmpeg
echo Downloading FFmpeg...
powershell -Command "(New-Object System.Net.WebClient).DownloadFile('!FFMPEG_URL!', 'ffmpeg.zip')"

:: Extract the downloaded zip file
echo Extracting files...
powershell -Command "Expand-Archive -Path ffmpeg.zip -DestinationPath '!INSTALL_DIR!' -Force"

:: Remove the downloaded zip file
del /f /q ffmpeg.zip

:: Assuming the structure of the zip has ffmpeg in a subdirectory
FOR /D %%i IN ("!INSTALL_DIR!\*") DO (
    SET "FFMPEG_BIN_DIR=%%i\bin"
)

:: Add FFmpeg to the system PATH
SETX PATH "%PATH%;!FFMPEG_BIN_DIR!" /M

echo FFmpeg has been installed and added to PATH.
echo Please restart your command line interface or your computer for the changes to take effect.

ENDLOCAL
