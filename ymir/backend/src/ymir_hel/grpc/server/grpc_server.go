package server

import (
	"context"
	"log"
	"net"

	"github.com/IndustryEssentials/ymir-hel/configs"
	"github.com/IndustryEssentials/ymir-hel/protos"
	"google.golang.org/grpc"
)

type HelGrpcServer struct{}

func (s HelGrpcServer) DataManageRequest(ctx context.Context, request *protos.GeneralReq) (*protos.GeneralResp, error) {
	log.Printf("Hel-gRPC server is called with request: \n%+v", request)
	return &protos.GeneralResp{Code: 1, Message: "response"}, nil
}

func StartGrpcService(config *configs.Config) error {
	lis, err := net.Listen("tcp", config.HelGrpcURL)
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	s := grpc.NewServer()
	log.Printf("Hel-gRPC server is running at %s.", config.HelGrpcURL)
	protos.RegisterMirControllerServiceServer(s, HelGrpcServer{})
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
	return nil
}
