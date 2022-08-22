package constants

import (
	"encoding/json"
	"sort"
	"time"

	"go.mongodb.org/mongo-driver/bson"
)

type Config struct {
	YmirSandbox string

	ViewerHost string
	ViewerPort int
	ViewerURI  string

	MongoDBURI       string
	MongoDataDBName  string
	MongoDataDBCache bool

	InnerTimeout time.Duration
}

type MirHist struct {
	Buckets   *map[string]string `json:"-"`
	LowerBNDs []float64          `json:"-"`
	Ops       interface{}        `json:"-"`
}

// Json as array, not a sub-field of struct.
func (h *MirHist) MarshalJSON() ([]byte, error) {
	histKeys := make([]string, 0)
	for histKey := range *h.Buckets {
		histKeys = append(histKeys, histKey)
	}

	sort.Slice(histKeys, func(i, j int) bool {
		l1, l2 := len(histKeys[i]), len(histKeys[j])
		if l1 != l2 {
			return l1 < l2
		}
		return histKeys[i] < histKeys[j]
	})

	output := []map[string]string{}
	for _, histKey := range histKeys {
		output = append(output, map[string]string{"x": histKey, "y": (*h.Buckets)[histKey]})
	}

	return json.Marshal(&output)
}

const (
	BytesPerMB float64 = 1048576
)

var ConstAssetsMirHist map[string]MirHist = map[string]MirHist{
	"quality": {Ops: "$quality", LowerBNDs: []float64{0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0}},
	"bytes": {Ops: "$metadata.byte_size", LowerBNDs: []float64{
		0,
		0.5 * BytesPerMB,
		1.0 * BytesPerMB,
		1.5 * BytesPerMB,
		2.0 * BytesPerMB,
		2.5 * BytesPerMB,
		3.0 * BytesPerMB,
		3.5 * BytesPerMB,
		4.0 * BytesPerMB,
		4.5 * BytesPerMB,
		5.0 * BytesPerMB,
	}},
	"area": {Ops: bson.M{"$multiply": bson.A{"$metadata.width", "$metadata.height"}},
		LowerBNDs: []float64{0, 100000, 500000, 1000000, 2000000, 4000000, 6000000, 8000000}},
	"hw_ratio": {Ops: bson.M{"$divide": bson.A{"$metadata.height", "$metadata.width"}},
		LowerBNDs: []float64{0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5}},
}

var ConstGtMirHist map[string]MirHist = map[string]MirHist{
	"quality": {Ops: "$gt.anno_quality", LowerBNDs: []float64{0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0}},
	"area": {
		Ops:       bson.M{"$multiply": bson.A{"$gt.box.w", "$gt.box.h"}},
		LowerBNDs: []float64{0, 50, 500, 2500, 5000, 10000, 50000, 100000, 200000},
	},
	"area_ratio": {
		Ops: bson.M{"$divide": bson.A{bson.M{"$multiply": bson.A{"$gt.box.w", "$gt.box.h"}},
			bson.M{"$multiply": bson.A{"$metadata.width", "$metadata.height"}}}},
		LowerBNDs: []float64{0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0}},
}

var ConstPredMirHist map[string]MirHist = map[string]MirHist{
	"quality": {Ops: "$pred.anno_quality", LowerBNDs: []float64{0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0}},
	"area": {
		Ops:       bson.M{"$multiply": bson.A{"$pred.box.w", "$pred.box.h"}},
		LowerBNDs: []float64{0, 50, 500, 2500, 5000, 10000, 50000, 100000, 200000},
	},
	"area_ratio": {
		Ops: bson.M{"$divide": bson.A{bson.M{"$multiply": bson.A{"$pred.box.w", "$pred.box.h"}},
			bson.M{"$multiply": bson.A{"$metadata.width", "$metadata.height"}}}},
		LowerBNDs: []float64{0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0}},
}
