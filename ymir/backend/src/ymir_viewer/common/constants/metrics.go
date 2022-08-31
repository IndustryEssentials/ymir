package constants

import (
	"time"
)

type MirMetrics int

const (
	MetricsUnknown MirMetrics = iota
	MetricsKeyIDs
	MetricsModel
	MetricsProject
	MetricsTask
)

var (
	MetricsDatasetStringList = []string{"_", "keyids", "model", "project", "task"}
)

func (mirMetrics MirMetrics) String() string {
	return MetricsDatasetStringList[mirMetrics]
}

func ParseMirMetrics(s string) MirMetrics {
	for idx, v := range MetricsDatasetStringList {
		if v == s {
			return MirMetrics(idx)
		}
	}
	return MetricsUnknown
}

type MetricsDataPoint struct {
	CreateTime time.Time `json:"create_time" bson:"create_time" mapstructure:"create_time"`
	ID         string    `json:"id"          bson:"id"          mapstructure:"id"`
	UserID     string    `json:"user_id"     bson:"user_id"     mapstructure:"user_id"`
	ProjectID  string    `json:"project_id"  bson:"project_id"  mapstructure:"project_id"`
	KeyIDs     []int     `json:"key_ids"     bson:"key_ids"     mapstructure:"key_ids"`

	Other map[string]interface{} `mapstructure:",remain"`
}

type MetricsQueryPoint struct {
	Legend string `json:"legend"`
	Count  int64  `json:"count"`
}
