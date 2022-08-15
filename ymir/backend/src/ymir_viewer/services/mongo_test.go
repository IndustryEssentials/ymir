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
		mockDatabase := MockDatabase{}
		mockDatabase.On("Collection", getDatasetExistenceName(), []*options.CollectionOptions(nil)).
			Return(mockCollection)

		mongoServer := NewMongoServer(context.Background(), &mockDatabase)
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
		mockDatabase := MockDatabase{}
		mockDatabase.On("Collection", getDatasetExistenceName(), []*options.CollectionOptions(nil)).
			Return(mockCollection)

		mongoServer := NewMongoServer(context.Background(), &mockDatabase)
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
		mockDatabase := MockDatabase{}
		mockDatabase.On("Collection", getDatasetExistenceName(), []*options.CollectionOptions(nil)).
			Return(mockCollection)
		mockDatabase.On("Collection", "@", []*options.CollectionOptions(nil)).
			Return(mockCollection)

		mongoServer := NewMongoServer(context.Background(), &mockDatabase)
		mt.AddMockResponses(mtest.CreateSuccessResponse(bson.E{Key: "n", Value: 0}))
		existence := mongoServer.CheckDatasetExistence(&mirRepo)
		assert.Equal(t, existence, false)

		mt.AddMockResponses(mtest.CreateSuccessResponse(bson.E{Key: "n", Value: 1}))

		find := mtest.CreateCursorResponse(
			1,
			"a.b",
			mtest.FirstBatch,
			bson.D{{Key: "ready", Value: true}})
		getMore := mtest.CreateCursorResponse(
			1,
			"a.b",
			mtest.NextBatch,
			bson.D{})
		killCursors := mtest.CreateCursorResponse(
			0,
			"a.b",
			mtest.NextBatch,
			bson.D{})
		mt.AddMockResponses(find, getMore, killCursors)
		existence = mongoServer.CheckDatasetExistence(&mirRepo)
		assert.Equal(t, existence, true)
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
		mockDatabase := MockDatabase{}
		mockDatabase.On("Collection", getDatasetExistenceName(), []*options.CollectionOptions(nil)).
			Return(mockCollection)

		mongoServer := NewMongoServer(context.Background(), &mockDatabase)
		mongoServer.CheckDatasetExistence(&mirRepo)
	})
}

func TestCheckDatasetExistenceFailure1(t *testing.T) {
	mt := mtest.New(t, mtest.NewOptions().ClientType(mtest.Mock))
	defer mt.Close()

	mt.Run("success", func(mt *mtest.T) {
		mirRepo := constants.MirRepo{}
		mockCollection := mt.Coll
		mockDatabase := MockDatabase{}
		mockDatabase.On("Collection", getDatasetExistenceName(), []*options.CollectionOptions(nil)).
			Return(mockCollection)
		mockDatabase.On("Collection", "@", []*options.CollectionOptions(nil)).
			Return(mockCollection)

		mongoServer := NewMongoServer(context.Background(), &mockDatabase)

		mt.AddMockResponses(mtest.CreateSuccessResponse(bson.E{Key: "n", Value: 1}))
		existence := mongoServer.CheckDatasetExistence(&mirRepo)
		assert.Equal(t, existence, false)
	})
}

func TestIndexDatasetDataSuccess(t *testing.T) {
	mt := mtest.New(t, mtest.NewOptions().ClientType(mtest.Mock))
	defer mt.Close()

	mt.Run("success", func(mt *mtest.T) {
		mirRepo := constants.MirRepo{}
		mockAssetsDetail := []constants.MirAssetDetail{{AssetID: "a"}}
		mockCollection := mt.Coll
		mockDatabase := MockDatabase{}
		mockDatabase.On("Collection", getDatasetExistenceName(), []*options.CollectionOptions(nil)).
			Return(mockCollection)
		mockDatabase.On("Collection", "@", []*options.CollectionOptions(nil)).
			Return(mockCollection)

		mongoServer := NewMongoServer(context.Background(), &mockDatabase)
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
		mockDatabase := MockDatabase{}
		mockDatabase.On("Collection", "@", []*options.CollectionOptions(nil)).
			Return(mockCollection)

		mongoServer := NewMongoServer(context.Background(), &mockDatabase)

		queryField := "abc"
		expectedCount := int64(1)
		classIds := []int{0, 1}
		countCursor := mtest.CreateCursorResponse(
			1,
			"a.b",
			mtest.FirstBatch,
			bson.D{{Key: "n", Value: expectedCount}})
		mt.AddMockResponses(countCursor)
		count := mongoServer.countDatasetAssetsInClass(collection, queryField, classIds)
		assert.Equal(t, expectedCount, count)
	})
}

func TestQueryAssetsSuccess(t *testing.T) {
	mt := mtest.New(t, mtest.NewOptions().ClientType(mtest.Mock))
	defer mt.Close()

	mt.Run("success", func(mt *mtest.T) {
		mirRepo := constants.MirRepo{}
		mockCollection := mt.Coll
		mockDatabase := MockDatabase{}
		mockDatabase.On("Collection", "@", []*options.CollectionOptions(nil)).
			Return(mockCollection)

		mongoServer := NewMongoServer(context.Background(), &mockDatabase)

		offset := 100
		limit := 10
		classIDs := []int{0, 1}
		currentAssetID := "abc"
		cmTypes := []int32{0, 1}
		cks := []string{"a", "b:c"}
		tags := []string{"x", "y:z"}
		expectedCount := int64(0)
		expectedResult := constants.QueryAssetsResult{
			AssetsDetail:     []constants.MirAssetDetail{},
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
		result := mongoServer.QueryDatasetAssets(&mirRepo, offset, limit, classIDs, currentAssetID, cmTypes, cks, tags)
		assert.Equal(t, expectedResult, result)
	})
}

func TestQueryDatasetStatsSuccess(t *testing.T) {
	mt := mtest.New(t, mtest.NewOptions().ClientType(mtest.Mock))
	defer mt.Close()

	mt.Run("success", func(mt *mtest.T) {
		mirRepo := constants.MirRepo{}
		mockCollection := mt.Coll
		mockDatabase := MockDatabase{}
		mockDatabase.On("Collection", "@", []*options.CollectionOptions(nil)).
			Return(mockCollection)

		mongoServer := NewMongoServer(context.Background(), &mockDatabase)

		classIDs := []int{0, 1}
		expectedCount := int64(1)
		expectedResult := constants.NewQueryDatasetStatsResult()
		expectedResult.TotalAssetsCount = 1
		expectedResult.Gt.ClassIdsCount[0] = 1
		expectedResult.Gt.ClassIdsCount[1] = 1
		expectedResult.Gt.PositiveImagesCount = 1
		expectedResult.Pred.ClassIdsCount[0] = 1
		expectedResult.Pred.ClassIdsCount[1] = 1
		expectedResult.Pred.PositiveImagesCount = 1

		countCursor := mtest.CreateCursorResponse(
			1,
			"a.b",
			mtest.FirstBatch,
			bson.D{{Key: "n", Value: expectedCount}})
		mt.AddMockResponses(countCursor, countCursor, countCursor, countCursor, countCursor, countCursor, countCursor)
		result := mongoServer.QueryDatasetStats(&mirRepo, classIDs)
		assert.Equal(t, expectedResult, result)
	})
}

func TestQueryDatasetDupSuccess(t *testing.T) {
	mt := mtest.New(t, mtest.NewOptions().ClientType(mtest.Mock))
	defer mt.Close()

	mt.Run("success", func(mt *mtest.T) {
		BranchID0 := "a"
		BranchID1 := "b"
		mirRepo0 := constants.MirRepo{BranchID: BranchID0}
		mirRepo1 := constants.MirRepo{BranchID: BranchID1}
		mockCollection := mt.Coll
		mockDatabase := MockDatabase{}
		mockDatabase.On("Collection", BranchID0+"@", []*options.CollectionOptions(nil)).
			Return(mockCollection)
		mockDatabase.On("Collection", BranchID1+"@", []*options.CollectionOptions(nil)).
			Return(mockCollection)

		mongoServer := NewMongoServer(context.Background(), &mockDatabase)

		expectedCount0 := int64(0)
		expectedCount1 := int64(1)
		countCursor0 := mtest.CreateCursorResponse(
			1,
			"a.b",
			mtest.FirstBatch,
			bson.D{{Key: "n", Value: expectedCount1}})
		countCursor1 := mtest.CreateCursorResponse(
			1,
			"a.b",
			mtest.FirstBatch,
			bson.D{{Key: "n", Value: expectedCount0}})
		mt.AddMockResponses(countCursor0, countCursor1)

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
		mt.AddMockResponses(first, second, killCursors) // Aggregate/All require a set of responses.

		resultData := mongoServer.QueryDatasetDup(&mirRepo0, &mirRepo1)
		assert.Equal(t, 2, resultData.Duplication)
		assert.Equal(t, expectedCount1, resultData.TotalCount["a"])
		assert.Equal(t, expectedCount0, resultData.TotalCount["b"])
	})
}
