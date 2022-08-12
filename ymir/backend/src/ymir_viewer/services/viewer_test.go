package services

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/IndustryEssentials/ymir-viewer/common/constants"
	"github.com/IndustryEssentials/ymir-viewer/common/loader"
	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

type MockViewerHandler struct {
}

func (viewerHandler *MockViewerHandler) GetAssetsHandler(
	mongo *MongoServer,
	mirLoader loader.BaseMirRepoLoader,
	offset int,
	limit int,
	classIds []int,
	currentAssetID string,
	cmTypes []int32,
	cks []string,
	tags []string,
) constants.QueryAssetsResult {
	return constants.QueryAssetsResult{}
}

func (viewerHandler *MockViewerHandler) GetDatasetMetaCountsHandler(
	mirLoader loader.BaseMirRepoLoader,
) constants.QueryDatasetStatsResult {
	return constants.NewQueryDatasetStatsResult()
}

func (viewerHandler *MockViewerHandler) GetDatasetStatsHandler(
	mongo *MongoServer,
	mirLoader loader.BaseMirRepoLoader,
	classIds []int,
) constants.QueryDatasetStatsResult {
	result := constants.NewQueryDatasetStatsResult()
	for classID := range classIds {
		result.Gt.ClassIdsCount[classID] = 0
		result.Pred.ClassIdsCount[classID] = 0
	}
	return result
}

func (viewerHandler *MockViewerHandler) GetDatasetDupHandler(
	mongo *MongoServer,
	mirLoader0 loader.BaseMirRepoLoader,
	mirLoader1 loader.BaseMirRepoLoader,
) (int, int64, int64) {
	return 0, 0, 0
}

func setUpViewer() *ViewerServer {
	return &ViewerServer{gin: gin.Default(), handler: &MockViewerHandler{}}
}

func buildResponseBody(
	code constants.ResponseCode,
	msg constants.ResponseMsg,
	success bool,
	result interface{},
) []byte {
	resp := &ResultVO{Code: code, Msg: msg, Success: success, Result: result}
	bytes, err := json.Marshal(resp)
	if err != nil {
		panic(err)
	}
	return bytes
}

func TestSimplePageHandlerSuccess(t *testing.T) {
	viewer := setUpViewer()
	r := viewer.gin
	r.GET("/users/:userId/repo/:repoId/branch/:branchId/dataset_stats", viewer.handleDatasetStats)
	r.GET("/users/:userId/repo/:repoId/branch/:branchId/dataset_meta_count", viewer.handleDatasetMetaCounts)

	userID := "userID"
	repoID := "repoID"
	branchID := "branchID"
	classIDs := []int{0, 1}
	classIDsStr := "0,1"
	statsRequestURL := fmt.Sprintf(
		"/users/%s/repo/%s/branch/%s/dataset_stats?class_ids=%s",
		userID,
		repoID,
		branchID,
		classIDsStr,
	)
	metaRequestURL := fmt.Sprintf(
		"/users/%s/repo/%s/branch/%s/dataset_meta_count",
		userID,
		repoID,
		branchID,
	)

	statsExpectedResult := constants.NewQueryDatasetStatsResult()
	for classID := range classIDs {
		statsExpectedResult.Gt.ClassIdsCount[classID] = 0
		statsExpectedResult.Pred.ClassIdsCount[classID] = 0
	}
	statsExpectedResponseData := buildResponseBody(
		constants.ViewerSuccessCode,
		"Success",
		true,
		statsExpectedResult,
	)
	metaExpectedResult := constants.NewQueryDatasetStatsResult()
	metaExpectedResponseData := buildResponseBody(
		constants.ViewerSuccessCode,
		"Success",
		true,
		metaExpectedResult,
	)

	req, _ := http.NewRequest("GET", statsRequestURL, nil)
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	assert.Equal(t, string(statsExpectedResponseData), w.Body.String())
	assert.Equal(t, http.StatusOK, w.Code)

	req, _ = http.NewRequest("GET", metaRequestURL, nil)
	w = httptest.NewRecorder()
	r.ServeHTTP(w, req)
	assert.Equal(t, string(metaExpectedResponseData), w.Body.String())
	assert.Equal(t, http.StatusOK, w.Code)
}
