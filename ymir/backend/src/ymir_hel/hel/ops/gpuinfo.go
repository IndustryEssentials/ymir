package ops

import (
	"github.com/IndustryEssentials/ymir-hel/common/constants"
	"github.com/IndustryEssentials/ymir-hel/configs"
	"github.com/IndustryEssentials/ymir-hel/protos"
)

type HandlerGpuInfo struct{}

func (h *HandlerGpuInfo) Process(
	request *protos.HelOpsRequest,
	config *configs.Config,
) *protos.HelOpsResponse {
	result := constants.HelOpsRespMessage(constants.CodeSuccess, request)
	result.GpuInfo = &protos.HelGpuInfo{}

	gpuIdleThr := 0.8
	err := GetGPUInfo(gpuIdleThr, result.GpuInfo)
	if err != nil {
		return constants.HelOpsRespMessage(constants.CodeHelNvmlError, request)
	}

	return result
}

func GetGPUInfo(gpuIdleThr float64, gpuInfo *protos.HelGpuInfo) error {
	// ret := nvml.Init()
	// if ret != nvml.SUCCESS {
	// 	log.Fatalf("Unable to initialize NVML: %v", nvml.ErrorString(ret))
	// 	return errors.New(nvml.ErrorString(ret))
	// }
	// defer func() {
	// 	ret := nvml.Shutdown()
	// 	if ret != nvml.SUCCESS {
	// 		log.Fatalf("Unable to shutdown NVML: %v", nvml.ErrorString(ret))
	// 	}
	// }()

	// count, ret := nvml.DeviceGetCount()
	// if ret != nvml.SUCCESS {
	// 	log.Fatalf("Unable to get device count: %v", nvml.ErrorString(ret))
	// 	return errors.New(nvml.ErrorString(ret))
	// }

	// gpuInfo.GpuCountTotal = int32(count)
	// for i := 0; i < count; i++ {
	// 	device, ret := nvml.DeviceGetHandleByIndex(i)
	// 	if ret != nvml.SUCCESS {
	// 		log.Fatalf("Unable to get device at index %d: %v", i, nvml.ErrorString(ret))
	// 		return errors.New(nvml.ErrorString(ret))
	// 	}

	// 	memoryInfo, ret := device.GetMemoryInfo()
	// 	if ret != nvml.SUCCESS {
	// 		log.Fatalf("Unable to get uuid of device at index %d: %v", i, nvml.ErrorString(ret))
	// 		return errors.New(nvml.ErrorString(ret))
	// 	}

	// 	if float64(memoryInfo.Free)/float64(memoryInfo.Total) > gpuIdleThr {
	// 		gpuInfo.GpuCountIdle += 1
	// 	} else {
	// 		gpuInfo.GpuCountBusy += 1
	// 	}
	// }
	return nil
}
