package dispatcher

// Credit to https://github.com/go-gl/gldebug

import (
	"bytes"
	"encoding/xml"
	"fmt"
	"log"
	"os/exec"
)

type NVGpu struct {
	MemTotal string `xml:"fb_memory_usage>total"`
	MemUsed  string `xml:"fb_memory_usage>used"`
	MemFree  string `xml:"fb_memory_usage>free"`
}

func (g NVGpu) Total() int {
	result := 0
	fmt.Sscanf(g.MemTotal, "%d MB", &result)
	return result
}

func (g NVGpu) Used() int {
	result := 0
	fmt.Sscanf(g.MemUsed, "%d MB", &result)
	return result
}

func (g NVGpu) Free() int {
	result := 0
	fmt.Sscanf(g.MemFree, "%d MB", &result)
	return result
}

type NVResult struct {
	Gpus []NVGpu `xml:"gpu"`
}

func (v NVResult) Total() int {
	result := 0
	for _, gpu := range v.Gpus {
		result += gpu.Total()
	}
	return result
}

func (v NVResult) Used() int {
	result := 0
	for _, gpu := range v.Gpus {
		result += gpu.Used()
	}
	return result
}

func (v NVResult) Free() int {
	result := 0
	for _, gpu := range v.Gpus {
		result += gpu.Free()
	}
	return result
}

type GPU interface {
	Total() int
	Used() int
	Free() int
	String() string
}

func Parse(x []byte) NVResult {
	v := NVResult{}
	err := xml.Unmarshal(x, &v)
	if err != nil {
		panic(err)
	}
	return v
}

type ChannelWriter struct {
	buf bytes.Buffer
	ch  chan GPU
	c   *exec.Cmd
}

var terminator = []byte("</nvidia_smi_log>\n")

func (cw *ChannelWriter) Write(content []byte) (n int, err error) {
	n, err = len(content), nil

	cw.buf.Write(content)

	idx := bytes.Index(cw.buf.Bytes(), terminator)
	if idx != -1 {
		content := make([]byte, idx+len(terminator))
		n1, err1 := cw.buf.Read(content)
		if err1 != nil || n1 != len(content) {
			panic(err1)
		}
		select {
		// Check if the channel is closed by trying to read from it
		// (We're the only writer so we know this is safe.
		//  There is only something to read from it if we're blocking.)
		case _, open := <-cw.ch:
			if !open {
				cw.c.Process.Kill()
				cw.c.Process.Wait()
				return
			}
		default:
		}
		cw.ch <- Parse(content)
	}
	return
}

func PollNvidiaGPUMemory() chan GPU {
	cw := &ChannelWriter{
		ch: make(chan GPU),
		c:  exec.Command("nvidia-smi", "-q", "-x"),
	}
	cw.c.Stdout = cw
	cw.c.Start()
	return cw.ch
}

func (v NVResult) String() string {
	return fmt.Sprintf("T: %d U: %d F: %d", v.Total(), v.Used(), v.Free())
}

func haveExe(name string) bool {
	_, err := exec.LookPath(name)
	return err == nil
}

// Returns a GPU{} struct every ~1s, or blocks indefinitely if there is no known
// way to get the spare GPU memory information.
// Polling is terminated by calling close() on the channel
func PollGPUMemory() chan GPU {
	switch {
	case haveExe("nvidia-smi"):
		return PollNvidiaGPUMemory()
	}
	log.Print("PollGPUMemory() doesn't know any way to measure GPU memory")
	return make(chan GPU)
}
