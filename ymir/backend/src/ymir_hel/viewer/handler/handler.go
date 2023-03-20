package handler

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/IndustryEssentials/ymir-hel/common/constants"
	"github.com/IndustryEssentials/ymir-hel/common/db/mongodb"
	"github.com/IndustryEssentials/ymir-hel/common/loader"
	"github.com/IndustryEssentials/ymir-hel/protos"
	"github.com/mitchellh/mapstructure"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type BaseMirRepoLoader interface {
	LoadSingleMirData(mirRepo *constants.MirRepo, mirFile constants.MirFile) interface{}
	LoadMutipleMirDatas(mirRepo *constants.MirRepo, mirFiles []constants.MirFile) []interface{}
	LoadModelInfo(mirRepo *constants.MirRepo) *constants.MirdataModel
}

type BaseMongoServer interface {
	CheckDatasetIndex(mirRepo *constants.MirRepo) (bool, bool)
	IndexDatasetData(
		mirRepo *constants.MirRepo,
		mirMetadatas *protos.MirMetadatas,
		mirAnnotations *protos.MirAnnotations,
	)
	RemoveNonReadyDataset()
	QueryDatasetAssets(
		mirRepo *constants.MirRepo,
		offset int,
		limit int,
		classIDs []int,
		annoTypes []string,
		currentAssetID string,
		inCMTypes []int,
		exCMTypes []int,
		cks []string,
		tags []string,
	) *constants.QueryAssetsResult
	QueryDatasetStats(
		mirRepo *constants.MirRepo,
		classIDs []int,
		requireAssetsHist bool,
		requireAnnotationsHist bool,
		result *constants.QueryDatasetStatsResult,
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
	mongoConnectTimeout int32,
) *ViewerHandler {
	var mongoServer *mongodb.MongoServer
	if len(mongoURI) > 0 {
		log.Printf("[viewer init] initing mongodb %s\n", mongoURI)

		mongoCtx := context.Background()
		client, err := mongo.Connect(
			mongoCtx,
			options.Client().
				ApplyURI(mongoURI).
				SetServerSelectionTimeout(1*time.Second).
				SetConnectTimeout(time.Duration(mongoConnectTimeout)*time.Second),
		)
		if err != nil {
			panic(err)
		}
		err = client.Ping(mongoCtx, nil)
		if err != nil {
			panic(err)
		}
		log.Printf("[viewer init] connect mongodb succeed.\n")

		mirDatabase := client.Database(mongoDataDBName)
		metricsDatabase := client.Database(mongoMetricsDBName)
		mongoServer = mongodb.NewMongoServer(mongoCtx, mirDatabase, metricsDatabase)
		if useDataDBCache {
			go func() {
				defer func() {
					if r := recover(); r != nil {
						fmt.Printf("RemoveNonReadyDataset fails: %s\n", r)
					}
				}()
				mongoServer.RemoveNonReadyDataset()
			}()
		} else {
			// Clear cached data.
			log.Printf("[viewer init] drop cached mongodb.\n")
			err = mirDatabase.Drop(mongoCtx)
			if err != nil {
				panic(err)
			}
		}

	}

	log.Printf("[viewer init] init mongodb succeed.\n")
	return &ViewerHandler{mongoServer: mongoServer, mirLoader: &loader.MirRepoLoader{}}
}

func (v *ViewerHandler) loadAndIndexAssets(mirRepo *constants.MirRepo) {
	exist, _ := v.mongoServer.CheckDatasetIndex(mirRepo)
	if exist {
		return
	}

	log.Printf("Mongodb %s not exist, loading mirdatas.", mirRepo.TaskID)
	filesToLoad := []constants.MirFile{constants.MirfileMetadatas, constants.MirfileAnnotations}
	mirDatas := v.mirLoader.LoadMutipleMirDatas(mirRepo, filesToLoad)
	mirMetadatas := mirDatas[0].(*protos.MirMetadatas)
	mirAnnotations := mirDatas[1].(*protos.MirAnnotations)
	v.mongoServer.IndexDatasetData(mirRepo, mirMetadatas, mirAnnotations)
}

func (v *ViewerHandler) GetAssetsHandler(
	mirRepo *constants.MirRepo,
	offset int,
	limit int,
	classIDs []int,
	annoTypes []string,
	currentAssetID string,
	inCMTypes []int,
	exCMTypes []int,
	cks []string,
	tags []string,
) *constants.QueryAssetsResult {
	v.loadAndIndexAssets(mirRepo)
	return v.mongoServer.QueryDatasetAssets(
		mirRepo,
		offset,
		limit,
		classIDs,
		annoTypes,
		currentAssetID,
		inCMTypes,
		exCMTypes,
		cks,
		tags,
	)
}

func (v *ViewerHandler) GetDatasetMetaCountsHandler(
	mirRepo *constants.MirRepo,
	checkIndexOnly bool,
) *constants.QueryDatasetStatsResult {
	result := constants.NewQueryDatasetStatsResult()
	exist, ready := v.mongoServer.CheckDatasetIndex(mirRepo)
	if !exist {
		// Index dataset in background task.
		go func() {
			defer func() {
				if r := recover(); r != nil {
					fmt.Printf("background index fails: %s\n", r)
				}
			}()
			v.loadAndIndexAssets(mirRepo)
		}()
	}

	result.QueryContext.RepoIndexExist = exist
	result.QueryContext.RepoIndexReady = ready
	result.QueryContext.CheckIndexOnly = checkIndexOnly
	if checkIndexOnly {
		return result
	}

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
		if gtStats.ClassIdsObjCnt != nil {
			for k, v := range gtStats.ClassIdsObjCnt {
				result.Gt.ClassObjCount[int(k)] = int64(v)
			}
		}
		result.Gt.AnnotationsCount = int64(gtStats.TotalObjCnt)

		result.Gt.TotalMaskArea = int64(gtStats.TotalMaskArea)
		if gtStats.ClassIdsMaskArea != nil {
			for k, v := range gtStats.ClassIdsMaskArea {
				result.Gt.ClassIDsMaskArea[int(k)] = int64(v)
			}
		}
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
		if predStats.ClassIdsObjCnt != nil {
			for k, v := range predStats.ClassIdsObjCnt {
				result.Pred.ClassObjCount[int(k)] = int64(v)
			}
		}
		result.Pred.AnnotationsCount = int64(predStats.TotalObjCnt)

		result.Pred.TotalMaskArea = int64(predStats.TotalMaskArea)
		if predStats.ClassIdsMaskArea != nil {
			for k, v := range predStats.ClassIdsMaskArea {
				result.Pred.ClassIDsMaskArea[int(k)] = int64(v)
			}
		}
	}

	mirTasks := v.mirLoader.LoadSingleMirData(mirRepo, constants.MirfileTasks).(*protos.MirTasks)
	task := mirTasks.Tasks[mirTasks.HeadTaskId]
	result.NewTypesAdded = task.NewTypesAdded
	if task.Evaluation != nil {
		result.EvaluationState = int(task.Evaluation.State)
	}

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
	// Use metadata_handler to fill basic info.
	result := v.GetDatasetMetaCountsHandler(mirRepo, false)
	// Two fields need indexed data:
	// 1. negative counts (classIDs)
	// 2. build histogram (requireAssetsHist, requireAnnotationsHist)
	return v.mongoServer.QueryDatasetStats(mirRepo, classIDs, requireAssetsHist, requireAnnotationsHist, result)
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
