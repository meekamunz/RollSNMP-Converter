@echo off

rmdir /s /q __pycache__
rmdir /s /q build
rmdir /s /q dist
del *.spec

pyinstaller --onefile --icon=icon.ico --name=SNMP-Packager snmp-packager.py