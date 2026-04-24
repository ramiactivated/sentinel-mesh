package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"net"
	"os"
	"strings"
	"time"
)

// Estructura de datos que espera nuestro "Cerebro"
type AttackLog struct {
	Timestamp string `json:"timestamp"`
	IP        string `json:"ip"`
	Port      string `json:"port"`
	Username  string `json:"username"`
	Password  string `json:"password"`
	Sensor    string `json:"sensor_type"`
}

func main() {
	// Usamos el puerto 2323 para pruebas locales (el puerto 23 real requiere ser admin)
	port := ":2323" 
	listener, err := net.Listen("tcp", port)
	if err != nil {
		fmt.Println("❌ Error iniciando Telnet Sensor:", err)
		return
	}
	defer listener.Close()

	fmt.Println("🕷️ Sensor Telnet (IoT Honeypot) escuchando en el puerto", port)

	for {
		conn, err := listener.Accept()
		if err != nil {
			continue
		}
		// Goroutine: permite manejar múltiples atacantes a la vez
		go handleConnection(conn) 
	}
}

func handleConnection(conn net.Conn) {
	defer conn.Close()
	ip := strings.Split(conn.RemoteAddr().String(), ":")[0]

	// 1. Simular el "Banner" de un router vulnerable
	conn.Write([]byte("BusyBox v1.36.1 (Debian) built-in shell (ash)\n"))
	conn.Write([]byte("Enter 'help' for a list of built-in commands.\n\n"))

	// 2. Pedir Usuario
	conn.Write([]byte("login: "))
	scanner := bufio.NewScanner(conn)
	scanner.Scan()
	username := strings.TrimSpace(scanner.Text())

	// 3. Pedir Contraseña
	conn.Write([]byte("Password: "))
	scanner.Scan()
	password := strings.TrimSpace(scanner.Text())

	// 4. Simular que falla el acceso y echar al atacante
	conn.Write([]byte("\nLogin incorrect\n"))

	// 5. Registrar la captura
	logAttack(ip, username, password)
}

func logAttack(ip, username, password string) {
	logEntry := AttackLog{
		Timestamp: time.Now().Format(time.RFC3339),
		IP:        ip,
		Port:      "23", 
		Username:  username,
		Password:  password,
		Sensor:    "TELNET",
	}

	logJSON, _ := json.Marshal(logEntry)
	
	// Imprimir en consola y guardar en un archivo para el Cerebro
	fmt.Println("🚨 CAZADO:", string(logJSON))
	
	f, _ := os.OpenFile("telnet_attacks.json", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	defer f.Close()
	f.WriteString(string(logJSON) + "\n")
}
