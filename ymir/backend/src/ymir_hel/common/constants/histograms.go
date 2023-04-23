package constants

import (
	"encoding/json"
	"fmt"

	"go.mongodb.org/mongo-driver/bson"
)

const (
	BytesPerMB float64 = 1048576
)

// Mir Histograms.
type MirHist struct {
	SparseBuckets *map[string]int32    `json:"-" bson:"-"`
	LowerBNDs     []float64            `json:"-" bson:"-"`
	Ops           interface{}          `json:"-" bson:"-"`
	Output        *[]map[string]string `json:"-" bson:"output"`
	SkipUnwind    bool                 `json:"-" bson:"-"`
	DecDigits     int16                `json:"-" bson:"-"`
}

func (h *MirHist) BuildMirHist(bucket *map[string]int32) {
	h.Output = &[]map[string]string{}
	h.SparseBuckets = bucket
	for _, LowerBND := range h.LowerBNDs {
		outputKey := fmt.Sprintf(fmt.Sprintf("%%.%df", h.DecDigits), LowerBND)

		outputValue := "0"
		histKey := fmt.Sprintf("%.2f", LowerBND)
		if data, ok := (*h.SparseBuckets)[histKey]; ok {
			outputValue = fmt.Sprintf("%d", data)
		}

		*h.Output = append(*h.Output, map[string]string{"x": outputKey, "y": outputValue})
	}
}

// MarshalJSON return json as array, not a sub-field of struct.
func (h *MirHist) MarshalJSON() ([]byte, error) {
	return json.Marshal(&h.Output)
}

// Pre-defined historgram schemas.
var ConstAssetsMirHist map[string]MirHist = map[string]MirHist{
	"quality": {
		Ops: "$quality", DecDigits: 2,
		LowerBNDs: []float64{0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0}},
	"bytes": {Ops: bson.M{"$divide": bson.A{"$metadata.byte_size", BytesPerMB}}, DecDigits: 2,
		LowerBNDs: []float64{0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0}},
	"area": {Ops: bson.M{"$multiply": bson.A{"$metadata.width", "$metadata.height"}}, DecDigits: 0,
		LowerBNDs: []float64{0, 100000, 500000, 1000000, 2000000, 4000000, 6000000, 8000000}},
	"hw_ratio": {Ops: bson.M{"$divide": bson.A{"$metadata.height", "$metadata.width"}}, DecDigits: 2,
		LowerBNDs: []float64{0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5}},
}

var ConstGtMirHist map[string]MirHist = map[string]MirHist{
	"quality": {
		Ops:       "$gt.anno_quality",
		DecDigits: 2,
		LowerBNDs: []float64{0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0},
	},
	"box_area": {
		Ops: bson.M{"$multiply": bson.A{"$gt.box.w", "$gt.box.h"}}, DecDigits: 0,
		LowerBNDs: []float64{0, 1, 50, 500, 2500, 5000, 10000, 50000, 100000, 200000},
	},
	"box_area_ratio": {
		Ops: bson.M{"$divide": bson.A{bson.M{"$multiply": bson.A{"$gt.box.w", "$gt.box.h"}},
			bson.M{"$multiply": bson.A{"$metadata.width", "$metadata.height"}}}}, DecDigits: 2,
		LowerBNDs: []float64{0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0}},
	"mask_area": {
		Ops:       "$gt.mask_area",
		DecDigits: 0,
		LowerBNDs: []float64{0, 1, 50, 500, 2500, 5000, 10000, 50000, 100000, 200000},
	},
	"obj_counts": {
		Ops: bson.M{"$size": "$gt"}, DecDigits: 0,
		LowerBNDs:  []float64{0, 1, 2, 3, 4, 5, 10, 15, 20, 30, 40, 50, 100},
		SkipUnwind: true,
	},
	"class_counts": {
		Ops: bson.M{"$size": "$gt_class_ids"}, DecDigits: 0,
		LowerBNDs:  []float64{0, 1, 2, 3, 4, 5, 10, 15, 20, 30, 40, 50, 100},
		SkipUnwind: true,
	},
	"class_counts_rank": {
		Ops: bson.M{"$size": "$gt"}, DecDigits: 0,
		LowerBNDs:  []float64{1, 4, 10},
		SkipUnwind: true,
	},
}

var ConstPredMirHist map[string]MirHist = map[string]MirHist{
	"quality": {
		Ops:       "$pred.anno_quality",
		DecDigits: 2,
		LowerBNDs: []float64{0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0},
	},
	"box_area": {
		Ops: bson.M{"$multiply": bson.A{"$pred.box.w", "$pred.box.h"}}, DecDigits: 0,
		LowerBNDs: []float64{0, 1, 50, 500, 2500, 5000, 10000, 50000, 100000, 200000},
	},
	"box_area_ratio": {
		Ops: bson.M{"$divide": bson.A{bson.M{"$multiply": bson.A{"$pred.box.w", "$pred.box.h"}},
			bson.M{"$multiply": bson.A{"$metadata.width", "$metadata.height"}}}}, DecDigits: 2,
		LowerBNDs: []float64{0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0}},
	"mask_area": {
		Ops: "$pred.mask_area", DecDigits: 0,
		LowerBNDs: []float64{0, 1, 50, 500, 2500, 5000, 10000, 50000, 100000, 200000},
	},
	"obj_counts": {
		Ops: bson.M{"$size": "$pred"}, DecDigits: 0,
		LowerBNDs:  []float64{0, 1, 2, 3, 4, 5, 10, 15, 20, 30, 40, 50, 100},
		SkipUnwind: true,
	},
	"class_counts": {
		Ops: bson.M{"$size": "$pred_class_ids"}, DecDigits: 0,
		LowerBNDs:  []float64{0, 1, 2, 3, 4, 5, 10, 15, 20, 30, 40, 50, 100},
		SkipUnwind: true,
	},
}
