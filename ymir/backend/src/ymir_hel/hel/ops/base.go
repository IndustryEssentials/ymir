package ops

import (
	"github.com/IndustryEssentials/ymir-hel/common/constants"
	"github.com/IndustryEssentials/ymir-hel/configs"
	"github.com/IndustryEssentials/ymir-hel/protos"
)

type HelOpsHandler interface {
	Process(request *protos.HelOpsRequest, config *configs.Config) *protos.HelOpsResponse
}

func HandleOps(request *protos.HelOpsRequest, config *configs.Config) (ret *protos.HelOpsResponse) {
	m := map[protos.HelOpsType]HelOpsHandler{
		protos.HelOpsType_HEL_OPS_GET_GPU: &HandlerGpuInfo{},
	}

	if opsHandler, ok := m[request.OpsType]; ok {
		ret = opsHandler.Process(request, config)
	} else {
		ret = constants.HelOpsRespMessage(constants.CodeHelInvalidParms, request)
	}
	return ret
}
