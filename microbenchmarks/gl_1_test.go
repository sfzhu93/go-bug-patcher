package microbenchmarks

import (
	"fmt"
	"testing"
	"time"
)


func gl1_before() {
	done := make(chan struct{})
	go func() int {
		sum := 0
		for i:= 0; i<10; i++ {
			sum += i*i^(i-1)*(i-1)
		}
		done <- struct{}{}
		return sum
	}()
	select {
	case <-time.After(100*time.Second):
		fmt.Println("timeout")
	case <-done:
		return
	}
}

func gl1_after() {
	done := make(chan struct{}, 1)
	go func() int {
		sum := 0
		for i:= 0; i<10; i++ {
			sum += i*i^(i-1)*(i-1)
		}
		done <- struct{}{}
		return sum
	}()
	select {
	case <-time.After(100*time.Second):
		fmt.Println("timeout")
	case <-done:
		return
	}
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