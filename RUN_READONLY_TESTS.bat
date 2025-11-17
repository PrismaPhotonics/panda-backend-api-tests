@echo off
REM Run Read-Only Tests (Safe for "waiting for fiber" state)
REM =========================================================

echo ========================================
echo Running Read-Only Tests
echo Safe for 'waiting for fiber' state
echo ========================================
echo.

REM Activate virtual environment if exists
if exist .venv\Scripts\Activate.bat (
    echo Activating virtual environment...
    call .venv\Scripts\Activate.bat
)

REM Get Python executable
if exist .venv\Scripts\python.exe (
    set PYTHON=.venv\Scripts\python.exe
) else if exist venv\Scripts\python.exe (
    set PYTHON=venv\Scripts\python.exe
) else (
    set PYTHON=python
)

echo.
echo Running tests...
echo.

REM Run all read-only tests
%PYTHON% -m pytest -v -s --tb=short --skip-health-check -k "not configure" ^
    tests/integration/api/test_health_check.py ^
    tests/integration/api/test_api_endpoints_high_priority.py::TestChannelsEndpoint ^
    tests/integration/api/test_api_endpoints_additional.py::TestSensorsEndpoint ^
    tests/integration/api/test_api_endpoints_additional.py::TestLiveMetadataEndpoint ^
    tests/infrastructure/ ^
    tests/data_quality/ ^
    tests/unit/

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo All tests completed successfully!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo Some tests failed (exit code: %ERRORLEVEL%)
    echo ========================================
)

exit /b %ERRORLEVEL%

