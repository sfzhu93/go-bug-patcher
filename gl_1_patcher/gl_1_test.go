package main

import (
	"go/parser"
	"go/token"
	"testing"
)

func TestPatch(t *testing.T) {
	src := `package main

func gl1_before() {
	done := make(chan struct{})
	go func() {
		done <- struct{}{}
	}()
	<-done
	return
}
`
	fset := token.NewFileSet() // positions are relative to fset
	f, err := parser.ParseFile(fset, "", src, 0)
	if err != nil {
		panic(err)
	}
	patchedCode := fixGoroutineLeakOnChannelType1(4, fset, f)
	//panic(patchedCode)
	if patchedCode != `package main

func gl1_before() {
	done := make(chan struct{}, 1)
	go func() {
		done <- struct{}{}
	}()
	<-done
	return
}
` {
	t.Fatal("failed")
	}
}