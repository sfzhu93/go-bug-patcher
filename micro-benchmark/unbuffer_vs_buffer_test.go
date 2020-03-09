package microbenchmarks

import (
	"testing"
)


func unbufferSync() {
	done := make(chan struct{})
	go func() {
		done <- struct{}{}
	}()
	<-done
	return
}

func bufferSync() {
	done := make(chan struct{}, 1)
	go func() {
		done <- struct{}{}
	}()
	<-done
	return
}

func BenchmarkUnbufferSync(b *testing.B) {
	for i:=0; i< b.N; i++ {
		unbufferSync()
	}
}

func BenchmarkBufferSync(b *testing.B) {
	for i:=0; i< b.N; i++ {
		bufferSync()
	}
}