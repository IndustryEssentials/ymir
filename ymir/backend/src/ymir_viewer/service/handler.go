package service

import (
	"fmt"
	"log"
	"time"

	"github.com/IndustryEssentials/ymir-viewer/common/constant"
	"github.com/IndustryEssentials/ymir-viewer/common/pbreader"
	"github.com/IndustryEssentials/ymir-viewer/tools"
)

func loadAndCacheAssets(mongo MongoServer, mirRepo constant.MirRepo) {
	defer tools.TimeTrack(time.Now())
	if mongo.checkExistence(mirRepo) {
		log.Printf("Mongodb ready for %s.", fmt.Sprint(mirRepo))
	} else {
		log.Printf("No data for %s, reading & building cache.", fmt.Sprint(mirRepo))
		mirAssetDetails := pbreader.LoadAssetsInfo(mirRepo)

		newData := make([]interface{}, 0)
		for _, v := range mirAssetDetails {
			newData = append(newData, v)
		}
		mongo.IndexMongoData(mirRepo, newData)
	}
}

func GetAssetsHandler(mongo MongoServer, mirRepo constant.MirRepo, offset int, limit int, classIds []int, currentAssetId string) constant.QueryAssetsResult {
	loadAndCacheAssets(mongo, mirRepo)
	return mongo.QueryAssets(mirRepo, offset, limit, classIds, currentAssetId)
}

func GetDatasetStatsHandler(mongo MongoServer, mirRepo constant.MirRepo, classIds []int) constant.QueryDatasetStatsResult {
	loadAndCacheAssets(mongo, mirRepo)
	return mongo.QueryDatasetStats(mirRepo, classIds)
}
