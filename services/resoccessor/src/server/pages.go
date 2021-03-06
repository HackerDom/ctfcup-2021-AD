package server

import (
	"fmt"
	"html/template"
	"log"
	"net/http"
	"path"
	"sort"
	"strconv"
)

type TableRow struct {
	Index        int
	Token        string
	UserId       uint64
	ResourceUUID string
}

type IndexState struct {
	Username        string
	Table           []TableRow
	TableHeight     int
	TokensHeight    int
	ResourcesHeight int
}

func HandleRegisterAdminPage(env *Env, w http.ResponseWriter, r *http.Request, tmpl *template.Template) {
	if err := tmpl.Execute(w, nil); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}

const redirectHtml = `<html><head><script>location.href="%s";</script></head><body></body></html>`

func redirect(w http.ResponseWriter, url string) {
	_, _ = w.Write([]byte(fmt.Sprintf(redirectHtml, url)))
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
			redirect(w, "/login_page")
			return
		}
		usernameCookie, err := r.Cookie("username")
		if err != nil {
			log.Println("can not get username: " + err.Error())
			redirect(w, "/login_page")
			return
		}

		if !env.sm.Validate(usernameCookie.Value, secretCookie.Value) {
			log.Println("bad auth")
			redirect(w, "/login_page")
			return
		}
		handler(env, w, r, tmpl, usernameCookie.Value)
	}
}

func Max(x, y int) int {
	if x < y {
		return y
	}
	return x
}

func UIntMax(x, y int) int {
	if x < y {
		return y
	}
	return x
}

func HandleIndexPage(env *Env, w http.ResponseWriter, r *http.Request, tmpl *template.Template, username string) {
	tokens, err := env.owner2tokens.List(username)
	if err != nil {
		log.Println("Can not render index page due to tokens listing error: " + err.Error())
		w.WriteHeader(400)
		return
	}

	resourceUuids, err := env.resources.List(username)
	if err != nil {
		log.Println("Can not render index page due to resources listing error: " + err.Error())
		w.WriteHeader(400)
		return
	}

	table := make([]TableRow, Max(len(tokens), len(resourceUuids)))
	for i := 0; i < len(tokens); i++ {
		rawCount, err := env.owner2tokens.Get(username, tokens[i])
		if err != nil {
			log.Println("Can not render index page due to token reading error: " + err.Error())
			w.WriteHeader(400)
			return
		}

		count, err := strconv.ParseUint(string(rawCount), 10, 64)
		if err != nil {
			log.Println("Can not render index page due to count parsing error: " + err.Error())
			w.WriteHeader(400)
			return
		}

		table[i].Token = tokens[i]
		table[i].UserId = count
	}
	sort.Slice(table, func(i, j int) bool {
		if table[j].UserId == 0 {
			return true
		}
		if table[i].UserId == 0 {
			return false
		}
		return table[i].UserId < table[j].UserId
	})
	for i := 0; i < len(table); i++ {
		table[i].Index = i
	}
	for i := 0; i < len(resourceUuids); i++ {
		table[i].ResourceUUID = resourceUuids[i]
	}

	tableHeight := Max(len(tokens), len(resourceUuids))

	if err := tmpl.Execute(w, &IndexState{
		username,
		table,
		tableHeight,
		len(tokens),
		len(resourceUuids),
	}); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}

func HandleGetResourcePage(env *Env, w http.ResponseWriter, r *http.Request, tmpl *template.Template) {
	if err := tmpl.Execute(w, nil); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}
