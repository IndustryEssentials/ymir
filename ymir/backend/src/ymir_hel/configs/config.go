package configs

import (
	"fmt"
	"log"

	"github.com/spf13/viper"
)

type Config struct {
	YmirSandbox string

	ViewerHost    string
	ViewerPort    int
	ViewerURI     string
	ViewerTimeout int32

	MongoDBURI         string
	MongoDataDBName    string
	MongoDataDBCache   bool
	MongoMetricsDBName string

	// Hel-grpc config
	HelGrpcHost string
	HelGrpcPort int
	HelGrpcURL  string

	// Hel-machineary config
	HelWorkerNum int
	HelWorkerTag string

	// Redis
	RedisURLHel     string
	RedisNumHelGrpc int
	RedisURLHelGrpc string
	RedisNumHelTask int
	RedisURLHelTask string
}

func InitViperConfig(configFile string) *Config {
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
	err = viper.BindEnv("MongoDataDBCache", "MONGODB_USE_CACHE")
	if err != nil {
		panic(err)
	}

	err = viper.BindEnv("HelGrpcPort", "HEL_GRPC_PORT")
	if err != nil {
		panic(err)
	}
	err = viper.BindEnv("RedisURLHel", "REDIS_URL_HEL")
	if err != nil {
		panic(err)
	}

	viper.SetConfigFile(configFile)
	err = viper.ReadInConfig()
	if err != nil {
		panic(err)
	}

	var config Config
	err = viper.Unmarshal(&config)
	if err != nil {
		panic(err)
	}

	if len(config.ViewerURI) < 1 {
		config.ViewerURI = fmt.Sprintf("%s:%d", config.ViewerHost, config.ViewerPort)
	}
	if len(config.HelGrpcURL) < 1 {
		config.HelGrpcURL = fmt.Sprintf("%s:%d", config.HelGrpcHost, config.HelGrpcPort)
	}

	config.RedisURLHelGrpc = fmt.Sprintf("%s/%d", config.RedisURLHel, config.RedisNumHelGrpc)
	config.RedisURLHelTask = fmt.Sprintf("%s/%d", config.RedisURLHel, config.RedisNumHelTask)

	log.Printf("ymir-hel config: %+v\n\n", config)
	return &config
}
