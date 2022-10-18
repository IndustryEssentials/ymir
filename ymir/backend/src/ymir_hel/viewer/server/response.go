package server

import (
	"log"
	"net/http"
	"runtime/debug"

	"github.com/gin-gonic/gin"

	"github.com/IndustryEssentials/ymir-hel/common/constants"
)

type ResultVO struct {
	Code    constants.ResponseCode `json:"code"`
	Msg     string                 `json:"msg"`
	Success bool                   `json:"success"`
	Result  interface{}            `json:"result"`
}

type FailureResult struct {
	Code constants.ResponseCode `json:"code"`
	Msg  string                 `json:"msg"`
}

func ViewerSuccess(ctx *gin.Context, result interface{}) {
	resp := &ResultVO{Code: constants.CodeSuccess, Msg: "Success", Success: true, Result: result}
	ctx.JSON(http.StatusOK, resp)
}

func ViewerFailure(ctx *gin.Context, result *FailureResult) {
	resp := &ResultVO{Code: result.Code, Msg: result.Msg, Success: false, Result: result}
	ctx.JSON(http.StatusBadRequest, resp)
	log.Printf("ViewerFailure\n%#v\n%s\n", *result, debug.Stack())
}

func ViewerFailureFromErr(ctx *gin.Context, err error) {
	errString := err.Error()
	errCode := constants.CodeViewerGeneral

	switch errString {
	case "unknown ref":
		errCode = constants.CodeViewerRepoNotExist
	}

	result := FailureResult{
		Code: errCode,
		Msg:  errString,
	}
	ViewerFailure(ctx, &result)
}
