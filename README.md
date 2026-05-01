# 🕸️ Sentinel Mesh

**Honeynet Distribuida e Inteligencia de Amenazas Nativa en la Nube**
   
Sentinel Mesh es una arquitectura de honeynet modular diseñada para capturar, analizar y alertar sobre actividad maliciosa en tiempo real. El sistema simula servicios vulnerables para atraer atacantes, extrae sus credenciales y geolocaliza su origen de forma autónoma.

<img width="789" height="514" alt="2026-05-01_09h57_01" src="https://github.com/user-attachments/assets/8abf5594-f7a3-4a3e-8934-243245ab8fa4" />


---

## 🏗️ Arquitectura del Sistema

La plataforma se compone de tres capas integradas:

1. **Sensores Activos (Go):** Honeypots ligeros.
   * **Sensor-SSH (Puerto 22):** Emula un servidor SSH estándar, capturando intentos de fuerza bruta.
   * **Sensor-HTTP (Puerto 8080):** Simula paneles de administración y trampas web.
   * **Sensor-Telnet (Puerto 2323):** Captura intentos de acceso en protocolos heredados.

2. **Cerebro / Shipper (Python):** Motor de procesamiento que realiza:
   * **Enriquecimiento GeoIP:** Localización de ataques por país y ciudad a través de APIs externas.
   * **Análisis Forense:** Extracción de usuarios y contraseñas probados por los atacantes.

3. **SOC Central (Elastic Stack):** Pila de Elasticsearch y Kibana para almacenamiento, indexación y visualización de métricas de ataque.

Gráfico de Sensores
<img width="921" height="510" alt="2026-05-01_09h57_23" src="https://github.com/user-attachments/assets/d0d4dcae-f432-4894-b538-3d49f3453765" />


---

## 🔥 Características Principales

* 🎯 **Captura de Credenciales:** Registro detallado de *user* y *password* utilizados en ataques de fuerza bruta.
* 📱 **Alertas en Tiempo Real:** Notificaciones inmediatas a dispositivos móviles mediante Telegram Bot API.
* 🗺️ **Visualización Geoespacial:** Mapas para identificar el origen geográfico de las amenazas.
* 🔄 **Persistencia Autónoma:** Configurado para arrancar automáticamente y sobrevivir a reinicios del servidor.

### 📱 Alertas en Telegram
El sistema cuenta con un bot que evalúa cada ataque, geolocaliza la IP del intruso y envía un informe detallado:

Alertas Telegram
<img width="942" height="2048" alt="WhatsApp Image 2026-05-01 at 09 59 02" src="https://github.com/user-attachments/assets/a53104fd-3a88-40d2-a30e-c58d7f355763" />


---

## 📊 Análisis de Datos e Inteligencia

Sentinel Mesh no solo recoge logs, sino que extrae inteligencia procesable para identificar patrones de ataque, credenciales por defecto más buscadas (como `admin` o `root`) y las IPs más agresivas.

**Credenciales más utilizadas por los atacantes:**

Tabla de Credenciales
<img width="930" height="237" alt="2026-05-01_09h57_17" src="https://github.com/user-attachments/assets/b3db4eb8-06dd-4c1f-a9d0-ba0ea0d1a049" />


**Top IPs Atacantes:**

Gráfico de IPs
<img width="930" height="512" alt="2026-05-01_09h57_08" src="https://github.com/user-attachments/assets/eb0e9022-b3dc-4d52-a862-37fe09d28293" />


---

## 🚀 Despliegue en AWS (EC2)

El sistema está diseñado para ejecutarse de forma autónoma en una instancia **Ubuntu Server 22.04 LTS** en Amazon Web Services.

### 🛡️ Configuración de Red (Security Groups)
Para el correcto funcionamiento del SOC y separar el tráfico de administración del tráfico malicioso, se han configurado las siguientes reglas:

Tabla de Puertos
<img width="774" height="168" alt="2026-05-01_09h57_57" src="https://github.com/user-attachments/assets/365a5dcd-e78b-4968-bcc9-24742de5685c" />


### 🔄 Persistencia y Automatización
Para garantizar que los sensores y el sistema de alertas se inicien automáticamente tras un reinicio del servidor en la nube, se utiliza:
* **Script de inicio (`iniciar_SOC.sh`):** Centraliza el arranque de todos los sensores (Go) y el script de envío de alertas (Python) en segundo plano (`nohup`). Los sensores que requieren puertos privilegiados (22) se ejecutan mediante `sudo`.
* **Crontab:** Se ha configurado la instrucción `@reboot` para ejecutar el script de inicio de forma completamente desatendida al arrancar el sistema.

---

## ⚠️ Aviso Legal

**Proyecto educativo y de investigación.** No desplegar en redes corporativas ni en entornos de producción sin el aislamiento adecuado, ya que la simulación de vulnerabilidades puede atraer tráfico malicioso indeseado a la red local.
