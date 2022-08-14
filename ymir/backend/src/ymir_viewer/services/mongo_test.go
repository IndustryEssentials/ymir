package services

import (
	"context"
	"testing"

	"github.com/IndustryEssentials/ymir-viewer/common/constants"
	"github.com/stretchr/testify/assert"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/integration/mtest"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type MockDatabase struct {
	collection *mongo.Collection
}

func (m *MockDatabase) Drop(ctx context.Context) error {
	return nil
}

func (m *MockDatabase) Collection(name string, opts ...*options.CollectionOptions) *mongo.Collection {
	return m.collection
}

func TestSetExistenceSuccess(t *testing.T) {
	mt := mtest.New(t, mtest.NewOptions().ClientType(mtest.Mock))
	defer mt.Close()

	mt.Run("success", func(mt *mtest.T) {
		mockDatabase := MockDatabase{collection: mt.Coll}
		mongoServer := NewMongoServer(context.Background(), &mockDatabase)
		mt.AddMockResponses(mtest.CreateSuccessResponse())
		mongoServer.setExistence("", true, false)
	})
}

func TestSetExistenceFailure(t *testing.T) {
	mt := mtest.New(t, mtest.NewOptions().ClientType(mtest.Mock))
	defer mt.Close()

	mt.Run("success", func(mt *mtest.T) {
		defer func() {
			if r := recover(); r == nil {
				t.Errorf("The code did not panic")
			}
		}()
		mockDatabase := MockDatabase{collection: mt.Coll}
		mongoServer := NewMongoServer(context.Background(), &mockDatabase)
		mt.AddMockResponses(mtest.CreateWriteErrorsResponse(mtest.WriteError{}))
		mongoServer.setExistence("", true, true)
	})
}

func TestCheckExistenceSuccess(t *testing.T) {
	mt := mtest.New(t, mtest.NewOptions().ClientType(mtest.Mock))
	defer mt.Close()

	mt.Run("success", func(mt *mtest.T) {
		mirRepo := constants.MirRepo{}

		mockDatabase := MockDatabase{collection: mt.Coll}
		mongoServer := NewMongoServer(context.Background(), &mockDatabase)
		mt.AddMockResponses(mtest.CreateSuccessResponse(bson.E{Key: "n", Value: 0}))
		existence := mongoServer.checkExistence(&mirRepo)
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
		existence = mongoServer.checkExistence(&mirRepo)
		assert.Equal(t, existence, true)
	})
}

func TestCheckExistenceFailure0(t *testing.T) {
	mt := mtest.New(t, mtest.NewOptions().ClientType(mtest.Mock))
	defer mt.Close()

	mt.Run("success", func(mt *mtest.T) {
		defer func() {
			if r := recover(); r == nil {
				t.Errorf("The code did not panic")
			}
		}()

		mirRepo := constants.MirRepo{}

		mockDatabase := MockDatabase{collection: mt.Coll}
		mongoServer := NewMongoServer(context.Background(), &mockDatabase)
		mongoServer.checkExistence(&mirRepo)
	})
}

func TestCheckExistenceFailure1(t *testing.T) {
	mt := mtest.New(t, mtest.NewOptions().ClientType(mtest.Mock))
	defer mt.Close()

	mt.Run("success", func(mt *mtest.T) {
		mirRepo := constants.MirRepo{}

		mockDatabase := MockDatabase{collection: mt.Coll}
		mongoServer := NewMongoServer(context.Background(), &mockDatabase)

		mt.AddMockResponses(mtest.CreateSuccessResponse(bson.E{Key: "n", Value: 1}))
		existence := mongoServer.checkExistence(&mirRepo)
		assert.Equal(t, existence, false)
	})
}

func TestIndexCollectionDataSuccess(t *testing.T) {
	mt := mtest.New(t, mtest.NewOptions().ClientType(mtest.Mock))
	defer mt.Close()

	mt.Run("success", func(mt *mtest.T) {
		mirRepo := constants.MirRepo{}
		mockAssetsDetail := []constants.MirAssetDetail{{AssetID: "a"}}

		mockDatabase := MockDatabase{collection: mt.Coll}
		mongoServer := NewMongoServer(context.Background(), &mockDatabase)
		mongoServer.IndexCollectionData(&mirRepo, []interface{}{})

		mt.AddMockResponses(
			mtest.CreateSuccessResponse(),
			mtest.CreateSuccessResponse(),
			mtest.CreateSuccessResponse(),
			mtest.CreateSuccessResponse(),
		)
		mongoServer.IndexCollectionData(&mirRepo, []interface{}{mockAssetsDetail[0]})
	})
}

func TestCountAssetsInClassSuccess(t *testing.T) {
	mt := mtest.New(t, mtest.NewOptions().ClientType(mtest.Mock))
	defer mt.Close()

	mt.Run("success", func(mt *mtest.T) {
		collection := mt.Coll
		mockDatabase := MockDatabase{collection: collection}
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
		count := mongoServer.countAssetsInClass(collection, queryField, classIds)
		assert.Equal(t, expectedCount, count)
	})
}

func TestQueryAssetsSuccess(t *testing.T) {
	mt := mtest.New(t, mtest.NewOptions().ClientType(mtest.Mock))
	defer mt.Close()

	mt.Run("success", func(mt *mtest.T) {
		mirRepo := constants.MirRepo{}
		mockDatabase := MockDatabase{collection: mt.Coll}
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
		result := mongoServer.QueryAssets(&mirRepo, offset, limit, classIDs, currentAssetID, cmTypes, cks, tags)
		assert.Equal(t, expectedResult, result)
	})
}

func TestQueryDatasetStatsSuccess(t *testing.T) {
	mt := mtest.New(t, mtest.NewOptions().ClientType(mtest.Mock))
	defer mt.Close()

	mt.Run("success", func(mt *mtest.T) {
		mirRepo := constants.MirRepo{}
		mockDatabase := MockDatabase{collection: mt.Coll}
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
		mirRepo := constants.MirRepo{}
		mockDatabase := MockDatabase{collection: mt.Coll}
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

		dup, count0, count1 := mongoServer.QueryDatasetDup(&mirRepo, &mirRepo)
		assert.Equal(t, 2, dup)
		assert.Equal(t, expectedCount1, count0)
		assert.Equal(t, expectedCount0, count1)
	})
}
