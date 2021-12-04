package common

import (
	"io/ioutil"
	"os"
	"path"
)

type FileStorage struct {
	dir string
}

func isDirExists(path string) bool {
	fileInfo, err := os.Stat(path)
	if err != nil {
		return false
	}

	return fileInfo.IsDir()
}

func (fs *FileStorage) ensureDir(path string) {
	if !isDirExists(path) {
		if err := os.MkdirAll(path, os.ModePerm); err != nil {
			panic(err)
		}
	}
}

func (fs *FileStorage) ensureSubdir(subdir string) {
	fs.ensureDir(path.Join(fs.dir, subdir))
}

func (fs *FileStorage) Init(dir string) {
	fs.ensureDir(dir)
	fs.dir = dir
}

func (fs *FileStorage) Put(subdir, filename string, value []byte) error {
	fs.ensureSubdir(subdir)
	return ioutil.WriteFile(path.Join(fs.dir, subdir, filename), value, 0644)
}

func (fs *FileStorage) Get(subdir, filename string) ([]byte, error) {
	fs.ensureSubdir(subdir)

	data, err := ioutil.ReadFile(path.Join(fs.dir, subdir, filename))
	if err != nil {
		return nil, err
	}
	return data, nil
}

func (fs *FileStorage) Exists(subdir, filename string) bool {
	fs.ensureSubdir(subdir)
	return isFileExists(path.Join(fs.dir, subdir, filename))
}

func (fs *FileStorage) List(subdir string) ([]string, error) {
	fs.ensureSubdir(subdir)

	files, err := ioutil.ReadDir(path.Join(fs.dir, subdir))
	if err != nil {
		return nil, err
	}

	var res []string

	for _, f := range files {
		res = append(res, f.Name())
	}
	return res, nil
}
