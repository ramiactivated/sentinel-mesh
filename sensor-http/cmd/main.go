package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"time"
)

// Estructura para registrar los ataques web
type WebAttackLog struct {
	Timestamp string `json:"timestamp"`
	IP        string `json:"ip"`
	Method    string `json:"method"`
	Path      string `json:"path"`
	Payload   string `json:"payload"`
	UserAgent string `json:"user_agent"`
}

func logAttack(w http.ResponseWriter, r *http.Request) {
	// Parsear los datos si es un POST (como un intento de login)
	r.ParseForm()

	attack := WebAttackLog{
		Timestamp: time.Now().Format(time.RFC3339),
		IP:        r.RemoteAddr,
		Method:    r.Method,
		Path:      r.URL.Path,
		Payload:   r.Form.Encode(), // Captura contraseñas o inyecciones SQL
		UserAgent: r.UserAgent(),
	}

	jsonData, _ := json.Marshal(attack)
	fmt.Printf("🕸️ [WEB ATTACK] %s\n", string(jsonData))

	// Guardar en el log
	f, err := os.OpenFile("logs/web_attacks.jsonl", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err == nil {
		f.WriteString(string(jsonData) + "\n")
		f.Close()
	}

	// TÁCTICA DE ENGAÑO: Falsificamos la cabecera del servidor
	w.Header().Set("Server", "Apache/2.4.41 (Ubuntu)")

	// Mostrar un falso panel si es GET, o un error falso si es POST
	if r.Method == "GET" {
		html := `
		<html><head><title>Admin Login</title></head>
		<body style="font-family: Arial; padding: 50px; text-align: center;">
			<h2>System Administration Portal</h2>
			<form method='POST'>
				<input type='text' name='username' placeholder='Username' required /><br><br>
				<input type='password' name='password' placeholder='Password' required /><br><br>
				<input type='submit' value='Login' />
			</form>
		</body></html>`
		fmt.Fprintf(w, html)
	} else {
		// Retrasamos la respuesta 2 segundos para hacer perder tiempo al bot
		time.Sleep(2 * time.Second)
		fmt.Fprintf(w, "Database Connection Error: Invalid credentials.")
	}
}

func main() {
	// Capturamos ABSOLUTAMENTE TODAS las rutas con "/"
	http.HandleFunc("/", logAttack)

	fmt.Println("🚀 Sentinel Sensor-HTTP escuchando en el puerto 8080...")
	
	// Levantamos el servidor
	err := http.ListenAndServe("0.0.0.0:8080", nil)
	if err != nil {
		fmt.Println("Error iniciando el servidor:", err)
	}
}
