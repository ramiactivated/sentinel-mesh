import os
import requests
import json
import time

# --- CONFIGURACIÓN REAL ---
ELASTIC_URL = "http://localhost:9200/sentinel-attacks/_doc"
HEADERS = {"Content-Type": "application/json"}
TELEGRAM_TOKEN = "8757724324:AAFbA602Yt2Y4Yq127mR1Chl_9J28Sbsz1w"
CHAT_ID = "1099041798"

def limpiar_ip(ip_sucia):
    ip = str(ip_sucia).replace("[", "").replace("]", "")
    if ":" in ip: ip = ip.split(":")[0]
    if ip == "::1" or not ip: ip = "127.0.0.1"
    return ip

def mandar_alerta_telegram(ip, objetivo, tipo):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    iconos = {"HTTP": "🌐", "SSH": "🔑", "TELNET": "📟"}
    mensaje = (
        f"🚨 *ALERTA CRÍTICA SOC* 🚨\n\n"
        f"{iconos.get(tipo, '👾')} *Sensor:* `{tipo}`\n"
        f"👤 *Intruso:* `{ip}`\n"
        f"🎯 *Objetivo:* `{objetivo}`\n\n"
        f"🛡️ _Sentinel Mesh ha interceptado el ataque._"
    )
    datos = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=datos, timeout=10)
    except:
        print("❌ Error contactando con Telegram.")

def get_geo_info(ip):
    if ip == "127.0.0.1" or ip.startswith(("192.", "10.")):
        return {"country": "LocalNet", "city": "Laboratorio", "lat": 0.0, "lon": 0.0}
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        return {"country": response.get("country"), "city": response.get("city"), "lat": response.get("lat"), "lon": response.get("lon")}
    except:
        return {"country": "Unknown", "city": "Unknown", "lat": 0.0, "lon": 0.0}

def ship_logs(filepath, attack_type):
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        return

    with open(filepath, 'r') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                ip = limpiar_ip(data.get("ip", "127.0.0.1"))
                
                # --- Lógica de Alerta ---
                objetivo = data.get("path") if attack_type == "HTTP" else f"User: {data.get('username')}"
                mandar_alerta_telegram(ip, objetivo, attack_type)

                # --- Envío a Elastic ---
                geo = get_geo_info(ip)
                data.update({"ip": ip, "geo": f"{geo['lat']},{geo['lon']}", "country": geo["country"], "sensor_type": attack_type})
                requests.post(ELASTIC_URL, headers=HEADERS, json=data, timeout=10)
                print(f"✅ [{attack_type}] Alerta enviada y log inyectado.")
            except: pass

if __name__ == "__main__":
    # RUTAS VERIFICADAS
    LOGS = [
        ("../sensor-ssh/logs/attacks.jsonl", "SSH"),
        ("../sensor-http/logs/web_attacks.jsonl", "HTTP"),
        ("/home/rami/sentinel-mesh/sensor-telnet/telnet_attacks.json", "TELNET")
    ]

    print("🤖 Motor activado con Telegram oficial.")
    while True:
        for path, tipo in LOGS:
            ship_logs(path, tipo)
            if os.path.exists(path): open(path, 'w').close()
        time.sleep(2)
