#!/bin/bash
# 🕸️ Sentinel Mesh - Secuencia de Arranque Automático

# 1. Ponerle las "gafas" a Cron (Cargar el mapa de rutas del sistema)
export PATH=$PATH:/usr/local/go/bin:/usr/local/bin:/usr/bin:/usr/sbin:/sbin:/bin:/snap/bin

# 2. Damos 15 segundos de margen al sistema
sleep 15

# 3. Levantar la base de datos y el panel (Kibana/Elastic)
cd /home/rami/sentinel-mesh/dashboard
docker-compose up -d

# 4. Arrancar los 3 sensores (Trampas)
cd /home/rami/sentinel-mesh
nohup go run sensor-ssh/cmd/main.go > startup_ssh.txt 2>&1 &
nohup go run sensor-http/cmd/main.go > startup_http.txt 2>&1 &
nohup go run sensor-telnet/cmd/main.go > startup_telnet.txt 2>&1 &

# 5. Arrancar el Cerebro de Python
cd /home/rami/sentinel-mesh/brain
source venv/bin/activate
nohup python shipper.py > startup_brain.txt 2>&1 &
