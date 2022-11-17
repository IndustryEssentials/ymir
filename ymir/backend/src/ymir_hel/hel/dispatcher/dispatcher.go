package dispatcher

import (
	"context"
	"log"
	"net"

	"github.com/IndustryEssentials/ymir-hel/protos"
	"github.com/RichardKnop/machinery/v1"
	"google.golang.org/grpc"
)

type HelGrpcServer struct {
	TaskServer *machinery.Server
}

func StartHelGrpc(grpcURL string, taskServer *machinery.Server) error {
	lis, err := net.Listen("tcp", grpcURL)
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
		return err
	}

	s := grpc.NewServer()
	protos.RegisterHelServiceServer(s, HelGrpcServer{TaskServer: taskServer})

	log.Printf("Hel-gRPC server is starting at %s.", grpcURL)
	err = s.Serve(lis)
	if err != nil {
		log.Fatalf("failed to serve: %v", err)
		return err
	}

	return nil
}

func (s HelGrpcServer) HelOpsProcess(
	context context.Context,
	request *protos.HelOpsRequest,
) (*protos.HelResponse, error) {
	log.Printf("Hel-gRPC server is called with request:\n%+v", request)

	nvResult := GetGPUInfo()
	if nvResult != nil {
		result := &protos.HelResponse{Code: 0, Message: "succeed"}
		result.GpuCountTotal = int32(nvResult.GpuCountTotal)
		result.GpuCountFree = int32(nvResult.GpuCountFree)
		return result, nil
	}

	return &protos.HelResponse{Code: 1, Message: "failed"}, nil
}
