package worker

import (
	"log"

	"github.com/RichardKnop/machinery/v1"
	"github.com/RichardKnop/machinery/v1/tasks"
)

func StartHelWorker(taskServer *machinery.Server, consumerTag string, consumerNum int) error {
	worker := taskServer.NewWorker(consumerTag, consumerNum)

	errorhandler := func(err error) {
		log.Fatalln("error handler", consumerTag, err)
	}

	pretaskhandler := func(signature *tasks.Signature) {
		log.Println("start worker", consumerTag, signature.Name)
	}

	posttaskhandler := func(signature *tasks.Signature) {
		log.Println("end worker", consumerTag, signature.Name)
	}

	worker.SetPostTaskHandler(posttaskhandler)
	worker.SetErrorHandler(errorhandler)
	worker.SetPreTaskHandler(pretaskhandler)
	return worker.Launch()
}
