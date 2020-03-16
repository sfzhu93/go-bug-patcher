package main

import (
	"fmt"
	"go/token"
	"golang.org/x/tools/go/packages"
	"golang.org/x/tools/go/ssa"
	"golang.org/x/tools/go/ssa/ssautil"
	"log"
	"os"
	"path"
	"strconv"
	"strings"
)

var debug bool = false

func hasDirectCallSites(calleeFunc *ssa.Function, program *ssa.Program) bool {
	for fn := range ssautil.AllFunctions(program) {
		for _, bb := range fn.Blocks {
			for _, ins := range bb.Instrs {
				callinst, ok := ins.(*ssa.Call)
				if ok {
					callInstCallee := callinst.Call.StaticCallee()
					/*
						if callInstCallee != nil {
							fmt.Println(callInstCallee.Name())
						} else {
							fmt.Println(callinst.Call)
						}
						fmt.Println(calleeFunc.Name())*/
					if callInstCallee == calleeFunc {
						return true
					}
				}
			}
		}
	}
	return false
}

func findGoInstSites(calleeFunc *ssa.Function, program *ssa.Program) []*ssa.Go {
	//fmt.Println(calleeFunc)
	ret := make([]*ssa.Go, 0)
	for fn := range ssautil.AllFunctions(program) {
		for _, bb := range fn.Blocks {
			for _, ins := range bb.Instrs {
				goinst, ok := ins.(*ssa.Go)
				if ok {
					//fmt.Println(goinst)
					callInstCallee := goinst.Call.StaticCallee()
					/*
						if callInstCallee != nil {
							fmt.Println(callInstCallee.Name())
						} else {
							fmt.Println(callinst.Call)
						}
						fmt.Println(calleeFunc.Name())*/
					if callInstCallee == calleeFunc {
						ret = append(ret, goinst)
					}
				}
			}
		}
	}
	return ret
}

func isGL1(send ssa.Instruction) bool {
	ssaFunc := send.Parent() //the goroutine function
	prog := ssaFunc.Prog
	if hasDirectCallSites(ssaFunc, prog) {
		if debug {
			fmt.Println("has other direct call sites!")
		}
		return false
	}
	sendInst, ok := send.(*ssa.Send)
	if !ok {
		if debug {
			fmt.Println("Not a send inst!") //TODO: not a correct way to handle error
		}
		return false
	}
	if !isLastSendBeforeReturn(sendInst) {
		if debug {
			fmt.Println("is not the last send before return!")
		}
		return false
	}
	goinsts := findGoInstSites(ssaFunc, prog)
	if len(goinsts) == 0 {
		if debug {
			fmt.Println("The goroutine is not created by an anonymous function. (TODO)")
		}
		return false
	} else if len(goinsts) > 1 {
		if debug {
			fmt.Println("more than one goroutine created")
		}
		return false
	}
	goinst := goinsts[0]
	parentFunc := goinst.Parent()
	loopinfo := NewLoopInfo(parentFunc)
	loopinfo.Analyze()
	_, ok = loopinfo.isLoopBB[goinst.Block()]
	if ok {
		if debug {
			fmt.Println("is in a loop!")
		}
		return false
	}
	return true
}

func getFileNameFromPath(path string) string {
	splits := strings.Split(path, "/")
	filename := splits[len(splits)-1]
	return filename
}

//TODO: should use absolute path
func findFunctionByLineNo(program *ssa.Program, fset *token.FileSet, filename string, lineno int) *ssa.Function {
	for fn := range ssautil.AllFunctions(program) {
		for _, bb := range fn.Blocks {
			for _, ins := range bb.Instrs {
				position := fset.Position(ins.Pos())
				fileNameInPath := getFileNameFromPath(position.Filename)
				if position.Line == lineno && fileNameInPath == filename {
					return fn
				}
			}
		}
	}
	return nil
}

func checkHasDirectCallSites(calleeFunc *ssa.Function, program *ssa.Program) bool {
	for fn := range ssautil.AllFunctions(program) {
		for _, bb := range fn.Blocks {
			for _, ins := range bb.Instrs {
				callinst, ok := ins.(*ssa.Call)
				if ok {
					fmt.Println(callinst.Call.StaticCallee().Name())
					fmt.Println(calleeFunc.Name())
					if callinst.Call.StaticCallee() == calleeFunc {
						return true
					}
				}
			}
		}
	}
	return false
}

func printSSA(program *ssa.Program) {
	for fn := range ssautil.AllFunctions(program) {
		fmt.Println(fn.String())
		for _, bb := range fn.Blocks {
			fmt.Println("  ", bb.String()+":")
			for _, ins := range bb.Instrs {
				fmt.Print("    ")
				value, ok := ins.(ssa.Value)
				if ok {
					fmt.Print(value.Name(), "=")
				}
				fmt.Println(ins.String())
			}
		}
	}
}

//TODO: change to find `new chan`
func findMakeByLineNo(program *ssa.Program, fset *token.FileSet, filename string, lineno int) *ssa.MakeChan {
	for fn := range ssautil.AllFunctions(program) {
		for _, bb := range fn.Blocks {
			for _, ins := range bb.Instrs {
				position := fset.Position(ins.Pos())
				fileNameInPath := getFileNameFromPath(position.Filename)
				if position.Line == lineno && fileNameInPath == filename {
					makeinst, ok := ins.(*ssa.MakeChan)
					if ok {
						return makeinst
					} else {
						fmt.Print(ins)
						panic("didn't find make in line" + string(lineno))
					}
				}
			}
		}
	}
	return nil
}

func findSendByLineNo(program *ssa.Program, fset *token.FileSet, filename string, lineno int) *ssa.Send {
	for fn := range ssautil.AllFunctions(program) {
		for _, bb := range fn.Blocks {
			entered := false
			for _, ins := range bb.Instrs {
				position := fset.Position(ins.Pos())
				fileNameInPath := getFileNameFromPath(position.Filename)
				if position.Line == lineno && fileNameInPath == filename {
					entered = true
					makeinst, ok := ins.(*ssa.Send)
					if ok {
						return makeinst
					}
				}
			}
			if entered {
				fmt.Println(bb)
				panic("didn't find send in line" + string(lineno))
			}
		}
	}
	return nil
}

func findSendByMake(makeInst *ssa.MakeChan) []*ssa.Send {
	refs := makeInst.Referrers()
	ret := make([]*ssa.Send, 0)
	for _, ins := range *refs {
		sendInst, ok := ins.(*ssa.Send)
		if ok {
			ret = append(ret, sendInst)
		}
	}
	return ret
}

func isLastSendBeforeReturn(sendInst *ssa.Send) bool {
	bb := sendInst.Block()
	state := 0
	for _, inst := range bb.Instrs {
		switch x := inst.(type) {
		case *ssa.Send:
			if x == sendInst {
				if state != 0 {
					return false
				} else {
					state = 1
				}
			}
		case *ssa.RunDefers:
			if state == 1 {
				state = 1
			}
		case *ssa.Return:
			if state > 0 {
				return true
			} else {
				return false
			}
		default:
			if state == 1 {
				return false
			}
		}
	}
	return false
}

func main() {
	pathToFile := os.Args[1]                //filename
	lineno, err := strconv.Atoi(os.Args[2]) //line no. of channel send instruction
	dirpath, filename := path.Split(pathToFile)
	if err != nil {
		log.Fatal("the line number is invalid\n")
	}
	cfg := packages.Config{Mode: packages.LoadAllSyntax}
	initial, err := packages.Load(&cfg, dirpath)
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
	sendInst := findSendByLineNo(prog, prog.Fset, filename, lineno)
	if isGL1(sendInst) {
		println("1")
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
