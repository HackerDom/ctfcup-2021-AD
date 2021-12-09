package server

import (
	"html/template"
	"resoccessor/common"
	"resoccessor/schema"
)

type Context struct {
	username string
	tmpl     template.Template
}

type Env struct {
	us           *UserStorage
	sm           *SessionManager
	userIdMap    *common.RedisStorage
	uuid2owners  *common.RedisStorage
	token2owners *common.RedisStorage
	resources    *common.FileStorage
	schema       *schema.Schema
}

func (env *Env) Init(redisHostname string) {
	env.us = &UserStorage{}
	env.us.Init(redisHostname)

	env.sm = &SessionManager{}
	env.sm.Init(redisHostname)

	env.userIdMap = &common.RedisStorage{}
	env.userIdMap.Init(redisHostname, 2, "idmap")

	env.uuid2owners = &common.RedisStorage{}
	env.uuid2owners.Init(redisHostname, 2, "uuid2owners")

	env.token2owners = &common.RedisStorage{}
	env.token2owners.Init(redisHostname, 2, "token2owners")

	env.resources = &common.FileStorage{}
	env.resources.Init("resources")

	env.schema = &schema.Schema{}
	env.schema.Init("schemas")
}
