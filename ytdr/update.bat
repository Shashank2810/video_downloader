@echo off
title YouTube Downloader - Maintenance

:MENU
cls

echo ======================================================
echo           YouTube Downloader Maintenance
echo ======================================================
echo.
echo 1. Install / Update Project Dependencies
echo 2. Update yt-dlp
echo 3. Update pip
echo 4. Install Everything (Recommended)
echo 5. Exit
echo.
set /p choice=Select an option (1-5): 

if "%choice%"=="1" goto INSTALL
if "%choice%"=="2" goto YTDLP
if "%choice%"=="3" goto PIP
if "%choice%"=="4" goto ALL
if "%choice%"=="5" goto END

echo.
echo Invalid choice.
pause
goto MENU

:INSTALL
cls
echo ======================================================
echo Installing Project Dependencies
echo ======================================================
echo.

python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Project dependencies installed successfully.
echo.
pause
goto MENU

:YTDLP
cls
echo ======================================================
echo Updating yt-dlp
echo ======================================================
echo.

python -m pip install --upgrade yt-dlp

echo.
echo yt-dlp updated successfully.
echo.
pause
goto MENU

:PIP
cls
echo ======================================================
echo Updating pip
echo ======================================================
echo.

python -m pip install --upgrade pip

echo.
echo pip updated successfully.
echo.
pause
goto MENU

:ALL
cls
echo ======================================================
echo Installing Everything
echo ======================================================
echo.

python -m pip install --upgrade pip

echo.
echo Installing project requirements...
pip install -r requirements.txt

echo.
echo Updating yt-dlp...
python -m pip install --upgrade yt-dlp

echo.
echo ======================================================
echo Maintenance Completed Successfully
echo ======================================================
echo.
pause
goto MENU

:END
exit