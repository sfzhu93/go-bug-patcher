package main

import (
	"flag"
	"git.gradebot.org/zxl381/goconcurrencychecker/global"
	"git.gradebot.org/zxl381/goconcurrencychecker/mycallgraph"
	"git.gradebot.org/zxl381/goconcurrencychecker/tools/go/callgraph"
	"git.gradebot.org/zxl381/goconcurrencychecker/tools/go/mypointer"
	"git.gradebot.org/zxl381/goconcurrencychecker/tools/go/ssa"
	"git.gradebot.org/zxl381/goconcurrencychecker/tools/go/ssa/ssautil"
	//"golang.org/x/tools/go/callgraph"
	"git.gradebot.org/zxl381/goconcurrencychecker/tools/go/packages"
	//"golang.org/x/tools/go/pointer"
	//"golang.org/x/tools/go/ssa"
	//"golang.org/x/tools/go/ssa/ssautil"
	"os"
	"path"
	"strings"
)

const MaxDepth = 8

func tryBuildOnPackagePath(packagePath string) []*packages.Package {
	gopath := os.Getenv("GOPATH")
	for ; strings.HasPrefix(packagePath, path.Join(gopath, "src")); packagePath, _ = path.Split(packagePath) {
		println(packagePath)
		pkgs := buildSSA(packagePath)
		if pkgs != nil {
			return pkgs
		}
	}
	return nil
}

func buildSSA(packagePath string) []*packages.Package {
	cfg := packages.Config{Mode: packages.LoadAllSyntax, Tests: true}
	pkgs, err := packages.Load(&cfg, packagePath)
	if err == nil {
		return pkgs
	} else {
		println(err)
	}
	return nil
}

func getFuncByLineNo(program *ssa.Program, filename string, lineno int) *ssa.Function {
	fset := program.Fset
	for fn := range ssautil.AllFunctions(program) {
		position := fset.Position(fn.Pos())
		if position.Filename == filename && position.Line == lineno {
			return fn
		}
	}
	return nil
}

func getMakeChannel(fn *ssa.Function, lineno int) *ssa.MakeChan {
	fset := fn.Prog.Fset
	for _, bb := range fn.Blocks {
		for _, ins := range bb.Instrs {
			position := fset.Position(ins.Pos())
			if position.Line == lineno {
				makeinst, ok := ins.(*ssa.MakeChan)
				if ok {
					return makeinst
				} else {
					//fmt.Print(ins)
					panic("didn't find make in line" + string(lineno))
				}
			}
		}
	}
	return nil
}

/*func makeCallGraph(ssapkgs []*ssa.Package) *callgraph.Graph {
	cfg := &pointer.Config{
		Mains:           ssapkgs,
		Reflection:      false,
		BuildCallGraph:  true,
		Queries:         nil,
		IndirectQueries: nil,
		Log:             nil,
	}
	result, err := pointer.Analyze(cfg)
	if err != nil {
		println("Error when building callgraph with nil Queries:\n", err.Error())
		return nil
	}
	return result.CallGraph
}*/

func prepareCallGraph(parent *ssa.Function) *mycallgraph.Call_node {
	parentNode := mycallgraph.New_Call_node(parent, 0)
	mycallgraph.Initialize(50000)
	parentNode.Fill_call_map_after_init(3)
	return parentNode
}

func insideFunc(fn *ssa.Function, makeLineNo int, opLineNo int) {
	makeChanInst := getMakeChannel(fn, makeLineNo) //find the corresponding channel. refer to list_local_unbuffer_chan in channel.go:83
	_ = makeChanInst

	//TODO: find somewhere to insert call graph computation. pointer.go:21
	//migrate loop.go:288-303 here to fill SRC operations and threads. Some may not be needed
	//Then GL-1 should be enough to run.
}

func printCallGraphNodes(graph *callgraph.Graph) {
	for _, node := range graph.Nodes {
		println(node.Func.Name())
	}
}

func Pointer_build_callgraph(prog *ssa.Program) *callgraph.Graph {
	cfg := &mypointer.Config{
		OLDMains:        nil,
		Prog:            prog,
		Reflection:      global.Pointer_consider_reflection,
		BuildCallGraph:  true,
		Queries:         nil,
		IndirectQueries: nil,
		Log:             nil,
	}
	result, err := mypointer.Analyze(cfg, nil)
	if err != nil {
		println("Error when building callgraph with nil Queries:\n", err.Error())
		return nil
	}
	graph := result.CallGraph
	//graph.PruneSDK()
	return graph
}

func main() {
	packagePath := flag.String("package", "", "The compilable package containing the buggy file.")
	pathToFile := flag.String("path", "", "The path to the buggy file.")
	bugType := *flag.Int("type", 0, "1: `send` definitely executed. 2: `recv/close` "+
		"definitely executed.")
	opLineNo := flag.Int("oplineno", 0, "The line no. of the definitely executed operation.")
	makeLineNo := flag.Int("makelineno", 0, "The line no. of the make operation.")
	flag.Parse()
	_ = bugType
	_ = opLineNo
	_ = makeLineNo
	println(*pathToFile)
	dirpath, filename := path.Split(*pathToFile)
	pkgs := tryBuildOnPackagePath(dirpath)
	if pkgs == nil {
		pkgs = buildSSA(*packagePath)
		if pkgs == nil {
			println("Cannot automatically find the package to build. Please specify in the arguments.")
		}
		return
	}

	prog, ssapkgs := ssautil.AllPackages(pkgs, ssa.NaiveForm)
	graph := Pointer_build_callgraph(prog)
	_ = ssapkgs
	//graph := makeCallGraph(ssapkgs)
	println(len(graph.Nodes))

	printCallGraphNodes(graph)
	// Create SSA packages for well-typed packages and their dependencies.
	// Build SSA code for the whole program.
	prog.Build()
	lineno := getFuncByLineNo(prog, filename, *makeLineNo)
	_ = lineno

	//printSSA(prog)
	/*
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
