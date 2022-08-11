package loader

import (
	"encoding/json"
	"sort"
	"time"

	"gopkg.in/yaml.v3"

	"github.com/vektra/gitreader"
	"google.golang.org/protobuf/encoding/protojson"
	"google.golang.org/protobuf/proto"

	"github.com/IndustryEssentials/ymir-viewer/common/constants"
	"github.com/IndustryEssentials/ymir-viewer/common/protos"
	"github.com/IndustryEssentials/ymir-viewer/tools"
)

type BaseMirRepoLoader interface {
	GetMirRepo() constants.MirRepo
	LoadSingleMirData(mirFile constants.MirFile) interface{}
	LoadAssetsDetail() []constants.MirAssetDetail
}

type MirRepoLoader struct {
	MirRepo constants.MirRepo
}

func (mirRepoLoader *MirRepoLoader) GetMirRepo() constants.MirRepo {
	return mirRepoLoader.MirRepo
}
func (mirRepoLoader *MirRepoLoader) LoadSingleMirData(mirFile constants.MirFile) interface{} {
	return mirRepoLoader.LoadMutipleMirDatas([]constants.MirFile{mirFile})[0]
}

func (mirRepoLoader *MirRepoLoader) LoadMutipleMirDatas(mirFiles []constants.MirFile) []interface{} {
	defer tools.TimeTrack(time.Now())
	mirRoot, mirRev := mirRepoLoader.MirRepo.BuildRepoId()

	repo, err := gitreader.OpenRepo(mirRoot)
	if err != nil {
		panic(err)
	}

	var sliceDatas = make([]interface{}, len(mirFiles))
	for i, mirFile := range mirFiles {
		blob, err := repo.CatFile(mirRev, mirFile.String())
		if err != nil {
			panic(err)
		}
		bytes, err := blob.Bytes()
		if err != nil {
			panic(err)
		}
		newData := mirFile.ProtoData()
		err = proto.Unmarshal(bytes, newData)
		if err != nil {
			panic(err)
		}
		sliceDatas[i] = newData
	}
	repo.Close()

	return sliceDatas
}

func (mirRepoLoader *MirRepoLoader) buildStructFromMessage(message proto.Message, structOut interface{}) interface{} {
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

func (mirRepoLoader *MirRepoLoader) LoadModelInfo() constants.MirdataModel {
	mirTasks := mirRepoLoader.LoadSingleMirData(constants.MirfileTasks).(*protos.MirTasks)
	task := mirTasks.Tasks[mirTasks.HeadTaskId]
	modelData := constants.NewMirdataModel(task.SerializedTaskParameters)
	if task.SerializedExecutorConfig != "" {
		if err := yaml.Unmarshal([]byte(task.SerializedExecutorConfig), &modelData.ExecutorConfig); err != nil {
			panic(err)
		}
	}
	mirRepoLoader.buildStructFromMessage(task.Model, &modelData)
	return modelData
}

func (mirRepoLoader *MirRepoLoader) LoadAssetsDetail() []constants.MirAssetDetail {
	defer tools.TimeTrack(time.Now())
	filesToLoad := []constants.MirFile{constants.MirfileMetadatas, constants.MirfileAnnotations}
	mirDatas := mirRepoLoader.LoadMutipleMirDatas(filesToLoad)
	mirMetadatas := mirDatas[0].(*protos.MirMetadatas)
	mirAnnotations := mirDatas[1].(*protos.MirAnnotations)

	gtAnnotations := map[string]*protos.SingleImageAnnotations{}
	if mirAnnotations.GroundTruth != nil && len(mirAnnotations.GroundTruth.ImageAnnotations) > 0 {
		gtAnnotations = mirAnnotations.GroundTruth.ImageAnnotations
	}
	predAnnotations := map[string]*protos.SingleImageAnnotations{}
	if mirAnnotations.Prediction != nil && len(mirAnnotations.Prediction.ImageAnnotations) > 0 {
		predAnnotations = mirAnnotations.Prediction.ImageAnnotations
	}
	mirCks := map[string]*protos.SingleImageCks{}
	if mirAnnotations.ImageCks != nil && len(mirAnnotations.ImageCks) > 0 {
		mirCks = mirAnnotations.ImageCks
	}

	mirAssetDetails := make([]constants.MirAssetDetail, len(mirMetadatas.Attributes))
	assetIds := make([]string, 0)
	for assetId := range mirMetadatas.Attributes {
		assetIds = append(assetIds, assetId)
	}
	sort.Strings(assetIds)
	for idx, assetId := range assetIds {
		mirAssetDetails[idx] = constants.NewMirAssetDetail()
		mirAssetDetails[idx].AssetId = assetId
		mirRepoLoader.buildStructFromMessage(mirMetadatas.Attributes[assetId], &mirAssetDetails[idx].MetaData)
		if cks, ok := mirCks[assetId]; ok {
			mirAssetDetails[idx].Cks = cks.Cks
		}

		mapClassIDs := map[int32]bool{}
		if gtAnnotation, ok := gtAnnotations[assetId]; ok {
			for _, annotation := range gtAnnotation.Annotations {
				annotationOut := mirRepoLoader.buildStructFromMessage(annotation, map[string]interface{}{}).(map[string]interface{})
				mirAssetDetails[idx].Gt = append(mirAssetDetails[idx].Gt, annotationOut)
				mapClassIDs[annotation.ClassId] = true
			}
		}
		if predAnnotation, ok := predAnnotations[assetId]; ok {
			for _, annotation := range predAnnotation.Annotations {
				annotationOut := mirRepoLoader.buildStructFromMessage(annotation, map[string]interface{}{}).(map[string]interface{})
				mirAssetDetails[idx].Pred = append(mirAssetDetails[idx].Pred, annotationOut)
				mapClassIDs[annotation.ClassId] = true
			}
		}

		mirAssetDetails[idx].JoinedClassIDs = make([]int32, 0, len(mapClassIDs))
		for k := range mapClassIDs {
			mirAssetDetails[idx].JoinedClassIDs = append(mirAssetDetails[idx].JoinedClassIDs, k)
		}
	}
	return mirAssetDetails
}
