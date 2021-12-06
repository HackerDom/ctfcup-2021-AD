package common

import (
	"errors"
	"github.com/gomodule/redigo/redis"
	"log"
	"os"
	"strconv"
)

type RedisStorage struct {
	redisPool *redis.Pool
	prefix    string
}

func (rs *RedisStorage) Init(hostname string, number int, prefix string) {
	log.Println("Init redis store with prefix: " + prefix + " and number: " + strconv.Itoa(number))
	rs.prefix = prefix
	rs.redisPool = &redis.Pool{
		MaxIdle:   80,
		MaxActive: 12000,
		Dial: func() (redis.Conn, error) {
			conn, err := redis.Dial("tcp", hostname+":6379", redis.DialDatabase(number))
			if err != nil {
				log.Printf("ERROR: fail Init redis pool: %s", err.Error())
				os.Exit(1)
			}
			return conn, err
		},
	}
}

func (rs *RedisStorage) Set(key, value string) error {
	conn := rs.redisPool.Get()
	defer conn.Close()

	if _, err := conn.Do("SET", rs.prefix+"/"+key, value); err != nil {
		return err
	}
	return nil
}

func (rs *RedisStorage) Get(key string) (*string, error) {
	conn := rs.redisPool.Get()
	defer conn.Close()

	value, err := conn.Do("GET", rs.prefix+"/"+key)
	if err != nil {
		return nil, err
	}
	if value == nil {
		return nil, nil
	}

	switch value := value.(type) {
	case []byte:
		vl := string(value)
		return &vl, nil
	case string:
		return &value, nil
	default:
		return nil, errors.New("can not take value")
	}
}

func (rs *RedisStorage) Del(key string) error {
	conn := rs.redisPool.Get()
	defer conn.Close()

	if _, err := conn.Do("DEL", rs.prefix+"/"+key); err != nil {
		return err
	}
	return nil
}

func (rs *RedisStorage) IncUserCounter(key string) (uint64, error) {
	conn := rs.redisPool.Get()
	defer conn.Close()

	err := conn.Send("MULTI")
	if err != nil {
		return 0, err
	}

	err = conn.Send("INCR", rs.prefix+"/"+key)
	if err != nil {
		return 0, err
	}

	err = conn.Send("GET", rs.prefix+"/"+key)
	if err != nil {
		return 0, err
	}

	value, err := redis.Values(conn.Do("EXEC"))
	if err != nil {
		return 0, err
	}

	var count uint64
	if _, err = redis.Scan(value, &count); err != nil {
		return 0, err
	}
	return count, nil
}
