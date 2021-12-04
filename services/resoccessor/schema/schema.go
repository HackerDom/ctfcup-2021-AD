package schema

import "C"
import (
	"fmt"
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

func (s *Schema) Save(subdir, filename, rawSchema string) error {
	cmd := exec.Command("schema/bin/schema", "dump", path.Join("schemas", subdir, filename+".bin"), common.RemoveWhitespaces(rawSchema))
	return cmd.Run()
}

func (s *Schema) Validate(subdir, filename string, userId uint) error {
	cmd := exec.Command("schema/bin/schema", "check", path.Join("schemas", subdir, filename+".bin"), strconv.Itoa(int(userId)))

	err := cmd.Run()
	fmt.Println(err)
	return err
}
