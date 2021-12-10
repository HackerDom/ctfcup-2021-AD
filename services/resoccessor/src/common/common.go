package common

import (
	"crypto/md5"
	b64 "encoding/base64"
	"math/rand"
	"os"
	"strings"
	"unicode"
)

const alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

type UserPair struct {
	Name     string `json:"name"`
	Password string `json:"password"`
}

func BaseHash(s string) string {
	data := md5.Sum([]byte(s))
	return b64.StdEncoding.EncodeToString(data[:])
}

func Base(s string) string {
	return b64.StdEncoding.EncodeToString([]byte(s))
}

func IsValidUserPair(userPair *UserPair) bool {
	return len(userPair.Name) > 3 && len(userPair.Name) < 25 && len(userPair.Password) > 3 && len(userPair.Password) < 25
}

func RemoveWhitespaces(str string) string {
	var b strings.Builder
	b.Grow(len(str))
	for _, ch := range str {
		if !unicode.IsSpace(ch) {
			b.WriteRune(ch)
		}
	}
	return b.String()
}

func IsFileExists(path string) bool {
	_, err := os.Stat(path)
	return err == nil
}

func GenString(n int) string {
	b := make([]byte, n)
	for i := range b {
		b[i] = alpha[rand.Intn(len(alpha))]
	}
	return string(b)
}
