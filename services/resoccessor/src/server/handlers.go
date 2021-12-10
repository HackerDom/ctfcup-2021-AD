package server

import (
	"encoding/json"
	"fmt"
	"github.com/google/uuid"
	"io"
	"log"
	"net/http"
	"resoccessor/common"
	"strconv"
)

func Wrapper(
	env *Env,
	handler func(env *Env, w http.ResponseWriter, r *http.Request),
) func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) { handler(env, w, r) }
}

func HandleRegisterAdmin(env *Env, w http.ResponseWriter, r *http.Request) {
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
	if !common.IsValidUserPair(&userPair) {
		log.Println("can not register user: invalid user pair")
		w.WriteHeader(400)
		_, _ = w.Write([]byte("invalid user pair"))
		return
	}
	if err, exists := env.us.Register(userPair.Name, userPair.Password); err != nil {
		w.WriteHeader(400)
		if exists {
			_, _ = w.Write([]byte("user is already exists"))
		}
		log.Println("can not register user: " + err.Error())
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

func HandleLoginAdmin(env *Env, w http.ResponseWriter, r *http.Request) {
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
	if !common.IsValidUserPair(&userPair) {
		log.Println("can not login user: invalid user pair")
		w.WriteHeader(400)
		_, _ = w.Write([]byte("invalid user pair"))
		return
	}
	if !env.us.Validate(userPair.Name, userPair.Password) {
		log.Println("can not login user: invalid user pair")
		w.WriteHeader(400)
		_, _ = w.Write([]byte("invalid user pair"))
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

type TokenResponse struct {
	Token string `json:"token"`
	Count uint64 `json:"count"`
}

func HandleGenToken(env *Env, w http.ResponseWriter, r *http.Request, username string) {
	token := common.GenString(32)
	count, err := env.userIdMap.IncUserCounter(username)
	if err != nil {
		log.Println("can not gen token due to error: " + err.Error())
		w.WriteHeader(500)
		return
	}

	if err := env.owner2tokens.Put(username, token, []byte(strconv.FormatUint(count, 10))); err != nil {
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

func HandleUploadResource(env *Env, w http.ResponseWriter, r *http.Request, username string) {
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

func HandleSetSchema(env *Env, w http.ResponseWriter, r *http.Request, username string) {
	data, err := io.ReadAll(r.Body)
	if err != nil {
		log.Println("Can not set schema due error: " + err.Error())
		w.WriteHeader(400)
		return
	}
	fmt.Println("data")
	fmt.Println(data)
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

func HandleGetResource(env *Env, w http.ResponseWriter, r *http.Request) {
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

	rawUserId, err := env.owner2tokens.Get(*username, token)
	if err != nil {
		log.Println("Can not get resource due error: " + err.Error())
		w.WriteHeader(400)
		return
	}

	userId, err := strconv.ParseUint(string(rawUserId), 10, 64)
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

func HandleListResources(env *Env, w http.ResponseWriter, r *http.Request, username string) {
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

func CheckAuth(handler func(env *Env, w http.ResponseWriter, r *http.Request, username string)) func(env *Env, w http.ResponseWriter, r *http.Request) {
	return func(env *Env, w http.ResponseWriter, r *http.Request) {
		secretCookie, err := r.Cookie("secret")
		if err != nil {
			log.Println("can not get auth: " + err.Error())
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
