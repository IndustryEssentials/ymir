package constants

import (
	"encoding/json"

	"google.golang.org/protobuf/encoding/protojson"
	"google.golang.org/protobuf/proto"
)

type MirdataModel struct {
	ModelHash     string                 `json:"model_hash"`
	MAP           float32                `json:"mAP"`
	Context       string                 `json:"context"`
	Stages        map[string]interface{} `json:"stages"`
	BestStageName string                 `json:"best_stage_name"`
	MIoU          float32                `json:"mIoU"`
	MaskAP        float32                `json:"maskAP"`

	TaskParameters string                 `json:"task_parameters"`
	ExecutorConfig map[string]interface{} `json:"executor_config"`

	ObjectType int32 `json:"object_type"`
}

func NewMirdataModel(taskParameters string) *MirdataModel {
	modelData := MirdataModel{TaskParameters: taskParameters, ExecutorConfig: map[string]interface{}{}}
	return &modelData
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

type IndexedDatasetMetadata struct {
	Exist bool `json:"exist" bson:"exist"`
	Ready bool `json:"ready" bson:"ready"`

	HistAssets    *map[string]*MirHist `json:"hist_assets"     bson:"hist_assets"`
	HistAnnosGt   *map[string]*MirHist `json:"hist_annos_gt"   bson:"hist_annos_gt"`
	HistAnnosPred *map[string]*MirHist `json:"hist_annos_pred" bson:"hist_annos_pred"`
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
