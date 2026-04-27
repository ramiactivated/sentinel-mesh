import os
import requests
import json
import time

# --- CONFIGURACIÓN SOC ---
ELASTIC_URL = "http://localhost:9200/sentinel-attacks/_doc"
HEADERS = {"Content-Type": "application/json"}
TELEGRAM_TOKEN = "8757724324:AAFbA602Yt2Y4Yq127mR1Chl_9J28Sbsz1w"
CHAT_ID = "1099041798"

def limpiar_ip(ip_sucia):
    """Elimina corchetes y puertos de la IP."""
    ip = str(ip_sucia).replace("[", "").replace("]", "")
    if ":" in ip:
        ip = ip.split(":")[0]
    if ip == "::1" or not ip or ip == "localhost":
        ip = "127.0.0.1"
    return ip

def mandar_alerta_telegram(ip, objetivo, tipo, clave=""):
    """Envía la alerta detallada a Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    iconos = {"HTTP": "🌐", "SSH": "🔑", "TELNET": "📟"}
    
    mensaje = (
        f"🚨 *VIGILANCIA TOTAL SOC* 🚨\n\n"
        f"{iconos.get(tipo, '👾')} *Sensor:* `{tipo}`\n"
        f"👤 *IP Intruso:* `{ip}`\n"
        f"🎯 *Acceso:* {objetivo}\n"
    )
    
    # Si tenemos contraseña (SSH/Telnet), la añadimos al mensaje
    if clave:
        mensaje += f"🔑 *Clave intentada:* `{clave}`\n"
    
    mensaje += f"\n🛡️ _Sentinel Mesh: Actividad detectada._"
    
    datos = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=datos, timeout=10)
    except:
        print("❌ Error contactando con Telegram.")

def get_geo_info(ip):
    """Obtiene la ubicación de la IP para el mapa de Kibana."""
    if ip == "127.0.0.1" or ip.startswith(("192.", "10.", "172.")):
        return {"country": "LocalNet", "city": "Laboratorio", "lat": 0.0, "lon": 0.0}
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        if response.get("status") == "success":
            return {
                "country": response.get("country"),
                "city": response.get("city"),
                "lat": response.get("lat"),
                "lon": response.get("lon")
            }
    except:
        pass
    return {"country": "Unknown", "city": "Unknown", "lat": 0.0, "lon": 0.0}

def ship_logs(filepath, attack_type):
    """Procesa logs, envía alertas y sube datos a Elastic."""
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        return

    with open(filepath, 'r') as f:
        for line in f:
            try:
                line_content = line.strip()
                if not line_content: continue
                
                data = json.loads(line_content)
                ip = limpiar_ip(data.get("ip", "127.0.0.1"))

                # --- LÓGICA DE ALERTA PERSONALIZADA ---
                if attack_type == "HTTP":
                    ruta = data.get("path", "Web")
                    objetivo = f"Ruta: `{ruta}`"
                    # Alertar solo en rutas críticas para evitar spam web
                    if any(x in ruta for x in [".env", "config", "admin", "php", "login"]):
                        mandar_alerta_telegram(ip, objetivo, attack_type)
                else:
                    # SSH y TELNET: Alertar SIEMPRE con Usuario y Contraseña
                    user = data.get("username", "desconocido")
                    password = data.get("password", "(vacia)")
                    objetivo = f"Usuario: `{user}`"
                    mandar_alerta_telegram(ip, objetivo, attack_type, clave=password)

                # --- ENVÍO A ELASTICSEARCH ---
                geo = get_geo_info(ip)
                data.update({
                    "ip": ip, 
                    "geo": f"{geo['lat']},{geo['lon']}", 
                    "country": geo["country"], 
                    "city": geo["city"],
                    "sensor_type": attack_type
                })
                
                resp = requests.post(ELASTIC_URL, headers=HEADERS, json=data, timeout=10)
                if resp.status_code in [200, 201]:
                    print(f"✅ [{attack_type}] Alerta enviada e inyectado en Elastic.")
                else:
                    print(f"❌ Error Elastic ({resp.status_code}): {resp.text}")

            except Exception as e:
                print(f"Error procesando línea: {e}")

if __name__ == "__main__":
    # RUTAS VERIFICADAS SEGÚN TU SISTEMA
    LOGS = [
        ("../sensor-ssh/logs/attacks.jsonl", "SSH"),
        ("../sensor-http/logs/web_attacks.jsonl", "HTTP"),
        ("/home/rami/sentinel-mesh/sensor-telnet/telnet_attacks.json", "TELNET")
    ]

    print("🤖 Motor Sentinel: Modo Forense Activo (Vigilancia Total).")
    
    try:
        while True:
            for path, tipo in LOGS:
                if os.path.exists(path) and os.path.getsize(path) > 0:
                    ship_logs(path, tipo)
                    # Vaciamos el archivo para no duplicar alertas
                    open(path, 'w').close()
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n🛑 SOC Apagado.")
