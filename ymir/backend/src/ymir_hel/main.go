package main

import (
	"os"

	"github.com/urfave/cli"

	"github.com/IndustryEssentials/ymir-hel/configs"
	server_hel "github.com/IndustryEssentials/ymir-hel/hel"
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
			Name:  "hel",
			Usage: "launch YMIR-Hel Service.",
			Action: func(c *cli.Context) error {
				if err := server_hel.StartHelServer(config); err != nil {
					return cli.NewExitError(err.Error(), 1)
				}
				return nil
			},
		},
		{
			Name:  "hel_client",
			Usage: "call YMIR-Hel Service.",
			Action: func(c *cli.Context) error {
				if err := server_hel.GrpcClientCall(config.HelGrpcURL); err != nil {
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
