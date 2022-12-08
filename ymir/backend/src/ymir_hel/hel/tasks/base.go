package tasks

import (
	"bytes"
	"fmt"
	"log"
	"os/exec"

	"github.com/IndustryEssentials/ymir-hel/common/constants"
	"github.com/IndustryEssentials/ymir-hel/configs"
	"github.com/IndustryEssentials/ymir-hel/protos"
)

type HelTaskHandler interface {
	PreProcess(request *protos.HelTaskRequest, config *configs.Config) *protos.HelTaskResponse
	Process(request *protos.HelTaskRequest, config *configs.Config)
	PostProcess(request *protos.HelTaskRequest, config *configs.Config)
}

func HandleTask(request *protos.HelTaskRequest, config *configs.Config) (ret *protos.HelTaskResponse) {
	m := map[protos.TaskType]HelTaskHandler{}

	if handler, ok := m[request.TaskType]; ok {
		ret = handler.PreProcess(request, config)
		if ret.Code != int32(constants.CodeSuccess) {
			return ret
		}

		// Async process task.
		go func() {
			handler.Process(request, config)
			handler.PostProcess(request, config)
		}()

		ret = constants.HelTaskRespMessage(constants.CodeSuccess, request)
	} else {
		ret = constants.HelTaskRespMessage(constants.CodeHelInvalidParms, request)
	}
	return ret
}

func SyncExecCmd(app string, args []string) (outStr string, errStr string, err error) {
	fmt.Printf("executing: %s %+v\n", app, args)

	cmd := exec.Command(app, args...)
	var stdout, stderr bytes.Buffer
	cmd.Stdout, cmd.Stderr = &stdout, &stderr

	err = cmd.Run()
	outStr, errStr = stdout.String(), stderr.String()
	if err != nil {
		log.Fatalf("cmd.Run() failed with %s\n", err)
	}

	fmt.Printf("exec result err: %s\nstdout: %s\nstderr: %s\n", err, outStr, errStr)
	return outStr, errStr, err
}
