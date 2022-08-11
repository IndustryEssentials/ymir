package services

import (
	"encoding/json"
	"testing"

	"github.com/IndustryEssentials/ymir-viewer/common/constants"
	"github.com/IndustryEssentials/ymir-viewer/common/protos"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type MockMirRepoLoader struct {
	mock.Mock
}

func (m *MockMirRepoLoader) GetMirRepo() constants.MirRepo {
	return constants.MirRepo{}
}

func (m *MockMirRepoLoader) LoadSingleMirData(mirFile constants.MirFile) interface{} {

	args := m.Called(mirFile)
	return args.Get(0).(*protos.MirContext)
}

func (m *MockMirRepoLoader) LoadAssetsDetail() []constants.MirAssetDetail {

	args := m.Called()
	return args.Get(0).([]constants.MirAssetDetail)
}

func TestGetDatasetMetaCountsHandler(t *testing.T) {
	mirFile := constants.MirfileContext
	mockMirContext := protos.MirContext{}
	err := json.Unmarshal([]byte(`{
		"images_cnt": 20,
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
	pbreaderMock.On("LoadSingleMirData", mirFile).Return(&mockMirContext)

	expectedResult := constants.QueryDatasetStatsResult{}
	result := GetDatasetMetaCountsHandler(&pbreaderMock)
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
		"cks_count_total": {},
		"cks_count": {}
	}`), &expectedResult)
	if err != nil {
		panic(err)
	}
	assert.Equal(t, result, expectedResult)
	pbreaderMock.AssertExpectations(t)

}
