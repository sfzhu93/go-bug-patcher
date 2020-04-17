package main

import (
	"flag"
	"golang.org/x/tools/go/packages"
	"golang.org/x/tools/go/ssa"
	"golang.org/x/tools/go/ssa/ssautil"
	"log"
	"os"
	"path"
	"strings"
)

func tryPackagePath(packagePath string) bool {
	gopath := os.Getenv("GOPATH")
	cfg := packages.Config{Mode: packages.LoadAllSyntax, Tests: true}
	for ; strings.HasPrefix(packagePath, path.Join(gopath, "src")); packagePath, _ = path.Split(packagePath) {
        println(packagePath)
		pkgs, err := packages.Load(&cfg, packagePath)
		_ = pkgs
		if err == nil {
			return true
		} else {
            println(err)
        }
	}
	return false
}

func main() {
	packagePath := *flag.String("package", "", "The compilable pacakge containing the buggy file.")
	pathToFile := flag.String("path", "", "The path to the buggy file.")
	bugType := *flag.Int("type", 0, "1: `send` definitely executed. 2: `recv/close` "+
		"definitely executed.")
	lineNo := *flag.Int("lineno", 0, "The line no. of the definitely executed operation.")
    flag.Parse()
	_ = bugType
	_ = lineNo
    println(*pathToFile)
	dirpath, filename := path.Split(*pathToFile)
	if tryPackagePath(dirpath) {
		println(dirpath + "1")
	} else {
		println(dirpath + "0")
	}
	return
	_ = dirpath
	cfg := packages.Config{Mode: packages.LoadAllSyntax, Tests: true}
	initial, err := packages.Load(&cfg, packagePath)
	//initial, err := packages.Load(&cfg, "examples")
	if err != nil {
		log.Fatal(err)
	}

	// Create SSA packages for well-typed packages and their dependencies.
	prog, pkgs := ssautil.AllPackages(initial, ssa.NaiveForm) //ssa.PrintPackages
	_ = pkgs

	// Build SSA code for the whole program.
	prog.Build()
	//printSSA(prog)
	sendInst := findSendByLineNo(prog, prog.Fset, filename, lineNo)
	if sendInst == nil {
		printIncludedFiles(prog)
		//printSSAByFileAndLineNo(prog, pathToFile, lineno)
		log.Fatal("couldn't find send in the line number")
	}
	if isGL1(sendInst) {
		println("1")
		return
	}
	/*fn := findFunctionByLineNo(prog, prog.Fset, "ex1.go", 4)
	if fn != nil {
		makeInst := findMakeByLineNo(prog, prog.Fset, "ex1.go", 4)
		allSend := findSendByMake(makeInst)
		for _, send := range allSend {
			if  !checkHasDirectCallSites(send.Parent(), prog) && isLastSendBeforeReturn(send) {
				println(1)
				return
			}
		}
	}*/
	println("unknown")
}
