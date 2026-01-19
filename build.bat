@echo off
echo Installing Requirements...
python -m pip install -r requirements.txt

echo.
echo Building One-Click EXE...
:: --onefile: Single EXE
:: --noconsole: No CMD window
:: --add-data: Include maki.bat
:: --name: Output name
:: --hidden-import: Ensure SQLAlchemy/pymem etc are found if needed

python -m PyInstaller --noconsole --onefile ^
    --name "MakiLauncher" ^
    --add-data "client/maki.bat;." ^
    --hidden-import="pymem" ^
    --hidden-import="sqlalchemy.sql.default_comparator" ^
    client/main.py

echo.
echo Build Complete! Check dist/MakiLauncher.exe
