@echo off
echo Lancement du serveur...
start cmd /k "py server.py"
timeout /t 2 /nobreak >nul

echo Lancement du premier client...
start cmd /k "py client.py"

echo Lancement du deuxième client...
start cmd /k "py client.py"

exit
