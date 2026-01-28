@echo off
echo ========================================
echo COURSE REGISTRATION SYSTEM
echo ========================================

REM Kiểm tra virtual environment
if not exist ".venv\" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Kích hoạt venv
echo Activating virtual environment...
call .venv\Scripts\activate

REM Cài dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Tạo database
echo Setting up database...
python create_database.py

REM Chạy test
echo Running tests...
python quick_test.py

REM Chạy ứng dụng
echo Starting application...
python app.py

pause