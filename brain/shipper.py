import os
import requests
import json
import time

# --- CONFIGURACIÓN DE ELASTICSEARCH ---
# Usamos el endpoint con '_doc' para versiones modernas
ELASTIC_URL = "http://localhost:9200/sentinel-attacks/_doc"
HEADERS = {"Content-Type": "application/json"}

# --- CONFIGURACIÓN DE TELEGRAM ---
TELEGRAM_TOKEN = "8757724324:AAFbA602Yt2Y4Yq127mR1Chl_9J28Sbsz1w"
CHAT_ID = "1099041798"

def mandar_alerta_telegram(ip, archivo):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    mensaje = f"🚨 *ALERTA CRÍTICA SOC* 🚨\n\n👾 *Intruso:* `{ip}`\n📂 *Objetivo:* `{archivo}`\n\n🛡️ Sentinel Mesh ha interceptado el ataque."
    datos = {
        "chat_id": CHAT_ID,
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=datos)
    except Exception as e:
        print("❌ Error contactando con Telegram:", e)

def get_geo_info(ip):
    # Si es IP local, mandamos a Null Island (0,0)
    if "127.0.0.1" in ip or "[::1]" in ip or ip.startswith("192.") or ip.startswith("10."):
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
    if not os.path.exists(filepath):
        return

    with open(filepath, 'r') as f:
        for line in f:
            try:
                data = json.loads(line.strip())

                # 1. Extraer e IP
                raw_ip = data.get("ip", "")
                ip = raw_ip.split("]")[0].replace("[", "") if "[" in raw_ip else raw_ip.split(":")[0]
                
                # --- ¡LA LÍNEA MÁGICA QUE ARREGLA EL ERROR! ---
                data["ip"] = ip 
                # ----------------------------------------------

                # 2. Enriquecer con GeoIP
                geo_data = get_geo_info(ip)

                # --- CORRECCIÓN CLAVE PARA EL MAPA ---
                # 'geo' debe ser solo un string "lat,lon" para que Kibana lo entienda
                data["geo"] = f"{geo_data['lat']},{geo_data['lon']}"
                # Guardamos el país y ciudad en campos aparte para poder filtrar
                data["country"] = geo_data["country"]
                data["city"] = geo_data["city"]
                data["sensor_type"] = attack_type
                # -------------------------------------

                # 3. Enviar a Elasticsearch
                resp = requests.post(ELASTIC_URL, headers=HEADERS, json=data)

                if resp.status_code == 201 or resp.status_code == 200:
                    print(f"✅ Inyectado ataque de {ip} ({data['country']}) en Elastic")
                else:
                    # Chivato de errores
                    print(f"❌ Error Elastic ({resp.status_code}): {resp.text}")

                time.sleep(0.5) # Pausa ligera

            except Exception as e:
                print(f"Error procesando línea: {e}")

if __name__ == "__main__":
    ssh_log = "../sensor-ssh/logs/attacks.jsonl"
    web_log = "../sensor-http/logs/web_attacks.jsonl"
    telnet_log = "/home/rami/sentinel-mesh/telnet_attacks.json" # Ruta absoluta recomendada

    print("🤖 Motor de Inteligencia activado.")

    try:
        while True:
            # --- SECCIÓN TELEGRAM ---
            def limpiar_ip(ip_sucia):
                ip_sucia = str(ip_sucia)
                if ip_sucia.startswith("[") or "::1" in ip_sucia or "127.0.0.1" in ip_sucia:
                    return "127.0.0.1"
                return ip_sucia.split(":")[0]

            # Telegram: Web
            try:
                if os.path.exists(web_log):
                    with open(web_log, 'r') as f:
                        for linea in f:
                            if any(x in linea for x in ["/.env", "/wp-config", ".php"]):
                                d = json.loads(linea)
                                mandar_alerta_telegram(limpiar_ip(d.get("ip")), d.get("path", "Web"))
            except: pass

            # Telegram: SSH/Telnet
            for log_f, name in [(ssh_log, "SSH"), (telnet_log, "TELNET")]:
                try:
                    if os.path.exists(log_f):
                        with open(log_f, 'r') as f:
                            for linea in f:
                                d = json.loads(linea)
                                if d.get("username") in ["root", "admin"]:
                                    mandar_alerta_telegram(limpiar_ip(d.get("ip")), f"Fuerza Bruta {name}")
                except: pass

            # --- SECCIÓN ELASTIC ---
            ship_logs(ssh_log, "SSH")
            ship_logs(web_log, "HTTP")
            ship_logs(telnet_log, "TELNET")

            # Vaciar archivos
            for f_to_clear in [ssh_log, web_log, telnet_log]:
                if os.path.exists(f_to_clear):
                    open(f_to_clear, 'w').close()

            time.sleep(5)
    except KeyboardInterrupt:
        print("\n🛑 SOC apagado.")
