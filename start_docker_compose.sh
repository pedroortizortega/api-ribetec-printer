#!/bin/bash
# bajando el compose actual
sleep 30

rm env_run

docker compose down 

windows_os="$(powershell.exe -NoProfile -Command '$env:OS')"
system="$(uname -s)"

echo "windows_os: $windows_os"

if [ "$windows_os" == "Windows_NT" ]; then
    echo "Windows"
    IP=$(powershell.exe -NoProfile -Command "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { \$_.IPAddress -like '192.168.*' } | Select-Object -First 1 -ExpandProperty IPAddress)")
    echo "Windows IP: $IP"
fi

if [ "$system" == "Linux" ]; then
    echo "Linux"
    IP=$(hostname -I | awk '{print $1}')
    echo "Linux IP: $IP"
fi
echo "Creando el archivo env_run"
echo "HOST_LAN_IP=$IP" >> env_run

echo "Ejecutando el compose"
docker compose up --build --remove-orphans
