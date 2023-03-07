package main

import (
	"fmt"
	"os"

	"github.com/urfave/cli/v2"

	"github.com/IndustryEssentials/ymir-hel/configs"
	hel_server "github.com/IndustryEssentials/ymir-hel/hel"
	viewer_client "github.com/IndustryEssentials/ymir-hel/viewer/client"
	viewer_server "github.com/IndustryEssentials/ymir-hel/viewer/server"
)

func BuildCliApp(config *configs.Config) (*cli.App, error) {
	var userID string
	var repoID string
	var taskID string

	app := &cli.App{
		Name:  "YMIR Hel",
		Usage: "YMIR Hel Server",
		Action: func(c *cli.Context) error {
			fmt.Println("YMIR Hel, see --help for usage")
			return nil
		},
	}

	app.Commands = []*cli.Command{
		{
			Name:    "viewer",
			Aliases: []string{"v"},
			Usage:   "start YMIR-Viewer Service.",
			Action: func(c *cli.Context) error {
				if err := viewer_server.StartViewerServer(config); err != nil {
					return cli.Exit(err.Error(), 1)
				}
				return nil
			},
		},
		{
			Name:    "viewer_client",
			Aliases: []string{"vc"},
			Usage:   "start YMIR-Viewer Client Call.",
			Flags: []cli.Flag{
				&cli.StringFlag{
					Name:        "user_id",
					Aliases:     []string{"uid"},
					Usage:       "user id",
					Destination: &userID,
				},
				&cli.StringFlag{
					Name:        "repo_id",
					Aliases:     []string{"rid"},
					Usage:       "repo id",
					Destination: &repoID,
				},
				&cli.StringFlag{
					Name:        "task_id",
					Aliases:     []string{"tid"},
					Usage:       "task id",
					Destination: &taskID,
				},
			},
			Subcommands: []*cli.Command{
				{
					Name:  "index",
					Usage: "create dataset index",
					Action: func(c *cli.Context) error {
						if err := viewer_client.IndexDataset(config.ViewerURI, userID, repoID, taskID); err != nil {
							return cli.Exit(err.Error(), 1)
						}
						return nil
					},
				},
				{
					Name:  "query",
					Usage: "query dataset metadata",
					Action: func(c *cli.Context) error {
						if err := viewer_client.QueryDataset(config.ViewerURI, userID, repoID, taskID); err != nil {
							return cli.Exit(err.Error(), 1)
						}
						return nil
					},
				},
			},
		}, {
			Name:  "hel",
			Usage: "launch YMIR-Hel Service.",
			Action: func(c *cli.Context) error {
				if err := hel_server.StartHelServer(config); err != nil {
					return cli.Exit(err.Error(), 1)
				}
				return nil
			},
		},
		{
			Name:    "hel_client",
			Aliases: []string{"hc"},
			Usage:   "call YMIR-Hel Service.",
			Action: func(c *cli.Context) error {
				if err := hel_server.GrpcClientCall(config.HelGrpcURL); err != nil {
					return cli.Exit(err.Error(), 1)
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
