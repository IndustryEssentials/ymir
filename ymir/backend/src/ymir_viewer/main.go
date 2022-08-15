package main

import (
	"fmt"
	"log"

	"github.com/spf13/viper"

	"github.com/IndustryEssentials/ymir-viewer/common/constants"
	"github.com/IndustryEssentials/ymir-viewer/services"
)

func InitViperConfig() constants.Config {
	err := viper.BindEnv("YmirSandbox", "BACKEND_SANDBOX_ROOT")
	if err != nil {
		panic(err)
	}
	err = viper.BindEnv("ViewerPort", "VIEWER_HOST_PORT")
	if err != nil {
		panic(err)
	}
	err = viper.BindEnv("MongoDBURI", "MONGODB_URI")
	if err != nil {
		panic(err)
	}

	viper.SetConfigName("config")
	viper.SetConfigType("yml")
	viper.AddConfigPath(".")
	err = viper.ReadInConfig()
	if err != nil {
		panic(err)
	}

	var config constants.Config
	err = viper.Unmarshal(&config)
	if err != nil {
		panic(err)
	}

	if len(config.ViewerURI) < 1 {
		config.ViewerURI = fmt.Sprintf("%s:%d", config.ViewerHost, config.ViewerPort)
	}

	log.Printf("viewer config: %+v\n", config)
	return config
}

func main() {
	viewerServer := services.NewViewerServer(InitViperConfig())
	defer viewerServer.Clear()

	viewerServer.Start()
}
