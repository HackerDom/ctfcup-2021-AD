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

func (fs *FileStorage) EnsureDir(path string) {
	if !isDirExists(path) {
		if err := os.MkdirAll(path, os.ModePerm); err != nil {
			panic(err)
		}
	}
}

func (fs *FileStorage) EnsureSubdir(subdir string) {
	fs.EnsureDir(path.Join(fs.dir, subdir))
}

func (fs *FileStorage) Init(dir string) {
	fs.EnsureDir(dir)
	fs.dir = dir
}

func (fs *FileStorage) Put(subdir, filename string, value []byte) error {
	fs.EnsureSubdir(subdir)
	return ioutil.WriteFile(path.Join(fs.dir, subdir, filename), value, 0644)
}

func (fs *FileStorage) Get(subdir, filename string) ([]byte, error) {
	fs.EnsureSubdir(subdir)

	data, err := ioutil.ReadFile(path.Join(fs.dir, subdir, filename))
	if err != nil {
		return nil, err
	}
	return data, nil
}

func (fs *FileStorage) Exists(subdir, filename string) bool {
	fs.EnsureSubdir(subdir)
	return IsFileExists(path.Join(fs.dir, subdir, filename))
}

func (fs *FileStorage) List(subdir string) ([]string, error) {
	fs.EnsureSubdir(subdir)

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
