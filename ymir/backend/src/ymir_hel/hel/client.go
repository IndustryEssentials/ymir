package hel

import (
	"context"
	"log"
	"time"

	"github.com/IndustryEssentials/ymir-hel/protos"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

func GrpcClientCall(addr string) error {
	// Set up a connection to the server.
	conn, err := grpc.Dial(addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("did not connect: %v", err)
		return err
	}
	defer conn.Close()
	c := protos.NewHelServiceClient(conn)

	// Contact the server and print out its response.
	ctx, cancel := context.WithTimeout(context.Background(), time.Second*60)
	defer cancel()
	r, err := c.HelOpsProcess(ctx, &protos.HelOpsRequest{OpsType: protos.HelOpsType_HEL_OPS_GET_GPU})
	if err != nil {
		log.Fatalf("serverice fail: %v", err)
		return err
	}
	log.Printf("Response: %+v", r)
	return nil
}
