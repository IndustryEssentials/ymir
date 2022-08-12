package services

import (
	"fmt"
	"log"
	"time"

	"github.com/IndustryEssentials/ymir-viewer/common/constants"
	"github.com/IndustryEssentials/ymir-viewer/common/loader"
	"github.com/IndustryEssentials/ymir-viewer/common/protos"
	"github.com/IndustryEssentials/ymir-viewer/tools"
)

func loadAndCacheAssets(mongo MongoServer, mirLoader loader.BaseMirRepoLoader) {
	defer tools.TimeTrack(time.Now())

	mirRepo := mirLoader.GetMirRepo()
	if mongo.checkExistence(mirRepo) {
		log.Printf("Mongodb ready for %s.", fmt.Sprint(mirRepo))
	} else {
		log.Printf("No data for %s, reading & building cache.", fmt.Sprint(mirRepo))
		mirAssetsDetail, _, _ := mirLoader.LoadAssetsDetail("", 0, 0)

		newData := make([]interface{}, 0)
		for _, v := range mirAssetsDetail {
			newData = append(newData, v)
		}
		mongo.IndexMongoData(mirRepo, newData)
	}
}

func GetAssetsHandler(
	mongo MongoServer,
	mirLoader loader.BaseMirRepoLoader,
	offset int,
	limit int,
	classIds []int,
	currentAssetId string,
	cmTypes []int32,
	cks []string,
	tags []string,
) constants.QueryAssetsResult {
	// Speed up when "first time" loading, i.e.: cache miss && only offset/limit/currentAssetId are set at most.
	if !mongo.checkExistence(mirLoader.GetMirRepo()) {
		if len(classIds) < 1 && len(cmTypes) < 1 && len(cks) < 1 && len(tags) < 1 {
			go loadAndCacheAssets(mongo, mirLoader)

			mirAssetsDetail, anchor, totalAssetsCount := mirLoader.LoadAssetsDetail(currentAssetId, offset, limit)
			return constants.QueryAssetsResult{
				AssetsDetail:     mirAssetsDetail,
				Offset:           offset,
				Limit:            limit,
				Anchor:           anchor,
				TotalAssetsCount: totalAssetsCount,
			}
		}
	}

	loadAndCacheAssets(mongo, mirLoader)
	return mongo.QueryAssets(mirLoader.GetMirRepo(), offset, limit, classIds, currentAssetId, cmTypes, cks, tags)
}

func GetDatasetMetaCountsHandler(
	mirLoader loader.BaseMirRepoLoader,
) constants.QueryDatasetStatsResult {
	defer tools.TimeTrack(time.Now())
	mirContext := mirLoader.LoadSingleMirData(constants.MirfileContext).(*protos.MirContext)
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

	for k, v := range mirContext.CksCnt {
		result.CksCountTotal[k] = int64(v.Cnt)
		result.CksCount[k] = map[string]int64{}
		for k2, v2 := range v.SubCnt {
			result.CksCount[k][k2] = int64(v2)
		}
	}

	return result
}

func GetDatasetStatsHandler(
	mongo MongoServer,
	mirLoader loader.BaseMirRepoLoader,
	classIds []int,
) constants.QueryDatasetStatsResult {
	loadAndCacheAssets(mongo, mirLoader)
	return mongo.QueryDatasetStats(mirLoader.GetMirRepo(), classIds)
}

func GetDatasetDupHandler(
	mongo MongoServer,
	mirLoader0 loader.BaseMirRepoLoader,
	mirLoader1 loader.BaseMirRepoLoader,
) (int, int64, int64) {
	loadAndCacheAssets(mongo, mirLoader0)
	loadAndCacheAssets(mongo, mirLoader1)
	return mongo.QueryDatasetDup(mirLoader0.GetMirRepo(), mirLoader1.GetMirRepo())
}
