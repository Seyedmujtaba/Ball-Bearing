@echo off
cd /d %~dp0
pip install pyinstaller pyqt5
pyinstaller --noconsole --onedir --name BallBearing ^
  --add-data "assets/background.jpg;assets" ^
  --add-data "DataBase/DataBase.json;DataBase" ^
  main.py
pause
