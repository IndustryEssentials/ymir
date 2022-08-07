package service

import (
	"fmt"
	"log"
	"time"

	"github.com/IndustryEssentials/ymir-viewer/common/constant"
	"github.com/IndustryEssentials/ymir-viewer/common/pbreader"
	"github.com/IndustryEssentials/ymir-viewer/tools"
)

func GetAssetsHandler(mongo MongoServer, mirRepo constant.MirRepo, offset int, limit int, classIds []int) []constant.MirAssetDetail {
	defer tools.TimeTrack(time.Now())
	if !mongo.checkExistence(mirRepo) {
		log.Printf("No cache for %s", fmt.Sprint(mirRepo))
		mirAssetDetails := pbreader.LoadAssetsInfo(mirRepo)

		newData := make([]interface{}, 0)
		for _, v := range mirAssetDetails {
			newData = append(newData, v)
		}
		mongo.IndexMongoData(mirRepo, newData)
	} else {
		log.Printf("Found cache for %s", fmt.Sprint(mirRepo))
	}
	return mongo.QueryAssetsClassIds(mirRepo, offset, limit, classIds)
}