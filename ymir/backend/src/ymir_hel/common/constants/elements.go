package constants

import (
	"fmt"
	"path"

	"google.golang.org/protobuf/proto"

	"github.com/IndustryEssentials/ymir-hel/protos"
)

// Mir Repos.
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

// Mir Storage Files.
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

// Elements structs.
type MirTimestamp struct {
	Start    int32   `json:"start"    bson:"start"`
	Duration float32 `json:"duration" bson:"duration"`
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

// Intermediate Mir datas.
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
	Mask        string            `json:"mask"         bson:"mask"`
	IsCrowd     int32             `json:"is_crowd"     bson:"is_crowd"`
	Type        int32             `json:"type"         bson:"type"`
	MaskArea    int32             `json:"mask_area"    bson:"mask_area"`
}

func NewMirObjectAnnotation() MirObjectAnnotation {
	return MirObjectAnnotation{Box: &MirRect{}, Tags: map[string]string{}, Polygon: []*MirIntPoint{}}
}

type DatasetStatsElement struct {
	// Assets count
	ClassIDsCount       map[int]int64 `json:"class_ids_count"`
	ClassObjCount       map[int]int64 `json:"class_obj_count"`
	NegativeAssetsCount int64         `json:"negative_assets_count"`
	PositiveAssetsCount int64         `json:"positive_assets_count"`

	EvalClassIDs []int32 `json:"eval_class_ids"`

	// Annotations
	AnnotationsCount int64                `json:"annos_count"`
	AnnotationsHist  *map[string]*MirHist `json:"annos_hist"`

	// Tags
	TagsCountTotal map[string]int64            `json:"tags_count_total"`
	TagsCount      map[string]map[string]int64 `json:"tags_count"`

	// Masks
	TotalMaskArea    int64         `json:"total_mask_area"`
	ClassIDsMaskArea map[int]int64 `json:"class_ids_mask_area"`
}
