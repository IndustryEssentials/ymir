package constants

import (
	"fmt"
	"path"

	"google.golang.org/protobuf/proto"

	"github.com/IndustryEssentials/ymir-viewer/common/protos"
)

type MirFile int

const (
	MirfileMetadatas MirFile = iota
	MirfileAnnotations
	MirfileKeywords
	MirfileContext
	MirfileTasks
)

func (mirFile MirFile) String() string {
	return []string{"metadatas.mir", "annotations.mir", "keywords.mir", "context.mir", "tasks.mir"}[mirFile]
}

func (mirFile MirFile) ProtoData() proto.Message {
	switch mirFile {
	case MirfileMetadatas:
		return &protos.MirMetadatas{}

	case MirfileAnnotations:
		return &protos.MirAnnotations{}

	case MirfileKeywords:
		return &protos.MirKeywords{}

	case MirfileContext:
		return &protos.MirContext{}

	case MirfileTasks:
		return &protos.MirTasks{}

	default:
		return nil
	}
}

type MirRepo struct {
	SandboxRoot string
	UserId      string
	RepoId      string
	BranchId    string
	TaskId      string
}

func (mirRepo MirRepo) BuildRepoId() (string, string) {
	mirRoot := path.Join(mirRepo.SandboxRoot, mirRepo.UserId, mirRepo.RepoId)
	mirRev := fmt.Sprintf("%s@%s", mirRepo.BranchId, mirRepo.TaskId)
	return mirRoot, mirRev
}

type MirdataModel struct {
	ModelHash            string                 `json:"model_hash"`
	MeanAveragePrecision float32                `json:"mean_average_precision"`
	Context              string                 `json:"context"`
	Stages               map[string]interface{} `json:"stages"`
	BestStageName        string                 `json:"best_stage_name"`

	TaskParameters string                 `json:"task_parameters"`
	ExecutorConfig map[string]interface{} `json:"executor_config"`
}

func NewMirdataModel(taskParameters string) MirdataModel {
	modelData := MirdataModel{TaskParameters: taskParameters, ExecutorConfig: map[string]interface{}{}}
	return modelData
}

type MirAssetDetail struct {
	// Export fields.
	AssetId        string                   `json:"asset_id"  bson:"asset_id"`
	MetaData       map[string]interface{}   `json:"metadata"  bson:"metadata"`
	JoinedClassIDs []int32                  `json:"class_ids" bson:"class_ids"`
	Gt             []map[string]interface{} `json:"gt"        bson:"gt"`
	Pred           []map[string]interface{} `json:"pred"      bson:"pred"`
	Cks            map[string]string        `json:"cks"       bson:"cks"`
}

func NewMirAssetDetail() MirAssetDetail {
	mirAssetDetail := MirAssetDetail{}
	mirAssetDetail.MetaData = map[string]interface{}{}
	mirAssetDetail.JoinedClassIDs = []int32{}
	mirAssetDetail.Pred = make([]map[string]interface{}, 0)
	mirAssetDetail.Gt = make([]map[string]interface{}, 0)
	mirAssetDetail.Cks = map[string]string{}
	return mirAssetDetail
}

type QueryAssetsResult struct {
	AssetsDetail     []MirAssetDetail `json:"elements"`
	Offset           int              `json:"offset"`
	Limit            int              `json:"limit"`
	Anchor           int64            `json:"anchor"`
	TotalAssetsCount int64            `json:"total_assets_count"`
}

type DatasetStatsElement struct {
	ClassIdsCount       map[int]int64 `json:"class_ids_count"`
	NegativeImagesCount int64         `json:"negative_images_count"`
	PositiveImagesCount int64         `json:"positive_images_count"`
}

type QueryDatasetStatsResult struct {
	Gt               DatasetStatsElement         `json:"gt"`
	Pred             DatasetStatsElement         `json:"pred"`
	TotalAssetsCount int64                       `json:"total_assets_count"`
	CksCountTotal    map[string]int64            `json:"cks_count_total"`
	CksCount         map[string]map[string]int64 `json:"cks_count"`
}

func NewQueryDatasetStatsResult() QueryDatasetStatsResult {
	queryResult := QueryDatasetStatsResult{
		Gt:               DatasetStatsElement{ClassIdsCount: map[int]int64{}},
		Pred:             DatasetStatsElement{ClassIdsCount: map[int]int64{}},
		TotalAssetsCount: 0,
		CksCount:         map[string]map[string]int64{},
		CksCountTotal:    map[string]int64{},
	}
	return queryResult
}
