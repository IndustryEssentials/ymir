package service

import (
	"context"
	"log"
	"time"

	"github.com/IndustryEssentials/ymir-viewer/common/constant"
	"github.com/IndustryEssentials/ymir-viewer/tools"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"go.mongodb.org/mongo-driver/x/bsonx"
	"gopkg.in/mgo.v2/bson"
)

type MongoServer struct {
	Clt *mongo.Client
	Ctx context.Context
	dbName string
	existenceName string
}

func (s *MongoServer) getRepoCollection(mirRepo constant.MirRepo) (*mongo.Collection, string){
	_, mirRev := mirRepo.BuildRepoId()
	return s.Clt.Database(s.dbName).Collection(mirRev), mirRev
}

func (s *MongoServer) setExistence(collectionName string, ready bool, insert bool) {
	collection := s.Clt.Database(s.dbName).Collection(s.existenceName)
	if insert {
		record := bson.M{"_id": collectionName, "ready": ready, "exist": true}
		collection.InsertOne(s.Ctx, record)
	} else {
		filter := bson.M{"_id": collectionName}
		update := bson.M{"$set": bson.M{"ready": ready}}
		collection.UpdateOne(s.Ctx, filter, update)
	}
}

func (s *MongoServer) checkExistence(mirRepo constant.MirRepo) bool{
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

func (s *MongoServer) IndexMongoData(mirRepo constant.MirRepo, newData []interface{}) {
	defer tools.TimeTrack(time.Now())

	collection, collectionName := s.getRepoCollection(mirRepo)
	s.setExistence(collectionName, false, true)

	_, err := collection.InsertMany(s.Ctx, newData)
	if err != nil {
		panic(err)
	}

	defer tools.TimeTrack(time.Now())
	index := []mongo.IndexModel{
        {
			Keys: bsonx.Doc{{Key: "assetid", Value: bsonx.Int32(1)}},
        },
        {
			Keys: bsonx.Doc{{Key: "predclassids", Value: bsonx.Int32(1)}},
        },
        {
			Keys: bsonx.Doc{{Key: "gtclassids", Value: bsonx.Int32(1)}},
        },
    }

    opts := options.CreateIndexes().SetMaxTime(10 * time.Second)
    _, err = collection.Indexes().CreateMany(s.Ctx, index, opts)
    if err != nil {
        panic(err)
    }

	s.setExistence(collectionName, true, false)
}

func (s *MongoServer) QueryAssetsClassIds(mirRepo constant.MirRepo, offset int, limit int, classIds []int, currentAssetId string) []constant.MirAssetDetail {
	defer tools.TimeTrack(time.Now())

	collection, _ := s.getRepoCollection(mirRepo)
	log.Printf("Query offset: %d, limit: %d, classIds: %v, currentId: %s\n", offset, limit, classIds, currentAssetId)

	filterQuery := bson.M{}
	if len(classIds) > 0 {
		filterQuery["predclassids"] = bson.M{"$in": classIds}
	}
	if len(currentAssetId) > 0 {
		filterQuery["assetid"] = bson.M{"$gte": currentAssetId}
	}
	pageOptions := options.Find().SetSort(bson.M{"assetid": 1}).SetSkip(int64(offset)).SetLimit(int64(limit))
	log.Printf("filterQuery: %+v\n", filterQuery)

	queryCursor, err := collection.Find(s.Ctx, filterQuery, pageOptions)
	if err != nil {
		panic(err)
	}
	var queryData []constant.MirAssetDetail
	if err = queryCursor.All(s.Ctx, &queryData); err != nil {
		panic(err)
	}
	return queryData
}

func NewMongoServer(uri string) MongoServer {
	mongoCtx := context.Background()
	mongoClient, err := mongo.Connect(mongoCtx, options.Client().ApplyURI(uri))
    if err != nil {
        panic(err)
    }

	defaultDbName := "YMIR"
	// Clear cached data.
	mongoClient.Database(defaultDbName).Drop(mongoCtx)

	return MongoServer{
		Clt: mongoClient,
		Ctx: mongoCtx,
		dbName: defaultDbName,
		existenceName: "__collection_existence__",
	}
}
