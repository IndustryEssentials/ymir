package loader

import (
	"crypto/rand"
	"encoding/json"
	"fmt"
	"math/big"
	"os"
	"path"
	"testing"

	"github.com/IndustryEssentials/ymir-viewer/common/constants"
	"github.com/IndustryEssentials/ymir-viewer/common/protos"
	"github.com/go-git/go-git/v5"
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
	r, _ := git.PlainInit(repoRoot, false)
	w, _ := r.Worktree()

	for fileName, fileContent := range fileContents {
		absFileName := path.Join(repoRoot, fileName)
		os.WriteFile(absFileName, fileContent, 0644)
		w.Add(fileName)
	}
	commitHash, _ := w.Commit("git commit", &git.CommitOptions{All: true})
	r.CreateTag(tagName, commitHash, nil)
}

func TestGetMirRepo(t *testing.T) {
	mirRepo := createTestMirRepo("")
	mirRepoLoader := MirRepoLoader{mirRepo}
	retMirRepo := mirRepoLoader.GetMirRepo()
	assert.Equal(t, mirRepo, retMirRepo)
}

func getRandTestDir() string {
	nBig, _ := rand.Int(rand.Reader, big.NewInt(10000))
	return fmt.Sprintf("%s/test-%03d", os.TempDir(), nBig)
}

func TestLoadModelInfo(t *testing.T) {
	workDir := path.Join(getRandTestDir(), "modelinfo")

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

	expectedModel := constants.MirdataModel{ModelHash: "model_hash",
		Stages:               map[string]interface{}{},
		MeanAveragePrecision: 0.42,
		Context:              "context",
		BestStageName:        "best_stage",
		ExecutorConfig:       map[string]interface{}{"abc": 1}}
	mirRepoLoader := MirRepoLoader{mirRepo}
	mirModel := mirRepoLoader.LoadModelInfo()
	assert.Equal(t, expectedModel, mirModel)

	os.RemoveAll(workDir)
}

func TestLoadAssetsDetail(t *testing.T) {
	workDir := path.Join(getRandTestDir(), "assets_detail")

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
				"a": {Annotations: []*protos.Annotation{{ClassId: 1}}},
			},
		},
		Prediction: &protos.SingleTaskAnnotations{
			ImageAnnotations: map[string]*protos.SingleImageAnnotations{
				"a": {Annotations: []*protos.Annotation{{ClassId: 1}}},
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
					"cm": 0,
					"det_link_id": 0,
					"index": 0,
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

	mirRepoLoader := MirRepoLoader{mirRepo}
	mirAssetsDetail, _, _ := mirRepoLoader.LoadAssetsDetail("", 0, 0)
	assert.Equal(t, expectedAssetsDetail, mirAssetsDetail)

	mirAssetsDetailSub, _, _ := mirRepoLoader.LoadAssetsDetail("a", 0, 1)
	assert.Equal(t, expectedAssetsDetail[:1], mirAssetsDetailSub)

	os.RemoveAll(workDir)
}
