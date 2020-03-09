package microbenchmarks

import (
	"testing"
)


func gl_leak_before() {
	done := make(chan struct{})
	go func() {
		done <- struct{}{}
	}()
	return
}

func gl_leak_after() {
	done := make(chan struct{}, 1)
	go func() {
		done <- struct{}{}
	}()
	return
}

func BenchmarkGoroutineLeak(b *testing.B) {
	for i:=0; i< b.N; i++ {
		gl_leak_before()
	}
}

func BenchmarkGoroutineNoLeak(b *testing.B) {
	for i:=0; i< b.N; i++ {
		gl_leak_after()
	}
}