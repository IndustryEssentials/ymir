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
	LoadModelInfo(mirRepo *constants.MirRepo) constants.MirdataModel
}

type BaseMongoServer interface {
	CheckDatasetExistenceReady(mirRepo *constants.MirRepo) (bool, bool)
	IndexDatasetData(mirRepo *constants.MirRepo, newData []interface{})
	QueryDatasetAssets(
		mirRepo *constants.MirRepo,
		offset int,
		limit int,
		classIds []int,
		annoTypes []string,
		currentAssetID string,
		cmTypes []int,
		cks []string,
		tags []string,
	) constants.QueryAssetsResult
	QueryDatasetDup(mirRepo0 *constants.MirRepo, mirRepo1 *constants.MirRepo) constants.QueryDatasetDupResult
	QueryDatasetStats(mirRepo *constants.MirRepo, classIDs []int) constants.QueryDatasetStatsResult
}

type ViewerHandler struct {
	mongoServer BaseMongoServer
	mirLoader   BaseMirRepoLoader
}

func NewViewerHandler(mongoURI string, mongoDBName string, clearCache bool) *ViewerHandler {
	var mongoServer *MongoServer
	if len(mongoURI) > 0 {
		log.Printf("[viewer] init mongodb %s\n", mongoURI)

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

func (v *ViewerHandler) loadAndIndexAssets(mirRepo *constants.MirRepo) {
	defer tools.TimeTrack(time.Now())

	exist, ready := v.mongoServer.CheckDatasetExistenceReady(mirRepo)
	// Dataset not exist, need to load&index.
	if !exist {
		log.Printf("No data for %s, reading & building cache.", fmt.Sprint(mirRepo))

		mirAssetsDetail, _, _ := v.mirLoader.LoadAssetsDetail(mirRepo, "", 0, 0)

		newData := make([]interface{}, 0)
		for _, v := range mirAssetsDetail {
			newData = append(newData, v)
		}
		v.mongoServer.IndexDatasetData(mirRepo, newData)
		return
	}

	// Data set exist, return if ready.
	if ready {
		log.Printf("Mongodb ready for %s.", fmt.Sprint(mirRepo))
		return
	}

	// Exist, but not ready, wait up to 30s.
	timeout := 30
	for i := 1; i <= timeout; i++ {
		log.Printf("Mongodb %s exists, but not ready, sleep %d/%d", fmt.Sprint(mirRepo), i, timeout)
		time.Sleep(1 * time.Second)
		waitExist, waitReady := v.mongoServer.CheckDatasetExistenceReady(mirRepo)
		if waitExist && waitReady {
			log.Printf("Mongodb ready for %s, after wait %d rounds.", fmt.Sprint(mirRepo), i)
			return
		}
	}
	panic("loadAndIndexAssets timeout")
}

func (v *ViewerHandler) loadAndCacheAssetsNoPanic(mirRepo *constants.MirRepo) {
	defer func() {
		if r := recover(); r != nil {
			log.Printf("loadAndCacheAssetsNoPanic panic %v", r)
		}
	}()
	v.loadAndIndexAssets(mirRepo)
}

func (v *ViewerHandler) GetAssetsHandler(
	mirRepo *constants.MirRepo,
	offset int,
	limit int,
	classIDs []int,
	annoTypes []string,
	currentAssetID string,
	cmTypes []int,
	cks []string,
	tags []string,
) constants.QueryAssetsResult {
	// Speed up when "first time" loading, i.e.: cache miss && only offset/limit/currentAssetID are set at most.
	_, ready := v.mongoServer.CheckDatasetExistenceReady(mirRepo)
	if !ready {
		if len(classIDs) < 1 && len(annoTypes) < 1 && len(cmTypes) < 1 && len(cks) < 1 && len(tags) < 1 {
			go v.loadAndCacheAssetsNoPanic(mirRepo)

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

	v.loadAndIndexAssets(mirRepo)
	return v.mongoServer.QueryDatasetAssets(
		mirRepo,
		offset,
		limit,
		classIDs,
		annoTypes,
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
	v.loadAndIndexAssets(mirRepo)
	return v.mongoServer.QueryDatasetStats(mirRepo, classIds)
}

func (v *ViewerHandler) GetDatasetDupHandler(
	mirRepo0 *constants.MirRepo,
	mirRepo1 *constants.MirRepo,
) constants.QueryDatasetDupResult {
	v.loadAndIndexAssets(mirRepo0)
	v.loadAndIndexAssets(mirRepo1)
	return v.mongoServer.QueryDatasetDup(mirRepo0, mirRepo1)
}
