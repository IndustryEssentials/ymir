package client

import (
	"encoding/json"
	"fmt"
	"log"
	"time"

	"github.com/IndustryEssentials/ymir-hel/common/constants"
	"github.com/IndustryEssentials/ymir-hel/viewer/server"
	"github.com/go-resty/resty/v2"
)

func IndexDataset(viewerURI string, userID string, repoID string, taskID string) error {
	log.Printf("[viewer client] IndexDataset URI: %s", viewerURI)

	requestURL := fmt.Sprintf(
		"http://%s/api/v1/users/%s/repo/%s/branch/%s/dataset_meta_count?check_index_only",
		viewerURI,
		userID,
		repoID,
		taskID,
	)
	var resultData constants.QueryDatasetStatsResult
	checkedCounts := 0
	for {
		log.Printf("[viewer client] indexing %s at interval %d", taskID, checkedCounts)
		err := sendHttpRequestGet(requestURL, &resultData, false)
		if err != nil {
			panic(err)
		}

		if resultData.QueryContext.RepoIndexReady {
			break
		}

		// Expect to start indexing process (RepoIndexExist==true) after the first call, throw error if not.
		if checkedCounts > 1 && !resultData.QueryContext.RepoIndexExist {
			panic(fmt.Sprintf("[viewer client] checked %s %d intervals, still not indexing\n", taskID, checkedCounts))
		}

		time.Sleep(5 * time.Second)
		checkedCounts += 1
	}
	log.Printf("[viewer client] index %s ready, cost %d intervals", taskID, checkedCounts)
	return nil
}

func QueryDataset(viewerURI string, userID string, repoID string, taskID string) error {
	log.Printf("[viewer client] QueryDataset URI: %s", viewerURI)

	requestURL := fmt.Sprintf(
		"http://%s/api/v1/users/%s/repo/%s/branch/%s/dataset_meta_count",
		viewerURI,
		userID,
		repoID,
		taskID,
	)
	var resultData constants.QueryDatasetStatsResult
	return sendHttpRequestGet(requestURL, &resultData, true)
}

func sendHttpRequestGet(requestURL string, resultData interface{}, printResult bool) (err error) {
	client := resty.New()
	var result *server.ResultVO

	// Send request and check resp
	resp, err := client.SetRetryCount(2).
		SetRetryWaitTime(1 * time.Second).
		R().
		SetResult(&result).
		Get(requestURL)
	if resp.StatusCode() != 200 || err != nil {
		panic(fmt.Sprintf("sendHttpRequestGet fail, Code: %d\nerr: %+v\n", resp.StatusCode(), err))
	}
	if result.Code != 0 {
		panic(fmt.Sprintf("viewer server error, Code: %d\nerr: %+v\n", result.Code, result))
	}

	// Parse result data
	jsonBytes, err := json.Marshal(result.Result)
	if err != nil {
		panic(err)
	}
	if err := json.Unmarshal(jsonBytes, &resultData); err != nil {
		panic(err)
	}

	if printResult {
		b, _ := json.MarshalIndent(resultData, "", "  ")
		fmt.Println("ResultData: \n" + string(b))
	}

	return err
}
