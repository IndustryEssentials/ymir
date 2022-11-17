package dispatcher

import (
	"context"
	"fmt"
	"log"
	"net"

	"github.com/IndustryEssentials/ymir-hel/protos"
	"github.com/RichardKnop/machinery/v1"
	"github.com/RichardKnop/machinery/v1/tasks"
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
	protos.RegisterMirControllerServiceServer(s, HelGrpcServer{TaskServer: taskServer})

	log.Printf("Hel-gRPC server is starting at %s.", grpcURL)
	err = s.Serve(lis)
	if err != nil {
		log.Fatalf("failed to serve: %v", err)
		return err
	}

	return nil
}

func (s HelGrpcServer) DataManageRequest(ctx context.Context, request *protos.GeneralReq) (*protos.GeneralResp, error) {
	log.Printf("Hel-gRPC server is called with request:\n%+v", request)

	signature := &tasks.Signature{
		Name: "add",
		Args: []tasks.Arg{
			{
				Type:  "int64",
				Value: 1,
			},
			{
				Type:  "int64",
				Value: 1,
			},
		},
	}

	asyncResult, err := s.TaskServer.SendTask(signature)
	if err != nil {
		log.Fatalf("failed to SendTask: %v\nerr: %v", signature, err)
		return &protos.GeneralResp{Code: 1, Message: "failed"}, err
	}
	return &protos.GeneralResp{Code: 0, Message: fmt.Sprint(asyncResult)}, nil
}
