package mongodb

import (
	"context"
	"encoding/json"
	"testing"

	"github.com/IndustryEssentials/ymir-hel/common/constants"
	"github.com/IndustryEssentials/ymir-hel/protos"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/integration/mtest"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type MockDatabase struct {
	mock.Mock
}

func (m *MockDatabase) Collection(name string, opts ...*options.CollectionOptions) *mongo.Collection {
	args := m.Called(name, opts)
	return args.Get(0).(*mongo.Collection)
}

func getDatasetMetadataName() string {
	return "__collection_metadata__@"
}

func TestSetDatasetExistenceSuccess(t *testing.T) {
	mt := mtest.New(t, mtest.NewOptions().ClientType(mtest.Mock))
	defer mt.Close()

	mt.Run("success", func(mt *mtest.T) {
		mockCollection := mt.Coll
		mockMirDatabase := MockDatabase{}
		mockMetricsDatabase := MockDatabase{}
		mockMirDatabase.On("Collection", getDatasetMetadataName(), []*options.CollectionOptions(nil)).
			Return(mockCollection)

		mongoServer := NewMongoServer(context.Background(), &mockMirDatabase, &mockMetricsDatabase)
		mt.AddMockResponses(mtest.CreateSuccessResponse())
		mongoServer.setDatasetExistence("", true, false)
	})
}

func TestSetDatasetExistenceFailure(t *testing.T) {
	mt := mtest.New(t, mtest.NewOptions().ClientType(mtest.Mock))
	defer mt.Close()

	mt.Run("success", func(mt *mtest.T) {
		defer func() {
			if r := recover(); r == nil {
				t.Errorf("The code did not panic")
			}
		}()
		mockCollection := mt.Coll
		mockMirDatabase := MockDatabase{}
		mockMetricsDatabase := MockDatabase{}
		mockMirDatabase.On("Collection", getDatasetMetadataName(), []*options.CollectionOptions(nil)).
			Return(mockCollection)

		mongoServer := NewMongoServer(context.Background(), &mockMirDatabase, &mockMetricsDatabase)
		mt.AddMockResponses(mtest.CreateWriteErrorsResponse(mtest.WriteError{}))
		mongoServer.setDatasetExistence("", true, true)
	})
}

func TestCheckDatasetExistenceSuccess(t *testing.T) {
	mt := mtest.New(t, mtest.NewOptions().ClientType(mtest.Mock))
	defer mt.Close()

	mt.Run("success", func(mt *mtest.T) {
		mirRepo := constants.MirRepo{}
		mockCollection := mt.Coll
		mockMirDatabase := MockDatabase{}
		mockMetricsDatabase := MockDatabase{}
		mockMirDatabase.On("Collection", getDatasetMetadataName(), []*options.CollectionOptions(nil)).
			Return(mockCollection)
		mockMirDatabase.On("Collection", "@", []*options.CollectionOptions(nil)).
			Return(mockCollection)

		mongoServer := NewMongoServer(context.Background(), &mockMirDatabase, &mockMetricsDatabase)
		find := mtest.CreateCursorResponse(
			1,
			"a.b",
			mtest.FirstBatch,
			bson.D{{Key: "exist", Value: true}, {Key: "ready", Value: true}})
		mt.AddMockResponses(find)
		existence, ready := mongoServer.CheckDatasetIndex(&mirRepo)
		assert.Equal(t, existence, true)
		assert.Equal(t, ready, true)
	})
}

func TestCheckDatasetExistenceFailure0(t *testing.T) {
	mt := mtest.New(t, mtest.NewOptions().ClientType(mtest.Mock))
	defer mt.Close()

	mt.Run("success", func(mt *mtest.T) {
		mirRepo := constants.MirRepo{}
		mockCollection := mt.Coll
		mockMirDatabase := MockDatabase{}
		mockMetricsDatabase := MockDatabase{}
		mockMirDatabase.On("Collection", getDatasetMetadataName(), []*options.CollectionOptions(nil)).
			Return(mockCollection)

		mongoServer := NewMongoServer(context.Background(), &mockMirDatabase, &mockMetricsDatabase)
		existence, ready := mongoServer.CheckDatasetIndex(&mirRepo)
		assert.Equal(t, existence, false)
		assert.Equal(t, ready, false)
	})
}

func TestCheckDatasetExistenceFailure1(t *testing.T) {
	mt := mtest.New(t, mtest.NewOptions().ClientType(mtest.Mock))
	defer mt.Close()

	mt.Run("success", func(mt *mtest.T) {
		mirRepo := constants.MirRepo{}
		mockCollection := mt.Coll
		mockMirDatabase := MockDatabase{}
		mockMetricsDatabase := MockDatabase{}
		mockMirDatabase.On("Collection", getDatasetMetadataName(), []*options.CollectionOptions(nil)).
			Return(mockCollection)
		mockMirDatabase.On("Collection", "@", []*options.CollectionOptions(nil)).
			Return(mockCollection)

		mongoServer := NewMongoServer(context.Background(), &mockMirDatabase, &mockMetricsDatabase)

		find := mtest.CreateCursorResponse(
			1,
			"a.b",
			mtest.FirstBatch,
			bson.D{{Key: "exist", Value: false}, {Key: "ready", Value: false}})
		mt.AddMockResponses(find)
		existence, ready := mongoServer.CheckDatasetIndex(&mirRepo)
		assert.Equal(t, existence, false)
		assert.Equal(t, ready, false)
	})
}

func TestCountAssetsInClassSuccess(t *testing.T) {
	mt := mtest.New(t, mtest.NewOptions().ClientType(mtest.Mock))
	defer mt.Close()

	mt.Run("success", func(mt *mtest.T) {
		collection := mt.Coll
		mockCollection := mt.Coll
		mockMirDatabase := MockDatabase{}
		mockMetricsDatabase := MockDatabase{}
		mockMirDatabase.On("Collection", "@", []*options.CollectionOptions(nil)).
			Return(mockCollection)

		mongoServer := NewMongoServer(context.Background(), &mockMirDatabase, &mockMetricsDatabase)

		queryField := "abc"
		expectedCount := int32(10)
		classIDs := []int{0, 1}
		first := mtest.CreateCursorResponse(
			1,
			"a.b",
			mtest.FirstBatch,
			bson.D{{Key: "count", Value: expectedCount}, {Key: "sum", Value: expectedCount}})
		second := mtest.CreateCursorResponse(
			1,
			"a.b",
			mtest.NextBatch,
			bson.D{{Key: "AssetID", Value: "aaa"}})
		killCursors := mtest.CreateCursorResponse(0, "a.b", mtest.NextBatch)
		mt.AddMockResponses(first, second, killCursors)
		count, _ := mongoServer.countDatasetAssetsInClass(collection, queryField, classIDs)
		assert.Equal(t, int64(expectedCount), count)
	})
}

func TestQueryAssetsSuccess(t *testing.T) {
	mt := mtest.New(t, mtest.NewOptions().ClientType(mtest.Mock))
	defer mt.Close()

	mt.Run("success", func(mt *mtest.T) {
		mirRepo := constants.MirRepo{}
		mockCollection := mt.Coll
		mockMirDatabase := MockDatabase{}
		mockMetricsDatabase := MockDatabase{}
		mockMirDatabase.On("Collection", getDatasetMetadataName(), []*options.CollectionOptions(nil)).
			Return(mockCollection)
		mockMirDatabase.On("Collection", "@", []*options.CollectionOptions(nil)).
			Return(mockCollection)

		mongoServer := NewMongoServer(context.Background(), &mockMirDatabase, &mockMetricsDatabase)

		offset := 100
		limit := 10
		classIDs := []int{0, 1}
		currentAssetID := "abc"
		annoTypes := []string{"gt", "pred"}
		inCMTypes := []int{0, 1}
		exCMTypes := []int{}
		cks := []string{"a", "b:c"}
		tags := []string{"x", "y:z"}
		expectedCount := int64(0)
		expectedResult := &constants.QueryAssetsResult{
			AssetsDetail:     []constants.MirAssetDetail{{}, {}},
			Offset:           offset,
			Limit:            limit,
			Anchor:           expectedCount,
			TotalAssetsCount: expectedCount,
		}

		find := mtest.CreateCursorResponse(
			1,
			"a.b",
			mtest.FirstBatch,
			bson.D{{Key: "exist", Value: true}, {Key: "ready", Value: true}})
		mt.AddMockResponses(find)
		mt.AddMockResponses(find)
		first := mtest.CreateCursorResponse(
			1,
			"a.b",
			mtest.FirstBatch,
			bson.D{})
		second := mtest.CreateCursorResponse(
			1,
			"a.b",
			mtest.NextBatch,
			bson.D{{Key: "AssetID", Value: "aaa"}})
		killCursors := mtest.CreateCursorResponse(0, "a.b", mtest.NextBatch)
		countCursor := mtest.CreateCursorResponse(
			1,
			"a.b",
			mtest.FirstBatch,
			bson.D{{Key: "n", Value: expectedCount}})
		mt.AddMockResponses(first, second, killCursors) // Find/All require a set of responses.
		mt.AddMockResponses(countCursor)
		mt.AddMockResponses(countCursor)
		result := mongoServer.QueryDatasetAssets(
			&mirRepo,
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
		assert.Equal(t, expectedResult, result)
	})
}

func TestQueryDatasetStatsSuccess(t *testing.T) {
	mt := mtest.New(t, mtest.NewOptions().ClientType(mtest.Mock))
	defer mt.Close()

	mt.Run("success", func(mt *mtest.T) {
		mirRepo := constants.MirRepo{}
		mockCollection := mt.Coll
		mockMirDatabase := MockDatabase{}
		mockMetricsDatabase := MockDatabase{}
		mockMirDatabase.On("Collection", getDatasetMetadataName(), []*options.CollectionOptions(nil)).
			Return(mockCollection)
		mockMirDatabase.On("Collection", "@", []*options.CollectionOptions(nil)).
			Return(mockCollection)

		mockMirContext := protos.MirContext{}
		err := json.Unmarshal([]byte(`{
			"pred_stats":
			{
				"class_ids_cnt":
				{
					"0": 7,
					"1": 8
				}
			},
			"gt_stats":
			{
				"class_ids_cnt":
				{
					"0": 3,
					"2": 3
				}
			}
		}`), &mockMirContext)
		if err != nil {
			panic(err)
		}
		mongoServer := NewMongoServer(context.Background(), &mockMirDatabase, &mockMetricsDatabase)

		classIDs := []int{0, 1}
		expectedCount := int32(1)
		expectedResult := constants.NewQueryDatasetStatsResult()
		expectedResult.TotalAssetsCount = 0
		expectedResult.Gt.ClassIDsCount[0] = 3
		expectedResult.Gt.ClassIDsCount[1] = 0
		expectedResult.Gt.AnnotationsCount = 1
		expectedResult.Gt.NegativeAssetsCount = -1
		expectedResult.Gt.PositiveAssetsCount = 1
		expectedResult.Pred.ClassIDsCount[0] = 7
		expectedResult.Pred.ClassIDsCount[1] = 8
		expectedResult.Pred.PositiveAssetsCount = 1
		expectedResult.Pred.NegativeAssetsCount = -1
		expectedResult.Pred.AnnotationsCount = 1
		expectedResult.QueryContext.RequireAssetsHist = false
		expectedResult.QueryContext.RequireAnnotationsHist = false

		metaResult := expectedResult
		metaResult.Gt.ClassIDsCount[2] = 5
		metaResult.Pred.ClassIDsCount[2] = 6

		find := mtest.CreateCursorResponse(
			1,
			"a.b",
			mtest.FirstBatch,
			bson.D{{Key: "exist", Value: true}, {Key: "ready", Value: true}})
		mt.AddMockResponses(find)
		countCursor := mtest.CreateCursorResponse(
			1,
			"a.b",
			mtest.FirstBatch,
			bson.D{{Key: "n", Value: int64(expectedCount)}})
		mt.AddMockResponses(countCursor)
		first := mtest.CreateCursorResponse(
			1,
			"a.b",
			mtest.FirstBatch,
			bson.D{{Key: "count", Value: expectedCount}, {Key: "sum", Value: expectedCount}})
		second := mtest.CreateCursorResponse(
			1,
			"a.b",
			mtest.NextBatch,
			bson.D{{Key: "AssetID", Value: "aaa"}})
		killCursors := mtest.CreateCursorResponse(0, "a.b", mtest.NextBatch)
		mt.AddMockResponses(first, second, killCursors)
		mt.AddMockResponses(first, second, killCursors)
		result := mongoServer.QueryDatasetStats(&mirRepo, classIDs, false, false, metaResult)
		assert.Equal(t, expectedResult, result)
	})
}

func TestLoadAssetsDetail(t *testing.T) {
	mirRepo := constants.MirRepo{}
	attributes := map[string]*protos.MetadataAttributes{
		"a": {},
		"b": {},
		"c": {},
	}
	mirMetadatas := &protos.MirMetadatas{Attributes: attributes}
	mirAnnotations := &protos.MirAnnotations{
		GroundTruth: &protos.SingleTaskAnnotations{
			ImageAnnotations: map[string]*protos.SingleImageAnnotations{
				"a": {Boxes: []*protos.ObjectAnnotation{{ClassId: 1}}},
			},
		},
		Prediction: &protos.SingleTaskAnnotations{
			ImageAnnotations: map[string]*protos.SingleImageAnnotations{
				"a": {Boxes: []*protos.ObjectAnnotation{{ClassId: 1}}},
			},
		},
		ImageCks: map[string]*protos.SingleImageCks{"a": {Cks: map[string]string{"abc": "1"}}},
	}

	expectedAssetsDetail := []constants.MirAssetDetail{}
	err := json.Unmarshal([]byte(`[
		{
			"asset_id": "a",
			"metadata":
			{
				"asset_type": 0,
				"byte_size": 0,
				"height": 0,
				"image_channels": 0,
				"timestamp": null,
				"tvt_type": 0,
				"width": 0,
				"origin_filename": ""
			},
			"class_ids":
			[
				1
			],
			"gt":
			[
				{
					"anno_quality": 0,
					"box": null,
					"class_id": 1,
					"class_name": "",
					"cm": 0,
					"det_link_id": 0,
					"index": 0,
					"polygon": [],
					"score": 0,
					"tags": {}
				}
			],
			"pred":
			[
				{
					"anno_quality": 0,
					"box": null,
					"class_id": 1,
					"polygon": [],
					"class_name": "",
					"cm": 0,
					"det_link_id": 0,
					"index": 0,
					"score": 0,
					"tags": {}
				}
			],
			"cks":
			{
				"abc": "1"
			},
			"image_quality": 0
		},
		{
			"asset_id": "b",
			"metadata":
			{
				"asset_type": 0,
				"byte_size": 0,
				"height": 0,
				"image_channels": 0,
				"timestamp": null,
				"tvt_type": 0,
				"width": 0,
				"origin_filename": ""
			},
			"class_ids":
			[],
			"gt":
			[],
			"pred":
			[],
			"cks":
			{},
			"image_quality": -1
		},
		{
			"asset_id": "c",
			"metadata":
			{
				"asset_type": 0,
				"byte_size": 0,
				"height": 0,
				"image_channels": 0,
				"timestamp": null,
				"tvt_type": 0,
				"width": 0,
				"origin_filename": ""
			},
			"class_ids":
			[],
			"gt":
			[],
			"pred":
			[],
			"cks":
			{},
			"image_quality": -1
		}
	]`), &expectedAssetsDetail)
	if err != nil {
		panic(err)
	}

	mt := mtest.New(t, mtest.NewOptions().ClientType(mtest.Mock))
	defer mt.Close()
	mt.Run("success", func(mt *mtest.T) {
		mockCollection := mt.Coll
		mockMirDatabase := MockDatabase{}
		mockMetricsDatabase := MockDatabase{}
		mockMirDatabase.On("Collection", "@", []*options.CollectionOptions(nil)).
			Return(mockCollection)
		mockMirDatabase.On("Collection", getDatasetMetadataName(), []*options.CollectionOptions(nil)).
			Return(mockCollection)

		find := mtest.CreateCursorResponse(
			1,
			"a.b",
			mtest.FirstBatch,
			bson.D{{Key: "exist", Value: false}, {Key: "ready", Value: false}})
		mt.AddMockResponses(find)
		mt.AddMockResponses(
			mtest.CreateSuccessResponse(),
			mtest.CreateSuccessResponse(),
			mtest.CreateSuccessResponse(),
			mtest.CreateSuccessResponse(),
			mtest.CreateSuccessResponse(),
			mtest.CreateSuccessResponse(),
			mtest.CreateSuccessResponse(),
			mtest.CreateSuccessResponse(),
		)
		mongoServer := NewMongoServer(context.Background(), &mockMirDatabase, &mockMetricsDatabase)
		mongoServer.IndexDatasetData(&mirRepo, mirMetadatas, mirAnnotations)
	})
}
