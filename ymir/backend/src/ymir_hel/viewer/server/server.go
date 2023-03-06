package server

import (
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"net/http"
	"runtime/debug"
	"strconv"
	"strings"
	"time"

	"github.com/IndustryEssentials/ymir-hel/common/constants"
	"github.com/IndustryEssentials/ymir-hel/configs"
	docs "github.com/IndustryEssentials/ymir-hel/viewer/docs"
	"github.com/IndustryEssentials/ymir-hel/viewer/handler"
	"github.com/gin-gonic/gin"
	"github.com/penglongli/gin-metrics/ginmetrics"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"
)

// BaseHandler delcare base handler interface, which is used in viewer.
type BaseHandler interface {
	GetAssetsHandler(
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
	GetDatasetDupHandler(
		candidateMirRepos []*constants.MirRepo,
		corrodeeMirRepos []*constants.MirRepo,
	) *constants.QueryDatasetDupResult
	GetDatasetMetaCountsHandler(
		mirRepo *constants.MirRepo,
		checkIndexOnly bool,
	) *constants.QueryDatasetStatsResult
	GetDatasetStatsHandler(
		mirRepo *constants.MirRepo,
		classIDs []int,
		requireAssetsHist bool,
		requireAnnotationsHist bool,
	) *constants.QueryDatasetStatsResult
	GetModelInfoHandler(
		mirRepo *constants.MirRepo,
	) *constants.MirdataModel
	MetricsQueryHandler(
		metricsGroup string,
		userID string,
		classIDs []int,
		queryField string,
		bucket string,
		unit string,
		limit int,
	) *[]constants.MetricsQueryPoint
	MetricsRecordHandler(
		metricsGroup string,
		postForm map[string]interface{},
	)
}

func StartViewerServer(config *configs.Config) error {
	s, _ := json.MarshalIndent(config, "", "\t")
	log.Printf("ymir-hel server config:\n%s\n\n", string(s))

	viewerServer, err := NewViewerServer(config)
	if err != nil {
		return err
	}
	defer viewerServer.Clear()
	viewerServer.Start()
	return nil
}

type ViewerServer struct {
	addr    string
	gin     *gin.Engine
	sandbox string
	config  *configs.Config
	handler BaseHandler
}

func NewViewerServer(config *configs.Config) (ViewerServer, error) {
	gin.SetMode(gin.ReleaseMode)
	viewerServer := ViewerServer{
		addr:    config.ViewerURI,
		gin:     gin.New(),
		sandbox: config.YmirSandbox,
		config:  config,
		handler: handler.NewViewerHandler(
			config.MongoDBURI,
			config.MongoDataDBName,
			config.MongoDataDBCache,
			config.MongoMetricsDBName,
			config.ViewerTimeout,
		),
	}

	viewerServer.gin.Use(
		gin.LoggerWithWriter(gin.DefaultWriter, "/health", "/metrics"),
		gin.Recovery(),
	)

	// get global Monitor object
	m := ginmetrics.GetMonitor()

	// +optional set metric path, default /debug/metrics
	m.SetMetricPath("/metrics")
	// +optional set slow time, default 5s
	m.SetSlowTime(10)
	// +optional set request duration, default {0.1, 0.3, 1.2, 5, 10}
	// used to p95, p99
	m.SetDuration([]float64{0.1, 0.3, 1.2, 5, 10})

	// set middleware for gin
	m.Use(viewerServer.gin)

	viewerServer.routes()
	return viewerServer, nil
}

func (s *ViewerServer) Start() {
	srv := &http.Server{
		Addr:         s.addr,
		Handler:      s.gin,
		ReadTimeout:  time.Duration(s.config.ViewerTimeout) * time.Second,
		WriteTimeout: time.Duration(s.config.ViewerTimeout) * time.Second,
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

	r.GET("/health", s.handleHealth)

	apiPath := r.Group("/api/v1")
	{
		apiPath.GET("/users/:userID/repo/:repoID/dataset_duplication", s.handleDatasetDup)
		apiPath.GET("/users/:userID/repo/:repoID/branch/:branchID/assets", s.handleAssets)
		apiPath.GET("/users/:userID/repo/:repoID/branch/:branchID/dataset_meta_count", s.handleDatasetMetaCounts)
		apiPath.GET("/users/:userID/repo/:repoID/branch/:branchID/dataset_stats", s.handleDatasetStats)
		apiPath.GET("/users/:userID/repo/:repoID/branch/:branchID/model_info", s.handleModelInfo)
		apiPath.GET("/user_metrics/:metrics_group", s.handleMetricsQuery)
		apiPath.POST("/user_metrics/:metrics_group", s.handleMetricsRecord)
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
// @Param   annotation_types     query    string     false        "e.g. annotation_types=GT,PRED"
// @Param   current_asset_id     query    string     false        "e.g. current_asset_id=xxxyyyzzz"
// @Param   in_cm_types     query    string     false        "e.g. in_cm_types=0,1,2,3 NotSet=0,TP=1,FP=2,FN=3,TN=4,Unknown=5,MTP=11,IGNORED=12"
// @Param   ex_cm_types     query    string     false        "e.g. ex_cm_types=0,1,2,3 NotSet=0,TP=1,FP=2,FN=3,TN=4,Unknown=5,MTP=11,IGNORED=12"
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
	inCMTypes := s.getIntSliceFromString(c.DefaultQuery("in_cm_types", ""))
	exCMTypes := s.getIntSliceFromString(c.DefaultQuery("ex_cm_types", ""))
	if len(inCMTypes) > 0 && len(exCMTypes) > 0 {
		ViewerFailure(c, &FailureResult{Code: constants.CodeViewerInvalidParms,
			Msg: "should not set both in_cm_types/ex_cm_types."})
		return
	}

	annoTypesStr := c.DefaultQuery("annotation_types", "")
	annoTypes := make([]string, 0)
	if len(annoTypesStr) > 0 {
		for _, v := range strings.Split(annoTypesStr, ",") {
			if len(v) > 0 {
				annoType := strings.ToLower(v)
				if annoType == "gt" || annoType == "pred" {
					annoTypes = append(annoTypes, annoType)
				}
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

	resultData := s.handler.GetAssetsHandler(
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
	ViewerSuccess(c, resultData)
}

// @Summary Query dataset info, lightweight api.
// @Accept  json
// @Produce  json
// @Param   userID     path    string     true        "User ID"
// @Param   repoID     path    string     true        "Repo ID"
// @Param   branchID     path    string     true        "Branch ID"
// @Param   check_index_only     query    string     false        "e.g. check_index_only=True"
// @Success 200 {string} string    "'code': 0, 'msg': 'Success', 'Success': true, 'result': constants.QueryDatasetStatsResult"
// @Router /api/v1/users/{userID}/repo/{repoID}/branch/{branchID}/dataset_meta_count [get]
func (s *ViewerServer) handleDatasetMetaCounts(c *gin.Context) {
	defer s.handleFailure(c)

	mirRepo := s.buildMirRepoFromParam(c)

	checkIndexOnlyStr := c.DefaultQuery("check_index_only", "False")
	if len(checkIndexOnlyStr) == 0 {
		checkIndexOnlyStr = "True"
	}
	checkIndexOnly, err := strconv.ParseBool(checkIndexOnlyStr)
	if err != nil {
		panic(err)
	}
	resultData := s.handler.GetDatasetMetaCountsHandler(mirRepo, checkIndexOnly)
	ViewerSuccess(c, resultData)
}

// @Summary Query dataset Stats.
// @Accept  json
// @Produce  json
// @Param   userID     path    string     true        "User ID"
// @Param   repoID     path    string     true        "Repo ID"
// @Param   branchID     path    string     true        "Branch ID"
// @Param   class_ids     query    string     false        "e.g. class_ids=1,3,7"
// @Param   require_assets_hist     query    string     false        "e.g. require_assets_hist=True"
// @Param   require_annos_hist     query    string     false        "e.g. require_annos_hist=True"
// @Success 200 {string} string    "'code': 0, 'msg': 'Success', 'Success': true, 'result': constants.QueryDatasetStatsResult"
// @Router /api/v1/users/{userID}/repo/{repoID}/branch/{branchID}/dataset_stats [get]
func (s *ViewerServer) handleDatasetStats(c *gin.Context) {
	defer s.handleFailure(c)

	mirRepo := s.buildMirRepoFromParam(c)
	classIDs := s.getIntSliceFromString(c.DefaultQuery("class_ids", ""))

	requireAssetsHistStr := c.DefaultQuery("require_assets_hist", "False")
	if len(requireAssetsHistStr) == 0 {
		requireAssetsHistStr = "True"
	}
	requireAssetsHist, err := strconv.ParseBool(requireAssetsHistStr)
	if err != nil {
		panic(err)
	}

	requireAnnotationsHistStr := c.DefaultQuery("require_annos_hist", "False")
	if len(requireAnnotationsHistStr) == 0 {
		requireAnnotationsHistStr = "True"
	}
	requireAnnotationsHist, err := strconv.ParseBool(requireAnnotationsHistStr)
	if err != nil {
		panic(err)
	}

	resultData := s.handler.GetDatasetStatsHandler(mirRepo, classIDs, requireAssetsHist, requireAnnotationsHist)
	ViewerSuccess(c, resultData)
}

// @Summary Query dataset dups.
// @Accept  json
// @Produce  json
// @Param   userID     path    string     true        "User ID"
// @Param   repoID     path    string     true        "Repo ID"
// @Param   candidate_dataset_ids     query    string     true        "e.g. candidate_dataset_ids=xxx,yyy"
// @Param   corrodee_dataset_ids     query    string     false        "dataset_ids to be corroded"
// @Success 200 {string} string    "'code': 0, 'msg': 'Success', 'Success': true, 'result': 'duplication: 50, total_count: {xxx: 100, yyy: 200}'"
// @Router /api/v1/users/{userID}/repo/{repoID}/dataset_duplication [get]
func (s *ViewerServer) handleDatasetDup(c *gin.Context) {
	defer s.handleFailure(c)

	candidateMirRepos := []*constants.MirRepo{}
	userID := c.Param("userID")
	repoID := c.Param("repoID")
	for _, v := range strings.Split(c.DefaultQuery("candidate_dataset_ids", ""), ",") {
		if len(v) < 1 {
			continue
		}
		candidateMirRepos = append(candidateMirRepos, &constants.MirRepo{
			SandboxRoot: s.sandbox,
			UserID:      userID,
			RepoID:      repoID,
			BranchID:    v,
			TaskID:      v,
		})
	}
	if len(candidateMirRepos) <= 0 {
		ViewerFailure(c, &FailureResult{Code: constants.CodeViewerInvalidParms,
			Msg: "Invalid candidate_dataset_ids."})
		return
	}

	corrodeeMirRepos := []*constants.MirRepo{}
	for _, v := range strings.Split(c.DefaultQuery("corrodee_dataset_ids", ""), ",") {
		if len(v) < 1 {
			continue
		}
		corrodeeMirRepos = append(corrodeeMirRepos, &constants.MirRepo{
			SandboxRoot: s.sandbox,
			UserID:      userID,
			RepoID:      repoID,
			BranchID:    v,
			TaskID:      v,
		})
	}

	resultData := s.handler.GetDatasetDupHandler(candidateMirRepos, corrodeeMirRepos)
	ViewerSuccess(c, resultData)
}

// @Summary Query model info.
// @Accept  json
// @Produce  json
// @Param   userID     path    string     true        "User ID"
// @Param   repoID     path    string     true        "Repo ID"
// @Param   branchID     path    string     true        "Branch ID"
// @Success 200 {string} string    "'code': 0, 'msg': 'Success', 'Success': true, 'result':  constants.MirdataModel"
// @Router /api/v1/users/{userID}/repo/{repoID}/branch/{branchID}/model_info [get]
func (s *ViewerServer) handleModelInfo(c *gin.Context) {
	defer s.handleFailure(c)

	mirRepo := s.buildMirRepoFromParam(c)

	resultData := s.handler.GetModelInfoHandler(mirRepo)
	ViewerSuccess(c, resultData)
}

func (s *ViewerServer) handleHealth(c *gin.Context) {
	ViewerSuccess(c, "Healthy")
}

// @Summary Record metrics signals.
// @Accept  json
// @Produce  json
// @Param   metricsGroup    path    string     true        "metrics_group"
// @Param   ID              post    string     true        "id"
// @Param   createTime      post    timestamp  true        "create_time"
// @Param   classIDs     	post    string     true        "e.g. class_ids=0,1,2"
// @Success 200 {string} string    "'code': 0, 'msg': 'Success', 'Success': true, 'result': ''"
// @Router /api/v1/user_metrics/:metrics_group [post]
func (s *ViewerServer) handleMetricsRecord(c *gin.Context) {
	metricsGroup := c.Param("metrics_group")
	if len(metricsGroup) <= 0 {
		ViewerFailure(c, &FailureResult{Code: constants.CodeViewerInvalidParms,
			Msg: "Missing metricsGroup."})
		return
	}

	if len(c.PostForm("id")) < 1 || len(c.PostForm("create_time")) < 1 ||
		len(c.PostForm("user_id")) < 1 || len(c.PostForm("project_id")) < 1 || len(c.PostForm("class_ids")) < 1 {
		ViewerFailure(c, &FailureResult{Code: constants.CodeViewerInvalidParms,
			Msg: "Missing required fields: id or create_time or user_id or project_id or class_ids."})
		return
	}

	dataMap := map[string]interface{}{}
	if err := c.Request.ParseForm(); err != nil {
		panic(err)
	}
	for key, value := range c.Request.PostForm {
		dataMap[key] = value[0]
	}

	// Normalize params.
	classIDsKey := "class_ids"
	createTimeKey := "create_time"
	dataMap[classIDsKey] = s.getIntSliceFromString(dataMap[classIDsKey].(string))
	// Parse time from timestamp.
	createTime, err := strconv.ParseInt(dataMap[createTimeKey].(string), 10, 64)
	if err != nil {
		panic(err)
	}
	dataMap[createTimeKey] = time.Unix(createTime, 0)

	log.Printf("recording metrics group: %s dataMap: %#v", metricsGroup, dataMap)
	s.handler.MetricsRecordHandler(metricsGroup, dataMap)
	ViewerSuccess(c, "")
}

// @Summary Query metrics signals.
// @Accept  json
// @Produce  json
// @Param   metricsGroup     path    string     true        "metrics_group"
// @Param   userID           query   string     true        "user_id for filter"
// @Param   classIDs         query   string     true        "class_ids for filter, e.g. 1,2,3,4,5"
// @Param   queryField       query   string     true        "query_field: field of data to query"
// @Param   bucket     		 query   string     true        "bucket type, e.g. bucket=count/time"
// @Param   unit     		 query   string     true        "valid with bucket=time e.g. unit=day week month"
// @Param   limit            query    string     false        "limit, default is 8"
// @Success 200 {string} string    "'code': 0, 'msg': 'Success', 'Success': true, 'result': ''"
// @Router /api/v1/user_metrics/:metrics_group [get]
func (s *ViewerServer) handleMetricsQuery(c *gin.Context) {
	metricsGroup := c.Param("metrics_group")
	if len(metricsGroup) <= 0 {
		ViewerFailure(c, &FailureResult{Code: constants.CodeViewerInvalidParms,
			Msg: "Missing metricsGroup."})
		return
	}

	// validate queries.
	userID := c.DefaultQuery("user_id", "")
	queryField := c.DefaultQuery("query_field", "")
	bucket := c.DefaultQuery("bucket", "")
	if len(userID) < 1 || len(queryField) < 1 || len(bucket) < 1 {
		ViewerFailure(c, &FailureResult{Code: constants.CodeViewerInvalidParms,
			Msg: "Missing required field: user_id, query_field, bucket"})
		return
	}
	limit := s.getInt(c.DefaultQuery("limit", "0"))
	if limit < 1 {
		limit = 8
	}
	unit := c.DefaultQuery("unit", "")

	// Optional filter field.
	classIDs := s.getIntSliceFromString(c.DefaultQuery("class_ids", ""))

	result := s.handler.MetricsQueryHandler(metricsGroup, userID, classIDs, queryField, bucket, unit, limit)
	log.Printf("MetricsQuery result: %+v", result)
	ViewerSuccess(c, result)
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

		panic(fmt.Sprintf("unhandled error type: %T\n%s\n", r, debug.Stack()))
	}
}
