#!/bin/bash
case "$(uname -s)" in 
    Linux*) OS=Linux ;;
    Darwin*) OS=Darwin ;;
    MINGW*|MSYS*|CYGWIN*) OS="Windows";;
    *) echo OS="Unknown";;
esac


# Este script es Bash, pero en Windows la IP LAN la obtendremos con PowerShell
# y la pasamos a docker compose como variable de entorno.
if [ $OS == "Windows" ]; then
    IP="$(powershell.exe -NoProfile -Command "(Get-NetIPAddress -InterfaceAlias 'Wi-Fi' -AddressFamily IPv4).IPAddress" | tr -d '\r')"
    export HOST_LAN_IP="$IP"
    docker compose up -d --build
else
    IP=$(ip -4 addr show wlan0 | grep -oP 'inet \K[\d.]+')
    export HOST_LAN_IP="$IP"
    docker compose up -d --build
fi