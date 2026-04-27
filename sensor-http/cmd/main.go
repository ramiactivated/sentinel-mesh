package main

import (
	"encoding/json"
	"fmt"
	"net"
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

	fmt.Println("🕸️  Sensor HTTP (Web Labyrinth) escuchando en el puerto", port)
	err := http.ListenAndServe(port, nil)
	if err != nil {
		fmt.Println("❌ Error iniciando Web Sensor:", err)
	}
}

func handleRequest(w http.ResponseWriter, r *http.Request) {
	// --- CORRECCIÓN DE IP ---
	// Usamos net.SplitHostPort para separar la IP del puerto correctamente
	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		host = r.RemoteAddr // Fallback por si no hay puerto
	}

	// Limpiamos corchetes de IPv6 y normalizamos localhost
	ip := strings.Trim(host, "[]")
	if ip == "::1" {
		ip = "127.0.0.1"
	}
	// ------------------------

	path := r.URL.Path
	method := r.Method
	payload := ""

	if method == "POST" {
		r.ParseForm()
		payload = r.Form.Encode()
	}

	// 🎭 EL LABERINTO: Respuestas personalizadas
	switch path {
	case "/wp-admin":
		if method == "POST" {
			w.Write([]byte("Login failed. Invalid username or password."))
		} else {
			w.Write([]byte("<html><body><h1>WordPress Admin Login</h1><form method='POST'><input name='username' placeholder='User'/><input name='password' type='password' placeholder='Pass'/><button>Login</button></form></body></html>"))
		}

	case "/.env":
		w.Header().Set("Content-Type", "text/plain")
		w.Write([]byte("DB_HOST=127.0.0.1\nDB_USER=root\nDB_PASS=S3cr3t_P@ssw0rd_2026\nAWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE\nAWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"))

	case "/wp-config.php.bak":
		w.Header().Set("Content-Type", "text/plain")
		w.Write([]byte("<?php\ndefine('DB_NAME', 'wordpress_db');\ndefine('DB_USER', 'admin_wp');\ndefine('DB_PASSWORD', 'admin123456');\n?>"))

	case "/phpmyadmin":
		w.Write([]byte("<html><body><h1>phpMyAdmin Access Denied</h1><p>Client IP rejected by firewall rules.</p></body></html>"))

	default:
		w.WriteHeader(http.StatusNotFound)
		w.Write([]byte("404 Not Found\n"))
	}

	// Registrar el ataque
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

	// Guardar en la ruta de logs
	os.MkdirAll("logs", os.ModePerm)
	f, _ := os.OpenFile("logs/web_attacks.jsonl", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)

	defer f.Close()
	f.WriteString(string(logJSON) + "\n")
}
