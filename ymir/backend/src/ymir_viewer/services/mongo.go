package services

import (
	"context"
	"fmt"
	"log"
	"strings"
	"time"

	"github.com/IndustryEssentials/ymir-viewer/common/constants"
	"github.com/IndustryEssentials/ymir-viewer/tools"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"go.mongodb.org/mongo-driver/x/bsonx"
)

type MongoServer struct {
	Clt           *mongo.Client
	Ctx           context.Context
	dbName        string
	existenceName string
}

func NewMongoServer(uri string) *MongoServer {
	mongoCtx := context.Background()
	mongoClient, err := mongo.Connect(mongoCtx, options.Client().ApplyURI(uri))
	if err != nil {
		panic(err)
	}

	defaultDbName := "YMIR"
	// Clear cached data.
	err = mongoClient.Database(defaultDbName).Drop(mongoCtx)
	if err != nil {
		panic(err)
	}

	return &MongoServer{
		Clt:           mongoClient,
		Ctx:           mongoCtx,
		dbName:        defaultDbName,
		existenceName: "__collection_existence__",
	}
}

func (s *MongoServer) getRepoCollection(mirRepo constants.MirRepo) (*mongo.Collection, string) {
	_, mirRev := mirRepo.BuildRepoID()
	return s.Clt.Database(s.dbName).Collection(mirRev), mirRev
}

func (s *MongoServer) setExistence(collectionName string, ready bool, insert bool) {
	collection := s.Clt.Database(s.dbName).Collection(s.existenceName)
	if insert {
		record := bson.M{"_id": collectionName, "ready": ready, "exist": true}
		_, err := collection.InsertOne(s.Ctx, record)
		if err != nil {
			panic(err)
		}
	} else {
		filter := bson.M{"_id": collectionName}
		update := bson.M{"$set": bson.M{"ready": ready}}
		_, err := collection.UpdateOne(s.Ctx, filter, update)
		if err != nil {
			panic(err)
		}
	}
}

func (s *MongoServer) checkExistence(mirRepo constants.MirRepo) bool {
	// Step 1: check collection exist.
	collectionData, collectionName := s.getRepoCollection(mirRepo)
	count, err := collectionData.EstimatedDocumentCount(s.Ctx)
	if err != nil {
		panic(err)
	}
	if count < 1 {
		return false
	}

	// Step 2: check collection ready.
	collectionExistence := s.Clt.Database(s.dbName).Collection(s.existenceName)
	filter := bson.M{"_id": collectionName}
	data := make(map[string]interface{})
	err = collectionExistence.FindOne(s.Ctx, filter).Decode(data)
	if err != nil {
		log.Printf("checkExistence Error: %s\n", err)
		return false
	}
	return data["ready"].(bool)
}

func (s *MongoServer) IndexMongoData(mirRepo constants.MirRepo, newData []interface{}) {
	defer tools.TimeTrack(time.Now())

	if len(newData) <= 0 {
		return
	}

	collection, collectionName := s.getRepoCollection(mirRepo)
	s.setExistence(collectionName, false, true)

	_, err := collection.InsertMany(s.Ctx, newData)
	if err != nil {
		panic(err)
	}

	defer tools.TimeTrack(time.Now())
	index := []mongo.IndexModel{
		{
			Keys: bson.M{"asset_id": bsonx.Int32(1)}, Options: options.Index(),
		},
		{
			Keys: bson.M{"cks": bsonx.Int32(1)}, Options: options.Index(),
		},
		{
			Keys: bson.M{"class_ids": bsonx.Int32(1)}, Options: options.Index(),
		},
		{
			Keys: bson.M{"gt.class_id": bsonx.Int32(1)}, Options: options.Index(),
		},
		{
			Keys: bson.M{"pred.class_id": bsonx.Int32(1)}, Options: options.Index(),
		},
		{
			Keys: bson.M{"gt.cm": bsonx.Int32(1)}, Options: options.Index(),
		},
		{
			Keys: bson.M{"pred.cm": bsonx.Int32(1)}, Options: options.Index(),
		},
		{
			Keys: bson.M{"gt.tags": bsonx.Int32(1)}, Options: options.Index(),
		},
		{
			Keys: bson.M{"pred.tags": bsonx.Int32(1)}, Options: options.Index(),
		},
	}

	opts := options.CreateIndexes().SetMaxTime(60 * time.Second)
	_, err = collection.Indexes().CreateMany(s.Ctx, index, opts)
	if err != nil {
		panic(err)
	}

	s.setExistence(collectionName, true, false)
}

func (s *MongoServer) countAssetsInClass(collection *mongo.Collection, queryField string, classIds []int) int64 {
	filterQuery := bson.M{}
	if len(classIds) > 0 {
		if len(queryField) < 1 {
			panic("classIds is set, but get empty queryField in countAssetsInClass.")
		} else {
			filterQuery[queryField] = bson.M{"$in": classIds}
		}
	}

	count, err := collection.CountDocuments(s.Ctx, filterQuery, &options.CountOptions{})
	if err != nil {
		panic(err)
	}
	return count
}

func (s *MongoServer) QueryAssets(
	mirRepo constants.MirRepo,
	offset int,
	limit int,
	classIds []int,
	currentAssetID string,
	cmTypes []int32,
	cks []string,
	tags []string,
) constants.QueryAssetsResult {
	defer tools.TimeTrack(time.Now())

	log.Printf(
		"Query offset: %d, limit: %d, classIds: %v, currentId: %s, cmTypes: %v cks: %v tags: %v\n",
		offset,
		limit,
		classIds,
		currentAssetID,
		cmTypes,
		cks,
		tags,
	)
	collection, _ := s.getRepoCollection(mirRepo)

	filterQuery := bson.M{}
	// class id in either field counts.
	if len(classIds) > 0 {
		filterQuery["class_ids"] = bson.M{"$in": classIds}
	}
	if len(currentAssetID) > 0 {
		filterQuery["asset_id"] = bson.M{"$gte": currentAssetID}
	}
	if len(cmTypes) > 0 {
		filterQuery["$or"] = bson.A{
			bson.M{"gt.cm": bson.M{"$in": cmTypes}},
			bson.M{"pred.cm": bson.M{"$in": cmTypes}},
		}
	}
	// ck format "xxx" "xxx:" "xxx:yyy"
	if len(cks) > 0 {
		for _, ck := range cks {
			ckStrs := strings.Split(ck, ":")
			if len(ckStrs) > 2 || len(ckStrs) < 1 || len(ckStrs[0]) == 0 {
				panic(fmt.Sprintf("invalid ck: %s", ck))
			}
			if len(ckStrs) == 1 || len(ckStrs[1]) == 0 {
				// case "xxx:" or "xxx"
				filterQuery["cks."+ckStrs[0]] = bson.M{"$exists": true}
			} else {
				// case "xxx:yyy"
				filterQuery["cks."+ckStrs[0]] = ckStrs[1]
			}
		}
	}
	// tag format "xxx" "xxx:" "xxx:yyy"
	if len(tags) > 0 {
		for _, tag := range tags {
			tagStrs := strings.Split(tag, ":")
			if len(tagStrs) > 2 || len(tagStrs) < 1 || len(tagStrs[0]) == 0 {
				panic(fmt.Sprintf("invalid tag: %s", tag))
			}
			if len(tagStrs) == 1 || len(tagStrs[1]) == 0 {
				// case "xxx:" or "xxx"
				filterQuery["$or"] = bson.A{
					bson.M{"gt.tags." + tagStrs[0]: bson.M{"$exists": true}},
					bson.M{"pred.tags." + tagStrs[0]: bson.M{"$exists": true}},
				}
			} else {
				// case "xxx:yyy"
				filterQuery["$or"] = bson.A{
					bson.M{"gt.tags." + tagStrs[0]: tagStrs[1]},
					bson.M{"pred.tags." + tagStrs[0]: tagStrs[1]},
				}
			}
		}
	}

	pageOptions := options.Find().SetSort(bson.M{"asset_id": 1}).SetSkip(int64(offset)).SetLimit(int64(limit))
	queryCursor, err := collection.Find(s.Ctx, filterQuery, pageOptions)
	if err != nil {
		panic(err)
	}
	queryData := []constants.MirAssetDetail{}
	if err = queryCursor.All(s.Ctx, &queryData); err != nil {
		panic(err)
	}

	remainingAssetsCount, err := collection.CountDocuments(s.Ctx, filterQuery, &options.CountOptions{})
	if err != nil {
		panic(err)
	}
	// Delete anchor query, so as to calculate count of documents.
	delete(filterQuery, "asset_id")
	totalAssetsCount, err := collection.CountDocuments(s.Ctx, filterQuery, &options.CountOptions{})
	if err != nil {
		panic(err)
	}
	anchor := totalAssetsCount - remainingAssetsCount
	log.Printf("filterQuery: %+v totalAssetsCount: %d anchor: %d\n", filterQuery, totalAssetsCount, anchor)

	return constants.QueryAssetsResult{
		AssetsDetail:     queryData,
		Offset:           offset,
		Limit:            limit,
		Anchor:           anchor,
		TotalAssetsCount: totalAssetsCount,
	}
}

func (s *MongoServer) QueryDatasetStats(mirRepo constants.MirRepo, classIDs []int) constants.QueryDatasetStatsResult {
	collection, _ := s.getRepoCollection(mirRepo)

	totalAssetsCount := s.countAssetsInClass(collection, "", []int{})
	queryData := constants.NewQueryDatasetStatsResult()
	queryData.TotalAssetsCount = totalAssetsCount
	for _, classID := range classIDs {
		queryData.Gt.ClassIdsCount[classID] = s.countAssetsInClass(collection, "gt.class_id", []int{classID})
		queryData.Pred.ClassIdsCount[classID] = s.countAssetsInClass(collection, "pred.class_id", []int{classID})
	}
	queryData.Gt.PositiveImagesCount = s.countAssetsInClass(collection, "gt.class_id", classIDs)
	queryData.Gt.NegativeImagesCount = totalAssetsCount - queryData.Gt.PositiveImagesCount
	queryData.Pred.PositiveImagesCount = s.countAssetsInClass(collection, "pred.class_id", classIDs)
	queryData.Pred.NegativeImagesCount = totalAssetsCount - queryData.Pred.PositiveImagesCount
	return queryData
}

func (s *MongoServer) QueryDatasetDup(mirRepo0 constants.MirRepo, mirRepo1 constants.MirRepo) (int, int64, int64) {
	defer tools.TimeTrack(time.Now())

	collection0, collectionName0 := s.getRepoCollection(mirRepo0)
	totalCount0 := s.countAssetsInClass(collection0, "", []int{})

	collection1, collectionName1 := s.getRepoCollection(mirRepo1)
	totalCount1 := s.countAssetsInClass(collection1, "", []int{})

	// No-SQL Aggregate Trick: always set smaller dataset to be joined.
	collectionJoined := collection0
	collectionNameToJoin := collectionName1
	if totalCount0 > totalCount1 {
		collectionJoined = collection1
		collectionNameToJoin = collectionName0
	}

	lookupStage := bson.D{
		bson.E{
			Key: "$lookup",
			Value: bson.D{
				bson.E{Key: "from", Value: collectionNameToJoin},
				bson.E{Key: "localField", Value: "asset_id"},
				bson.E{Key: "foreignField", Value: "asset_id"},
				bson.E{Key: "as", Value: "joinAssets"},
			},
		},
	}
	showLoadedCursor, err := collectionJoined.Aggregate(s.Ctx, mongo.Pipeline{lookupStage})
	if err != nil {
		panic(err)
	}
	var showsLoaded []bson.M
	if err = showLoadedCursor.All(s.Ctx, &showsLoaded); err != nil {
		panic(err)
	}
	return len(showsLoaded), totalCount0, totalCount1
}
