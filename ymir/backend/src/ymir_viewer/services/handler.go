package services

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/IndustryEssentials/ymir-viewer/common/constants"
	"github.com/IndustryEssentials/ymir-viewer/common/loader"
	"github.com/IndustryEssentials/ymir-viewer/common/protos"
	"github.com/mitchellh/mapstructure"
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
	LoadModelInfo(mirRepo *constants.MirRepo) *constants.MirdataModel
}

type BaseMongoServer interface {
	CheckDatasetExistenceReady(mirRepo *constants.MirRepo) (bool, bool)
	IndexDatasetData(mirRepo *constants.MirRepo, newData []interface{})
	RemoveNonReadyDataset()
	QueryDatasetAssets(
		mirRepo *constants.MirRepo,
		offset int,
		limit int,
		classIDs []int,
		annoTypes []string,
		currentAssetID string,
		cmTypes []int,
		cks []string,
		tags []string,
	) *constants.QueryAssetsResult
	QueryDatasetStats(
		mirRepo *constants.MirRepo,
		classIDs []int,
		requireAssetsHist bool,
		requireAnnotationsHist bool,
	) *constants.QueryDatasetStatsResult
	MetricsQuerySignals(
		collectionSuffix string,
		userID string,
		classIDs []int,
		queryField string,
		bucket string,
		unit string,
		limit int,
	) *[]constants.MetricsQueryPoint
	MetricsRecordSignals(collectionSuffix string, id string, data interface{})
}

type ViewerHandler struct {
	mongoServer BaseMongoServer
	mirLoader   BaseMirRepoLoader
}

func NewViewerHandler(
	mongoURI string,
	mongoDataDBName string,
	useDataDBCache bool,
	mongoMetricsDBName string,
) *ViewerHandler {
	var mongoServer *MongoServer
	if len(mongoURI) > 0 {
		log.Printf("[viewer] init mongodb %s\n", mongoURI)

		mongoCtx := context.Background()
		client, err := mongo.Connect(mongoCtx, options.Client().ApplyURI(mongoURI))
		if err != nil {
			panic(err)
		}

		mirDatabase := client.Database(mongoDataDBName)
		metricsDatabase := client.Database(mongoMetricsDBName)
		mongoServer = NewMongoServer(mongoCtx, mirDatabase, metricsDatabase)
		if useDataDBCache {
			go mongoServer.RemoveNonReadyDataset()
		} else {
			// Clear cached data.
			err = mirDatabase.Drop(mongoCtx)
			if err != nil {
				panic(err)
			}
		}

	}

	return &ViewerHandler{mongoServer: mongoServer, mirLoader: &loader.MirRepoLoader{}}
}

func (v *ViewerHandler) loadAndIndexAssets(mirRepo *constants.MirRepo) {
	exist, ready := v.mongoServer.CheckDatasetExistenceReady(mirRepo)
	// Dataset not exist, need to load&index.
	if !exist {
		log.Printf("No data for %s, reading & building cache.", mirRepo.TaskID)

		mirAssetsDetail, _, _ := v.mirLoader.LoadAssetsDetail(mirRepo, "", 0, 0)
		newData := make([]interface{}, 0)
		for _, v := range mirAssetsDetail {
			newData = append(newData, v)
		}

		// check again, in case cache process started during data loading.
		exist, _ = v.mongoServer.CheckDatasetExistenceReady(mirRepo)
		if exist {
			log.Printf("Cache exists, skip data indexing.")
			return
		}
		v.mongoServer.IndexDatasetData(mirRepo, newData)
		return
	}

	// Data set exist, return if ready.
	if ready {
		log.Printf("Mongodb ready for %s.", mirRepo.TaskID)
		return
	}

	// Exist, but not ready, wait up to 30s.
	timeout := 30
	for i := 1; i <= timeout; i++ {
		log.Printf("Mongodb %s exists, but not ready, sleep %d/%d", fmt.Sprint(mirRepo), i, timeout)
		time.Sleep(1 * time.Second)
		waitExist, waitReady := v.mongoServer.CheckDatasetExistenceReady(mirRepo)
		if waitExist && waitReady {
			log.Printf("Mongodb ready for %s, after wait %d rounds.", mirRepo.TaskID, i)
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
) *constants.QueryAssetsResult {
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
			return &constants.QueryAssetsResult{
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
) *constants.QueryDatasetStatsResult {
	result := constants.NewQueryDatasetStatsResult()

	mirContext := v.mirLoader.LoadSingleMirData(mirRepo, constants.MirfileContext).(*protos.MirContext)
	result.TotalAssetsCount = int64(mirContext.ImagesCnt)

	gtStats := mirContext.GtStats
	if gtStats != nil {
		result.Gt.NegativeAssetsCount = int64(gtStats.NegativeAssetCnt)
		result.Gt.PositiveAssetsCount = int64(gtStats.PositiveAssetCnt)
		if gtStats.ClassIdsCnt != nil {
			for k, v := range gtStats.ClassIdsCnt {
				result.Gt.ClassIDsCount[int(k)] = int64(v)
			}
		}
		result.Gt.AnnotationsCount = int64(gtStats.TotalCnt)
	}

	predStats := mirContext.PredStats
	if predStats != nil {
		result.Pred.NegativeAssetsCount = int64(predStats.NegativeAssetCnt)
		result.Pred.PositiveAssetsCount = int64(predStats.PositiveAssetCnt)
		if predStats.ClassIdsCnt != nil {
			for k, v := range predStats.ClassIdsCnt {
				result.Pred.ClassIDsCount[int(k)] = int64(v)
			}
		}
		result.Pred.AnnotationsCount = int64(predStats.TotalCnt)
	}

	go v.loadAndCacheAssetsNoPanic(mirRepo)

	return v.fillupDatasetUniverseFields(mirRepo, result)
}

func (v *ViewerHandler) fillupDatasetUniverseFields(
	mirRepo *constants.MirRepo,
	result *constants.QueryDatasetStatsResult,
) *constants.QueryDatasetStatsResult {
	mirTasks := v.mirLoader.LoadSingleMirData(mirRepo, constants.MirfileTasks).(*protos.MirTasks)
	task := mirTasks.Tasks[mirTasks.HeadTaskId]
	result.NewTypesAdded = task.NewTypesAdded

	mirContext := v.mirLoader.LoadSingleMirData(mirRepo, constants.MirfileContext).(*protos.MirContext)
	result.TotalAssetsFileSize = int64(mirContext.TotalAssetMbytes)
	for k, v := range mirContext.CksCnt {
		result.CksCountTotal[k] = int64(v.Cnt)
		result.CksCount[k] = map[string]int64{}
		for k2, v2 := range v.SubCnt {
			result.CksCount[k][k2] = int64(v2)
		}
	}

	if mirContext.GtStats != nil && mirContext.GtStats.TagsCnt != nil {
		for k, v := range mirContext.GtStats.TagsCnt {
			result.Gt.TagsCountTotal[k] = int64(v.Cnt)
			result.Gt.TagsCount[k] = map[string]int64{}
			for k2, v2 := range v.SubCnt {
				result.Gt.TagsCount[k][k2] = int64(v2)
			}
		}
	}

	if mirContext.PredStats != nil {
		result.Pred.EvalClassIDs = mirContext.PredStats.EvalClassIds
		if mirContext.PredStats.TagsCnt != nil {
			for k, v := range mirContext.PredStats.TagsCnt {
				result.Pred.TagsCountTotal[k] = int64(v.Cnt)
				result.Pred.TagsCount[k] = map[string]int64{}
				for k2, v2 := range v.SubCnt {
					result.Pred.TagsCount[k][k2] = int64(v2)
				}
			}
		}
	}

	return result
}

func (v *ViewerHandler) GetDatasetStatsHandler(
	mirRepo *constants.MirRepo,
	classIDs []int,
	requireAssetsHist bool,
	requireAnnotationsHist bool,
) *constants.QueryDatasetStatsResult {
	if len(classIDs) < 1 && !requireAssetsHist && !requireAnnotationsHist {
		panic("same result as dataset_meta_count, should use lightweight interface instead.")
	}
	v.loadAndIndexAssets(mirRepo)
	result := v.mongoServer.QueryDatasetStats(mirRepo, classIDs, requireAssetsHist, requireAnnotationsHist)

	// Backfill task and context info, to align with GetDatasetMetaCountsHandler result.
	return v.fillupDatasetUniverseFields(mirRepo, result)
}

func (v *ViewerHandler) GetDatasetDupHandler(
	candidateMirRepos []*constants.MirRepo,
	corrodeeMirRepos []*constants.MirRepo,
) *constants.QueryDatasetDupResult {
	joinAssetCountMax := 0
	assetsCountMap := make(map[string]int64, len(candidateMirRepos))
	candidateMetadatas := []*protos.MirMetadatas{}
	for _, mirRepo := range candidateMirRepos {
		candidateMetadata := v.mirLoader.LoadSingleMirData(mirRepo, constants.MirfileMetadatas).(*protos.MirMetadatas)

		joinAssetCountMax += len(candidateMetadata.Attributes)
		assetsCountMap[mirRepo.TaskID] = int64(len(candidateMetadata.Attributes))
		candidateMetadatas = append(candidateMetadatas, candidateMetadata)
	}

	// Count dups.
	dupCount := 0
	joinedAssetIDMap := make(map[string]bool, joinAssetCountMax)
	for _, candidateMetadata := range candidateMetadatas {
		for assetID := range candidateMetadata.Attributes {
			if _, ok := joinedAssetIDMap[assetID]; ok {
				dupCount++
			} else {
				joinedAssetIDMap[assetID] = true
			}
		}
	}

	// Count corrode residency.
	residualCountMap := make(map[string]int64, len(corrodeeMirRepos))
	for _, mirRepo := range corrodeeMirRepos {
		corrodeeMetadata := v.mirLoader.LoadSingleMirData(mirRepo, constants.MirfileMetadatas).(*protos.MirMetadatas)

		residualCount := len(corrodeeMetadata.Attributes)
		for assetID := range corrodeeMetadata.Attributes {
			if _, ok := joinedAssetIDMap[assetID]; ok {
				residualCount--
			}
		}
		residualCountMap[mirRepo.TaskID] = int64(residualCount)
	}

	return &constants.QueryDatasetDupResult{
		Duplication:   dupCount,
		TotalCount:    assetsCountMap,
		ResidualCount: residualCountMap,
	}
}

func (v *ViewerHandler) GetModelInfoHandler(
	mirRepo *constants.MirRepo,
) *constants.MirdataModel {
	return v.mirLoader.LoadModelInfo(mirRepo)
}

func (v *ViewerHandler) MetricsRecordHandler(
	metricsGroup string,
	postForm map[string]interface{},
) {
	dataType := constants.ParseMirMetrics(metricsGroup)
	if dataType == constants.MetricsUnknown {
		panic("unknown metrics type")
	}

	data := constants.MetricsDataPoint{}
	err := mapstructure.Decode(postForm, &data)
	if err != nil {
		panic(err)
	}

	v.mongoServer.MetricsRecordSignals(metricsGroup, postForm["id"].(string), data)
}

func (v *ViewerHandler) MetricsQueryHandler(
	metricsGroup string,
	userID string,
	classIDs []int,
	queryField string,
	bucket string,
	unit string,
	limit int,
) *[]constants.MetricsQueryPoint {
	dataType := constants.ParseMirMetrics(metricsGroup)
	if dataType == constants.MetricsUnknown {
		panic("unknown metrics type")
	}

	return v.mongoServer.MetricsQuerySignals(metricsGroup, userID, classIDs, queryField, bucket, unit, limit)
}
