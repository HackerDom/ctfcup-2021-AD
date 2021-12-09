package schema

import (
	"fmt"
	"log"
	"os/exec"
	"path"
	"resoccessor/common"
	"strconv"
)

type Schema struct {
	storage *common.FileStorage
}

func (s *Schema) Init(dir string) {
	s.storage = &common.FileStorage{}
	s.storage.Init(dir)
}

func getSchemaPath(subdir, filename string) string {
	return path.Join("schemas", subdir, filename+".bin")
}

func (s *Schema) Save(subdir, filename, rawSchema string) error {
	s.storage.EnsureSubdir(subdir)
	fmt.Printf("%s %s %s %s\n", "schema/bin/schema", "dump", path.Join("schemas", subdir, filename+".bin"), common.RemoveWhitespaces(rawSchema))
	cmd := exec.Command("schema/bin/schema", "dump", path.Join("schemas", subdir, filename+".bin"), common.RemoveWhitespaces(rawSchema))
	return cmd.Run()
}

func (s *Schema) Validate(subdir, filename string, userId uint64) bool {
	schemaPath := getSchemaPath(subdir, filename)

	if !common.IsFileExists(schemaPath) {
		log.Println("Validation failed: schema path doesnt exists")
		return false
	}
	cmd := exec.Command("schema/bin/schema", "check", path.Join("schemas", subdir, filename+".bin"), strconv.FormatUint(userId, 10))
	err := cmd.Run()
	if err != nil {
		log.Println("Validation failed: " + err.Error())
	}
	return err == nil
}
