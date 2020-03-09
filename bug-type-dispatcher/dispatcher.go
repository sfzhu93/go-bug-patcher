package main

import (
	"fmt"
	"go/token"
	"golang.org/x/tools/go/packages"
	"golang.org/x/tools/go/ssa"
	"golang.org/x/tools/go/ssa/ssautil"
	"strings"
)

func getFileNameFromPath(path string) string {
	splits := strings.Split(path, "/")
	filename := splits[len(splits)-1]
	return filename
}

//TODO: should use absolute path
func findFunctionByLineNo(program *ssa.Program, fset *token.FileSet, filename string, lineno int) (*ssa.Function) {
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
func findMakeByLineNo(program *ssa.Program, fset *token.FileSet, filename string, lineno int) *ssa.MakeChan{
	for fn := range ssautil.AllFunctions(program) {
		for _, bb := range fn.Blocks {
			for _, ins := range bb.Instrs {
				position := fset.Position(ins.Pos())
				fileNameInPath := getFileNameFromPath(position.Filename)
				if position.Line == lineno && fileNameInPath == filename {
					makeinst, ok := ins.(*ssa.MakeChan); if ok {
						return makeinst
					} else {
						fmt.Print(ins)
						panic("didn't find make in line"+string(lineno))
					}
				}
			}
		}
	}
	return nil
}

func findSendByLineNo(program *ssa.Program, fset *token.FileSet, filename string, lineno int) *ssa.MakeChan{
	for fn := range ssautil.AllFunctions(program) {
		for _, bb := range fn.Blocks {
			for _, ins := range bb.Instrs {
				position := fset.Position(ins.Pos())
				fileNameInPath := getFileNameFromPath(position.Filename)
				if position.Line == lineno && fileNameInPath == filename {
					makeinst, ok := ins.(*ssa.MakeChan); if ok {
						return makeinst
					} else {
						fmt.Print(ins)
						panic("didn't find make in line"+string(lineno))
					}
				}
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
/*	path := os.Args[1]//filename
	lineno, _ := strconv.Atoi(os.Args[2])//lineno
*/
	cfg := packages.Config{Mode: packages.LoadAllSyntax}
	//initial, err := packages.Load(&cfg, path)
	initial, err := packages.Load(&cfg, "examples")
	if err != nil {
		//log.Fatal(err)
	}

	// Create SSA packages for well-typed packages and their dependencies.
	prog, pkgs := ssautil.AllPackages(initial, ssa.NaiveForm)//ssa.PrintPackages
	_ = pkgs

	// Build SSA code for the whole program.
	prog.Build()
	printSSA(prog)
	fn := findFunctionByLineNo(prog, prog.Fset, "ex1.go", 4)
	if fn != nil {
		makeInst := findMakeByLineNo(prog, prog.Fset, "ex1.go", 4)
		allSend := findSendByMake(makeInst)
		for _, send := range allSend {
			if  !checkHasDirectCallSites(send.Parent(), prog) && isLastSendBeforeReturn(send) {
				println(1)
				return
			}
		}
	}
	println("unknown")
}