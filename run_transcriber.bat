@echo off
echo Running transcription...

REM Activate the virtual environment and run the script
call ".venv\Scripts\activate.bat"
python transcribe.py

echo Done!
pause
