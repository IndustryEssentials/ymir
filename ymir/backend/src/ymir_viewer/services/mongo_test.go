package services

import (
	"context"
	"testing"

	"github.com/IndustryEssentials/ymir-viewer/common/constants"
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

func getDatasetExistenceName() string {
	return "__collection_existence__@"
}

func TestSetDatasetExistenceSuccess(t *testing.T) {
	mt := mtest.New(t, mtest.NewOptions().ClientType(mtest.Mock))
	defer mt.Close()

	mt.Run("success", func(mt *mtest.T) {
		mockCollection := mt.Coll
		mockMirDatabase := MockDatabase{}
		mockMetricsDatabase := MockDatabase{}
		mockMirDatabase.On("Collection", getDatasetExistenceName(), []*options.CollectionOptions(nil)).
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
		mockMirDatabase.On("Collection", getDatasetExistenceName(), []*options.CollectionOptions(nil)).
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
		mockMirDatabase.On("Collection", getDatasetExistenceName(), []*options.CollectionOptions(nil)).
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
		existence, ready := mongoServer.CheckDatasetExistenceReady(&mirRepo)
		assert.Equal(t, existence, true)
		assert.Equal(t, ready, true)
	})
}

func TestCheckDatasetExistenceFailure0(t *testing.T) {
	mt := mtest.New(t, mtest.NewOptions().ClientType(mtest.Mock))
	defer mt.Close()

	mt.Run("success", func(mt *mtest.T) {
		defer func() {
			if r := recover(); r == nil {
				t.Errorf("The code did not panic")
			}
		}()

		mirRepo := constants.MirRepo{}
		mockCollection := mt.Coll
		mockMirDatabase := MockDatabase{}
		mockMetricsDatabase := MockDatabase{}
		mockMirDatabase.On("Collection", getDatasetExistenceName(), []*options.CollectionOptions(nil)).
			Return(mockCollection)

		mongoServer := NewMongoServer(context.Background(), &mockMirDatabase, &mockMetricsDatabase)
		mongoServer.CheckDatasetExistenceReady(&mirRepo)
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
		mockMirDatabase.On("Collection", getDatasetExistenceName(), []*options.CollectionOptions(nil)).
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
		existence, ready := mongoServer.CheckDatasetExistenceReady(&mirRepo)
		assert.Equal(t, existence, false)
		assert.Equal(t, ready, false)
	})
}

func TestIndexDatasetDataSuccess(t *testing.T) {
	mt := mtest.New(t, mtest.NewOptions().ClientType(mtest.Mock))
	defer mt.Close()

	mt.Run("success", func(mt *mtest.T) {
		mirRepo := constants.MirRepo{}
		mockAssetsDetail := []constants.MirAssetDetail{{AssetID: "a"}}
		mockCollection := mt.Coll
		mockMirDatabase := MockDatabase{}
		mockMetricsDatabase := MockDatabase{}
		mockMirDatabase.On("Collection", getDatasetExistenceName(), []*options.CollectionOptions(nil)).
			Return(mockCollection)
		mockMirDatabase.On("Collection", "@", []*options.CollectionOptions(nil)).
			Return(mockCollection)

		mongoServer := NewMongoServer(context.Background(), &mockMirDatabase, &mockMetricsDatabase)
		mongoServer.IndexDatasetData(&mirRepo, []interface{}{})

		mt.AddMockResponses(
			mtest.CreateSuccessResponse(),
			mtest.CreateSuccessResponse(),
			mtest.CreateSuccessResponse(),
			mtest.CreateSuccessResponse(),
		)
		mongoServer.IndexDatasetData(&mirRepo, []interface{}{mockAssetsDetail[0]})
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
		mockMirDatabase.On("Collection", "@", []*options.CollectionOptions(nil)).
			Return(mockCollection)

		mongoServer := NewMongoServer(context.Background(), &mockMirDatabase, &mockMetricsDatabase)

		offset := 100
		limit := 10
		classIDs := []int{0, 1}
		currentAssetID := "abc"
		annoTypes := []string{"gt", "pred"}
		cmTypes := []int{0, 1}
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
			cmTypes,
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
		mockMirDatabase.On("Collection", "@", []*options.CollectionOptions(nil)).
			Return(mockCollection)

		mongoServer := NewMongoServer(context.Background(), &mockMirDatabase, &mockMetricsDatabase)

		classIDs := []int{0, 1}
		expectedCount := int32(1)
		expectedResult := constants.NewQueryDatasetStatsResult()
		expectedResult.TotalAssetsCount = 1
		expectedResult.Gt.ClassIDsCount[0] = 1
		expectedResult.Gt.ClassIDsCount[1] = 1
		expectedResult.Gt.AnnotationsCount = 1
		expectedResult.Gt.PositiveAssetsCount = 1
		expectedResult.Pred.ClassIDsCount[0] = 1
		expectedResult.Pred.ClassIDsCount[1] = 1
		expectedResult.Pred.PositiveAssetsCount = 1
		expectedResult.Pred.AnnotationsCount = 1
		expectedResult.QueryContext.RequireAssetsHist = false
		expectedResult.QueryContext.RequireAnnotationsHist = false

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
		mt.AddMockResponses(first, second, killCursors)
		mt.AddMockResponses(first, second, killCursors)
		mt.AddMockResponses(first, second, killCursors)
		mt.AddMockResponses(first, second, killCursors)
		result := mongoServer.QueryDatasetStats(&mirRepo, classIDs, false, false)
		assert.Equal(t, expectedResult, result)
	})
}
