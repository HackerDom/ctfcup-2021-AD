package main

import (
	"encoding/json"
	"fmt"
	"github.com/google/uuid"
	"io"
	"log"
	"net/http"
	"resoccessor/common"
	"resoccessor/schema"
	"resoccessor/server"
	"strconv"
)

type Env struct {
	us           *server.UserStorage
	sm           *server.SessionManager
	userIdMap    *common.RedisStorage
	uuid2owners  *common.RedisStorage
	token2owners *common.RedisStorage
	resources    *common.FileStorage
	schema       *schema.Schema
}

func (env *Env) Init(redisHostname string) {
	env.us = &server.UserStorage{}
	env.us.Init(redisHostname)

	env.sm = &server.SessionManager{}
	env.sm.Init(redisHostname)

	env.userIdMap = &common.RedisStorage{}
	env.userIdMap.Init(redisHostname, 2, "idmap")

	env.uuid2owners = &common.RedisStorage{}
	env.uuid2owners.Init(redisHostname, 2, "uuid2owners")

	env.token2owners = &common.RedisStorage{}
	env.token2owners.Init(redisHostname, 2, "token2owners")

	env.resources = &common.FileStorage{}
	env.resources.Init("resources")

	env.schema = &schema.Schema{}
	env.schema.Init("schemas")
}

func wrapper(
	env *Env,
	handler func(env *Env, w http.ResponseWriter, r *http.Request),
) func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) { handler(env, w, r) }
}

func handleRegisterAdmin(env *Env, w http.ResponseWriter, r *http.Request) {
	data, err := io.ReadAll(r.Body)
	if err != nil {
		log.Println("can not register user: " + err.Error())
		w.WriteHeader(400)
		return
	}
	var userPair common.UserPair
	if err := json.Unmarshal(data, &userPair); err != nil {
		log.Println("can not register user: " + err.Error())
		w.WriteHeader(400)
		return
	}
	if !common.IsValidUser(&userPair) {
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
		log.Println("can not create session for user: " + err.Error())
		w.WriteHeader(400)
		return
	}
	http.SetCookie(w, &http.Cookie{
		Name:  "secret",
		Value: secret,
	})
	http.SetCookie(w, &http.Cookie{
		Name:  "username",
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
	var userPair common.UserPair
	if err := json.Unmarshal(data, &userPair); err != nil {
		log.Println("can not login user: " + err.Error())
		w.WriteHeader(400)
		return
	}
	if !common.IsValidUser(&userPair) {
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
		Name:  "secret",
		Value: secret,
	})
	http.SetCookie(w, &http.Cookie{
		Name:  "username",
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
	if err := env.userIdMap.Set(username+"/"+token, strconv.FormatUint(count, 10)); err != nil {
		log.Println("can not gen token due to error: " + err.Error())
		w.WriteHeader(500)
		return
	}

	if err := env.token2owners.Set(token, username); err != nil {
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

func handleSetSchema(env *Env, w http.ResponseWriter, r *http.Request, username string) {
	data, err := io.ReadAll(r.Body)
	if err != nil {
		log.Println("Can not set schema due error: " + err.Error())
		w.WriteHeader(400)
		return
	}
	resourceUuid := r.URL.Path[len("/set_schema/"):]

	if !env.resources.Exists(username, resourceUuid) {
		log.Println("No such resource: " + resourceUuid)
		w.WriteHeader(400)
		return
	}

	if err = env.schema.Save(username, resourceUuid, string(data)); err != nil {
		log.Println("Can not set schema due error: " + err.Error())
		w.WriteHeader(400)
		return
	}
}

func handleGetResource(env *Env, w http.ResponseWriter, r *http.Request) {
	resourceUuid := r.URL.Path[len("/get_resource/"):]

	token := r.URL.Query().Get("token")
	if len(token) != 32 {
		log.Println("Invalid token")
		w.WriteHeader(400)
		return
	}
	username, err := env.token2owners.Get(token)
	if err != nil {
		log.Println("Can not get resource due error: " + err.Error())
		w.WriteHeader(400)
		return
	}
	if username == nil {
		log.Println("Can not get resource, username doesnt contains in token2owners")
		w.WriteHeader(400)
		return
	}
	rawUserId, err := env.userIdMap.Get(*username + "/" + token)
	if err != nil {
		log.Println("Can not get resource due error: " + err.Error())
		w.WriteHeader(400)
		return
	}

	userId, err := strconv.ParseUint(*rawUserId, 10, 64)
	if err != nil {
		log.Println("Can not get resource due error: " + err.Error())
		w.WriteHeader(400)
		return
	}

	if ok := env.schema.Validate(*username, resourceUuid, userId); !ok {
		log.Printf("User %d has no access to resource %s\n", userId, resourceUuid)
		w.WriteHeader(404)
		return
	}

	data, err := env.resources.Get(*username, resourceUuid)
	if err != nil {
		log.Println("Can not get resource due error: " + err.Error())
		w.WriteHeader(400)
		return
	}

	if _, err := w.Write(data); err != nil {
		log.Println("Can not get resource due error: " + err.Error())
		w.WriteHeader(400)
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

func checkAuth(handler func(env *Env, w http.ResponseWriter, r *http.Request, username string)) func(env *Env, w http.ResponseWriter, r *http.Request) {
	return func(env *Env, w http.ResponseWriter, r *http.Request) {
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
	env := &Env{}
	env.Init("redis")

	http.HandleFunc("/register", wrapper(env, handleRegisterAdmin))
	http.HandleFunc("/login", wrapper(env, handleLoginAdmin))
	http.HandleFunc("/gen_token", wrapper(env, checkAuth(handleGenToken)))
	http.HandleFunc("/upload_resource", wrapper(env, checkAuth(handleUploadResource)))
	http.HandleFunc("/list_resources", wrapper(env, checkAuth(handleListResources)))
	http.HandleFunc("/set_schema/", wrapper(env, checkAuth(handleSetSchema)))
	http.HandleFunc("/get_resource/", wrapper(env, handleGetResource))
	log.Fatal(http.ListenAndServe(fmt.Sprintf("%s:%d", "0.0.0.0", 3000), nil))
}
