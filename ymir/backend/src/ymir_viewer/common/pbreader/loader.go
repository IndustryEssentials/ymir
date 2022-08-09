package pbreader

import (
	"encoding/json"
	"sort"
	"time"

	"gopkg.in/yaml.v3"

	"github.com/vektra/gitreader"
	"google.golang.org/protobuf/encoding/protojson"
	"google.golang.org/protobuf/proto"

	"github.com/IndustryEssentials/ymir-viewer/common/constant"
	"github.com/IndustryEssentials/ymir-viewer/common/protos"
	"github.com/IndustryEssentials/ymir-viewer/tools"
)

func LoadSingleMirData(mirRepo constant.MirRepo, mirFile constant.MirFile) interface{} {
	return LoadMutipleMirDatas(mirRepo, []constant.MirFile{mirFile})[0]
}

func LoadMutipleMirDatas(mirRepo constant.MirRepo, mirFiles []constant.MirFile) []interface{} {
	defer tools.TimeTrack(time.Now())
	mirRoot, mirRev := mirRepo.BuildRepoId()

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

func LoadModelInfo(repoId constant.MirRepo) constant.MirdataModel {
	mirTasks := LoadSingleMirData(repoId, constant.MirfileTasks).(*protos.MirTasks)
	task := mirTasks.Tasks[mirTasks.HeadTaskId]
	modelData := constant.NewMirdataModel(task.SerializedTaskParameters)
	if task.SerializedExecutorConfig != "" {
		if err := yaml.Unmarshal([]byte(task.SerializedExecutorConfig), &modelData.ExecutorConfig); err != nil {
			panic(err)
		}
	}
	BuildStructFromMessage(task.Model, &modelData)
	return modelData
}

func LoadAssetsInfo(repoId constant.MirRepo) []constant.MirAssetDetail {
	defer tools.TimeTrack(time.Now())
	filesToLoad := []constant.MirFile{constant.MirfileMetadatas, constant.MirfileAnnotations}
	mirDatas := LoadMutipleMirDatas(repoId, filesToLoad)
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

	mirAssetDetails := make([]constant.MirAssetDetail, len(mirMetadatas.Attributes))
	assetIds := make([]string, 0)
	for assetId := range mirMetadatas.Attributes {
		assetIds = append(assetIds, assetId)
	}
	sort.Strings(assetIds)
	for idx, assetId := range assetIds {
		mirAssetDetails[idx] = constant.NewMirAssetDetail()
		mirAssetDetails[idx].AssetId = assetId
		BuildStructFromMessage(mirMetadatas.Attributes[assetId], &mirAssetDetails[idx].MetaData)
		if cks, ok := mirCks[assetId]; ok {
			mirAssetDetails[idx].Cks = cks.Cks
		}

		if gtAnnotation, ok := gtAnnotations[assetId]; ok {
			for _, annotation := range gtAnnotation.Annotations {
				annotationOut := BuildStructFromMessage(annotation, map[string]interface{}{}).(map[string]interface{})
				mirAssetDetails[idx].Gt = append(mirAssetDetails[idx].Gt, annotationOut)
			}
		}
		if predAnnotation, ok := predAnnotations[assetId]; ok {
			for _, annotation := range predAnnotation.Annotations {
				annotationOut := BuildStructFromMessage(annotation, map[string]interface{}{}).(map[string]interface{})
				mirAssetDetails[idx].Pred = append(mirAssetDetails[idx].Pred, annotationOut)
			}
		}
	}
	return mirAssetDetails
}
