package server

import (
	"math/rand"
)


const alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


func GenString(n int) string {
	b := make([]byte, n)
	for i := range b {
		b[i] = alpha[rand.Intn(len(alpha))]
	}
	return string(b)
}


type SessionManager struct {
	redisStorage *RedisStorage
}


func (sm *SessionManager) Init() {
	sm.redisStorage = &RedisStorage{}
	sm.redisStorage.Init(0, "session")
}


func (sm *SessionManager) Create(username string) (string, error) {
	salt := GenString(32)
	secret := baseHash(username + salt)

	if err := sm.redisStorage.Set(username, salt); err != nil {
		return "", err
	}

	if err := sm.redisStorage.Set(username, salt); err != nil {
		return "", err
	}
	return secret, nil
}



func (sm *SessionManager) Delete(username string) {
	_ = sm.redisStorage.Del(username)
}


func (sm *SessionManager) Validate(username, secret string) bool {
	salt, err := sm.redisStorage.Get(username)
	if err != nil || salt == nil {
		return false
	}

	return baseHash(username + *salt) == secret
}
