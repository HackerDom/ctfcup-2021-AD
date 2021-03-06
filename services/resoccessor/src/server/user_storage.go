package server

import (
	"errors"
	"resoccessor/common"
)

type UserStorage struct {
	redisStorage *common.RedisStorage
}

func (us *UserStorage) Init(redisHostname string) {
	us.redisStorage = &common.RedisStorage{}
	us.redisStorage.Init(redisHostname, 1, "user")
}

func (us *UserStorage) Register(username, password string) (error, bool) {
	res, err := us.redisStorage.Get(common.Base(username))
	if err != nil {
		return err, false
	}

	if res != nil {
		return errors.New("user is already exists"), true
	}

	if err = us.redisStorage.Set(common.Base(username), common.BaseHash(password)); err != nil {
		return err, false
	}
	return nil, false
}

func (us *UserStorage) Validate(username, password string) bool {
	passwordBaseHash, err := us.redisStorage.Get(common.Base(username))
	if err != nil || passwordBaseHash == nil {
		return false
	}

	return common.BaseHash(password) == *passwordBaseHash
}

func (us *UserStorage) incTokenCounter(username string) (uint64, error) {
	if count, err := us.redisStorage.IncUserCounter(username); err != nil {
		return 0, err
	} else {
		return count, nil
	}
}
