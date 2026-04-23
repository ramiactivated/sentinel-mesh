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

// Definimos la estructura de cómo se verá nuestro log en JSON
type AttackLog struct {
	Timestamp string `json:"timestamp"`
	IP        string `json:"ip"`
	Username  string `json:"username"`
	Password  string `json:"password"`
}

func main() {
	config := &ssh.ServerConfig{
		PasswordCallback: func(c ssh.ConnMetadata, pass []byte) (*ssh.Permissions, error) {
			// 1. Crear el objeto de ataque con la hora exacta
			attack := AttackLog{
				Timestamp: time.Now().Format(time.RFC3339),
				IP:        c.RemoteAddr().String(),
				Username:  c.User(),
				Password:  string(pass),
			}

			// 2. Convertir el objeto a formato JSON
			jsonData, err := json.Marshal(attack)
			if err != nil {
				return nil, nil
			}

			// 3. Imprimir en consola para nosotros
			fmt.Printf("👾 [ATAQUE CAPTURADO] %s\n", string(jsonData))

			// 4. Guardar silenciosamente en el archivo (modo 'append' para no borrar lo anterior)
			f, err := os.OpenFile("logs/attacks.jsonl", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
			if err == nil {
				f.WriteString(string(jsonData) + "\n")
				f.Close()
			}

			return nil, nil
		},
	}

	privateBytes, err := ioutil.ReadFile("keys/server.key")
	if err != nil {
		log.Fatal("Error cargando la clave privada: ", err)
	}
	private, err := ssh.ParsePrivateKey(privateBytes)
	if err != nil {
		log.Fatal("Error parseando la clave: ", err)
	}
	config.AddHostKey(private)

	listener, err := net.Listen("tcp", "0.0.0.0:2222")
	if err != nil {
		log.Fatal("Error al iniciar el listener: ", err)
	}
	fmt.Println("🚀 Sentinel Sensor-SSH escuchando en el puerto 2222... (Guardando en JSON)")

	for {
		nConn, err := listener.Accept()
		if err != nil {
			continue
		}

		go func(conn net.Conn) {
			_, chans, reqs, err := ssh.NewServerConn(conn, config)
			if err != nil {
				return
			}
			go ssh.DiscardRequests(reqs)
			for newChannel := range chans {
				newChannel.Reject(ssh.Prohibited, "No shell allowed")
			}
		}(nConn)
	}
}
