package service

import (
	"log"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/IndustryEssentials/ymir-viewer/common/constant"
	"github.com/gin-gonic/gin"
	"go.mongodb.org/mongo-driver/bson"
)


type ViewerServer struct {
	addr  string
	gin   *gin.Engine
	Mongo MongoServer
	sandbox string
	config constant.Config
}

func NewViewerServer(config constant.Config) ViewerServer{
	sandbox := config.YmirSandbox
	viewerUri := config.ViewerUri
	mongoUri := config.MongodbUri
	gin.SetMode(gin.ReleaseMode)
	viewerServer := ViewerServer{
		addr:  viewerUri,
		gin:   gin.Default(),
		Mongo: NewMongoServer(mongoUri),
		sandbox: sandbox,
		config: config,
	}
	viewerServer.routes()
	return viewerServer
}

func (s *ViewerServer) Start() {
	srv := &http.Server{
		Addr:         s.addr,
		Handler:      s.gin,
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 5 * time.Second,
	}
	log.Fatal(srv.ListenAndServe())
}

func (s *ViewerServer) Clear() {

}

func (s *ViewerServer) routes() {
	apiPath := s.gin.Group("/api")
	{
		v1Path := apiPath.Group("/v1")
		{
			v1Path.GET("/users/:userId/repo/:repoId/branch/:branchId/assets", s.handleAssets)
			v1Path.GET("/users/:userId/repo/:repoId/branch/:branchId/dataset_stats", s.handleDatasetStats)
			v1Path.GET("/users/:userId/repo/:repoId/dataset_duplication", s.handleDatasetDup)
		}
	}
}

func (s *ViewerServer) buildMirRepoFromParam(c *gin.Context) constant.MirRepo {
	userId := c.Param("userId")
	repoId := c.Param("repoId")
	branchId := c.Param("branchId")
	return constant.MirRepo{SandboxRoot: s.sandbox, UserId: userId, RepoId: repoId, BranchId: branchId, TaskId: branchId}
}

func (s *ViewerServer) getIntFromQuery(c *gin.Context, field string) int {
	data, err := strconv.Atoi(c.DefaultQuery(field, "0"))
	if err != nil {
		panic(err)
	}
	return data
}

func (s *ViewerServer) getIntSliceFromQuery(c *gin.Context, field string) []int {
	classIdsStrs := strings.Split(c.DefaultQuery(field, ""), ",")
	classIds := make([]int, 0)
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

func (s *ViewerServer) handleAssets(c *gin.Context) {
	mirRepo := s.buildMirRepoFromParam(c)
	classIds := s.getIntSliceFromQuery(c, "class_ids")
	offset := s.getIntFromQuery(c, "offset")
	limit := s.getIntFromQuery(c, "limit")
	currentAssetId := c.DefaultQuery("current_asset_id", "")

	resultData := GetAssetsHandler(s.Mongo, mirRepo, offset, limit, classIds, currentAssetId)
	ViewerSuccess(c, constant.ViewerSuccessCode, constant.ViewerSuccessMsg, resultData)
}

func (s *ViewerServer) handleDatasetStats(c *gin.Context) {
	mirRepo := s.buildMirRepoFromParam(c)
	classIds := s.getIntSliceFromQuery(c, "class_ids")

	resultData := GetDatasetStatsHandler(s.Mongo, mirRepo, classIds)
	ViewerSuccess(c, constant.ViewerSuccessCode, constant.ViewerSuccessMsg, resultData)
}

func (s *ViewerServer) handleDatasetDup(c *gin.Context) {
	// Validate candidate_dataset_ids
	candidateDatasetIds := c.DefaultQuery("candidate_dataset_ids", "")
	if len(candidateDatasetIds) <= 0 {
		ViewerFailure(c, constant.FailInvalidParmsCode, constant.FailInvalidParmsMsg, "Invalid candidate_dataset_ids")
	}
	datasetIds := strings.Split(candidateDatasetIds, ",")
	if len(datasetIds) != 2 {
		ViewerFailure(c, constant.FailInvalidParmsCode, constant.FailInvalidParmsMsg, "candidate_dataset_ids requires exact two datasets.")
	}

	userId := c.Param("userId")
	repoId := c.Param("repoId")
	mirRepo0 := constant.MirRepo{SandboxRoot: s.sandbox, UserId: userId, RepoId: repoId, BranchId: datasetIds[0], TaskId: datasetIds[0]}
	mirRepo1 := constant.MirRepo{SandboxRoot: s.sandbox, UserId: userId, RepoId: repoId, BranchId: datasetIds[1], TaskId: datasetIds[1]}

	duplicateCount, mirRepoCount0, mirRepoCount1 := GetDatasetDupHandler(s.Mongo, mirRepo0, mirRepo1)
	resultData := bson.M{"result": duplicateCount, "total_count": bson.M{datasetIds[0]: mirRepoCount0, datasetIds[1]: mirRepoCount1}}
	ViewerSuccess(c, constant.ViewerSuccessCode, constant.ViewerSuccessMsg, resultData)
}
