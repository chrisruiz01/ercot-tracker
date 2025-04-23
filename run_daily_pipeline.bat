@echo off
cd C:\Users\chris\energy-market-tracker
call activate ercot_env

:: Run each step and log output to daily log file
set LOG=logs\%date:~-4%%date:~4,2%%date:~7,2%.log

echo Running fetch_data.py >> %LOG%
python scripts\fetch_data.py >> %LOG% 2>&1

echo Running load_to_db.py >> %LOG%
python scripts\load_to_db.py >> %LOG% 2>&1

echo Running query_rolling_avg.py >> %LOG%
python scripts\query_rolling_avg.py >> %LOG% 2>&1

echo Complete on %date% %time% >> %LOG%
exit