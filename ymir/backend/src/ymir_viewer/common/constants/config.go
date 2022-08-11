package constants

import "time"

type Config struct {
	YmirSandbox  string
	ViewerHost   string
	ViewerPort   int
	ViewerUri    string
	MongodbUri   string
	InnerTimeout time.Duration
}
