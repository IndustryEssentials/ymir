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
	"go.mongodb.org/mongo-driver/bson"
)

func TestCreateViewer(t *testing.T) {
	server := NewViewerServer(constants.Config{ViewerURI: "127.0.0.1:9527"})

	server.getInt("invalid")
	server.getIntSliceFromString("")
	server.getIntSliceFromString(",")
	server.getIntSliceFromString("getIntSliceFromQuery")

	go server.Start()
	server.Clear()
}

type MockViewerHandler struct {
}

func (viewerHandler *MockViewerHandler) GetAssetsHandler(
	mongo *MongoServer,
	mirLoader loader.BaseMirRepoLoader,
	offset int,
	limit int,
	classIDs []int,
	currentAssetID string,
	cmTypes []int32,
	cks []string,
	tags []string,
) constants.QueryAssetsResult {
	return constants.QueryAssetsResult{
		AssetsDetail:     []constants.MirAssetDetail{},
		Offset:           offset,
		Limit:            limit,
		Anchor:           int64(len(classIDs)),
		TotalAssetsCount: 42,
	}
}

func (viewerHandler *MockViewerHandler) GetDatasetMetaCountsHandler(
	mirLoader loader.BaseMirRepoLoader,
) constants.QueryDatasetStatsResult {
	return constants.NewQueryDatasetStatsResult()
}

func (viewerHandler *MockViewerHandler) GetDatasetStatsHandler(
	mongo *MongoServer,
	mirLoader loader.BaseMirRepoLoader,
	classIDs []int,
) constants.QueryDatasetStatsResult {
	result := constants.NewQueryDatasetStatsResult()
	for classID := range classIDs {
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
	return 100, 1000, 2000
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
	r.GET("/users/:userID/repo/:repoID/branch/:branchID/dataset_stats", viewer.handleDatasetStats)
	r.GET("/users/:userID/repo/:repoID/branch/:branchID/dataset_meta_count", viewer.handleDatasetMetaCounts)

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

func TestDupPageHandlerSuccess(t *testing.T) {
	viewer := setUpViewer()
	r := viewer.gin
	r.GET("/users/:userID/repo/:repoID/dataset_duplication", viewer.handleDatasetDup)

	userID := "userID"
	repoID := "repoID"
	branchID0 := "branchID0"
	branchID1 := "branchID1"
	dupRequestURL := fmt.Sprintf(
		"/users/%s/repo/%s/dataset_duplication?candidate_dataset_ids=%s,%s",
		userID,
		repoID,
		branchID0,
		branchID1,
	)

	statsExpectedResult := bson.M{
		"duplication": 100,
		"total_count": bson.M{branchID0: 1000, branchID1: 2000},
	}
	statsExpectedResponseData := buildResponseBody(
		constants.ViewerSuccessCode,
		"Success",
		true,
		statsExpectedResult,
	)

	req, _ := http.NewRequest("GET", dupRequestURL, nil)
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	assert.Equal(t, string(statsExpectedResponseData), w.Body.String())
	assert.Equal(t, http.StatusOK, w.Code)
}

func TestDupPageHandlerFailure(t *testing.T) {
	viewer := setUpViewer()
	r := viewer.gin
	r.GET("/users/:userID/repo/:repoID/dataset_duplication", viewer.handleDatasetDup)

	userID := "userID"
	repoID := "repoID"
	branchID0 := "branchID0"
	dupRequestURL0 := fmt.Sprintf(
		"/users/%s/repo/%s/dataset_duplication",
		userID,
		repoID,
	)
	dupRequestURL1 := fmt.Sprintf(
		"/users/%s/repo/%s/dataset_duplication?candidate_dataset_ids=%s",
		userID,
		repoID,
		branchID0,
	)

	statsExpectedResponseData := buildResponseBody(
		constants.FailInvalidParmsCode,
		constants.FailInvalidParmsMsg,
		false,
		"Invalid candidate_dataset_ids",
	)
	req, _ := http.NewRequest("GET", dupRequestURL0, nil)
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	assert.Equal(t, string(statsExpectedResponseData), w.Body.String())
	assert.Equal(t, http.StatusOK, w.Code)

	statsExpectedResponseData = buildResponseBody(
		constants.FailInvalidParmsCode,
		constants.FailInvalidParmsMsg,
		false,
		"candidate_dataset_ids requires exact two datasets.",
	)
	req, _ = http.NewRequest("GET", dupRequestURL1, nil)
	w = httptest.NewRecorder()
	r.ServeHTTP(w, req)
	assert.Equal(t, string(statsExpectedResponseData), w.Body.String())
	assert.Equal(t, http.StatusOK, w.Code)
}

func TestAssetsPageHandlerSuccess(t *testing.T) {
	viewer := setUpViewer()
	r := viewer.gin
	r.GET("/users/:userID/repo/:repoID/branch/:branchID/assets", viewer.handleAssets)

	userID := "userID"
	repoID := "repoID"
	branchID := "branchID"
	offset := -1
	limit := 0
	classIDs := []int{0, 1}
	classIDsStr := "0,1"
	currentAssetID := "asset_id"
	cmTypes := "FP,FN"
	cks := "ck0,ck1"
	tags := "tag0,tag1"
	querySuffix := fmt.Sprintf("offset=%d&limit=%d&class_ids=%s&current_asset_id=%s&cm_types=%s&cks=%s&tags=%s",
		offset,
		limit,
		classIDsStr,
		currentAssetID,
		cmTypes,
		cks,
		tags,
	)
	dupRequestURL := fmt.Sprintf(
		"/users/%s/repo/%s/branch/%s/assets?%s",
		userID,
		repoID,
		branchID,
		querySuffix,
	)

	assetsExpectedResult := constants.QueryAssetsResult{
		AssetsDetail:     []constants.MirAssetDetail{},
		Offset:           0,
		Limit:            1,
		Anchor:           int64(len(classIDs)),
		TotalAssetsCount: 42,
	}
	assetsExpectedResponseData := buildResponseBody(
		constants.ViewerSuccessCode,
		"Success",
		true,
		assetsExpectedResult,
	)

	req, _ := http.NewRequest("GET", dupRequestURL, nil)
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	assert.Equal(t, string(assetsExpectedResponseData), w.Body.String())
	assert.Equal(t, http.StatusOK, w.Code)
}
