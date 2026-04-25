package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net"
	"os"
	"time"

	"golang.org/x/crypto/ssh"
)

type AttackLog struct {
	Timestamp string `json:"timestamp"`
	IP        string `json:"ip"`
	Username  string `json:"username"`
	Password  string `json:"password"`
}

func main() {
	config := &ssh.ServerConfig{
		PasswordCallback: func(c ssh.ConnMetadata, pass []byte) (*ssh.Permissions, error) {
			attack := AttackLog{
				Timestamp: time.Now().Format(time.RFC3339),
				IP:        c.RemoteAddr().String(),
				Username:  c.User(),
				Password:  string(pass),
			}
			
			// Imprimir en pantalla para nosotros
			fmt.Printf("👾 [ATAQUE SSH] Usuario: %s | IP: %s\n", attack.Username, attack.IP)

			// Guardar en el archivo JSON
			file, _ := os.OpenFile("logs/attacks.jsonl", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
			jsonData, _ := json.Marshal(attack)
			file.WriteString(string(jsonData) + "\n")
			file.Close()

			return nil, fmt.Errorf("password rejected for %q", c.User())
		},
	}

	// Cargar la llave privada
	privateBytes, err := ioutil.ReadFile("keys/server.key")
	if err != nil {
		log.Fatal("❌ Error: No se encuentra keys/server.key. Ejecuta ssh-keygen primero.")
	}
	private, _ := ssh.ParsePrivateKey(privateBytes)
	config.AddHostKey(private)

	// Escuchar en el puerto 2222
	listener, err := net.Listen("tcp", "0.0.0.0:2222")
	if err != nil {
		log.Fatal("❌ Error abriendo puerto: ", err)
	}

	fmt.Println("🚀 Sentinel Sensor-SSH escuchando en el puerto 2222...")

	for {
		conn, _ := listener.Accept()
		go func(c net.Conn) {
			_, chans, reqs, err := ssh.NewServerConn(c, config)
			if err != nil {
				// Este mensaje nos dirá si falla el "apretón de manos"
				fmt.Printf("⚠️ Intento de conexión fallido desde %s\n", c.RemoteAddr())
				return
			}
			go ssh.DiscardRequests(reqs)
			for newChannel := range chans {
				newChannel.Reject(ssh.Prohibited, "no shell access")
			}
		}(conn)
	}
}
