@echo off
REM 🎤 Easy Windows Installer for Speech-Enabled Network Management
REM One-click installation for non-technical Windows users

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║              🎤 Speech-Enabled Network Management              ║
echo ║                    Windows Easy Installer                       ║
echo ║                                                                 ║
echo ║   Installing enterprise AI network management with voice control   ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

REM Check for admin rights
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo ❌ Please run this as Administrator
    echo Right-click this file and select "Run as administrator"
    pause
    exit /B 1
)

echo [1/10] ✅ Checking permissions...

REM Check for Chocolatey
where choco >nul 2>nul
if %errorlevel% neq 0 (
    echo [2/10] 📦 Installing Chocolatey package manager...
    powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
) else (
    echo [2/10] ✅ Chocolatey already installed...
)

echo [3/10] 📦 Installing system dependencies...
choco install -y python3 git docker-desktop

echo [4/10] ✅ Checking Python installation...
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python installation failed
    pause
    exit /B 1
)

echo [5/10] 🐳 Starting Docker Desktop...
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
echo     ⏳ Waiting 30 seconds for Docker to start...
timeout /t 30 >nul

echo [6/10] 📥 Downloading AI Research Platform...
set "INSTALL_DIR=%USERPROFILE%\ai-research-platform"
if exist "%INSTALL_DIR%" (
    cd /d "%INSTALL_DIR%"
    git pull origin main
) else (
    git clone https://github.com/kmransom56/ai-research-platform.git "%INSTALL_DIR%"
    cd /d "%INSTALL_DIR%"
)

echo [7/10] 🐍 Setting up Python environment...
cd /d "%INSTALL_DIR%\network-agents"
python -m venv easy-install-env
call easy-install-env\Scripts\activate.bat
python -m pip install --upgrade pip
pip install neo4j==5.28.2 flask==3.1.1 speechrecognition==3.14.3 pyttsx3==2.99 pyaudio==0.2.14 requests==2.32.4 aiohttp==3.12.15

echo [8/10] 🐳 Starting AI database services...
cd /d "%INSTALL_DIR%"

REM Create Windows docker-compose
echo version: '3.8' > docker-compose-easy-windows.yml
echo services: >> docker-compose-easy-windows.yml
echo   neo4j: >> docker-compose-easy-windows.yml
echo     image: neo4j:5.23-community >> docker-compose-easy-windows.yml
echo     container_name: ai-platform-neo4j-easy >> docker-compose-easy-windows.yml
echo     ports: >> docker-compose-easy-windows.yml
echo       - "7474:7474" >> docker-compose-easy-windows.yml
echo       - "7687:7687" >> docker-compose-easy-windows.yml
echo     environment: >> docker-compose-easy-windows.yml
echo       NEO4J_AUTH: neo4j/password >> docker-compose-easy-windows.yml
echo       NEO4J_PLUGINS: '["apoc"]' >> docker-compose-easy-windows.yml
echo     volumes: >> docker-compose-easy-windows.yml
echo       - neo4j_data:/data >> docker-compose-easy-windows.yml
echo     restart: unless-stopped >> docker-compose-easy-windows.yml
echo volumes: >> docker-compose-easy-windows.yml
echo   neo4j_data: >> docker-compose-easy-windows.yml

docker-compose -f docker-compose-easy-windows.yml down >nul 2>nul
docker-compose -f docker-compose-easy-windows.yml up -d
echo     ⏳ Waiting for database to start...
timeout /t 15 >nul

echo [9/10] 📊 Loading network intelligence data...
cd /d "%INSTALL_DIR%\network-agents"
call easy-install-env\Scripts\activate.bat

REM Create sample data loader for Windows
echo import time > load_windows_data.py
echo from neo4j import GraphDatabase >> load_windows_data.py
echo. >> load_windows_data.py
echo def load_sample_data(): >> load_windows_data.py
echo     driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "password")) >> load_windows_data.py
echo     with driver.session() as session: >> load_windows_data.py
echo         session.run("MATCH (n) DETACH DELETE n") >> load_windows_data.py
echo         session.run("""CREATE  >> load_windows_data.py
echo             (inspire:Organization {id: '1', name: 'Inspire Brands', device_count: 399}), >> load_windows_data.py
echo             (bww:Organization {id: '2', name: 'Buffalo-Wild-Wings', device_count: 100}), >> load_windows_data.py
echo             (arbys:Organization {id: '3', name: 'Arbys', device_count: 46}) >> load_windows_data.py
echo         """) >> load_windows_data.py
echo         for i in range(50): >> load_windows_data.py
echo             session.run("""CREATE (d:Device { >> load_windows_data.py
echo                 serial: $serial, name: $name, model: 'MR53', >> load_windows_data.py
echo                 organization_name: 'Inspire Brands', >> load_windows_data.py
echo                 health_score: 90.0, status: 'online', platform: 'meraki'}) >> load_windows_data.py
echo             """, serial=f"MR53-{i:03d}", name=f"AP-{i:03d}") >> load_windows_data.py
echo     driver.close() >> load_windows_data.py
echo     print("✅ Sample data loaded!") >> load_windows_data.py
echo. >> load_windows_data.py
echo if __name__ == "__main__": >> load_windows_data.py
echo     time.sleep(5) >> load_windows_data.py
echo     load_sample_data() >> load_windows_data.py

python load_windows_data.py

echo [10/10] 🚀 Creating startup script...
cd /d "%INSTALL_DIR%"

REM Create Windows startup batch file
echo @echo off > start-speech-network-windows.bat
echo echo 🚀 Starting Speech-Enabled Network Management... >> start-speech-network-windows.bat
echo cd /d "%INSTALL_DIR%\network-agents" >> start-speech-network-windows.bat
echo call easy-install-env\Scripts\activate.bat >> start-speech-network-windows.bat
echo echo 🔍 Checking services... >> start-speech-network-windows.bat
echo docker ps ^>nul 2^>nul >> start-speech-network-windows.bat
echo if errorlevel 1 ( >> start-speech-network-windows.bat
echo     echo 🐳 Starting Docker services... >> start-speech-network-windows.bat
echo     cd /d "%INSTALL_DIR%" >> start-speech-network-windows.bat
echo     docker-compose -f docker-compose-easy-windows.yml up -d >> start-speech-network-windows.bat
echo     cd /d "%INSTALL_DIR%\network-agents" >> start-speech-network-windows.bat
echo     echo ⏳ Waiting for database... >> start-speech-network-windows.bat
echo     timeout /t 10 ^>nul >> start-speech-network-windows.bat
echo ) >> start-speech-network-windows.bat
echo echo 🎤 Starting speech interface... >> start-speech-network-windows.bat
echo echo 🌐 Opening http://localhost:11031 in 5 seconds... >> start-speech-network-windows.bat
echo start "" python simple-speech-interface.py >> start-speech-network-windows.bat
echo timeout /t 5 ^>nul >> start-speech-network-windows.bat
echo start "" http://localhost:11031 >> start-speech-network-windows.bat
echo echo. >> start-speech-network-windows.bat
echo echo 🎉 Speech Network Management is ready! >> start-speech-network-windows.bat
echo echo 🎤 Click the microphone in your browser and start talking! >> start-speech-network-windows.bat
echo echo. >> start-speech-network-windows.bat
echo echo Try saying: >> start-speech-network-windows.bat
echo echo   • How many devices do we have? >> start-speech-network-windows.bat
echo echo   • Give me a network summary >> start-speech-network-windows.bat
echo echo. >> start-speech-network-windows.bat
echo pause >> start-speech-network-windows.bat

REM Create desktop shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%USERPROFILE%\Desktop\Speech Network Management.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%INSTALL_DIR%\start-speech-network-windows.bat" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "Voice-controlled AI network management" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript CreateShortcut.vbs >nul
del CreateShortcut.vbs

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                    🎉 INSTALLATION COMPLETE! 🎉                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.
echo ✅ Your Speech-Enabled Network Management System is ready!
echo.
echo 🚀 TO GET STARTED:
echo    1. Double-click "Speech Network Management" on your desktop
echo    2. Your browser will open to: http://localhost:11031
echo    3. Click the 🎤 microphone button
echo    4. Start talking to your network!
echo.
echo 🎤 TRY THESE VOICE COMMANDS:
echo    • "How many devices do we have?"
echo    • "Give me a network summary"
echo    • "Are there any problems?"
echo.
echo 🌟 Welcome to the future of network management!
echo.
pause