package dispatcher

// Modified from https://github.com/go-gl/gldebug

import (
	"bytes"
	"encoding/json"
	"encoding/xml"
	"log"
	"os/exec"
)

type NVGpu struct {
	MemTotal string `xml:"fb_memory_usage>total"`
	MemUsed  string `xml:"fb_memory_usage>used"`
	MemFree  string `xml:"fb_memory_usage>free"`
}

type NVResult struct {
	Gpus          []NVGpu `xml:"gpu"`
	GpuCountTotal int     `xml:"-"`
	GpuCountFree  int     `xml:"-"`
}

func (NVResult) UnmarshalJSON(b []byte) error {
	var v NVResult
	if err := json.Unmarshal(b, &v); err != nil {
		return err
	}
	v.GpuCountTotal = len(v.Gpus)
	return nil
}

func GetGPUInfo() *NVResult {
	cmdString := "nvidia-smi"
	_, err := exec.LookPath(cmdString)
	if err == nil {
		cmd := exec.Command(cmdString, "-q", "-x")
		var stdout bytes.Buffer
		cmd.Stdout = &stdout
		err := cmd.Run()
		if err != nil {
			log.Fatalf("%s failed with %s\n", cmdString, err)
		}

		terminator := []byte("</nvidia_smi_log>\n")
		idx := bytes.Index(stdout.Bytes(), terminator)
		if idx != -1 {
			content := make([]byte, idx+len(terminator))
			n1, err1 := stdout.Read(content)
			if err1 != nil || n1 != len(content) {
				panic(err1)
			}
			v := &NVResult{}
			err := xml.Unmarshal(content, v)
			if err != nil {
				panic(err)
			}
			return v

		}
	} else {
		log.Print("nvidia-smi not installed.")
	}
	return nil
}
