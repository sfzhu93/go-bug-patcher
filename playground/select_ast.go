package main

import (
	"go/ast"
	"go/parser"
	"go/token"
)

func main_select_ast() {
	var src = `package main

func TestGL2Ex3() {
	done := make(chan struct{})
	defer close(done)
	go func() {
		time.Sleep(5*time.Second)
		select {
		case <-time.After(5*time.Second):
		case <-done:
			return
		}
	}()
	if true {
		log.Fatal("123")
	}
}
`

	fset := token.NewFileSet() // positions are relative to fset
	f, err := parser.ParseFile(fset, "", src, parser.ParseComments)
	_ = f
	ast.Print(fset, f)
	if err != nil {
		panic(err)
	}

}

func main() {
	main_select_ast()
}
