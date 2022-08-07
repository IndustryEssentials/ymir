package constant

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
	UserId string
	RepoId string
	BranchId string
	TaskId string
}

func (mirRepo MirRepo) BuildRepoId() (string, string) {
	mirRoot := path.Join(mirRepo.SandboxRoot, mirRepo.UserId, mirRepo.RepoId)
	mirRev := fmt.Sprintf("%s@%s", mirRepo.BranchId, mirRepo.TaskId)
	return mirRoot, mirRev
}

type MirdataModel struct {
	ModelHash string `json:"model_hash"`
	MeanAveragePrecision float32 `json:"mean_average_precision"`
	Context string `json:"context"`
	Stages map[string]interface{} `json:"stages"`
	BestStageName string `json:"best_stage_name"`

	TaskParameters string `json:"task_parameters"`
	ExecutorConfig map[string]interface{} `json:"executor_config"`
}

func NewMirdataModel(taskParameters string) MirdataModel {
	modelData := MirdataModel{TaskParameters: taskParameters, ExecutorConfig: map[string]interface{}{}}
	return modelData
}

type MirAssetDetail struct {
	AssetId string `json:"asset_id"`
	MetaData map[string]*interface{} `json:"metadata"`
	Pred []map[string]interface{} `json:"pred"`
	PredClassIds []int32 `json:"pred_class_ids"`
	Gt []map[string]interface{} `json:"gt"`
	GtClassIds []int32 `json:"gt_class_ids"`
}

func NewMirAssetDetail() MirAssetDetail {
	mirAssetDetail := MirAssetDetail{}
	mirAssetDetail.Pred = make([]map[string]interface{}, 0)
	mirAssetDetail.PredClassIds = []int32{}
	mirAssetDetail.Gt = make([]map[string]interface{}, 0)
	mirAssetDetail.GtClassIds = []int32{}
	return mirAssetDetail
}