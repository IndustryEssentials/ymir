package loader

import (
	"encoding/json"
	"log"
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

type MirRepoLoader struct {
}

func (l *MirRepoLoader) LoadSingleMirData(
	mirRepo *constants.MirRepo,
	mirFile constants.MirFile,
) interface{} {
	return l.LoadMutipleMirDatas(mirRepo, []constants.MirFile{mirFile})[0]
}

func (l *MirRepoLoader) LoadMutipleMirDatas(
	mirRepo *constants.MirRepo,
	mirFiles []constants.MirFile,
) []interface{} {
	defer tools.TimeTrack(time.Now())
	mirRoot, mirRev := mirRepo.BuildRepoID()

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

func (l *MirRepoLoader) buildStructFromMessage(message proto.Message, structOut interface{}) interface{} {
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

func (l *MirRepoLoader) LoadModelInfo(mirRepo *constants.MirRepo) *constants.MirdataModel {
	mirTasks := l.LoadSingleMirData(mirRepo, constants.MirfileTasks).(*protos.MirTasks)
	task := mirTasks.Tasks[mirTasks.HeadTaskId]
	modelData := constants.NewMirdataModel(task.SerializedTaskParameters)
	if task.SerializedExecutorConfig != "" {
		if err := yaml.Unmarshal([]byte(task.SerializedExecutorConfig), &modelData.ExecutorConfig); err != nil {
			panic(err)
		}
	}
	l.buildStructFromMessage(task.Model, &modelData)
	return modelData
}

func (l *MirRepoLoader) LoadAssetsDetail(
	mirRepo *constants.MirRepo,
	anchorAssetID string,
	offset int,
	limit int,
) ([]constants.MirAssetDetail, int64, int64) {
	defer tools.TimeTrack(time.Now())
	filesToLoad := []constants.MirFile{constants.MirfileMetadatas, constants.MirfileAnnotations}
	mirDatas := l.LoadMutipleMirDatas(mirRepo, filesToLoad)
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

	assetIDs := make([]string, 0)
	for assetID := range mirMetadatas.Attributes {
		assetIDs = append(assetIDs, assetID)
	}
	sort.Strings(assetIDs)

	anchorIdx := 0
	// Taking shortcut, only return a "limit" subset of assetIds.
	if limit > 0 {
		if len(anchorAssetID) > 0 {
			for idx, assetID := range assetIDs {
				if assetID == anchorAssetID {
					anchorIdx = idx
					break
				}
			}
		}

		start := anchorIdx + offset
		if start > len(assetIDs) {
			start = len(assetIDs)
		}
		end := anchorIdx + offset + limit
		if end > len(assetIDs) {
			end = len(assetIDs)
		}
		assetIDs = assetIDs[start:end]
		log.Printf(" shortcut: anchorIdx %d, offset %d, limit %d assets %d\n", anchorIdx, offset, limit, len(assetIDs))
	}
	mirAssetDetails := make([]constants.MirAssetDetail, len(assetIDs))

	for idx, assetID := range assetIDs {
		mirAssetDetails[idx] = constants.NewMirAssetDetail()
		mirAssetDetails[idx].AssetID = assetID
		l.buildStructFromMessage(mirMetadatas.Attributes[assetID], &mirAssetDetails[idx].MetaData)
		if cks, ok := mirCks[assetID]; ok {
			if len(cks.Cks) > 0 {
				mirAssetDetails[idx].Cks = cks.Cks
			}
			mirAssetDetails[idx].Quality = cks.ImageQuality
		}

		mapClassIDs := map[int32]bool{}
		if gtAnnotation, ok := gtAnnotations[assetID]; ok {
			for _, annotation := range gtAnnotation.Annotations {
				annotationOut := l.buildStructFromMessage(annotation, map[string]interface{}{}).(map[string]interface{})
				mirAssetDetails[idx].Gt = append(mirAssetDetails[idx].Gt, annotationOut)
				mapClassIDs[annotation.ClassId] = true
			}
		}
		if predAnnotation, ok := predAnnotations[assetID]; ok {
			for _, annotation := range predAnnotation.Annotations {
				annotationOut := l.buildStructFromMessage(annotation, map[string]interface{}{}).(map[string]interface{})
				mirAssetDetails[idx].Pred = append(mirAssetDetails[idx].Pred, annotationOut)
				mapClassIDs[annotation.ClassId] = true
			}
		}

		mirAssetDetails[idx].JoinedClassIDs = make([]int32, 0, len(mapClassIDs))
		for k := range mapClassIDs {
			mirAssetDetails[idx].JoinedClassIDs = append(mirAssetDetails[idx].JoinedClassIDs, k)
		}
	}
	return mirAssetDetails, int64(anchorIdx), int64(len(mirMetadatas.Attributes))
}
