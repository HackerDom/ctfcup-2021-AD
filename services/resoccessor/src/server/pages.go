package server

import (
	"html/template"
	"log"
	"net/http"
	"path"
)

type PageState struct {
	Username string
}

func HandleRegisterAdminPage(env *Env, w http.ResponseWriter, r *http.Request, tmpl *template.Template) {
	if err := tmpl.Execute(w, nil); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}

func WithTemplate(
	templateName string,
	handler func(env *Env, w http.ResponseWriter, r *http.Request, tmpl *template.Template),
) func(env *Env, w http.ResponseWriter, r *http.Request) {
	fp := path.Join("server", "templates", templateName)
	tmpl, err := template.ParseFiles(fp)
	if err != nil {
		panic(err.Error())
	}

	return func(env *Env, w http.ResponseWriter, r *http.Request) {
		handler(env, w, r, tmpl)
	}
}

func CheckPageAuth(
	handler func(env *Env, w http.ResponseWriter, r *http.Request, tmpl *template.Template, username string),
) func(env *Env, w http.ResponseWriter, r *http.Request, tmpl *template.Template) {
	return func(env *Env, w http.ResponseWriter, r *http.Request, tmpl *template.Template) {
		secretCookie, err := r.Cookie("secret")
		if err != nil {
			log.Println("can not get secret: " + err.Error())
			http.Redirect(w, r, "/login_page", 302)
			return
		}
		usernameCookie, err := r.Cookie("username")
		if err != nil {
			log.Println("can not get username: " + err.Error())
			w.WriteHeader(400)
			return
		}

		if !env.sm.Validate(usernameCookie.Value, secretCookie.Value) {
			log.Println("bad auth")
			w.WriteHeader(400)
			return
		}
		handler(env, w, r, tmpl, usernameCookie.Value)
	}
}

func HandleIndexPage(env *Env, w http.ResponseWriter, r *http.Request, tmpl *template.Template, username string) {
	if err := tmpl.Execute(w, &PageState{
		username,
	}); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}
