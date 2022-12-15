package hel

import (
	"context"
	"log"
	"net"

	"github.com/IndustryEssentials/ymir-hel/configs"
	"github.com/IndustryEssentials/ymir-hel/hel/ops"
	"github.com/IndustryEssentials/ymir-hel/hel/tasks"
	"github.com/IndustryEssentials/ymir-hel/protos"
	"google.golang.org/grpc"
)

// Note: pubsub>=v1.25.0

func StartHelServer(config *configs.Config) error {
	// This version only adds grpc server.
	err := StartHelGrpc(config.HelGrpcURL, config)
	if err != nil {
		return err
	}

	return nil
}

// GRPC server
type HelGrpcServer struct {
	ServerConfig *configs.Config
}

func (s *HelGrpcServer) HelOpsProcess(
	ctx context.Context,
	request *protos.HelOpsRequest,
) (ret *protos.HelOpsResponse, err error) {
	log.Printf("Hel-Ops request:\n%+v", request)
	defer func() {
		log.Printf("Hel-Ops result:\n%+v", ret)
	}()

	return ops.HandleOps(request, s.ServerConfig), nil
}

func (s *HelGrpcServer) HelTaskProcess(
	ctx context.Context,
	request *protos.HelTaskRequest,
) (ret *protos.HelTaskResponse, err error) {
	log.Printf("Hel-Task request:\n%+v", request)
	defer func() {
		log.Printf("Hel-Task result:\n%+v", ret)
	}()

	return tasks.HandleTask(request, s.ServerConfig), nil
}

func StartHelGrpc(grpcURL string, config *configs.Config) error {
	lis, err := net.Listen("tcp", grpcURL)
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
		return err
	}

	s := grpc.NewServer()
	protos.RegisterHelServiceServer(s, &HelGrpcServer{ServerConfig: config})

	log.Printf("Hel-gRPC server is starting at %s.", grpcURL)
	err = s.Serve(lis)
	if err != nil {
		log.Fatalf("failed to serve: %v", err)
		return err
	}

	return nil
}
