package server

import (
	"crypto/md5"
	b64 "encoding/base64"
)


type UserPair struct {
	Name     string `json:"name"`
	Password string `json:"password"`
}


func baseHash(s string) string {
	data := md5.Sum([]byte(s))
	return b64.StdEncoding.EncodeToString(data[:])
}


func base(s string) string {
	return b64.StdEncoding.EncodeToString([]byte(s))
}


func IsValidUser(userPair *UserPair) bool {
	return len(userPair.Name) > 3 && len(userPair.Name) < 25 && len(userPair.Password) > 3 && len(userPair.Password) < 25
}
