package constants

import "time"

type Config struct {
	YmirSandbox  string
	ViewerHost   string
	ViewerPort   int
	ViewerURI    string
	MongodbURI   string
	InnerTimeout time.Duration
}
