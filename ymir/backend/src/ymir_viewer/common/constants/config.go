package constants

import (
	"encoding/json"
	"fmt"
	"time"

	"go.mongodb.org/mongo-driver/bson"
)

type Config struct {
	YmirSandbox string

	ViewerHost string
	ViewerPort int
	ViewerURI  string

	MongoDBURI         string
	MongoDataDBName    string
	MongoDataDBCache   bool
	MongoMetricsDBName string

	InnerTimeout time.Duration
}

type MirHist struct {
	SparseBuckets *map[string]int32    `json:"-" bson:"-"`
	LowerBNDs     []float64            `json:"-" bson:"-"`
	Ops           interface{}          `json:"-" bson:"-"`
	Output        *[]map[string]string `json:"-" bson:"output"`
}

func (h *MirHist) BuildMirHist(bucket *map[string]int32) {
	h.Output = &[]map[string]string{}
	h.SparseBuckets = bucket
	for _, LowerBND := range h.LowerBNDs {
		histKey := fmt.Sprintf("%.2f", LowerBND)
		value := "0"
		if data, ok := (*h.SparseBuckets)[histKey]; ok {
			value = fmt.Sprintf("%d", data)
		}
		*h.Output = append(*h.Output, map[string]string{"x": histKey, "y": value})
	}
}

// MarshalJSON return json as array, not a sub-field of struct.
func (h *MirHist) MarshalJSON() ([]byte, error) {
	return json.Marshal(&h.Output)
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
