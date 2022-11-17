package dispatcher

import (
	"context"
	"log"
	"net"

	"github.com/IndustryEssentials/ymir-hel/common/constants"
	"github.com/IndustryEssentials/ymir-hel/configs"
	"github.com/IndustryEssentials/ymir-hel/hel/ops"
	"github.com/IndustryEssentials/ymir-hel/protos"
	"google.golang.org/grpc"
)

type HelGrpcServer struct {
	ServerConfig *configs.Config
}

func (s HelGrpcServer) HelOpsProcess(
	context context.Context,
	request *protos.HelOpsRequest,
) (*protos.HelResponse, error) {
	log.Printf("Hel-gRPC server is called with request:\n%+v", request)

	nvResult := ops.GetGPUInfo()
	if nvResult != nil {
		result := &protos.HelResponse{Code: int32(constants.CodeSuccess)}
		result.GpuInfo.GpuCountTotal = int32(nvResult.GpuCountTotal)
		result.GpuInfo.GpuCountBusy = 0
		result.GpuInfo.GpuCountFree = int32(nvResult.GpuCountFree)
		result.GpuInfo.GpuCountInUse = 0
		return result, nil
	}

	return &protos.HelResponse{Code: 1, Message: "failed"}, nil
}

func StartHelGrpc(grpcURL string, config *configs.Config) error {
	lis, err := net.Listen("tcp", grpcURL)
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
		return err
	}

	s := grpc.NewServer()
	protos.RegisterHelServiceServer(s, HelGrpcServer{ServerConfig: config})

	log.Printf("Hel-gRPC server is starting at %s.", grpcURL)
	err = s.Serve(lis)
	if err != nil {
		log.Fatalf("failed to serve: %v", err)
		return err
	}

	return nil
}
