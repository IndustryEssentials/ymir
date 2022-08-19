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
	UserID      string
	RepoID      string
	BranchID    string
	TaskID      string
}

func (mirRepo MirRepo) BuildRepoID() (string, string) {
	mirRoot := path.Join(mirRepo.SandboxRoot, mirRepo.UserID, mirRepo.RepoID)
	mirRev := fmt.Sprintf("%s@%s", mirRepo.BranchID, mirRepo.TaskID)
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

func NewMirdataModel(taskParameters string) *MirdataModel {
	modelData := MirdataModel{TaskParameters: taskParameters, ExecutorConfig: map[string]interface{}{}}
	return &modelData
}

type MirAssetDetail struct {
	// Export fields.
	AssetID        string                   `json:"asset_id"      bson:"asset_id"`
	MetaData       map[string]interface{}   `json:"metadata"      bson:"metadata"`
	JoinedClassIDs []int32                  `json:"class_ids"     bson:"class_ids"`
	Gt             []map[string]interface{} `json:"gt"            bson:"gt"`
	Pred           []map[string]interface{} `json:"pred"          bson:"pred"`
	Cks            map[string]string        `json:"cks"           bson:"cks"`
	Quality        float32                  `json:"image_quality" bson:"quality"`
}

func NewMirAssetDetail() MirAssetDetail {
	mirAssetDetail := MirAssetDetail{}
	mirAssetDetail.MetaData = map[string]interface{}{}
	mirAssetDetail.JoinedClassIDs = []int32{}
	mirAssetDetail.Pred = make([]map[string]interface{}, 0)
	mirAssetDetail.Gt = make([]map[string]interface{}, 0)
	mirAssetDetail.Cks = map[string]string{}
	mirAssetDetail.Quality = -1
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
	// Assets count
	ClassIDsCount       map[int]int64 `json:"class_ids_count"`
	NegativeAssetsCount int64         `json:"negative_assets_count"`
	PositiveAssetsCount int64         `json:"positive_assets_count"`

	// Annotations
	AnnotationsCount int64               `json:"annos_count"`
	AnnotationsHist  map[string]*MirHist `json:"annos_hist"`

	// Tags
	TagsCountTotal map[string]int64            `json:"tags_count_total"`
	TagsCount      map[string]map[string]int64 `json:"tags_count"`
}

type QueryDatasetStatsContext struct {
	RequireAssetsHist      bool `json:"require_assets_hist"`
	RequireAnnotationsHist bool `json:"require_annos_hist"`
}

type QueryDatasetStatsResult struct {
	// Assets
	TotalAssetsCount    int64               `json:"total_assets_count"`
	TotalAssetsFileSize int64               `json:"total_assets_mbytes"`
	AssetsHist          map[string]*MirHist `json:"assets_hist"`

	// Annotations
	Gt   DatasetStatsElement `json:"gt"`
	Pred DatasetStatsElement `json:"pred"`

	// Cks
	CksCountTotal map[string]int64            `json:"cks_count_total"`
	CksCount      map[string]map[string]int64 `json:"cks_count"`

	// Task and query context.
	NewTypesAdded bool                     `json:"new_types_added"`
	QueryContext  QueryDatasetStatsContext `json:"query_context"`
}

func NewQueryDatasetStatsResult() *QueryDatasetStatsResult {
	queryResult := QueryDatasetStatsResult{
		AssetsHist: map[string]*MirHist{},
		Gt: DatasetStatsElement{
			ClassIDsCount:   map[int]int64{},
			AnnotationsHist: map[string]*MirHist{},
			TagsCount:       map[string]map[string]int64{},
			TagsCountTotal:  map[string]int64{},
		},
		Pred: DatasetStatsElement{
			ClassIDsCount:   map[int]int64{},
			AnnotationsHist: map[string]*MirHist{},
			TagsCount:       map[string]map[string]int64{},
			TagsCountTotal:  map[string]int64{},
		},

		CksCount:      map[string]map[string]int64{},
		CksCountTotal: map[string]int64{},
	}
	return &queryResult
}

type QueryDatasetDupResult struct {
	Duplication int              `json:"duplication"`
	TotalCount  map[string]int64 `json:"total_count"`
}
