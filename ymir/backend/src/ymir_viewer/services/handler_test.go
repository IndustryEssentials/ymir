package services

import (
	"encoding/json"
	"strconv"
	"testing"

	"github.com/IndustryEssentials/ymir-viewer/common/constants"
	"github.com/IndustryEssentials/ymir-viewer/common/protos"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type MockMirRepoLoader struct {
	mock.Mock
}

func (m *MockMirRepoLoader) LoadSingleMirData(mirRepo *constants.MirRepo, mirFile constants.MirFile) interface{} {
	args := m.Called(mirRepo, mirFile)
	return args.Get(0)
}

func (m *MockMirRepoLoader) LoadMutipleMirDatas(
	mirRepo *constants.MirRepo,
	mirFiles []constants.MirFile,
) []interface{} {
	args := m.Called(mirRepo, mirFiles)
	return args.Get(0).([]interface{})
}

func (m *MockMirRepoLoader) LoadAssetsDetail(
	mirRepo *constants.MirRepo,
	anchorAssetID string,
	offset int,
	limit int,
) ([]constants.MirAssetDetail, int64, int64) {
	args := m.Called(mirRepo, anchorAssetID, offset, limit)
	return args.Get(0).([]constants.MirAssetDetail), args.Get(1).(int64), args.Get(2).(int64)
}

func (m *MockMirRepoLoader) LoadModelInfo(mirRepo *constants.MirRepo) *constants.MirdataModel {
	args := m.Called(mirRepo)
	return args.Get(0).(*constants.MirdataModel)
}

type MockMongoServer struct {
	mock.Mock
}

func (m *MockMongoServer) CheckDatasetExistenceReady(mirRepo *constants.MirRepo) (bool, bool) {
	args := m.Called(mirRepo)
	return args.Bool(0), args.Bool(1)
}

func (m *MockMongoServer) IndexDatasetData(mirRepo *constants.MirRepo, newData []interface{}) {
	m.Called(mirRepo, newData)
}

func (m *MockMongoServer) QueryDatasetAssets(
	mirRepo *constants.MirRepo,
	offset int,
	limit int,
	classIds []int,
	annoTypes []string,
	currentAssetID string,
	cmTypes []int,
	cks []string,
	tags []string,
) *constants.QueryAssetsResult {
	args := m.Called(mirRepo, offset, limit, classIds, annoTypes, currentAssetID, cmTypes, cks, tags)
	return args.Get(0).(*constants.QueryAssetsResult)
}

func (m *MockMongoServer) QueryDatasetStats(
	mirRepo *constants.MirRepo,
	classIDs []int,
	requireAssetsHist bool,
	requireAnnotationsHist bool,
) *constants.QueryDatasetStatsResult {
	args := m.Called(mirRepo, classIDs)
	return args.Get(0).(*constants.QueryDatasetStatsResult)
}

func TestGetDatasetMetaCountsHandler(t *testing.T) {
	mirFileContext := constants.MirfileContext
	mirFileTasks := constants.MirfileTasks
	mockMirContext := protos.MirContext{}
	err := json.Unmarshal([]byte(`{
		"images_cnt": 20,
		"cks_cnt":
		{
			"city":
			{
				"cnt": 1,
				"sub_cnt":
				{
					"hangzhou": 1
				}
			}
		},
		"pred_stats":
		{
			"positive_asset_cnt": 8,
			"negative_asset_cnt": 5,
			"class_ids_cnt":
			{
				"1": 8
			},
			"tags_cnt": {
				"city": {
					"cnt": 1,
					"sub_cnt":
					{
						"shenzhen": 1
					}
			}}
		},
		"gt_stats":
		{
			"positive_asset_cnt": 3,
			"negative_asset_cnt": 2,
			"class_ids_cnt":
			{
				"0": 3
			},
			"tags_cnt": {
				"city": {
					"cnt": 1,
					"sub_cnt":
					{
						"guangzhou": 1
					}
			}}
		}
	}`), &mockMirContext)
	if err != nil {
		panic(err)
	}
	expectedResult := constants.QueryDatasetStatsResult{}
	err = json.Unmarshal([]byte(`{
		"gt":
		{
			"class_ids_count":
			{
				"0": 3
			},
			"negative_assets_count": 2,
			"annos_hist": {},
			"positive_assets_count": 3,
			"tags_count_total":
			{
				"city": 1
			},
			"tags_count":
			{
				"city":
				{
					"guangzhou": 1
				}
			}
		},
		"pred":
		{
			"class_ids_count":
			{
				"1": 8
			},
			"negative_assets_count": 5,
			"annos_hist": {},
			"positive_assets_count": 8,
			"tags_count_total":
			{
				"city": 1
			},
			"tags_count":
			{
				"city":
				{
					"shenzhen": 1
				}
			}
		},
		"total_assets_count": 20,
		"assets_hist": {},
		"cks_count_total":
		{
			"city": 1
		},
		"cks_count":
		{
			"city":
			{
				"hangzhou": 1
			}
		},
		"new_types_added": true
	}`), &expectedResult)
	if err != nil {
		panic(err)
	}

	mirRepo := constants.MirRepo{}
	mockLoader := MockMirRepoLoader{}
	mockLoader.On("LoadSingleMirData", &mirRepo, mirFileContext).Return(&mockMirContext, 0, 0).Twice()
	mockLoader.On("LoadSingleMirData", &mirRepo, mirFileTasks).
		Return(&protos.MirTasks{HeadTaskId: "h", Tasks: map[string]*protos.Task{"h": {NewTypesAdded: true}}}, 0, 0).
		Once()
	mockMongoServer := MockMongoServer{}

	handler := &ViewerHandler{mongoServer: &mockMongoServer, mirLoader: &mockLoader}
	result := handler.GetDatasetMetaCountsHandler(&mirRepo)

	assert.Equal(t, &expectedResult, result)
	mockLoader.AssertExpectations(t)

}

func TestGetDatasetDupHandler(t *testing.T) {
	mirRepo0 := constants.MirRepo{BranchID: "a"}
	mirRepo1 := constants.MirRepo{BranchID: "b"}

	expectedDup := 100
	expectedCount0 := int64(expectedDup)
	expectedCount1 := int64(expectedDup)

	mockMongoServer := MockMongoServer{}
	mockLoader := MockMirRepoLoader{}
	mockMirMetadatas := protos.MirMetadatas{Attributes: map[string]*protos.MetadataAttributes{}}
	for i := 0; i < expectedDup; i++ {
		mockMirMetadatas.Attributes[strconv.Itoa(i)] = &protos.MetadataAttributes{}
	}
	mockLoader.On("LoadSingleMirData", &mirRepo0, constants.MirfileMetadatas).Return(&mockMirMetadatas).Once()
	mockLoader.On("LoadSingleMirData", &mirRepo1, constants.MirfileMetadatas).Return(&mockMirMetadatas).Once()

	expectedResult := &constants.QueryDatasetDupResult{
		Duplication: expectedDup,
		TotalCount:  map[string]int64{"a": expectedCount0, "b": expectedCount1},
	}

	handler := &ViewerHandler{mongoServer: &mockMongoServer, mirLoader: &mockLoader}
	resultData := handler.GetDatasetDupHandler(&mirRepo0, &mirRepo1)
	assert.Equal(t, expectedResult, resultData)
}

func TestGetDatasetStatsHandler(t *testing.T) {
	mirFileContext := constants.MirfileContext
	mirFileTasks := constants.MirfileTasks
	mockMirContext := protos.MirContext{}
	mockAssetsDetail := []constants.MirAssetDetail{{AssetID: "a"}}
	mirRepo := constants.MirRepo{}
	mockLoader := MockMirRepoLoader{}
	mockLoader.On("LoadAssetsDetail", &mirRepo, "", 0, 0).Return(mockAssetsDetail, int64(0), int64(0))
	mockLoader.On("LoadSingleMirData", &mirRepo, mirFileContext).Return(&mockMirContext, 0, 0).Once()
	mockLoader.On("LoadSingleMirData", &mirRepo, mirFileTasks).
		Return(&protos.MirTasks{HeadTaskId: "h", Tasks: map[string]*protos.Task{"h": {NewTypesAdded: true}}}, 0, 0).
		Once()

	classIDs := []int{0, 1}
	expectedResult := &constants.QueryDatasetStatsResult{}
	mockMongoServer := MockMongoServer{}
	mockMongoServer.On("CheckDatasetExistenceReady", &mirRepo).Return(false, false)
	mockMongoServer.On("IndexDatasetData", &mirRepo, []interface{}{mockAssetsDetail[0]})
	mockMongoServer.On("QueryDatasetStats", &mirRepo, classIDs).Return(expectedResult)
	handler := &ViewerHandler{mongoServer: &mockMongoServer, mirLoader: &mockLoader}

	result := handler.GetDatasetStatsHandler(&mirRepo, classIDs, true, true)
	assert.Equal(t, expectedResult, result)
}

func TestGetAssetsHandler(t *testing.T) {
	mirRepo := constants.MirRepo{}
	mockLoader := MockMirRepoLoader{}

	offset := 100
	limit := 10
	classIDs := []int{0, 1}
	annoTypes := []string{"gt", "pred"}
	currentAssetID := "abc"
	cmTypes := []int{0, 1}
	cks := []string{"a", "b", "c"}
	tags := []string{"x", "y", "z"}
	expectedResult := &constants.QueryAssetsResult{}
	mockMongoServer := MockMongoServer{}
	mockMongoServer.On("CheckDatasetExistenceReady", &mirRepo).Return(true, true)
	mockMongoServer.On("QueryDatasetAssets", &mirRepo, offset, limit, classIDs, annoTypes, currentAssetID, cmTypes, cks, tags).
		Return(expectedResult)
	handler := &ViewerHandler{mongoServer: &mockMongoServer, mirLoader: &mockLoader}

	result := handler.GetAssetsHandler(
		&mirRepo,
		offset,
		limit,
		classIDs,
		annoTypes,
		currentAssetID,
		cmTypes,
		cks,
		tags,
	)
	assert.Equal(t, expectedResult, result)
}

func TestLoadAndIndexAssets(t *testing.T) {
	mirRepo := constants.MirRepo{}
	mockLoader := MockMirRepoLoader{}
	mockMongoServer := MockMongoServer{}
	mockMongoServer.On("CheckDatasetExistenceReady", &mirRepo).Return(true, false).Once()
	mockMongoServer.On("CheckDatasetExistenceReady", &mirRepo).Return(true, true)
	handler := &ViewerHandler{mongoServer: &mockMongoServer, mirLoader: &mockLoader}
	handler.loadAndIndexAssets(&mirRepo)
}

func TestGetAssetsHandlerShortcut(t *testing.T) {
	offset := 100
	limit := 10
	classIDs := []int{}
	annoTypes := []string{}
	currentAssetID := "abc"
	cmTypes := []int{}
	cks := []string{}
	tags := []string{}
	anchor := int64(0)
	totalAssetsCount := int64(100)

	expectedResult := &constants.QueryAssetsResult{
		AssetsDetail:     []constants.MirAssetDetail{},
		Offset:           offset,
		Limit:            limit,
		Anchor:           anchor,
		TotalAssetsCount: totalAssetsCount}

	mockAssetsDetail := []constants.MirAssetDetail{}
	mirRepo := constants.MirRepo{}
	mockLoader := MockMirRepoLoader{}
	mockLoader.On("LoadAssetsDetail", &mirRepo, "", 0, 0).Return(mockAssetsDetail, int64(0), int64(0))
	mockLoader.On("LoadAssetsDetail", &mirRepo, currentAssetID, offset, limit).
		Return(mockAssetsDetail, anchor, totalAssetsCount)

	mockMongoServer := MockMongoServer{}
	mockMongoServer.On("CheckDatasetExistenceReady", &mirRepo).Return(false, false)
	mockMongoServer.On("IndexDatasetData", &mirRepo, []interface{}{})
	handler := &ViewerHandler{mongoServer: &mockMongoServer, mirLoader: &mockLoader}

	result := handler.GetAssetsHandler(
		&mirRepo,
		offset,
		limit,
		classIDs,
		annoTypes,
		currentAssetID,
		cmTypes,
		cks,
		tags,
	)
	assert.Equal(t, expectedResult, result)
}
