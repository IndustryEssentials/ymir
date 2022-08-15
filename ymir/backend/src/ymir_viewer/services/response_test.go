package services

import (
	"encoding/json"
	"net/http/httptest"
	"testing"

	"github.com/IndustryEssentials/ymir-viewer/common/constants"
	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

func TestViewerSuccess(t *testing.T) {
	gin.SetMode(gin.TestMode)
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)

	msg := "testing ViewerSuccess"
	ViewerSuccess(c, msg)

	expectedData := ResultVO{
		Code:    constants.ViewerSuccessCode,
		Msg:     constants.ViewerSuccessMsg,
		Success: true,
		Result:  msg,
	}
	expectedDataBytes, _ := json.Marshal(expectedData)
	assert.Equal(t, 200, w.Code)
	assert.Equal(t, expectedDataBytes, w.Body.Bytes())
}

func TestViewerFailure(t *testing.T) {

	gin.SetMode(gin.TestMode)
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)

	result := FailureResult{Code: constants.FailGeneralCode, Msg: "testing ViewerFailure"}
	ViewerFailure(
		c,
		&result,
	)

	expectedData := ResultVO{
		Code:    result.Code,
		Msg:     result.Msg,
		Success: false,
		Result:  result,
	}
	expectedDataBytes, _ := json.Marshal(expectedData)
	assert.Equal(t, 400, w.Code)
	assert.Equal(t, expectedDataBytes, w.Body.Bytes())
}
