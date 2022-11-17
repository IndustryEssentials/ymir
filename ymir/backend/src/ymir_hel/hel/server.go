package hel

import (
	"github.com/IndustryEssentials/ymir-hel/configs"
	"github.com/IndustryEssentials/ymir-hel/hel/dispatcher"

	"github.com/RichardKnop/machinery/v1"
	"github.com/RichardKnop/machinery/v1/config"
	// exampletasks "github.com/RichardKnop/machinery/example/tasks"
)

// Note: pubsub>=v1.25.0

func StartHelServer(config *configs.Config) error {
	taskServer, err := CreateTaskServer(config.RedisURLHelTask, config.HelWorkerTag)
	if err != nil {
		return err
	}
	err = dispatcher.StartHelGrpc(config.HelGrpcURL, taskServer)
	if err != nil {
		return err
	}

	// err = worker.StartHelWorker(taskServer, config.HelWorkerTag, config.HelWorkerNum)
	// if err != nil {
	// 	log.Fatalf("failed to start worker: %v", err)
	// 	return err
	// }

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
	tasks := map[string]interface{}{
		// "add":               exampletasks.Add,
		// "multiply":          exampletasks.Multiply,
		// "sum_ints":          exampletasks.SumInts,
		// "sum_floats":        exampletasks.SumFloats,
		// "concat":            exampletasks.Concat,
		// "split":             exampletasks.Split,
		// "panic_task":        exampletasks.PanicTask,
		// "long_running_task": exampletasks.LongRunningTask,
	}

	return server, server.RegisterTasks(tasks)
}
