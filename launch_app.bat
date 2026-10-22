@echo off

cd /d "C:\Users\joshu\Desktop\Application_Tracker"

call "%USERPROFILE%\miniconda3\Scripts\activate.bat" job_tracker

python -m streamlit run app.py

pause