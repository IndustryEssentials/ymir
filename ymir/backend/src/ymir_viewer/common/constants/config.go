package constants

import "time"

type Config struct {
	YmirSandbox string

	ViewerHost string
	ViewerPort int
	ViewerURI  string

	MongoDBURI     string
	MongoDBName    string
	MongoDBNoCache bool

	InnerTimeout time.Duration
}
