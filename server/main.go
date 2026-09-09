package main

import (
	"log"
	"net/http"
)

func main() {
	// init router
	mux := http.NewServeMux()

	mux.HandleFunc("GET /health", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("ok"))
	})

	if err := http.ListenAndServe(":8080", mux); err != nil {
		log.Fatal(err)
	}

}
