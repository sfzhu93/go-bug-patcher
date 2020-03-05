package microbenchmarks

import (
	"testing"
)


func gl1_before() {
	done := make(chan struct{})
	go func() {
		done <- struct{}{}
	}()
	<-done
	return
}

func gl1_after() {
	done := make(chan struct{}, 1)
	go func() {
		done <- struct{}{}
	}()
	<-done
	return
}

func BenchmarkGL1Before(b *testing.B) {
	for i:=0; i< b.N; i++ {
		gl1_before()
	}
}

func BenchmarkGL1After(b *testing.B) {
	for i:=0; i< b.N; i++ {
		gl1_after()
	}
}