package configs

import (
	"fmt"

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

	// Hel-config
	AssetsLocation  string
	ModelsLocation  string
	TensorboardRoot string

	// Openpai-config
	OpenpaiHost    string
	OpenpaiToken   string
	OpenpaiStorage string
	OpenpaiUser    string
	OpenpaiCluster string
	OpenpaiGpuType string
	ServerRuntime  string

	// Redis
	RedisURLHel     string
	RedisNumHelGrpc int
	RedisURLHelGrpc string
	RedisNumHelTask int
	RedisURLHelTask string
}

func InitViperConfig(configFile string) *Config {
	bindEnvMap := map[string]string{
		"YmirSandbox":      "BACKEND_SANDBOX_ROOT",
		"ViewerPort":       "VIEWER_HOST_PORT",
		"MongoDBURI":       "MONGODB_URI",
		"MongoDataDBCache": "MONGODB_USE_CACHE",
		"HelGrpcPort":      "HEL_GRPC_PORT",
		"RedisURLHel":      "REDIS_URL_HEL",
		"AssetsLocation":   "ASSETS_PATH",
		"ModelsLocation":   "MODELS_PATH",
		"TensorboardRoot":  "TENSORBOARD_ROOT",
		"OpenpaiHost":      "OPENPAI_HOST",
		"OpenpaiToken":     "OPENPAI_TOKEN",
		"OpenpaiStorage":   "OPENPAI_STORAGE",
		"OpenpaiUser":      "OPENPAI_USER",
		"OpenpaiCluster":   "OPENPAI_CLUSTER",
		"OpenpaiGpuType":   "OPENPAI_GPUTYPE",
		"ServerRuntime":    "SERVER_RUNTIME",
	}
	for k, v := range bindEnvMap {
		err := viper.BindEnv(k, v)
		if err != nil {
			panic(err)
		}
	}

	viper.SetConfigFile(configFile)
	err := viper.ReadInConfig()
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

	return &config
}
