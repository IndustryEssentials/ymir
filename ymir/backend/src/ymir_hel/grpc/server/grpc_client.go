package server

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
	c := protos.NewMirControllerServiceClient(conn)

	// Contact the server and print out its response.
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()
	r, err := c.DataManageRequest(ctx, &protos.GeneralReq{UserId: "0001"})
	if err != nil {
		log.Fatalf("serverice fail: %v", err)
		return err
	}
	log.Printf("Succeed: %s", r.GetMessage())
	return nil
}
