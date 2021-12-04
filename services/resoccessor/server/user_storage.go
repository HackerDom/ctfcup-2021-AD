package server

import (
	"errors"
)

type UserStorage struct {
	redisStorage *RedisStorage
}

func (us *UserStorage) Init() {
	us.redisStorage = &RedisStorage{}
	us.redisStorage.Init(1, "user")
}

func (us *UserStorage) Register(username, password string) error {
	res, err := us.redisStorage.Get(base(username))
	if err != nil {
		return err
	}

	if res != nil {
		return errors.New("user is already exists")
	}

	if err = us.redisStorage.Set(base(username), baseHash(password)); err != nil {
		return err
	}
	return nil
}


func (us *UserStorage) Validate(username, password string) bool {
	passwordBaseHash, err := us.redisStorage.Get(base(username))
	if err != nil {
		return false
	}

	return baseHash(password) == *passwordBaseHash
}


func (us *UserStorage) incTokenCounter(username string) (uint64, error) {
	if count, err := us.redisStorage.IncUserCounter(username); err != nil {
		return 0, err
	} else {
		return count, nil
	}
}
