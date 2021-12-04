package schema

// #cgo LDFLAGS: -ldl
// #include <dlfcn.h>
// #include <lib.h>
import "C"
import (
	"fmt"
)

func Do() {
	handle := C.dlopen(C.CString("schema/lib.so"), C.RTLD_LAZY)
	fmt.Println(handle)
	add_func := C.dlsym(handle, C.CString("check_schema"))
	fmt.Println(add_func)
	fmt.Println(C.add_func)
}
