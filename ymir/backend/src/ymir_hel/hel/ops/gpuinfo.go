package ops

import (
	"log"

	"github.com/IndustryEssentials/ymir-hel/common/constants"
	"github.com/IndustryEssentials/ymir-hel/configs"
	"github.com/IndustryEssentials/ymir-hel/protos"
	"github.com/NVIDIA/go-nvml/pkg/nvml"
)

func OpsGpuInfo(
	request *protos.HelOpsRequest,
	config *configs.Config,
) *protos.HelResponse {
	nvResult := GetGPUInfo()
	if nvResult != nil {
		result := constants.HelRespMessage(constants.CodeSuccess)
		result.GpuInfo.GpuCountTotal = int32(nvResult.GpuCountTotal)
		result.GpuInfo.GpuCountBusy = 0
		result.GpuInfo.GpuCountFree = int32(nvResult.GpuCountFree)
		result.GpuInfo.GpuCountInUse = 0
		return result
	}

	return constants.HelRespMessage(constants.CodeHelNvmlError)
}

type NVResult struct {
	GpuCountTotal int
	GpuCountFree  int
	GpuCountUsed  int
}

func GetGPUInfo() *NVResult {
	ret := nvml.Init()
	if ret != nvml.SUCCESS {
		log.Fatalf("Unable to initialize NVML: %v", nvml.ErrorString(ret))
		return nil
	}
	defer func() {
		ret := nvml.Shutdown()
		if ret != nvml.SUCCESS {
			log.Fatalf("Unable to shutdown NVML: %v", nvml.ErrorString(ret))
		}
	}()

	count, ret := nvml.DeviceGetCount()
	if ret != nvml.SUCCESS {
		log.Fatalf("Unable to get device count: %v", nvml.ErrorString(ret))
		return nil
	}

	gpuFreeThr := 0.8
	infoResult := &NVResult{GpuCountTotal: count}
	for i := 0; i < count; i++ {
		device, ret := nvml.DeviceGetHandleByIndex(i)
		if ret != nvml.SUCCESS {
			log.Fatalf("Unable to get device at index %d: %v", i, nvml.ErrorString(ret))
			return nil
		}

		memoryInfo, ret := device.GetMemoryInfo()
		if ret != nvml.SUCCESS {
			log.Fatalf("Unable to get uuid of device at index %d: %v", i, nvml.ErrorString(ret))
			return nil
		}

		if float64(memoryInfo.Free)/float64(memoryInfo.Total) > gpuFreeThr {
			infoResult.GpuCountFree += 1
		}
	}
	return infoResult
}
