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

	classIdsStrs := strings.Split(c.DefaultQuery("classIds", ""), ",")
	classIds := make([]int, len(classIdsStrs))
	for i, v := range classIdsStrs {
		classIds[i], _ = strconv.Atoi(v)
	}
	offset, err := strconv.Atoi(c.DefaultQuery("offset", "0"))
	if err != nil {
		panic(err)
	}
	limit, err := strconv.Atoi(c.DefaultQuery("limit", "0"))
	if err != nil {
		panic(err)
	}
	mirSssetDetails := GetAssetsHandler(s.Mongo, mirRepo, offset, limit, classIds)

	ViewerSuccess(c, constant.ViewerSuccessCode, constant.ViewerSuccessMsg, mirSssetDetails)
}
