package main

import (
	"golang.org/x/tools/go/ssa"
)


func handleBasicBlock(bb *ssa.BasicBlock, in []*ssa.Defer) ([]*ssa.Defer, *ssa.RunDefers) {
	ret := in
	var retRunDefers *ssa.RunDefers = nil
	for _, ins := range bb.Instrs {
		deferInst, ok := ins.(*ssa.Defer); if ok {
			ret = append(ret, deferInst)
		}
		runDefersInst, ok := ins.(*ssa.RunDefers); if ok {
			retRunDefers = runDefersInst
		}
	}
	return ret, retRunDefers
}

func contains(list []*ssa.Defer, item *ssa.Defer) bool {
	for _, x := range list{
		if x == item {
			return true
		}
	}
	return false
}

func union(a []*ssa.Defer, b []*ssa.Defer) []*ssa.Defer {
	ret := a
	for _, item := range b {
		if !contains(ret, item) {
			ret = append(ret, item)
		}
	}
	return ret
}

func get(m *map[*ssa.BasicBlock][]*ssa.Defer, key *ssa.BasicBlock) []*ssa.Defer {
	value, ok := (*m)[key]
	if ! ok {
		(*m)[key] = make([]*ssa.Defer, 0)
		value = (*m)[key]
	}
	return value
}

func gen_defer_map_in_fn(fn *ssa.Function) {
	worklist := []*ssa.BasicBlock{fn.Blocks[0]}
	in := make(map[*ssa.BasicBlock][]*ssa.Defer)
	out := make(map[*ssa.BasicBlock][]*ssa.Defer)
	rundefer2defers := make(map[*ssa.RunDefers][]*ssa.Defer)
	//visited := make(map[*ssa.BasicBlock]struct{})
	head := 0
	for head<len(worklist) {
		bb := worklist[head]
		head += 1
		inDefers := get(&in, bb)
		oldout := get(&out, bb)
		deferInsts, runDeferInst := handleBasicBlock(bb, inDefers)
		if runDeferInst != nil {
			rundefer2defers[runDeferInst] = deferInsts
		}
		newout := deferInsts
		for _, predBB := range bb.Preds {
			outpredbb := get(&out, predBB)
			newout = union(newout, outpredbb)
		}
		if len(newout) != len(oldout) {
			for _, succBB := range bb.Succs {
				worklist = append(worklist, succBB)
			}
		}
	}
}
