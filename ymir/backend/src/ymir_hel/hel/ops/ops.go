package ops

import (
	"github.com/IndustryEssentials/ymir-hel/configs"
	"github.com/IndustryEssentials/ymir-hel/protos"
)

func GetOpsFunc(
	opsType protos.HelOpsType,
) func(request *protos.HelOpsRequest, config *configs.Config) *protos.HelResponse {
	m := map[protos.HelOpsType]func(request *protos.HelOpsRequest, config *configs.Config) *protos.HelResponse{
		protos.HelOpsType_HEL_OPS_GET_GPU: OpsGpuInfo,
	}
	return m[opsType]
}
