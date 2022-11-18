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
) (ret *protos.HelOpsResponse, err error) {
	log.Printf("Hel-Ops request:\n%+v", request)
	defer func() {
		log.Printf("Hel-Ops result:\n%+v", ret)
	}()

	m := map[protos.HelOpsType]func(request *protos.HelOpsRequest, config *configs.Config) *protos.HelOpsResponse{
		protos.HelOpsType_HEL_OPS_GET_GPU: ops.OpsGpuInfo,
	}

	if opsFunc, ok := m[request.OpsType]; ok {
		ret = opsFunc(request, s.ServerConfig)
	} else {
		ret = constants.HelRespMessage(constants.CodeHelInvalidParms, request)
	}

	return ret, nil
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
