package main

import (
	"go/ast"
	"go/parser"
	"go/token"
)

func main() {
	var src = `package main

func gl1_before() {
	done := make(chan struct{})
	defer func() { 
		close(done)
	}()
	defer close(done)
	go func() {
		done <- struct{}{}
	}()
	<-done
	return
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
