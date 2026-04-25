package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strings"
	"time"
)

type AttackLog struct {
	Timestamp string `json:"timestamp"`
	IP        string `json:"ip"`
	Port      string `json:"port"`
	Method    string `json:"method"`
	Path      string `json:"path"`
	Payload   string `json:"payload"`
	Sensor    string `json:"sensor_type"`
}

func main() {
	port := ":8080"
	http.HandleFunc("/", handleRequest)

	fmt.Println("🕸️ Sensor HTTP (Web Labyrinth) escuchando en el puerto", port)
	err := http.ListenAndServe(port, nil)
	if err != nil {
		fmt.Println("❌ Error iniciando Web Sensor:", err)
	}
}

func handleRequest(w http.ResponseWriter, r *http.Request) {
	ip := strings.Split(r.RemoteAddr, ":")[0]
	path := r.URL.Path
	method := r.Method
	payload := ""

	if method == "POST" {
		r.ParseForm()
		payload = r.Form.Encode()
	}

	// 🎭 EL LABERINTO: Respuestas personalizadas según lo que busque el hacker
	switch path {
	case "/wp-admin":
		if method == "POST" {
			w.Write([]byte("Login failed. Invalid username or password."))
		} else {
			w.Write([]byte("<html><body><h1>WordPress Admin Login</h1><form method='POST'><input name='username' placeholder='User'/><input name='password' type='password' placeholder='Pass'/><button>Login</button></form></body></html>"))
		}

	case "/.env":
		// ¡El cebo perfecto! Claves de base de datos y AWS falsas
		w.Header().Set("Content-Type", "text/plain")
		w.Write([]byte("DB_HOST=127.0.0.1\nDB_USER=root\nDB_PASS=S3cr3t_P@ssw0rd_2026\nAWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE\nAWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"))

	case "/wp-config.php.bak":
		// Backup falso de WordPress
		w.Header().Set("Content-Type", "text/plain")
		w.Write([]byte("<?php\ndefine('DB_NAME', 'wordpress_db');\ndefine('DB_USER', 'admin_wp');\ndefine('DB_PASSWORD', 'admin123456');\n?>"))

	case "/phpmyadmin":
		// Panel falso bloqueado para generar intriga
		w.Write([]byte("<html><body><h1>phpMyAdmin Access Denied</h1><p>Client IP rejected by firewall rules.</p></body></html>"))

	default:
		w.WriteHeader(http.StatusNotFound)
		w.Write([]byte("404 Not Found\n"))
	}

	// Registrar el ataque (ignoramos el favicon para no ensuciar los logs)
	if path != "/favicon.ico" {
		logAttack(ip, method, path, payload)
	}
}

func logAttack(ip, method, path, payload string) {
	logEntry := AttackLog{
		Timestamp: time.Now().Format(time.RFC3339),
		IP:        ip,
		Port:      "80", 
		Method:    method,
		Path:      path,
		Payload:   payload,
		Sensor:    "HTTP",
	}

	logJSON, _ := json.Marshal(logEntry)
	
// Guardar en la ruta que vigila el piloto automático de Python
	os.MkdirAll("sensor-http/logs", os.ModePerm)
	f, _ := os.OpenFile("sensor-http/logs/web_attacks.jsonl", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	defer f.Close()
	f.WriteString(string(logJSON) + "\n")
}
