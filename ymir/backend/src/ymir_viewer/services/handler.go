package services

import (
	"fmt"
	"log"
	"time"

	"github.com/IndustryEssentials/ymir-viewer/common/constants"
	"github.com/IndustryEssentials/ymir-viewer/common/pbreader"
	"github.com/IndustryEssentials/ymir-viewer/common/protos"
	"github.com/IndustryEssentials/ymir-viewer/tools"
)

func loadAndCacheAssets(mongo MongoServer, mirRepo constants.MirRepo) {
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

func GetAssetsHandler(
	mongo MongoServer,
	mirRepo constants.MirRepo,
	offset int,
	limit int,
	classIds []int,
	currentAssetId string,
	cmTypes []int32,
	cks []string,
	tags []string,
) constants.QueryAssetsResult {
	loadAndCacheAssets(mongo, mirRepo)
	return mongo.QueryAssets(mirRepo, offset, limit, classIds, currentAssetId, cmTypes, cks, tags)
}

func GetDatasetMetaCountsHandler(
	mongo MongoServer,
	mirRepo constants.MirRepo,
) constants.QueryDatasetStatsResult {
	defer tools.TimeTrack(time.Now())
	mirContext := pbreader.LoadSingleMirData(mirRepo, constants.MirfileContext).(*protos.MirContext)
	result := constants.NewQueryDatasetStatsResult()
	result.TotalAssetsCount = int64(mirContext.ImagesCnt)

	gtStats := mirContext.GtStats
	result.Gt.NegativeImagesCount = int64(gtStats.NegativeAssetCnt)
	result.Gt.PositiveImagesCount = int64(gtStats.PositiveAssetCnt)
	for k, v := range gtStats.ClassIdsCnt {
		result.Gt.ClassIdsCount[int(k)] = int64(v)
	}

	predStats := mirContext.PredStats
	result.Pred.NegativeImagesCount = int64(predStats.NegativeAssetCnt)
	result.Pred.PositiveImagesCount = int64(predStats.PositiveAssetCnt)
	for k, v := range predStats.ClassIdsCnt {
		result.Pred.ClassIdsCount[int(k)] = int64(v)
	}

	return result
}

func GetDatasetStatsHandler(
	mongo MongoServer,
	mirRepo constants.MirRepo,
	classIds []int,
) constants.QueryDatasetStatsResult {
	loadAndCacheAssets(mongo, mirRepo)
	return mongo.QueryDatasetStats(mirRepo, classIds)
}

func GetDatasetDupHandler(
	mongo MongoServer,
	mirRepo0 constants.MirRepo,
	mirRepo1 constants.MirRepo,
) (int, int64, int64) {
	loadAndCacheAssets(mongo, mirRepo0)
	loadAndCacheAssets(mongo, mirRepo1)
	return mongo.QueryDatasetDup(mirRepo0, mirRepo1)
}
