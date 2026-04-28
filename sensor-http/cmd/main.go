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
	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		host = r.RemoteAddr
	}

	ip := strings.Trim(host, "[]")
	if ip == "::1" {
		ip = "127.0.0.1"
	}

	path := r.URL.Path
	method := r.Method
	payload := ""

	if method == "POST" {
		r.ParseForm()
		payload = r.Form.Encode()
	}

	// 🎭 EL LABERINTO: Respuestas personalizadas
	switch path {
	// Añadimos wp-login.php y wp-admin para que no den 404
	case "/wp-admin", "/wp-login.php", "/login":
		if method == "POST" {
			w.Header().Set("Content-Type", "text/html")
			w.Write([]byte("<html><body style='font-family:sans-serif; background:#f1f1f1; display:flex; justify-content:center; align-items:center; height:100vh;'><div style='background:white; padding:20px; border:1px solid #ccd0d4; box-shadow:0 1px 3px rgba(0,0,0,.04);'><strong>ERROR</strong>: The password you entered for the username admin is incorrect.</div></body></html>"))
		} else {
			// HTML con estilo de WordPress
			fmt.Fprintf(w, `
				<html>
				<body style="background:#f1f1f1; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen-Sans,Ubuntu,Cantarell,Helvetica Neue,sans-serif;">
					<div style="width:320px; margin:7% auto; background:#fff; padding:26px; box-shadow:0 1px 3px rgba(0,0,0,.13);">
						<div style="text-align:center; margin-bottom:20px;">
							<img src="https://upload.wikimedia.org/wikipedia/commons/2/20/WordPress_logo.svg" width="80">
						</div>
						<form method="POST">
							<label>Username</label><br>
							<input name="log" style="width:100%%; padding:10px; margin:5px 0 15px; border:1px solid #ddd;" type="text"><br>
							<label>Password</label><br>
							<input name="pwd" style="width:100%%; padding:10px; margin:5px 0 15px; border:1px solid #ddd;" type="password"><br>
							<button style="background:#2271b1; color:white; border:none; padding:10px 15px; cursor:pointer; width:100%%; border-radius:3px;">Log In</button>
						</form>
					</div>
				</body>
				</html>
			`)
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
		Port:      "8080",
		Method:    method,
		Path:      path,
		Payload:   payload,
		Sensor:    "HTTP",
	}

	logJSON, _ := json.Marshal(logEntry)

	os.MkdirAll("logs", os.ModePerm)
	f, _ := os.OpenFile("logs/web_attacks.jsonl", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)

	defer f.Close()
	f.WriteString(string(logJSON) + "\n")
}
