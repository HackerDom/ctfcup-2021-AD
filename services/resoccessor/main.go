package main

import (
	"encoding/json"
	"fmt"
	"github.com/google/uuid"
	"io"
	"log"
	"net/http"
	"sandbox/schema"
	"sandbox/server"
	"strconv"
)


type Env struct {
	us *server.UserStorage
	sm *server.SessionManager
	userIdMap *server.RedisStorage
	uuid2owners *server.RedisStorage
	resources *server.FileStorage
}


func (env *Env) Init() {
	env.us = &server.UserStorage{}
	env.us.Init()

	env.sm = &server.SessionManager{}
	env.sm.Init()

	env.userIdMap = &server.RedisStorage{}
	env.userIdMap.Init(2, "idmap")

	env.uuid2owners = &server.RedisStorage{}
	env.uuid2owners.Init(2, "uuid2owners")

	env.resources = &server.FileStorage{}
	env.resources.Init("storage")
}


func wrapper(
	env *Env,
	handler func (env *Env, w http.ResponseWriter, r *http.Request),
	) func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {handler(env, w, r)}
}



func handleRegisterAdmin(env *Env, w http.ResponseWriter, r *http.Request) {
	data, err := io.ReadAll(r.Body)
	if err != nil {
		log.Println("can not register user: " + err.Error())
		w.WriteHeader(400)
		return
	}
	var userPair server.UserPair
	if err := json.Unmarshal(data, &userPair); err != nil {
		log.Println("can not register user: " + err.Error())
		w.WriteHeader(400)
		return
	}
	if !server.IsValidUser(&userPair) {
		log.Println("can not register user: invalid user pair")
		w.WriteHeader(400)
		return
	}
	if err := env.us.Register(userPair.Name, userPair.Password); err != nil {
		log.Println("can not register user: " + err.Error())
		w.WriteHeader(400)
		return
	}
	secret, err := env.sm.Create(userPair.Name)
	if err != nil {
		log.Println("can not Create session for user: " + err.Error())
		w.WriteHeader(400)
		return
	}
	http.SetCookie(w, &http.Cookie{
		Name: "secret",
		Value: secret,
	})
	http.SetCookie(w, &http.Cookie{
		Name: "username",
		Value: userPair.Name,
	})
}


func handleLoginAdmin(env *Env, w http.ResponseWriter, r *http.Request) {
	data, err := io.ReadAll(r.Body)
	if err != nil {
		log.Println("can not login user: " + err.Error())
		w.WriteHeader(400)
		return
	}
	var userPair server.UserPair
	if err := json.Unmarshal(data, &userPair); err != nil {
		log.Println("can not login user: " + err.Error())
		w.WriteHeader(400)
		return
	}
	if !server.IsValidUser(&userPair) {
		log.Println("can not login user: invalid user pair")
		w.WriteHeader(400)
		return
	}
	if !env.us.Validate(userPair.Name, userPair.Password) {
		log.Println("can not login user: invalid user pair")
		w.WriteHeader(400)
		return
	}
	secret, err := env.sm.Create(userPair.Name)
	if err != nil {
		log.Println("can not Create session for user: " + err.Error())
		w.WriteHeader(400)
		return
	}
	http.SetCookie(w, &http.Cookie{
		Name: "secret",
		Value: secret,
	})
	http.SetCookie(w, &http.Cookie{
		Name: "username",
		Value: userPair.Name,
	})
}


type TokenResponse struct {
	Token string `json:"token"`
	Count uint64 `json:"count"`
}


func handleGenToken(env *Env, w http.ResponseWriter, r *http.Request, username string) {
	token := server.GenString(32)
	count, err := env.userIdMap.IncUserCounter(username)
	if err != nil {
		log.Println("can not gen token due to error: " + err.Error())
		w.WriteHeader(500)
		return
	}
	if err := env.userIdMap.Set(username + "/" + token, strconv.FormatUint(count, 10)); err != nil {
		log.Println("can not gen token due to error: " + err.Error())
		w.WriteHeader(500)
		return
	}

	data, err := json.Marshal(TokenResponse{
		token,
		count,
	})
	if err != nil {
		log.Println("can not gen token due to error: " + err.Error())
		w.WriteHeader(500)
		return
	}
	if _, err = w.Write(data); err != nil {
		log.Println("can not gen token due to error: " + err.Error())
		w.WriteHeader(500)
		return
	}
}


func handleUploadResource(env *Env, w http.ResponseWriter, r *http.Request, username string) {
	data, err := io.ReadAll(r.Body)
	if err != nil {
		log.Println("Can not upload resource due error: " + err.Error())
		w.WriteHeader(500)
		return
	}
	resourceUuid := uuid.New().String()
	if err := env.resources.Put(username, resourceUuid, data); err != nil {
		log.Println("Can not upload resource due error: " + err.Error())
		w.WriteHeader(500)
		return
	}
	if err := env.uuid2owners.Set(resourceUuid, username); err != nil {
		log.Println("Can not upload resource due error: " + err.Error())
		w.WriteHeader(500)
		return
	}
	if _, err := w.Write([]byte(resourceUuid)); err != nil {
		log.Println("Can not return resource uuid due error: " + err.Error())
		w.WriteHeader(500)
		return
	}
}


func handleListResources(env *Env, w http.ResponseWriter, r *http.Request, username string) {
	resources, err := env.resources.List(username)
	if err != nil {
		log.Println("Can not list resources due error: " + err.Error())
		w.WriteHeader(500)
		return
	}
	data, err := json.Marshal(resources)
	if err != nil {
		log.Println("Can not list resources due error: " + err.Error())
		w.WriteHeader(500)
		return
	}
	if _, err := w.Write(data); err != nil {
		log.Println("Can not list resources due error: " + err.Error())
		w.WriteHeader(500)
		return
	}
}


func checkAuth(handler func (env *Env, w http.ResponseWriter, r *http.Request, username string)) func (env *Env, w http.ResponseWriter, r *http.Request) {
	return func (env *Env, w http.ResponseWriter, r *http.Request) {
		secretCookie, err := r.Cookie("secret")
		if err != nil {
			log.Println("can not get token: " + err.Error())
			w.WriteHeader(400)
			return
		}
		usernameCookie, err := r.Cookie("username")
		if err != nil {
			log.Println("can not get token: " + err.Error())
			w.WriteHeader(400)
			return
		}

		if !env.sm.Validate(usernameCookie.Value, secretCookie.Value) {
			log.Println("bad auth")
			w.WriteHeader(400)
			return
		}
		handler(env, w, r, usernameCookie.Value)
	}
}


func main() {
	schema.Do()
	return
	env := &Env{}
	env.Init()

	http.HandleFunc("/register", wrapper(env, handleRegisterAdmin))
	http.HandleFunc("/login", wrapper(env, handleLoginAdmin))
	http.HandleFunc("/gen_token", wrapper(env, checkAuth(handleGenToken)))
	http.HandleFunc("/upload_resource", wrapper(env, checkAuth(handleUploadResource)))
	http.HandleFunc("/list_resources", wrapper(env, checkAuth(handleListResources)))
	log.Fatal(http.ListenAndServe(fmt.Sprintf("%s:%d", "127.0.0.1", 8080), nil))
}
