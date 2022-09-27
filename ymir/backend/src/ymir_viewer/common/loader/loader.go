package loader

import (
	"gopkg.in/yaml.v3"

	"github.com/vektra/gitreader"
	"google.golang.org/protobuf/proto"

	"github.com/IndustryEssentials/ymir-viewer/common/constants"
	"github.com/IndustryEssentials/ymir-viewer/common/protos"
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

func (l *MirRepoLoader) LoadModelInfo(mirRepo *constants.MirRepo) *constants.MirdataModel {
	mirTasks := l.LoadSingleMirData(mirRepo, constants.MirfileTasks).(*protos.MirTasks)
	task := mirTasks.Tasks[mirTasks.HeadTaskId]
	modelData := constants.NewMirdataModel(task.SerializedTaskParameters)
	if task.SerializedExecutorConfig != "" {
		if err := yaml.Unmarshal([]byte(task.SerializedExecutorConfig), &modelData.ExecutorConfig); err != nil {
			panic(err)
		}
	}
	constants.BuildStructFromMessage(task.Model, &modelData)
	if len(modelData.ModelHash) < 1 {
		panic("invalid model")
	}
	return modelData
}
