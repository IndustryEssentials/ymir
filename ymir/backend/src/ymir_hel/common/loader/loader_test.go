package loader

import (
	"fmt"
	"os"
	"os/exec"
	"path"
	"testing"

	"github.com/IndustryEssentials/ymir-hel/common/constants"
	"github.com/IndustryEssentials/ymir-hel/protos"
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
			ModelHash:     "model_hash",
			MAP:           0.42,
			Context:       "context",
			BestStageName: "best_stage",
		},
		SerializedExecutorConfig: "{abc: 1}",
	}
	mirTasks := protos.MirTasks{Tasks: mirTaskMap, HeadTaskId: headTaskID}
	encodedData, _ := proto.Marshal(&mirTasks)
	createGitRepo(t, mirRoot, map[string][]byte{"tasks.mir": encodedData}, mirRev)

	expectedModel := &constants.MirdataModel{
		ModelHash:      "model_hash",
		Stages:         map[string]interface{}{},
		MAP:            0.42,
		Context:        "context",
		BestStageName:  "best_stage",
		ExecutorConfig: map[string]interface{}{"abc": 1}}

	mirRepoLoader := MirRepoLoader{}
	mirModel := mirRepoLoader.LoadModelInfo(mirRepo)
	assert.Equal(t, expectedModel, mirModel)
}
