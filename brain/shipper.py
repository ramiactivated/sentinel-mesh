import os
import requests
import json
import time

# --- CONFIGURACIÓN DE ELASTICSEARCH ---
ELASTIC_URL = "http://localhost:9200/sentinel-attacks/_doc"
HEADERS = {"Content-Type": "application/json"}

# --- CONFIGURACIÓN DE TELEGRAM ---
TELEGRAM_TOKEN = "tutoken"
CHAT_ID = "tuid"

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

    print(f"📦 Enviando logs de {attack_type} a Elastic...")

    with open(filepath, 'r') as f:
        for line in f:
            try:
                data = json.loads(line.strip())

                # Extraer y limpiar IP
                raw_ip = data.get("ip", "")
                ip = raw_ip.split("]")[0].replace("[", "") if "[" in raw_ip else raw_ip.split(":")[0]

                # Enriquecer con GeoIP
                geo = get_geo_info(ip)
                data["sensor_type"] = attack_type
                data["geo"] = geo

                # Enviar a Elasticsearch
                resp = requests.post(ELASTIC_URL, headers=HEADERS, json=data)
                if resp.status_code == 201:
                    print(f"✅ Inyectado ataque de {ip} ({geo['country']})")

                # Pequeña pausa para no saturar la API de geolocalización
                time.sleep(1)

            except Exception as e:
                print(f"Error procesando línea: {e}")

if __name__ == "__main__":
    ssh_log = "../sensor-ssh/logs/attacks.jsonl"
    web_log = "../sensor-http/logs/web_attacks.jsonl"
    telnet_log = "../telnet_attacks.json"

    print("🤖 Motor de Inteligencia activado en MODO AUTOMÁTICO.")
    print("Vigilando los sensores 24/7... (Pulsa Ctrl+C para apagarlo)")

    try:
        while True:
# --- ESPIONAJE DE ALTO NIVEL (Alertas a Telegram) ---
            # Función interna para limpiar la IP antes de mandarla al móvil
            def limpiar_ip(ip_sucia):
                ip_sucia = str(ip_sucia)
                # Si es IPv6 local o empieza por corchete, devolvemos LocalNet
                if ip_sucia.startswith("[") or "::1" in ip_sucia or "127.0.0.1" in ip_sucia:
                    return "127.0.0.1 (Local)"
                # Quitar el puerto si existe (ej: 192.168.1.1:5432 -> 192.168.1.1)
                return ip_sucia.split(":")[0]

            # 1. Vigilar Web
            try:
                with open(web_log, 'r') as f:
                    for linea in f:
                        if "/.env" in linea or "/wp-config.php.bak" in linea:
                            try:
                                datos = json.loads(linea)
                                ip = limpiar_ip(datos.get("ip", "Desconocida"))
                                mandar_alerta_telegram(ip, datos.get("path", "Archivo Secreto Web"))
                            except: pass
            except FileNotFoundError: pass

            # 2. Vigilar SSH y Telnet
            for archivo_log, nombre_puerta in [(ssh_log, "SSH"), (telnet_log, "TELNET")]:
                try:
                    with open(archivo_log, 'r') as f:
                        for linea in f:
                            try:
                                datos = json.loads(linea)
                                user = datos.get("username", "").lower()
                                if user in ["root", "admin", "administrator"]:
                                    ip = limpiar_ip(datos.get("ip", "Desconocida"))
                                    mandar_alerta_telegram(ip, f"Fuerza Bruta en {nombre_puerta} (User: {user})")
                            except: pass
                except FileNotFoundError: pass
            # ----------------------------------------------------
            # ----------------------------------------------------
            # ----------------------------------------------------
            # ----------------------------------------------------

            # 1. Leer y enviar todo lo nuevo que hayan capturado los sensores
            ship_logs(ssh_log, "SSH")
            ship_logs(web_log, "HTTP")
            ship_logs(telnet_log, "TELNET")

            # 2. Vaciar los archivos de texto para no enviar datos repetidos en la próxima vuelta
            open(ssh_log, 'w').close()
            open(web_log, 'w').close()
            open(telnet_log, 'w').close()

            # 3. Descansar 5 segundos antes de volver a mirar (para no saturar la CPU)
            time.sleep(5)

    except KeyboardInterrupt:
        print("\n🛑 Apagando el motor de inteligencia de forma segura. ¡Hasta la próxima!")
