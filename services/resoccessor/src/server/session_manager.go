package server

import (
	"resoccessor/common"
)

type SessionManager struct {
	redisStorage *common.RedisStorage
}

func (sm *SessionManager) Init(redisHostname string) {
	sm.redisStorage = &common.RedisStorage{}
	sm.redisStorage.Init(redisHostname, 0, "session")
}

func (sm *SessionManager) Create(username string) (string, error) {
	salt := common.GenString(32)
	secret := common.BaseHash(username + salt)

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

	return common.BaseHash(username+*salt) == secret
}
