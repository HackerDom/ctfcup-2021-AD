package main

import (
	"fmt"
	"log"
	"net/http"
	"resoccessor/server"
)

func main() {
	env := &server.Env{}
	env.Init("localhost")

	http.HandleFunc("/register", server.Wrapper(env, server.HandleRegisterAdmin))
	http.HandleFunc("/login", server.Wrapper(env, server.HandleLoginAdmin))
	http.HandleFunc("/gen_token", server.Wrapper(env, server.CheckAuth(server.HandleGenToken)))
	http.HandleFunc("/upload_resource", server.Wrapper(env, server.CheckAuth(server.HandleUploadResource)))
	http.HandleFunc("/list_resources", server.Wrapper(env, server.CheckAuth(server.HandleListResources)))
	http.HandleFunc("/set_schema/", server.Wrapper(env, server.CheckAuth(server.HandleSetSchema)))
	http.HandleFunc("/get_resource/", server.Wrapper(env, server.HandleGetResource))

	http.HandleFunc("/", server.Wrapper(env, server.WithTemplate("index.html", server.CheckPageAuth(server.HandleIndexPage))))
	http.HandleFunc("/register_page", server.Wrapper(env, server.WithTemplate("register.html", server.HandleRegisterAdminPage)))
	http.HandleFunc("/login_page", server.Wrapper(env, server.WithTemplate("login.html", server.HandleRegisterAdminPage)))

	fs := http.FileServer(http.Dir("./server/static"))
	http.Handle("/static/", http.StripPrefix("/static/", fs))

	log.Fatal(http.ListenAndServe(fmt.Sprintf("%s:%d", "127.0.0.1", 3000), nil))
}
