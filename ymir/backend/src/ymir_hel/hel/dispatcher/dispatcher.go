package dispatcher

import (
	"context"
	"log"
	"net"

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
	return ops.GetOpsFunc(request.OpsType)(request, s.ServerConfig), nil
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
