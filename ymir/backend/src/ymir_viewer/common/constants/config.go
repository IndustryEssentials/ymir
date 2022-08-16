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

// const {
// 	BYTES_PER_MB = 1048576
// QUALITY_DESC_LOWER_BNDS = [x / 10 for x in range(10, -1, -1)]
// ANNO_AREA_DESC_LOWER_BNDS = [200000, 100000, 50000, 10000, 5000, 2500, 500, 50, 0]
// ASSET_BYTES_DESC_LOWER_BNDS = [x * BYTES_PER_MB / 2 for x in range(10, -1, -1)]
// ASSET_AREA_DESC_LOWER_BNDS = [8000000, 6000000, 4000000, 2000000, 1000000, 500000, 100000, 0]
// ASSET_HW_RATIO_DESC_LOWER_BNDS = [x / 10 for x in range(15, -1, -1)]
// }
