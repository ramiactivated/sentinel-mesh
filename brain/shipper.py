import json
import os
import requests
import time

ELASTIC_URL = "http://localhost:9200/sentinel-attacks/_doc"
HEADERS = {"Content-Type": "application/json"}

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
    
    ship_logs(ssh_log, "SSH")
    ship_logs(web_log, "HTTP")
    print("🚀 Todos los datos han sido enviados al SOC.")
