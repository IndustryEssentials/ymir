package main

import (
	"os"

	"github.com/urfave/cli"

	"github.com/IndustryEssentials/ymir-hel/configs"
	server_grpc "github.com/IndustryEssentials/ymir-hel/grpc/server"
	server_viewer "github.com/IndustryEssentials/ymir-hel/viewer/server"
)

func BuildCliApp(config *configs.Config) (*cli.App, error) {
	app := cli.NewApp()
	app.Commands = []cli.Command{
		{
			Name:  "viewer",
			Usage: "start YMIR-Viewer Service.",
			Action: func(c *cli.Context) error {
				if err := server_viewer.StartViewerServer(config); err != nil {
					return cli.NewExitError(err.Error(), 1)
				}
				return nil
			},
		},
		{
			Name:  "grpc_service",
			Usage: "launch YMIR-Hel Grpc Service.",
			Action: func(c *cli.Context) error {
				if err := server_grpc.StartGrpcService(config); err != nil {
					return cli.NewExitError(err.Error(), 1)
				}
				return nil
			},
		},
		{
			Name:  "grpc_client",
			Usage: "call YMIR-Hel Grpc Service.",
			Action: func(c *cli.Context) error {
				if err := server_grpc.GrpcClientCall(config.HelGrpcURL); err != nil {
					return cli.NewExitError(err.Error(), 1)
				}
				return nil
			},
		},
	}

	return app, nil
}

func main() {
	helConfig := configs.InitViperConfig("configs/config.yml")

	app, err := BuildCliApp(helConfig)
	if err != nil {
		panic(err)
	}
	// Run the CLI app
	err = app.Run(os.Args)
	if err != nil {
		panic(err)
	}
}
