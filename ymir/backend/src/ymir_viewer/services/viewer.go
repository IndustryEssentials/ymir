package services

import (
	"errors"
	"fmt"
	"log"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/IndustryEssentials/ymir-viewer/common/constants"
	docs "github.com/IndustryEssentials/ymir-viewer/docs"
	"github.com/gin-gonic/gin"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"
)

// Delcare base handler interface, which is used in viewer.
type BaseHandler interface {
	GetAssetsHandler(
		mirRepo *constants.MirRepo,
		offset int,
		limit int,
		classIDs []int,
		currentAssetID string,
		cmTypes []int,
		cks []string,
		tags []string,
	) constants.QueryAssetsResult
	GetDatasetDupHandler(
		mirRepo0 *constants.MirRepo,
		mirRepo1 *constants.MirRepo,
	) constants.QueryDatasetDupResult
	GetDatasetMetaCountsHandler(
		mirRepo *constants.MirRepo,
	) constants.QueryDatasetStatsResult
	GetDatasetStatsHandler(
		mirRepo *constants.MirRepo,
		classIDs []int,
	) constants.QueryDatasetStatsResult
}

type ViewerServer struct {
	addr    string
	gin     *gin.Engine
	sandbox string
	config  constants.Config
	handler BaseHandler
}

func NewViewerServer(config constants.Config) ViewerServer {
	gin.SetMode(gin.ReleaseMode)
	viewerServer := ViewerServer{
		addr:    config.ViewerURI,
		gin:     gin.Default(),
		sandbox: config.YmirSandbox,
		config:  config,
		handler: NewViewerHandler(config.MongoDBURI, config.MongoDBName, config.MongoDBNoCache),
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
	fmt.Println("server cleared.")
}

func (s *ViewerServer) routes() {
	r := s.gin

	docs.SwaggerInfo.BasePath = "/api/v1"
	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	apiPath := r.Group("/api/v1")
	{
		apiPath.GET("/users/:userID/repo/:repoID/branch/:branchID/assets", s.handleAssets)
		apiPath.GET("/users/:userID/repo/:repoID/branch/:branchID/dataset_meta_count", s.handleDatasetMetaCounts)
		apiPath.GET("/users/:userID/repo/:repoID/branch/:branchID/dataset_stats", s.handleDatasetStats)
		apiPath.GET("/users/:userID/repo/:repoID/dataset_duplication", s.handleDatasetDup)
	}
}

func (s *ViewerServer) buildMirRepoFromParam(c *gin.Context) *constants.MirRepo {
	userID := c.Param("userID")
	repoID := c.Param("repoID")
	branchID := c.Param("branchID")
	return &constants.MirRepo{
		SandboxRoot: s.sandbox,
		UserID:      userID,
		RepoID:      repoID,
		BranchID:    branchID,
		TaskID:      branchID,
	}
}

func (s *ViewerServer) getInt(input string) int {
	data, err := strconv.Atoi(input)
	if err != nil {
		data = 0
	}
	return data
}

func (s *ViewerServer) getIntSliceFromString(input string) []int {
	classIDs := make([]int, 0)
	classIDsStr := input
	if len(classIDsStr) < 1 {
		return classIDs
	}

	classIDsStrs := strings.Split(classIDsStr, ",")
	for _, v := range classIDsStrs {
		if len(v) < 1 {
			continue
		}

		classID, err := strconv.Atoi(v)
		if err != nil {
			continue
		}
		classIDs = append(classIDs, classID)
	}
	return classIDs
}

// @Summary Query single or set of assets.
// @Accept  json
// @Produce  json
// @Param   userID     path    string     true        "User ID"
// @Param   repoID     path    string     true        "Repo ID"
// @Param   branchID     path    string     true        "Branch ID"
// @Param   offset     query    string     false        "Offset, default is 0"
// @Param   limit     query    string     false        "limit, default is 1"
// @Param   class_ids     query    string     false        "e.g. class_ids=1,3,7"
// @Param   current_asset_id     query    string     false        "e.g. current_asset_id=xxxyyyzzz"
// @Param   cm_types     query    string     false        "e.g. cm_types=0,1,2,3 NotSet=0,TP=1,FP=2,FN=3,TN=4,Unknown=5,MTP=11,IGNORED=12"
// @Param   cks     query    string     false        "ck pairs, e.g. cks=xxx,xxx:,xxx:yyy, e.g. camera_id:1"
// @Param   tags     query    string     false        "tag pairs, e.g. cks=xxx,xxx:,xxx:yyy, e.g. camera_id:1"
// @Success 200 {string} string    "'code': 0, 'msg': 'Success', 'Success': true, 'result': constants.QueryAssetsResult"
// @Router /api/v1/users/{userID}/repo/{repoID}/branch/{branchID}/assets [get]
func (s *ViewerServer) handleAssets(c *gin.Context) {
	defer s.handleFailure(c)

	mirRepo := s.buildMirRepoFromParam(c)
	offset := s.getInt(c.DefaultQuery("offset", "0"))
	if offset < 0 {
		offset = 0
	}
	limit := s.getInt(c.DefaultQuery("limit", "0"))
	if limit < 1 {
		limit = 1
	}
	classIDs := s.getIntSliceFromString(c.DefaultQuery("class_ids", ""))
	currentAssetID := c.DefaultQuery("current_asset_id", "")
	cmTypes := s.getIntSliceFromString(c.DefaultQuery("cm_types", ""))

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

	resultData := s.handler.GetAssetsHandler(
		mirRepo,
		offset,
		limit,
		classIDs,
		currentAssetID,
		cmTypes,
		cks,
		tags,
	)
	ViewerSuccess(c, resultData)
}

// @Summary Query dataset info, lightweight api.
// @Accept  json
// @Produce  json
// @Param   userID     path    string     true        "User ID"
// @Param   repoID     path    string     true        "Repo ID"
// @Param   branchID     path    string     true        "Branch ID"
// @Success 200 {string} string    "'code': 0, 'msg': 'Success', 'Success': true, 'result': constants.QueryDatasetStatsResult"
// @Router /api/v1/users/{userID}/repo/{repoID}/branch/{branchID}/dataset_meta_count [get]
func (s *ViewerServer) handleDatasetMetaCounts(c *gin.Context) {
	defer s.handleFailure(c)

	mirRepo := s.buildMirRepoFromParam(c)

	resultData := s.handler.GetDatasetMetaCountsHandler(mirRepo)
	ViewerSuccess(c, resultData)
}

// @Summary Query dataset Stats.
// @Accept  json
// @Produce  json
// @Param   userID     path    string     true        "User ID"
// @Param   repoID     path    string     true        "Repo ID"
// @Param   branchID     path    string     true        "Branch ID"
// @Param   class_ids     query    string     false        "e.g. class_ids=1,3,7"
// @Success 200 {string} string    "'code': 0, 'msg': 'Success', 'Success': true, 'result': constants.QueryDatasetStatsResult"
// @Router /api/v1/users/{userID}/repo/{repoID}/branch/{branchID}/dataset_stats [get]
func (s *ViewerServer) handleDatasetStats(c *gin.Context) {
	defer s.handleFailure(c)

	mirRepo := s.buildMirRepoFromParam(c)
	classIDs := s.getIntSliceFromString(c.DefaultQuery("class_ids", ""))

	resultData := s.handler.GetDatasetStatsHandler(mirRepo, classIDs)
	ViewerSuccess(c, resultData)
}

// @Summary Query dataset dups.
// @Accept  json
// @Produce  json
// @Param   userID     path    string     true        "User ID"
// @Param   repoID     path    string     true        "Repo ID"
// @Param   candidate_dataset_ids     query    string     true        "e.g. candidate_dataset_ids=xxx,yyy"
// @Success 200 {string} string    "'code': 0, 'msg': 'Success', 'Success': true, 'result': 'duplication: 50, total_count: {xxx: 100, yyy: 200}'"
// @Router /api/v1/users/{userID}/repo/{repoID}/dataset_duplication [get]
func (s *ViewerServer) handleDatasetDup(c *gin.Context) {
	defer s.handleFailure(c)

	// Validate candidate_dataset_ids
	candidateDatasetIDs := c.DefaultQuery("candidate_dataset_ids", "")
	if len(candidateDatasetIDs) <= 0 {
		ViewerFailure(c, &FailureResult{Code: constants.FailInvalidParmsCode,
			Msg: "Invalid candidate_dataset_ids."})
		return
	}
	datasetIDs := strings.Split(candidateDatasetIDs, ",")
	if len(datasetIDs) != 2 {
		ViewerFailure(c, &FailureResult{Code: constants.FailInvalidParmsCode,
			Msg: "candidate_dataset_ids requires exact two datasets."})
		return
	}

	userID := c.Param("userID")
	repoID := c.Param("repoID")
	mirRepo0 := &constants.MirRepo{
		SandboxRoot: s.sandbox,
		UserID:      userID,
		RepoID:      repoID,
		BranchID:    datasetIDs[0],
		TaskID:      datasetIDs[0],
	}
	mirRepo1 := &constants.MirRepo{
		SandboxRoot: s.sandbox,
		UserID:      userID,
		RepoID:      repoID,
		BranchID:    datasetIDs[1],
		TaskID:      datasetIDs[1],
	}

	resultData := s.handler.GetDatasetDupHandler(mirRepo0, mirRepo1)
	ViewerSuccess(c, resultData)
}

func (s *ViewerServer) handleFailure(c *gin.Context) {
	if r := recover(); r != nil {
		if s, ok := r.(string); ok {
			r = errors.New(s)
		}
		if r, ok := r.(error); ok {
			ViewerFailureFromErr(c, r)
			return
		}

		panic(fmt.Sprintf("unhandled error type: %T\n", r))
	}
}
