package service

import (
	"log"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/IndustryEssentials/ymir-viewer/common/constant"
	"github.com/IndustryEssentials/ymir-viewer/common/protos"
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


// optional query example:
// offset=100
// limit=10
// class_ids=1,3,7
// current_asset_id=xxxyyyzzz
// cm_types=FN,TP,MTP,IGNORED
// cks=xxx,xxx:,xxx:yyy (key:value, key is required, :yyy is not valid)
// tags=xxx,xxx:,xxx:yyy (key:value, key is required, :yyy is not valid)
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

	resultData := GetAssetsHandler(s.Mongo, mirRepo, offset, limit, classIds, currentAssetId, cmTypes, cks, tags)
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
