package constants

import (
	"encoding/json"
	"fmt"
	"path"

	"google.golang.org/protobuf/encoding/protojson"
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

type MirTimestamp struct {
	Start    int32   `json:"start"    bson:"start"`
	Duration float32 `json:"duration" bson:"duration"`
}

type MirAssetAttributes struct {
	Timestamp      *MirTimestamp `json:"timestamp"       bson:"timestamp"`
	TvtType        int32         `json:"tvt_type"        bson:"tvt_type"`
	AssetType      int32         `json:"asset_type"      bson:"asset_type"`
	Width          int32         `json:"width"           bson:"width"`
	Height         int32         `json:"height"          bson:"height"`
	ImageChannels  int32         `json:"image_channels"  bson:"image_channels"`
	ByteSize       int32         `json:"byte_size"       bson:"byte_size"`
	OriginFilename string        `json:"origin_filename" bson:"origin_filename"`
}

type MirObjectAnnotation struct {
	Index       int32             `json:"index"        bson:"index"`
	Box         *MirRect          `json:"box"          bson:"box"`
	ClassId     int32             `json:"class_id"     bson:"class_id"`
	Score       float64           `json:"score"        bson:"score"`
	AnnoQuality float32           `json:"anno_quality" bson:"anno_quality"`
	Tags        map[string]string `json:"tags"         bson:"tags"`
	Cm          int32             `json:"cm"           bson:"cm"`
	DetLinkId   int32             `json:"det_link_id"  bson:"det_link_id"`
	ClassName   string            `json:"class_name"   bson:"class_name"`
	Polygon     []*MirIntPoint    `json:"polygon"      bson:"polygon"`
}

type MirIntPoint struct {
	X int32 `json:"x" bson:"x"`
	Y int32 `json:"y" bson:"y"`
	Z int32 `json:"z" bson:"z"`
}

type MirRect struct {
	X           int32   `json:"x"            bson:"x"`
	Y           int32   `json:"y"            bson:"y"`
	W           int32   `json:"w"            bson:"w"`
	H           int32   `json:"h"            bson:"h"`
	RotateAngle float32 `json:"rotate_angle" bson:"rotate_angle"` // unit in pi.
}

type MirAssetDetail struct {
	// Export fields.
	DocID          string                 `json:"-"             bson:"_id"`
	AssetID        string                 `json:"asset_id"      bson:"asset_id"`
	MetaData       *MirAssetAttributes    `json:"metadata"      bson:"metadata"`
	JoinedClassIDs []int32                `json:"class_ids"     bson:"class_ids"`
	Gt             []*MirObjectAnnotation `json:"gt"            bson:"gt"`
	Pred           []*MirObjectAnnotation `json:"pred"          bson:"pred"`
	Cks            map[string]string      `json:"cks"           bson:"cks"`
	Quality        float32                `json:"image_quality" bson:"quality"`
}

func NewMirObjectAnnotation() MirObjectAnnotation {
	return MirObjectAnnotation{Box: &MirRect{}, Tags: map[string]string{}, Polygon: []*MirIntPoint{}}
}

func NewMirAssetDetail() MirAssetDetail {
	mirAssetDetail := MirAssetDetail{}
	mirAssetDetail.MetaData = &MirAssetAttributes{Timestamp: &MirTimestamp{}}
	mirAssetDetail.JoinedClassIDs = []int32{}
	mirAssetDetail.Pred = make([]*MirObjectAnnotation, 0)
	mirAssetDetail.Gt = make([]*MirObjectAnnotation, 0)
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

	EvalClassIDs []int32 `json:"eval_class_ids"`

	// Annotations
	AnnotationsCount int64                `json:"annos_count"`
	AnnotationsHist  *map[string]*MirHist `json:"annos_hist"`

	// Tags
	TagsCountTotal map[string]int64            `json:"tags_count_total"`
	TagsCount      map[string]map[string]int64 `json:"tags_count"`
}

type QueryDatasetStatsContext struct {
	RequireAssetsHist      bool `json:"require_assets_hist"`
	RequireAnnotationsHist bool `json:"require_annos_hist"`
	RepoIndexExist         bool `json:"repo_index_exist"`
	RepoIndexReady         bool `json:"repo_index_ready"`
}

type QueryDatasetStatsResult struct {
	// Assets
	TotalAssetsCount    int64                `json:"total_assets_count"`
	TotalAssetsFileSize int64                `json:"total_assets_mbytes"`
	AssetsHist          *map[string]*MirHist `json:"assets_hist"`

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

type IndexedDatasetMetadata struct {
	Exist bool `json:"exist" bson:"exist"`
	Ready bool `json:"ready" bson:"ready"`

	HistAssets    *map[string]*MirHist `json:"hist_assets"     bson:"hist_assets"`
	HistAnnosGt   *map[string]*MirHist `json:"hist_annos_gt"   bson:"hist_annos_gt"`
	HistAnnosPred *map[string]*MirHist `json:"hist_annos_pred" bson:"hist_annos_pred"`
}

func NewQueryDatasetStatsResult() *QueryDatasetStatsResult {
	queryResult := QueryDatasetStatsResult{
		Gt: DatasetStatsElement{
			ClassIDsCount:  map[int]int64{},
			TagsCount:      map[string]map[string]int64{},
			TagsCountTotal: map[string]int64{},
		},
		Pred: DatasetStatsElement{
			ClassIDsCount:  map[int]int64{},
			TagsCount:      map[string]map[string]int64{},
			TagsCountTotal: map[string]int64{},
		},

		CksCount:      map[string]map[string]int64{},
		CksCountTotal: map[string]int64{},
	}
	return &queryResult
}

type QueryDatasetDupResult struct {
	Duplication   int              `json:"duplication"`
	TotalCount    map[string]int64 `json:"total_count"`
	ResidualCount map[string]int64 `json:"residual_count"`
}

func BuildStructFromMessage(message proto.Message, structOut interface{}) interface{} {
	m := protojson.MarshalOptions{EmitUnpopulated: true, AllowPartial: true, UseProtoNames: true, UseEnumNumbers: true}
	jsonBytes, err := m.Marshal(message)
	if err != nil {
		panic(err)
	}
	if err := json.Unmarshal(jsonBytes, &structOut); err != nil {
		panic(err)
	}
	return structOut
}
