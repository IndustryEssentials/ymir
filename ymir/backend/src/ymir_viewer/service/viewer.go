package service

import (
	"log"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/IndustryEssentials/ymir-viewer/common/constant"
	"github.com/gin-gonic/gin"
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
		}
	}
}

func (s *ViewerServer) handleAssets(c *gin.Context) {
	userId := c.Param("userId")
	repoId := c.Param("repoId")
	branchId := c.Param("branchId")
	mirRepo := constant.MirRepo{SandboxRoot: s.sandbox, UserId: userId, RepoId: repoId, BranchId: branchId, TaskId: branchId}

	classIdsStrs := strings.Split(c.DefaultQuery("class_ids", ""), ",")
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

	offset, err := strconv.Atoi(c.DefaultQuery("offset", "0"))
	if err != nil {
		panic(err)
	}

	limit, err := strconv.Atoi(c.DefaultQuery("limit", "1"))
	if err != nil {
		panic(err)
	}

	currentAssetId := c.DefaultQuery("current_asset_id", "")
	mirSssetDetails := GetAssetsHandler(s.Mongo, mirRepo, offset, limit, classIds, currentAssetId)

	ViewerSuccess(c, constant.ViewerSuccessCode, constant.ViewerSuccessMsg, mirSssetDetails)
}
