package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"net"

	"golang.org/x/crypto/ssh"
)

func main() {
	config := &ssh.ServerConfig{
		PasswordCallback: func(c ssh.ConnMetadata, pass []byte) (*ssh.Permissions, error) {
			// Registramos el ataque en la consola
			fmt.Printf("[ALERTA] Intento de acceso -> IP: %s | Usuario: %s | Contraseña: %s\n", c.RemoteAddr(), c.User(), string(pass))
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
	fmt.Println("🚀 Sentinel Sensor-SSH escuchando en el puerto 2222...")

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
