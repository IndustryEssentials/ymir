package hel

import (
	"github.com/IndustryEssentials/ymir-hel/configs"
	"github.com/IndustryEssentials/ymir-hel/hel/dispatcher"

	"github.com/RichardKnop/machinery/v1"
	"github.com/RichardKnop/machinery/v1/config"
)

// Note: pubsub>=v1.25.0

func StartHelServer(config *configs.Config) error {
	err := dispatcher.StartHelGrpc(config.HelGrpcURL, config)
	if err != nil {
		return err
	}

	return nil
}

func CreateTaskServer(RedisURLHelTask string, consumerTag string) (*machinery.Server, error) {
	cnf := &config.Config{
		DefaultQueue:    consumerTag,
		ResultsExpireIn: 3600,
		Broker:          RedisURLHelTask,
		ResultBackend:   RedisURLHelTask,
		Redis: &config.RedisConfig{
			MaxIdle:                3,
			IdleTimeout:            240,
			ReadTimeout:            15,
			WriteTimeout:           15,
			ConnectTimeout:         15,
			NormalTasksPollPeriod:  1000,
			DelayedTasksPollPeriod: 500,
		},
	}

	server, err := machinery.NewServer(cnf)
	if err != nil {
		return nil, err
	}

	// Register tasks
	tasks := map[string]interface{}{}

	return server, server.RegisterTasks(tasks)
}
