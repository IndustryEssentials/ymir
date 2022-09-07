package loader

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path"
	"testing"

	"github.com/IndustryEssentials/ymir-viewer/common/constants"
	"github.com/IndustryEssentials/ymir-viewer/common/protos"
	"github.com/stretchr/testify/assert"
	"google.golang.org/protobuf/proto"
)

func createTestMirRepo(sandbox string) *constants.MirRepo {
	return &constants.MirRepo{
		SandboxRoot: sandbox,
		UserID:      "user",
		RepoID:      "repo",
		BranchID:    "branch",
		TaskID:      "task",
	}
}

func createGitRepo(t *testing.T, repoRoot string, fileContents map[string][]byte, tagName string) {
	os.RemoveAll(repoRoot)
	err := exec.Command("mkdir", "-p", repoRoot).Run()
	if err != nil {
		panic(err)
	}

	cmd := exec.Command("git", "init")
	cmd.Dir = repoRoot
	err = cmd.Run()
	if err != nil {
		panic(err)
	}

	for fileName, fileContent := range fileContents {
		absFileName := path.Join(repoRoot, fileName)
		err = os.WriteFile(absFileName, fileContent, 0777)
		if err != nil {
			panic(err)
		}
	}

	cmd = exec.Command("git", "add", ".")
	cmd.Dir = repoRoot
	err = cmd.Run()
	if err != nil {
		panic(err)
	}

	cmd = exec.Command("git", "commit", "-m", "\"msg\"")
	cmd.Dir = repoRoot
	err = cmd.Run()
	if err != nil {
		panic(err)
	}

	cmd = exec.Command("git", "tag", tagName)
	cmd.Dir = repoRoot
	err = cmd.Run()
	if err != nil {
		panic(err)
	}
}

func TestLoadModelInfo(t *testing.T) {
	workDir := fmt.Sprintf("%s/modelinfo", "/tmp/test1")
	//	workDir := fmt.Sprintf("%s/modelinfo", t.TempDir())
	mirRepo := createTestMirRepo(workDir)
	mirRoot, mirRev := mirRepo.BuildRepoID()

	headTaskID := "task_id"
	mirTaskMap := map[string]*protos.Task{}
	mirTaskMap[headTaskID] = &protos.Task{
		Model: &protos.ModelMeta{
			ModelHash:            "model_hash",
			MeanAveragePrecision: 0.42,
			Context:              "context",
			BestStageName:        "best_stage",
		},
		SerializedExecutorConfig: "{abc: 1}",
	}
	mirTasks := protos.MirTasks{Tasks: mirTaskMap, HeadTaskId: headTaskID}
	encodedData, _ := proto.Marshal(&mirTasks)
	createGitRepo(t, mirRoot, map[string][]byte{"tasks.mir": encodedData}, mirRev)

	expectedModel := &constants.MirdataModel{
		ModelHash:            "model_hash",
		Stages:               map[string]interface{}{},
		MeanAveragePrecision: 0.42,
		Context:              "context",
		BestStageName:        "best_stage",
		ExecutorConfig:       map[string]interface{}{"abc": 1}}

	mirRepoLoader := MirRepoLoader{}
	mirModel := mirRepoLoader.LoadModelInfo(mirRepo)
	assert.Equal(t, expectedModel, mirModel)
}

func TestLoadAssetsDetail(t *testing.T) {
	workDir := fmt.Sprintf("%s/modelinfo", "/tmp/test2")
	//	workDir := fmt.Sprintf("%s/assets_detail", t.TempDir())
	mirRepo := createTestMirRepo(workDir)
	mirRoot, mirRev := mirRepo.BuildRepoID()

	attributes := map[string]*protos.MetadataAttributes{
		"a": {},
		"b": {},
		"c": {},
	}
	mirMetadatas := &protos.MirMetadatas{Attributes: attributes}
	encodedMetadatas, _ := proto.Marshal(mirMetadatas)
	mirAnnotations := &protos.MirAnnotations{
		GroundTruth: &protos.SingleTaskAnnotations{
			ImageAnnotations: map[string]*protos.SingleImageAnnotations{
				"a": {Boxes: []*protos.ObjectAnnotation{{ClassId: 1}}},
			},
		},
		Prediction: &protos.SingleTaskAnnotations{
			ImageAnnotations: map[string]*protos.SingleImageAnnotations{
				"a": {Boxes: []*protos.ObjectAnnotation{{ClassId: 1}}},
			},
		},
		ImageCks: map[string]*protos.SingleImageCks{"a": {Cks: map[string]string{"abc": "1"}}},
	}
	encodedAnnotations, _ := proto.Marshal(mirAnnotations)
	createGitRepo(
		t,
		mirRoot,
		map[string][]byte{"metadatas.mir": encodedMetadatas, "annotations.mir": encodedAnnotations},
		mirRev,
	)

	expectedAssetsDetail := []constants.MirAssetDetail{}
	err := json.Unmarshal([]byte(`[
		{
			"asset_id": "a",
			"metadata":
			{
				"asset_type": 0,
				"byte_size": 0,
				"dataset_name": "",
				"height": 0,
				"image_channels": 0,
				"timestamp": null,
				"tvt_type": 0,
				"width": 0
			},
			"class_ids":
			[
				1
			],
			"gt":
			[
				{
					"anno_quality": 0,
					"box": null,
					"class_id": 1,
					"class_name": "",
					"cm": 0,
					"det_link_id": 0,
					"index": 0,
					"polygon": [],
					"score": 0,
					"tags":
					{}
				}
			],
			"pred":
			[
				{
					"anno_quality": 0,
					"box": null,
					"class_id": 1,
					"polygon": [],
					"class_name": "",
					"cm": 0,
					"det_link_id": 0,
					"index": 0,
					"score": 0,
					"tags":
					{}
				}
			],
			"cks":
			{
				"abc": "1"
			},
			"image_quality": 0
		},
		{
			"asset_id": "b",
			"metadata":
			{
				"asset_type": 0,
				"byte_size": 0,
				"dataset_name": "",
				"height": 0,
				"image_channels": 0,
				"timestamp": null,
				"tvt_type": 0,
				"width": 0
			},
			"class_ids":
			[],
			"gt":
			[],
			"pred":
			[],
			"cks":
			{},
			"image_quality": -1
		},
		{
			"asset_id": "c",
			"metadata":
			{
				"asset_type": 0,
				"byte_size": 0,
				"dataset_name": "",
				"height": 0,
				"image_channels": 0,
				"timestamp": null,
				"tvt_type": 0,
				"width": 0
			},
			"class_ids":
			[],
			"gt":
			[],
			"pred":
			[],
			"cks":
			{},
			"image_quality": -1
		}
	]`), &expectedAssetsDetail)
	if err != nil {
		panic(err)
	}

	mirRepoLoader := MirRepoLoader{}
	mirAssetsDetail, _, _ := mirRepoLoader.LoadAssetsDetail(mirRepo, "", 0, 0)
	assert.Equal(t, expectedAssetsDetail, mirAssetsDetail)

	mirAssetsDetailSub, _, _ := mirRepoLoader.LoadAssetsDetail(mirRepo, "a", 0, 1)
	assert.Equal(t, expectedAssetsDetail[:1], mirAssetsDetailSub)
}
