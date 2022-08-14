package services

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/IndustryEssentials/ymir-viewer/common/constants"
	"github.com/IndustryEssentials/ymir-viewer/common/loader"
	"github.com/IndustryEssentials/ymir-viewer/common/protos"
	"github.com/IndustryEssentials/ymir-viewer/tools"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type BaseMirRepoLoader interface {
	LoadSingleMirData(mirRepo *constants.MirRepo, mirFile constants.MirFile) interface{}
	LoadMutipleMirDatas(mirRepo *constants.MirRepo, mirFiles []constants.MirFile) []interface{}
	LoadAssetsDetail(
		mirRepo *constants.MirRepo,
		anchorAssetID string,
		offset int,
		limit int,
	) ([]constants.MirAssetDetail, int64, int64)
}

type BaseMongoServer interface {
	setExistence(collectionName string, ready bool, insert bool)
	checkExistence(mirRepo *constants.MirRepo) bool
	IndexCollectionData(mirRepo *constants.MirRepo, newData []interface{})
	QueryAssets(
		mirRepo *constants.MirRepo,
		offset int,
		limit int,
		classIds []int,
		currentAssetID string,
		cmTypes []int32,
		cks []string,
		tags []string,
	) constants.QueryAssetsResult
	QueryDatasetStats(mirRepo *constants.MirRepo, classIDs []int) constants.QueryDatasetStatsResult
	QueryDatasetDup(mirRepo0 *constants.MirRepo, mirRepo1 *constants.MirRepo) (int, int64, int64)
	countAssetsInClass(collection *mongo.Collection, queryField string, classIds []int) int64
	getRepoCollection(mirRepo *constants.MirRepo) (*mongo.Collection, string)
}

type ViewerHandler struct {
	mongoServer BaseMongoServer
	mirLoader   BaseMirRepoLoader
}

func NewViewerHandler(mongoURI string, mongoDBName string, clearCache bool) *ViewerHandler {
	var mongoServer *MongoServer
	if len(mongoURI) > 0 {
		mongoCtx := context.Background()
		client, err := mongo.Connect(mongoCtx, options.Client().ApplyURI(mongoURI))
		if err != nil {
			panic(err)
		}

		database := client.Database(mongoDBName)
		if clearCache {
			// Clear cached data.
			err = database.Drop(mongoCtx)
			if err != nil {
				panic(err)
			}
		}

		mongoServer = NewMongoServer(mongoCtx, database)
	}

	return &ViewerHandler{mongoServer: mongoServer, mirLoader: &loader.MirRepoLoader{}}
}

func (v *ViewerHandler) loadAndCacheAssets(mirRepo *constants.MirRepo) {
	defer tools.TimeTrack(time.Now())

	if v.mongoServer.checkExistence(mirRepo) {
		log.Printf("Mongodb ready for %s.", fmt.Sprint(mirRepo))
	} else {
		log.Printf("No data for %s, reading & building cache.", fmt.Sprint(mirRepo))

		mirAssetsDetail, _, _ := v.mirLoader.LoadAssetsDetail(mirRepo, "", 0, 0)

		newData := make([]interface{}, 0)
		for _, v := range mirAssetsDetail {
			newData = append(newData, v)
		}
		v.mongoServer.IndexCollectionData(mirRepo, newData)
	}
}

func (v *ViewerHandler) GetAssetsHandler(
	mirRepo *constants.MirRepo,
	offset int,
	limit int,
	classIDs []int,
	currentAssetID string,
	cmTypes []int32,
	cks []string,
	tags []string,
) constants.QueryAssetsResult {
	// Speed up when "first time" loading, i.e.: cache miss && only offset/limit/currentAssetID are set at most.
	if !v.mongoServer.checkExistence(mirRepo) {
		if len(classIDs) < 1 && len(cmTypes) < 1 && len(cks) < 1 && len(tags) < 1 {
			go v.loadAndCacheAssets(mirRepo)

			mirAssetsDetail, anchor, totalAssetsCount := v.mirLoader.LoadAssetsDetail(
				mirRepo,
				currentAssetID,
				offset,
				limit,
			)
			return constants.QueryAssetsResult{
				AssetsDetail:     mirAssetsDetail,
				Offset:           offset,
				Limit:            limit,
				Anchor:           anchor,
				TotalAssetsCount: totalAssetsCount,
			}
		}
	}

	v.loadAndCacheAssets(mirRepo)
	return v.mongoServer.QueryAssets(
		mirRepo,
		offset,
		limit,
		classIDs,
		currentAssetID,
		cmTypes,
		cks,
		tags,
	)
}

func (v *ViewerHandler) GetDatasetMetaCountsHandler(
	mirRepo *constants.MirRepo,
) constants.QueryDatasetStatsResult {
	defer tools.TimeTrack(time.Now())
	mirContext := v.mirLoader.LoadSingleMirData(mirRepo, constants.MirfileContext).(*protos.MirContext)
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

func (v *ViewerHandler) GetDatasetStatsHandler(
	mirRepo *constants.MirRepo,
	classIds []int,
) constants.QueryDatasetStatsResult {
	v.loadAndCacheAssets(mirRepo)
	return v.mongoServer.QueryDatasetStats(mirRepo, classIds)
}

func (v *ViewerHandler) GetDatasetDupHandler(
	mirRepo0 *constants.MirRepo,
	mirRepo1 *constants.MirRepo,
) (int, int64, int64) {
	v.loadAndCacheAssets(mirRepo0)
	v.loadAndCacheAssets(mirRepo1)
	return v.mongoServer.QueryDatasetDup(mirRepo0, mirRepo1)
}
