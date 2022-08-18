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

type BaseDatabase interface {
	Collection(name string, opts ...*options.CollectionOptions) *mongo.Collection
}
type MongoServer struct {
	database      BaseDatabase
	Ctx           context.Context
	existenceName string
}

func NewMongoServer(mongoCtx context.Context, database BaseDatabase) *MongoServer {
	return &MongoServer{
		database:      database,
		Ctx:           mongoCtx,
		existenceName: "__collection_existence__",
	}
}

func (s *MongoServer) getRepoCollection(mirRepo *constants.MirRepo) (*mongo.Collection, string) {
	_, mirRev := mirRepo.BuildRepoID()
	return s.database.Collection(mirRev), mirRev
}

func (s *MongoServer) getExistenceCollection() *mongo.Collection {
	collection, _ := s.getRepoCollection(&constants.MirRepo{BranchID: s.existenceName})
	return collection
}

func (s *MongoServer) setDatasetExistence(collectionName string, ready bool, insert bool) {
	collection := s.getExistenceCollection()
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
func (s *MongoServer) CheckDatasetExistenceReady(mirRepo *constants.MirRepo) (bool, bool) {
	_, collectionName := s.getRepoCollection(mirRepo)
	collectionExistence := s.getExistenceCollection()
	filter := bson.M{"_id": collectionName}
	data := make(map[string]interface{})
	err := collectionExistence.FindOne(s.Ctx, filter).Decode(data)
	if err != nil {
		return false, false
	}
	return data["exist"].(bool), data["ready"].(bool)
}

func (s *MongoServer) IndexDatasetData(mirRepo *constants.MirRepo, newData []interface{}) {
	defer tools.TimeTrack(time.Now())

	if len(newData) <= 0 {
		return
	}

	collection, collectionName := s.getRepoCollection(mirRepo)
	s.setDatasetExistence(collectionName, false, true)

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

	s.setDatasetExistence(collectionName, true, false)
}

func (s *MongoServer) countDatasetAssetsInClass(
	collection *mongo.Collection,
	queryField string,
	classIds []int,
) (int64, int64) {
	if len(queryField) < 1 {
		panic("invalid queryField in countDatasetAssetsInClass")
	}

	matchStage := bson.D{bson.E{Key: "$match", Value: bson.M{queryField: bson.M{"$in": classIds}}}}
	countStage := bson.D{
		bson.E{
			Key: "$group",
			Value: bson.D{
				bson.E{Key: "_id", Value: nil},
				bson.E{Key: "count", Value: bson.M{"$sum": 1}},
				bson.E{Key: "sum", Value: bson.M{"$sum": bson.M{"$size": "$" + queryField}}}}}}

	showInfoCursor, err := collection.Aggregate(s.Ctx, mongo.Pipeline{matchStage, countStage})
	if err != nil {
		panic(err)
	}

	var showsWithInfo []bson.M
	if err = showInfoCursor.All(s.Ctx, &showsWithInfo); err != nil {
		panic(err)
	}
	if len(showsWithInfo) < 1 {
		return 0, 0
	}
	return int64(showsWithInfo[0]["count"].(int32)), int64(showsWithInfo[0]["sum"].(int32))
}

func (s *MongoServer) QueryDatasetAssets(
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
	defer tools.TimeTrack(time.Now())

	log.Printf(
		"Query offset: %d, limit: %d, classIds: %v, annoTypes: %v, currentId: %s, cmTypes: %v cks: %v tags: %v\n",
		offset,
		limit,
		classIds,
		annoTypes,
		currentAssetID,
		cmTypes,
		cks,
		tags,
	)
	collection, _ := s.getRepoCollection(mirRepo)

	// "and" for inter-group, "or" for inner-group
	filterAndConditions := bson.A{}
	// class id in either field counts.
	if len(classIds) > 0 {
		singleQuery := bson.M{"class_ids": bson.M{"$in": classIds}}
		filterAndConditions = append(filterAndConditions, singleQuery)
	}

	if len(annoTypes) > 0 {
		singleQuery := bson.M{annoTypes[0] + ".class_id": bson.M{"$exists": true}}

		// Both gt and pred.
		if len(annoTypes) > 1 {
			singleQuery = bson.M{"$or": bson.A{
				bson.M{"gt.class_id": bson.M{"$exists": true}},
				bson.M{"pred.class_id": bson.M{"$exists": true}},
			}}
		}
		filterAndConditions = append(filterAndConditions, singleQuery)
	}

	if len(cmTypes) > 0 {
		singleQuery := bson.M{"$or": bson.A{
			bson.M{"gt.cm": bson.M{"$in": cmTypes}},
			bson.M{"pred.cm": bson.M{"$in": cmTypes}},
		}}
		filterAndConditions = append(filterAndConditions, singleQuery)
	}

	// ck format "xxx" "xxx:" "xxx:yyy"
	if len(cks) > 0 {
		orConditions := bson.A{}
		for _, ck := range cks {
			ckStrs := strings.Split(ck, ":")
			if len(ckStrs) > 2 || len(ckStrs) < 1 || len(ckStrs[0]) == 0 {
				panic(fmt.Sprintf("invalid ck: %s", ck))
			}

			if len(ckStrs) == 1 || len(ckStrs[1]) == 0 {
				// case "xxx:" or "xxx"
				orConditions = append(orConditions, bson.M{"cks." + ckStrs[0]: bson.M{"$exists": true}})
			} else {
				// case "xxx:yyy"
				orConditions = append(orConditions, bson.M{"cks." + ckStrs[0]: ckStrs[1]})
			}
		}
		filterAndConditions = append(filterAndConditions, bson.M{"$or": orConditions})
	}

	// tag format "xxx" "xxx:" "xxx:yyy"
	if len(tags) > 0 {
		orConditions := bson.A{}
		for _, tag := range tags {
			tagStrs := strings.Split(tag, ":")
			if len(tagStrs) > 2 || len(tagStrs) < 1 || len(tagStrs[0]) == 0 {
				panic(fmt.Sprintf("invalid tag: %s", tag))
			}

			if len(tagStrs) == 1 || len(tagStrs[1]) == 0 {
				// case "xxx:" or "xxx"
				orConditions = append(orConditions, bson.M{"$or": bson.A{
					bson.M{"gt.tags." + tagStrs[0]: bson.M{"$exists": true}},
					bson.M{"pred.tags." + tagStrs[0]: bson.M{"$exists": true}},
				}})
			} else {
				// case "xxx:yyy"
				orConditions = append(orConditions, bson.M{"$or": bson.A{
					bson.M{"gt.tags." + tagStrs[0]: tagStrs[1]},
					bson.M{"pred.tags." + tagStrs[0]: tagStrs[1]},
				}})
			}
		}
		filterAndConditions = append(filterAndConditions, bson.M{"$or": orConditions})
	}

	filterQuery := bson.M{}
	if len(filterAndConditions) > 0 {
		filterQuery["$and"] = filterAndConditions
	}

	// This is a special field, used as anchor.
	if len(currentAssetID) > 0 {
		filterQuery["asset_id"] = bson.M{"$gte": currentAssetID}
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

	return &constants.QueryAssetsResult{
		AssetsDetail:     queryData,
		Offset:           offset,
		Limit:            limit,
		Anchor:           anchor,
		TotalAssetsCount: totalAssetsCount,
	}
}

func (s *MongoServer) queryHistogram(
	collection *mongo.Collection,
	ops interface{},
	lowerBNDs []float64,
	unwindField string,
) *map[string]string {
	buckets := map[string]string{}
	for _, lowerBND := range lowerBNDs {
		buckedKeyStr := fmt.Sprintf("%.2f", lowerBND)
		buckets[buckedKeyStr] = "0"
	}

	unwindStage := bson.D{bson.E{
		Key: "$unwind", Value: unwindField,
	}}

	bucketStage := bson.D{
		bson.E{
			Key: "$bucket",
			Value: bson.D{
				bson.E{
					Key:   "groupBy",
					Value: ops,
				},
				bson.E{Key: "default", Value: "_others_"},
				bson.E{
					Key:   "boundaries",
					Value: lowerBNDs,
				},
				bson.E{Key: "output", Value: bson.M{"count": bson.M{"$sum": 1}}},
			}}}

	showInfoCursor, err := collection.Aggregate(s.Ctx, mongo.Pipeline{unwindStage, bucketStage})
	if err != nil {
		panic(err)
	}

	var showsWithInfo []map[string]interface{}
	if err = showInfoCursor.All(s.Ctx, &showsWithInfo); err != nil {
		panic(err)
	}

	for _, bucketMap := range showsWithInfo {
		if buckedKey, ok := bucketMap["_id"].(float64); ok {
			buckedKeyStr := fmt.Sprintf("%.2f", buckedKey)
			buckets[buckedKeyStr] = fmt.Sprintf("%d", bucketMap["count"].(int32))
		}
	}
	return &buckets
}

func (s *MongoServer) QueryDatasetStats(
	mirRepo *constants.MirRepo,
	classIDs []int,
	requireAssetsHist bool,
	requireAnnotationsHist bool,
) *constants.QueryDatasetStatsResult {
	collection, _ := s.getRepoCollection(mirRepo)
	totalAssetsCount, err := collection.CountDocuments(s.Ctx, bson.M{}, &options.CountOptions{})
	if err != nil {
		panic(err)
	}

	queryData := constants.NewQueryDatasetStatsResult()

	// Build Asset fields.
	queryData.TotalAssetsCount = totalAssetsCount
	if requireAssetsHist {
		for histKey, hist := range constants.ConstAssetsMirHist {
			assetHist := hist
			assetHist.Buckets = s.queryHistogram(
				collection,
				assetHist.Ops,
				assetHist.LowerBNDs,
				"$metadata",
			)
			queryData.AssetsHist[histKey] = &assetHist
		}
	}

	// Build Annotation fields.
	for _, classID := range classIDs {
		queryData.Gt.ClassIDsCount[classID], _ = s.countDatasetAssetsInClass(collection, "gt.class_id", []int{classID})
		queryData.Pred.ClassIDsCount[classID], _ = s.countDatasetAssetsInClass(
			collection,
			"pred.class_id",
			[]int{classID},
		)
	}

	queryData.Gt.PositiveImagesCount, queryData.Gt.AnnotationsCount = s.countDatasetAssetsInClass(
		collection,
		"gt.class_id",
		classIDs,
	)
	queryData.Gt.NegativeImagesCount = totalAssetsCount - queryData.Gt.PositiveImagesCount

	queryData.Pred.PositiveImagesCount, queryData.Pred.AnnotationsCount = s.countDatasetAssetsInClass(
		collection,
		"pred.class_id",
		classIDs,
	)
	queryData.Pred.NegativeImagesCount = totalAssetsCount - queryData.Pred.PositiveImagesCount

	if requireAnnotationsHist {

		for histKey, hist := range constants.ConstGtMirHist {
			annoHist := hist
			annoHist.Buckets = s.queryHistogram(
				collection,
				annoHist.Ops,
				annoHist.LowerBNDs,
				"$gt",
			)
			queryData.Gt.AnnotationsHist[histKey] = &annoHist
		}
		for histKey, hist := range constants.ConstPredMirHist {
			annoHist := hist
			annoHist.Buckets = s.queryHistogram(
				collection,
				annoHist.Ops,
				annoHist.LowerBNDs,
				"$pred",
			)
			queryData.Pred.AnnotationsHist[histKey] = &annoHist
		}
	}

	// Build Query Context.
	queryData.QueryContext.RequireAssetsHist = requireAssetsHist
	queryData.QueryContext.RequireAnnotationsHist = requireAnnotationsHist

	return queryData
}

func (s *MongoServer) QueryDatasetDup(
	mirRepo0 *constants.MirRepo,
	mirRepo1 *constants.MirRepo,
) *constants.QueryDatasetDupResult {
	defer tools.TimeTrack(time.Now())

	collection0, collectionName0 := s.getRepoCollection(mirRepo0)
	totalCount0, err := collection0.CountDocuments(s.Ctx, bson.M{}, &options.CountOptions{})
	if err != nil {
		panic(err)
	}

	collection1, collectionName1 := s.getRepoCollection(mirRepo1)
	totalCount1, err := collection0.CountDocuments(s.Ctx, bson.M{}, &options.CountOptions{})
	if err != nil {
		panic(err)
	}

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

	return &constants.QueryDatasetDupResult{
		Duplication: len(showsLoaded),
		TotalCount:  map[string]int64{mirRepo0.BranchID: totalCount0, mirRepo1.BranchID: totalCount1},
	}
}
