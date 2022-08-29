package services

import (
	"log"
	"net/http"
	"runtime/debug"

	"github.com/IndustryEssentials/ymir-viewer/common/constants"
	"github.com/gin-gonic/gin"
)

type ResultVO struct {
	Code    constants.ResponseCode `json:"code"`
	Msg     constants.ResponseMsg  `json:"msg"`
	Success bool                   `json:"success"`
	Result  interface{}            `json:"result"`
}

type FailureResult struct {
	Code constants.ResponseCode `json:"code"`
	Msg  constants.ResponseMsg  `json:"msg"`
}

func ViewerSuccess(ctx *gin.Context, result interface{}) {
	resp := &ResultVO{Code: constants.ViewerSuccessCode, Msg: constants.ViewerSuccessMsg, Success: true, Result: result}
	ctx.JSON(http.StatusOK, resp)
}

func ViewerFailure(ctx *gin.Context, result *FailureResult) {
	resp := &ResultVO{Code: result.Code, Msg: result.Msg, Success: false, Result: result}
	ctx.JSON(http.StatusBadRequest, resp)
	log.Printf("ViewerFailure\n%#v\n%s\n", *result, debug.Stack())
}

func ViewerFailureFromErr(ctx *gin.Context, err error) {
	errString := err.Error()
	errCode := constants.FailGeneralCode

	switch errString {
	case "unknown ref":
		errCode = constants.FailRepoNotExistCode
	}

	result := FailureResult{
		Code: errCode,
		Msg:  constants.ResponseMsg(errString),
	}
	ViewerFailure(ctx, &result)
}
