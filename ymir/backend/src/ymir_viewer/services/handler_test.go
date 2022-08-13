package services

import (
	"encoding/json"
	"testing"

	"github.com/IndustryEssentials/ymir-viewer/common/constants"
	"github.com/IndustryEssentials/ymir-viewer/common/protos"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"go.mongodb.org/mongo-driver/mongo"
)

type MockMirRepoLoader struct {
	mock.Mock
}

func (m *MockMirRepoLoader) GetMirRepo() *constants.MirRepo {
	args := m.Called()
	return args.Get(0).(*constants.MirRepo)
}

func (m *MockMirRepoLoader) LoadSingleMirData(mirFile constants.MirFile) interface{} {
	args := m.Called(mirFile)
	return args.Get(0).(*protos.MirContext)
}

func (m *MockMirRepoLoader) LoadAssetsDetail(
	anchorAssetID string,
	offset int,
	limit int,
) ([]constants.MirAssetDetail, int64, int64) {
	args := m.Called(anchorAssetID, offset, limit)
	return args.Get(0).([]constants.MirAssetDetail), args.Get(1).(int64), args.Get(2).(int64)
}

type MockMongoServer struct {
	mock.Mock
}

func (m *MockMongoServer) setExistence(collectionName string, ready bool, insert bool) {
	m.Called(collectionName, ready, insert)
}

func (m *MockMongoServer) checkExistence(mirRepo *constants.MirRepo) bool {
	args := m.Called(mirRepo)
	return args.Bool(0)
}

func (m *MockMongoServer) IndexCollectionData(mirRepo *constants.MirRepo, newData []interface{}) {
	m.Called(mirRepo, newData)
}

func (m *MockMongoServer) QueryAssets(
	mirRepo *constants.MirRepo,
	offset int,
	limit int,
	classIds []int,
	currentAssetID string,
	cmTypes []int32,
	cks []string,
	tags []string,
) constants.QueryAssetsResult {
	args := m.Called(mirRepo, offset, limit, classIds, currentAssetID, cmTypes, cks, tags)
	return args.Get(0).(constants.QueryAssetsResult)
}

func (m *MockMongoServer) QueryDatasetStats(
	mirRepo *constants.MirRepo,
	classIDs []int,
) constants.QueryDatasetStatsResult {
	args := m.Called(mirRepo, classIDs)
	return args.Get(0).(constants.QueryDatasetStatsResult)
}

func (m *MockMongoServer) QueryDatasetDup(
	mirRepo0 *constants.MirRepo,
	mirRepo1 *constants.MirRepo,
) (int, int64, int64) {
	args := m.Called(mirRepo0, mirRepo1)
	return args.Int(0), args.Get(1).(int64), args.Get(2).(int64)
}

func (m *MockMongoServer) countAssetsInClass(collection *mongo.Collection, queryField string, classIds []int) int64 {
	args := m.Called(collection, queryField, classIds)
	return args.Get(0).(int64)
}

func (m *MockMongoServer) getRepoCollection(mirRepo *constants.MirRepo) (*mongo.Collection, string) {
	args := m.Called(mirRepo)
	return args.Get(0).(*mongo.Collection), args.String(1)
}

func TestGetDatasetMetaCountsHandler(t *testing.T) {
	mirFile := constants.MirfileContext
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
			}
		},
		"gt_stats":
		{
			"positive_asset_cnt": 3,
			"negative_asset_cnt": 2,
			"class_ids_cnt":
			{
				"0": 3
			}
		}
	}`), &mockMirContext)
	if err != nil {
		panic(err)
	}

	pbreaderMock := MockMirRepoLoader{}
	pbreaderMock.On("LoadSingleMirData", mirFile).Return(&mockMirContext, 0, 0)

	expectedResult := constants.QueryDatasetStatsResult{}
	handler := &ViewerHandler{}
	result := handler.GetDatasetMetaCountsHandler(&pbreaderMock)
	err = json.Unmarshal([]byte(`{
		"gt":
		{
			"class_ids_count":
			{
				"0": 3
			},
			"negative_images_count": 2,
			"positive_images_count": 3
		},
		"pred":
		{
			"class_ids_count":
			{
				"1": 8
			},
			"negative_images_count": 5,
			"positive_images_count": 8
		},
		"total_assets_count": 20,
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
		}
	}`), &expectedResult)
	if err != nil {
		panic(err)
	}
	assert.Equal(t, expectedResult, result)
	pbreaderMock.AssertExpectations(t)

}

func TestGetDatasetDupHandler(t *testing.T) {
	mirRepo := constants.MirRepo{}
	pbreaderMock0 := MockMirRepoLoader{}
	pbreaderMock0.On("GetMirRepo").Return(&mirRepo)
	pbreaderMock1 := MockMirRepoLoader{}
	pbreaderMock1.On("GetMirRepo").Return(&mirRepo)

	expectedDup := 100
	expectedCount0 := int64(200)
	expectedCount1 := int64(300)
	mockMongoServer := MockMongoServer{}
	mockMongoServer.On("checkExistence", &mirRepo).Return(true)
	mockMongoServer.On("QueryDatasetDup", &mirRepo, &mirRepo).Return(expectedDup, expectedCount0, expectedCount1)
	handler := &ViewerHandler{}

	retDup, retCount0, retCount1 := handler.GetDatasetDupHandler(&mockMongoServer, &pbreaderMock0, &pbreaderMock1)
	assert.Equal(t, expectedDup, retDup)
	assert.Equal(t, expectedCount0, retCount0)
	assert.Equal(t, expectedCount1, retCount1)
}

func TestGetDatasetStatsHandler(t *testing.T) {
	mockAssetsDetail := []constants.MirAssetDetail{{AssetID: "a"}}
	mirRepo := constants.MirRepo{}
	pbreaderMock := MockMirRepoLoader{}
	pbreaderMock.On("GetMirRepo").Return(&mirRepo)
	pbreaderMock.On("LoadAssetsDetail", "", 0, 0).Return(mockAssetsDetail, int64(0), int64(0))

	classIDs := []int{0, 1}
	expectedResult := constants.QueryDatasetStatsResult{}
	mockMongoServer := MockMongoServer{}
	mockMongoServer.On("checkExistence", &mirRepo).Return(false)
	mockMongoServer.On("IndexCollectionData", &mirRepo, []interface{}{mockAssetsDetail[0]})
	mockMongoServer.On("QueryDatasetStats", &mirRepo, classIDs).Return(expectedResult)
	handler := &ViewerHandler{}

	result := handler.GetDatasetStatsHandler(&mockMongoServer, &pbreaderMock, classIDs)
	assert.Equal(t, expectedResult, result)
}

func TestGetAssetsHandler(t *testing.T) {
	mirRepo := constants.MirRepo{}
	pbreaderMock := MockMirRepoLoader{}
	pbreaderMock.On("GetMirRepo").Return(&mirRepo)

	offset := 100
	limit := 10
	classIDs := []int{0, 1}
	currentAssetID := "abc"
	cmTypes := []int32{0, 1}
	cks := []string{"a", "b", "c"}
	tags := []string{"x", "y", "z"}
	expectedResult := constants.QueryAssetsResult{}
	mockMongoServer := MockMongoServer{}
	mockMongoServer.On("checkExistence", &mirRepo).Return(true)
	mockMongoServer.On("QueryAssets", &mirRepo, offset, limit, classIDs, currentAssetID, cmTypes, cks, tags).
		Return(expectedResult)
	handler := &ViewerHandler{}

	result := handler.GetAssetsHandler(
		&mockMongoServer,
		&pbreaderMock,
		offset,
		limit,
		classIDs,
		currentAssetID,
		cmTypes,
		cks,
		tags,
	)
	assert.Equal(t, expectedResult, result)
}

func TestGetAssetsHandlerShortcut(t *testing.T) {
	offset := 100
	limit := 10
	classIDs := []int{}
	currentAssetID := "abc"
	cmTypes := []int32{}
	cks := []string{}
	tags := []string{}
	anchor := int64(0)
	totalAssetsCount := int64(100)

	expectedResult := constants.QueryAssetsResult{
		AssetsDetail:     []constants.MirAssetDetail{},
		Offset:           offset,
		Limit:            limit,
		Anchor:           anchor,
		TotalAssetsCount: totalAssetsCount}

	mockAssetsDetail := []constants.MirAssetDetail{}
	mirRepo := constants.MirRepo{}
	pbreaderMock := MockMirRepoLoader{}
	pbreaderMock.On("GetMirRepo").Return(&mirRepo)
	pbreaderMock.On("LoadAssetsDetail", "", 0, 0).Return(mockAssetsDetail, int64(0), int64(0))
	pbreaderMock.On("LoadAssetsDetail", currentAssetID, offset, limit).
		Return(mockAssetsDetail, anchor, totalAssetsCount)

	mockMongoServer := MockMongoServer{}
	mockMongoServer.On("checkExistence", &mirRepo).Return(false)
	mockMongoServer.On("IndexCollectionData", &mirRepo, []interface{}{})
	handler := &ViewerHandler{}

	result := handler.GetAssetsHandler(
		&mockMongoServer,
		&pbreaderMock,
		offset,
		limit,
		classIDs,
		currentAssetID,
		cmTypes,
		cks,
		tags,
	)
	assert.Equal(t, expectedResult, result)
}
