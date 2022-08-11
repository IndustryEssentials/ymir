package services

import (
	"log"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/IndustryEssentials/ymir-viewer/common/constants"
	"github.com/IndustryEssentials/ymir-viewer/common/loader"
	"github.com/IndustryEssentials/ymir-viewer/common/protos"
	docs "github.com/IndustryEssentials/ymir-viewer/docs"
	"github.com/gin-gonic/gin"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"
	"go.mongodb.org/mongo-driver/bson"
)

type ViewerServer struct {
	addr    string
	gin     *gin.Engine
	Mongo   MongoServer
	sandbox string
	config  constants.Config
}

func NewViewerServer(config constants.Config) ViewerServer {
	sandbox := config.YmirSandbox
	viewerUri := config.ViewerUri
	mongoUri := config.MongodbUri
	gin.SetMode(gin.ReleaseMode)
	viewerServer := ViewerServer{
		addr:    viewerUri,
		gin:     gin.Default(),
		Mongo:   NewMongoServer(mongoUri),
		sandbox: sandbox,
		config:  config,
	}
	viewerServer.routes()
	return viewerServer
}

func (s *ViewerServer) Start() {
	srv := &http.Server{
		Addr:         s.addr,
		Handler:      s.gin,
		ReadTimeout:  s.config.InnerTimeout * time.Second,
		WriteTimeout: s.config.InnerTimeout * time.Second,
	}
	log.Fatal(srv.ListenAndServe())
}

func (s *ViewerServer) Clear() {

}

func (s *ViewerServer) routes() {
	r := s.gin

	docs.SwaggerInfo.BasePath = "/api/v1"
	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	apiPath := r.Group("/api/v1")
	{
		apiPath.GET("/users/:userId/repo/:repoId/branch/:branchId/assets", s.handleAssets)
		apiPath.GET("/users/:userId/repo/:repoId/branch/:branchId/dataset_meta_count", s.handleDatasetMetaCounts)
		apiPath.GET("/users/:userId/repo/:repoId/branch/:branchId/dataset_stats", s.handleDatasetStats)
		apiPath.GET("/users/:userId/repo/:repoId/dataset_duplication", s.handleDatasetDup)
	}
}

func (s *ViewerServer) buildMirRepoFromParam(c *gin.Context) constants.MirRepo {
	userId := c.Param("userId")
	repoId := c.Param("repoId")
	branchId := c.Param("branchId")
	return constants.MirRepo{
		SandboxRoot: s.sandbox,
		UserId:      userId,
		RepoId:      repoId,
		BranchId:    branchId,
		TaskId:      branchId,
	}
}

func (s *ViewerServer) getIntFromQuery(c *gin.Context, field string) int {
	data, err := strconv.Atoi(c.DefaultQuery(field, "0"))
	if err != nil {
		panic(err)
	}
	return data
}

func (s *ViewerServer) getIntSliceFromQuery(c *gin.Context, field string) []int {
	classIds := make([]int, 0)
	classIdsStr := c.DefaultQuery(field, "")
	if len(classIdsStr) < 1 {
		return classIds
	}

	classIdsStrs := strings.Split(classIdsStr, ",")
	for _, v := range classIdsStrs {
		if len(v) < 1 {
			continue
		}

		classId, err := strconv.Atoi(v)
		if err != nil {
			panic(err)
		}
		classIds = append(classIds, classId)
	}
	return classIds
}

// @Summary Query single or set of assets.
// @Accept  json
// @Produce  json
// @Param   userId     path    string     true        "User ID"
// @Param   repoId     path    string     true        "Repo ID"
// @Param   branchId     path    string     true        "Branch ID"
// @Param   offset     query    string     false        "Offset, default is 0"
// @Param   limit     query    string     false        "limit, default is 20"
// @Param   class_ids     query    string     false        "e.g. class_ids=1,3,7"
// @Param   current_asset_id     query    string     false        "e.g. current_asset_id=xxxyyyzzz"
// @Param   cm_types     query    string     false        "e.g. cm_types=FN,TP,MTP,IGNORED"
// @Param   cks     query    string     false        "ck pairs, e.g. cks=xxx,xxx:,xxx:yyy"
// @Param   tags     query    string     false        "tag pairs, e.g. cks=xxx,xxx:,xxx:yyy"
// @Success 200 {string} string    "'code': 0, 'msg': 'Success', 'Success': true, 'Data': constants.QueryAssetsResult"
// @Router /api/v1/users/{userId}/repo/{repoId}/branch/{branchId}/assets [get]
func (s *ViewerServer) handleAssets(c *gin.Context) {
	mirRepo := s.buildMirRepoFromParam(c)
	offset := s.getIntFromQuery(c, "offset")
	limit := s.getIntFromQuery(c, "limit")
	classIds := s.getIntSliceFromQuery(c, "class_ids")
	currentAssetId := c.DefaultQuery("current_asset_id", "")

	// Convert cm query.
	cmTypesStr := c.DefaultQuery("cm_types", "")
	cmTypes := make([]int32, 0)
	if len(cmTypesStr) > 0 {
		cmTypesStrs := strings.Split(cmTypesStr, ",")
		for _, v := range cmTypesStrs {
			if cmValue, ok := protos.ConfusionMatrixType_value[v]; ok {
				cmTypes = append(cmTypes, cmValue)
			}
		}
	}

	cksStr := c.DefaultQuery("cks", "")
	cks := make([]string, 0)
	if len(cksStr) > 0 {
		for _, v := range strings.Split(cksStr, ",") {
			if len(v) > 0 {
				cks = append(cks, v)
			}
		}
	}

	tagsStr := c.DefaultQuery("tags", "")
	tags := make([]string, 0)
	if len(tagsStr) > 0 {
		for _, v := range strings.Split(tagsStr, ",") {
			if len(v) > 0 {
				tags = append(tags, v)
			}
		}
	}

	resultData := GetAssetsHandler(
		s.Mongo,
		&loader.MirRepoLoader{MirRepo: mirRepo},
		offset,
		limit,
		classIds,
		currentAssetId,
		cmTypes,
		cks,
		tags,
	)
	ViewerSuccess(c, resultData)
}

// @Summary Query dataset info, lightweight api.
// @Accept  json
// @Produce  json
// @Param   userId     path    string     true        "User ID"
// @Param   repoId     path    string     true        "Repo ID"
// @Param   branchId     path    string     true        "Branch ID"
// @Success 200 {string} string    "'code': 0, 'msg': 'Success', 'Success': true, 'Data': constants.QueryDatasetStatsResult"
// @Router /api/v1/users/{userId}/repo/{repoId}/branch/{branchId}/dataset_meta_count [get]
func (s *ViewerServer) handleDatasetMetaCounts(c *gin.Context) {
	mirRepo := s.buildMirRepoFromParam(c)
	resultData := GetDatasetMetaCountsHandler(&loader.MirRepoLoader{MirRepo: mirRepo})
	ViewerSuccess(c, resultData)
}

// @Summary Query dataset Stats.
// @Accept  json
// @Produce  json
// @Param   userId     path    string     true        "User ID"
// @Param   repoId     path    string     true        "Repo ID"
// @Param   branchId     path    string     true        "Branch ID"
// @Param   class_ids     query    string     false        "e.g. class_ids=1,3,7"
// @Success 200 {string} string    "'code': 0, 'msg': 'Success', 'Success': true, 'Data': constants.QueryDatasetStatsResult"
// @Router /api/v1/users/{userId}/repo/{repoId}/branch/{branchId}/dataset_stats [get]
func (s *ViewerServer) handleDatasetStats(c *gin.Context) {
	mirRepo := s.buildMirRepoFromParam(c)
	classIds := s.getIntSliceFromQuery(c, "class_ids")

	resultData := GetDatasetStatsHandler(s.Mongo, &loader.MirRepoLoader{MirRepo: mirRepo}, classIds)
	ViewerSuccess(c, resultData)
}

// @Summary Query dataset dups.
// @Accept  json
// @Produce  json
// @Param   userId     path    string     true        "User ID"
// @Param   repoId     path    string     true        "Repo ID"
// @Param   candidate_dataset_ids     query    string     true        "e.g. candidate_dataset_ids=xxx,yyy"
// @Success 200 {string} string    "'code': 0, 'msg': 'Success', 'Success': true, 'Data': 'duplication: 50, total_count: {xxx: 100, yyy: 200}'"
// @Router /api/v1/users/{userId}/repo/{repoId}/dataset_duplication [get]
func (s *ViewerServer) handleDatasetDup(c *gin.Context) {
	// Validate candidate_dataset_ids
	candidateDatasetIds := c.DefaultQuery("candidate_dataset_ids", "")
	if len(candidateDatasetIds) <= 0 {
		ViewerFailure(c, constants.FailInvalidParmsCode, constants.FailInvalidParmsMsg, "Invalid candidate_dataset_ids")
	}
	datasetIds := strings.Split(candidateDatasetIds, ",")
	if len(datasetIds) != 2 {
		ViewerFailure(
			c,
			constants.FailInvalidParmsCode,
			constants.FailInvalidParmsMsg,
			"candidate_dataset_ids requires exact two datasets.",
		)
	}

	userId := c.Param("userId")
	repoId := c.Param("repoId")
	mirRepo0 := constants.MirRepo{
		SandboxRoot: s.sandbox,
		UserId:      userId,
		RepoId:      repoId,
		BranchId:    datasetIds[0],
		TaskId:      datasetIds[0],
	}
	mirRepo1 := constants.MirRepo{
		SandboxRoot: s.sandbox,
		UserId:      userId,
		RepoId:      repoId,
		BranchId:    datasetIds[1],
		TaskId:      datasetIds[1],
	}

	duplicateCount, mirRepoCount0, mirRepoCount1 := GetDatasetDupHandler(
		s.Mongo,
		&loader.MirRepoLoader{MirRepo: mirRepo0},
		&loader.MirRepoLoader{MirRepo: mirRepo1},
	)
	resultData := bson.M{
		"duplication": duplicateCount,
		"total_count": bson.M{datasetIds[0]: mirRepoCount0, datasetIds[1]: mirRepoCount1},
	}
	ViewerSuccess(c, resultData)
}
