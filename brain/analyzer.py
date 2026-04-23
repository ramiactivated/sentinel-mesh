import json
import os
import requests

def get_geo_info(ip):
    # Si el ataque viene de tu propia máquina (pruebas locales), lo detectamos
    if "127.0.0.1" in ip or "[::1]" in ip or ip.startswith("192.168.") or ip.startswith("10."):
        return "Red Local (Laboratorio)"
    
    try:
        # Consultamos la API pública de geolocalización
        url = f"http://ip-api.com/json/{ip}"
        response = requests.get(url, timeout=5).json()
        
        if response.get("status") == "success":
            return f"{response.get('country')}, {response.get('city')} (ISP: {response.get('isp')})"
    except Exception as e:
        pass
    
    return "Origen Desconocido"

def analyze_logs(filepath, attack_type):
    if not os.path.exists(filepath):
        print(f"⚠️ Archivo {filepath} no encontrado. ¿Has arrancado el sensor {attack_type}?")
        return
    
    print(f"\n--- 🕵️ Analizando registros de {attack_type} ---")
    
    with open(filepath, 'r') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                
                # Extraer IP y limpiar el puerto (ej: 192.168.1.5:54321 -> 192.168.1.5)
                raw_ip = data.get("ip", "")
                ip = raw_ip.split("]")[0].replace("[", "") if "[" in raw_ip else raw_ip.split(":")[0]
                
                geo = get_geo_info(ip)
                timestamp = data.get("timestamp", "").split("T")[0] # Solo la fecha para que quede limpio
                
                if attack_type == "SSH":
                    print(f"🚨 [{timestamp}] IP: {ip} | Geo: {geo} | User probados: '{data.get('username')}'")
                elif attack_type == "HTTP":
                    print(f"🕸️  [{timestamp}] IP: {ip} | Geo: {geo} | Buscaba: '{data.get('path')}'")
            
            except json.JSONDecodeError:
                continue

if __name__ == "__main__":
    # Rutas relativas a donde están guardando los datos nuestros sensores de Go
    ssh_log = "../sensor-ssh/logs/attacks.jsonl"
    web_log = "../sensor-http/logs/web_attacks.jsonl"
    
    print("🧠 Iniciando el Motor de Inteligencia de Sentinel Mesh...")
    analyze_logs(ssh_log, "SSH")
    analyze_logs(web_log, "HTTP")
    print("\n✅ Análisis completado.")
