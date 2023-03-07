package server

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/IndustryEssentials/ymir-hel/common/constants"
	"github.com/IndustryEssentials/ymir-hel/configs"
	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

func TestCreateViewer(t *testing.T) {
	server, _ := NewViewerServer(&configs.Config{ViewerURI: "127.0.0.1:9527"})

	server.getInt("invalid")
	server.getIntSliceFromString("")
	server.getIntSliceFromString(",")
	server.getIntSliceFromString("getIntSliceFromQuery")

	go server.Start()
	server.Clear()
}

type MockViewerHandler struct {
	mock.Mock
}

func (h *MockViewerHandler) GetAssetsHandler(
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
	args := h.Called(mirRepo, offset, limit, classIDs, currentAssetID, inCMTypes, exCMTypes, cks, tags)
	return args.Get(0).(*constants.QueryAssetsResult)
}

func (h *MockViewerHandler) GetDatasetDupHandler(
	candidateMirRepos []*constants.MirRepo,
	corrodeeMirRepos []*constants.MirRepo,
) *constants.QueryDatasetDupResult {
	args := h.Called(candidateMirRepos, corrodeeMirRepos)
	return args.Get(0).(*constants.QueryDatasetDupResult)
}

func (h *MockViewerHandler) MetricsQueryHandler(
	metricsGroup string,
	userID string,
	classIDs []int,
	queryField string,
	bucket string,
	unit string,
	limit int,
) *[]constants.MetricsQueryPoint {
	args := h.Called(metricsGroup, userID, classIDs, queryField, bucket, unit, limit)
	return args.Get(0).(*[]constants.MetricsQueryPoint)
}
func (h *MockViewerHandler) MetricsRecordHandler(
	metricsGroup string,
	postForm map[string]interface{},
) {
	h.Called(metricsGroup, postForm)
}

func (h *MockViewerHandler) GetDatasetMetaCountsHandler(
	mirRepo *constants.MirRepo,
	checkIndexOnly bool,
) *constants.QueryDatasetStatsResult {
	args := h.Called(mirRepo, checkIndexOnly)
	return args.Get(0).(*constants.QueryDatasetStatsResult)
}

func (h *MockViewerHandler) GetDatasetStatsHandler(
	mirRepo *constants.MirRepo,
	classIDs []int,
	requireAssetsHist bool,
	requireAnnotationsHist bool,
) *constants.QueryDatasetStatsResult {
	args := h.Called(mirRepo, classIDs, requireAssetsHist, requireAnnotationsHist)
	return args.Get(0).(*constants.QueryDatasetStatsResult)
}

func (h *MockViewerHandler) GetModelInfoHandler(mirRepo *constants.MirRepo) *constants.MirdataModel {
	args := h.Called(mirRepo)
	return args.Get(0).(*constants.MirdataModel)
}

func buildResponseBody(
	code constants.ResponseCode,
	msg string,
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

func TestStatsPageHandlerSuccess(t *testing.T) {
	mockHandler := MockViewerHandler{}
	viewer := &ViewerServer{gin: gin.Default(), handler: &mockHandler}

	r := viewer.gin
	r.GET("/users/:userID/repo/:repoID/branch/:branchID/dataset_stats", viewer.handleDatasetStats)

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

	statsExpectedResult := constants.NewQueryDatasetStatsResult()
	for classID := range classIDs {
		statsExpectedResult.Gt.ClassIDsCount[classID] = 0
		statsExpectedResult.Pred.ClassIDsCount[classID] = 0
	}
	statsExpectedResponseData := buildResponseBody(
		constants.CodeSuccess,
		"Success",
		true,
		statsExpectedResult,
	)

	mirRepo := constants.MirRepo{UserID: userID, RepoID: repoID, BranchID: branchID, TaskID: branchID}
	mockHandler.On("GetDatasetStatsHandler", &mirRepo, classIDs, false, false).Return(statsExpectedResult)

	req, _ := http.NewRequest("GET", statsRequestURL, nil)
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	assert.Equal(t, string(statsExpectedResponseData), w.Body.String())
	assert.Equal(t, http.StatusOK, w.Code)
}

func TestMetaCountPageHandlerSuccess(t *testing.T) {
	mockHandler := MockViewerHandler{}
	viewer := &ViewerServer{gin: gin.Default(), handler: &mockHandler}

	r := viewer.gin
	r.GET("/users/:userID/repo/:repoID/branch/:branchID/dataset_meta_count", viewer.handleDatasetMetaCounts)

	userID := "userID"
	repoID := "repoID"
	branchID := "branchID"
	metaRequestURL := fmt.Sprintf(
		"/users/%s/repo/%s/branch/%s/dataset_meta_count",
		userID,
		repoID,
		branchID,
	)

	metaExpectedResult := constants.NewQueryDatasetStatsResult()
	metaExpectedResponseData := buildResponseBody(
		constants.CodeSuccess,
		"Success",
		true,
		metaExpectedResult,
	)

	mirRepo := constants.MirRepo{UserID: userID, RepoID: repoID, BranchID: branchID, TaskID: branchID}
	mockHandler.On("GetDatasetMetaCountsHandler", &mirRepo, false).Return(metaExpectedResult)

	req, _ := http.NewRequest("GET", metaRequestURL, nil)
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	assert.Equal(t, string(metaExpectedResponseData), w.Body.String())
	assert.Equal(t, http.StatusOK, w.Code)
}

func TestMetaCountPageHandlerFailure(t *testing.T) {
	mockHandler := MockViewerHandler{}
	viewer := &ViewerServer{gin: gin.Default(), handler: &mockHandler}

	r := viewer.gin
	r.GET("/users/:userID/repo/:repoID/branch/:branchID/dataset_meta_count", viewer.handleDatasetMetaCounts)

	userID := "userID"
	repoID := "repoID"
	branchID := "branchID"
	metaRequestURL := fmt.Sprintf(
		"/users/%s/repo/%s/branch/%s/dataset_meta_count",
		userID,
		repoID,
		branchID,
	)

	failureResult := FailureResult{
		Code: constants.CodeViewerRepoNotExist,
		Msg:  "unknown ref",
	}
	statsExpectedResponseData := buildResponseBody(
		failureResult.Code,
		failureResult.Msg,
		false,
		failureResult,
	)

	mirRepo := constants.MirRepo{UserID: userID, RepoID: repoID, BranchID: branchID, TaskID: branchID}
	mockHandler.On("GetDatasetMetaCountsHandler", &mirRepo, false).Panic("unknown ref")

	req, _ := http.NewRequest("GET", metaRequestURL, nil)
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	assert.Equal(t, string(statsExpectedResponseData), w.Body.String())
	assert.Equal(t, http.StatusBadRequest, w.Code)
}

func TestDupPageHandlerSuccess(t *testing.T) {
	mockHandler := MockViewerHandler{}
	viewer := &ViewerServer{gin: gin.Default(), handler: &mockHandler}

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

	dupCount := 100
	branchCount0 := int64(1000)
	branchCount1 := int64(2000)
	mockDupResult := &constants.QueryDatasetDupResult{
		Duplication: dupCount,
		TotalCount:  map[string]int64{branchID0: branchCount0, branchID1: branchCount1},
	}
	statsExpectedResponseData := buildResponseBody(
		constants.CodeSuccess,
		"Success",
		true,
		mockDupResult,
	)

	// Set mock funcs.
	mirRepo0 := constants.MirRepo{UserID: userID, RepoID: repoID, BranchID: branchID0, TaskID: branchID0}
	mirRepo1 := constants.MirRepo{UserID: userID, RepoID: repoID, BranchID: branchID1, TaskID: branchID1}
	mockHandler.On("GetDatasetDupHandler", []*constants.MirRepo{&mirRepo0, &mirRepo1}, []*constants.MirRepo{}).
		Return(mockDupResult)

	req, _ := http.NewRequest("GET", dupRequestURL, nil)
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	assert.Equal(t, string(statsExpectedResponseData), w.Body.String())
	assert.Equal(t, http.StatusOK, w.Code)
}

func TestDupPageHandlerFailure(t *testing.T) {
	mockHandler := MockViewerHandler{}
	viewer := &ViewerServer{gin: gin.Default(), handler: &mockHandler}

	r := viewer.gin
	r.GET("/users/:userID/repo/:repoID/dataset_duplication", viewer.handleDatasetDup)

	userID := "userID"
	repoID := "repoID"
	dupRequestURL0 := fmt.Sprintf(
		"/users/%s/repo/%s/dataset_duplication",
		userID,
		repoID,
	)
	failureResult := FailureResult{
		Code: constants.CodeViewerInvalidParms,
		Msg:  "Invalid candidate_dataset_ids.",
	}
	statsExpectedResponseData := buildResponseBody(
		failureResult.Code,
		failureResult.Msg,
		false,
		failureResult,
	)
	req, _ := http.NewRequest("GET", dupRequestURL0, nil)
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	assert.Equal(t, string(statsExpectedResponseData), w.Body.String())
	assert.Equal(t, http.StatusBadRequest, w.Code)

	dupRequestURL1 := fmt.Sprintf(
		"/users/%s/repo/%s/dataset_duplication?candidate_dataset_ids=,",
		userID,
		repoID,
	)
	failureResult = FailureResult{
		Code: constants.CodeViewerInvalidParms,
		Msg:  "Invalid candidate_dataset_ids.",
	}
	statsExpectedResponseData = buildResponseBody(
		failureResult.Code,
		failureResult.Msg,
		false,
		failureResult,
	)
	req, _ = http.NewRequest("GET", dupRequestURL1, nil)
	w = httptest.NewRecorder()
	r.ServeHTTP(w, req)
	assert.Equal(t, string(statsExpectedResponseData), w.Body.String())
	assert.Equal(t, http.StatusBadRequest, w.Code)
}

func TestAssetsPageHandlerSuccess(t *testing.T) {
	mockHandler := MockViewerHandler{}
	viewer := &ViewerServer{gin: gin.Default(), handler: &mockHandler}

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
	inCMTypes := "0,1"
	exCMTypes := ""
	cks := "ck0,ck1"
	tags := "tag0,tag1"
	querySuffix := fmt.Sprintf(
		"offset=%d&limit=%d&class_ids=%s&current_asset_id=%s&in_cm_types=%s&ex_cm_types=%s&cks=%s&tags=%s",
		offset,
		limit,
		classIDsStr,
		currentAssetID,
		inCMTypes,
		exCMTypes,
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

	assetsExpectedResult := &constants.QueryAssetsResult{
		AssetsDetail:     []constants.MirAssetDetail{},
		Offset:           0,
		Limit:            1,
		Anchor:           int64(len(classIDs)),
		TotalAssetsCount: 42,
	}
	assetsExpectedResponseData := buildResponseBody(
		constants.CodeSuccess,
		"Success",
		true,
		assetsExpectedResult,
	)

	revisedOffset := 0
	revisedLimit := 1
	revisedInCMTypes := []int{0, 1}
	revisedExCMTypes := []int{}
	revisedCks := []string{"ck0", "ck1"}
	revisedTags := []string{"tag0", "tag1"}
	mirRepo := constants.MirRepo{UserID: userID, RepoID: repoID, BranchID: branchID, TaskID: branchID}
	mockHandler.On(
		"GetAssetsHandler",
		&mirRepo,
		revisedOffset,
		revisedLimit,
		classIDs,
		currentAssetID,
		revisedInCMTypes,
		revisedExCMTypes,
		revisedCks,
		revisedTags).
		Return(assetsExpectedResult)

	req, _ := http.NewRequest("GET", dupRequestURL, nil)
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	assert.Equal(t, string(assetsExpectedResponseData), w.Body.String())
	assert.Equal(t, http.StatusOK, w.Code)
}
