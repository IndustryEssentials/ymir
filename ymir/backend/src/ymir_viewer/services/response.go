package services

import (
	"net/http"

	"github.com/IndustryEssentials/ymir-viewer/common/constants"
	"github.com/gin-gonic/gin"
)

type ResultVO struct {
	Code    constants.ResponseCode `json:"code"`
	Msg     constants.ResponseMsg  `json:"msg"`
	Success bool                   `json:"success"`
	Result  interface{}            `json:"result"`
}

func ViewerSuccess(ctx *gin.Context, result interface{}) {
	resp := &ResultVO{Code: constants.ViewerSuccessCode, Msg: constants.ViewerSuccessMsg, Success: true, Result: result}
	ctx.JSON(http.StatusOK, resp)
}

func ViewerFailure(ctx *gin.Context, code constants.ResponseCode, msg constants.ResponseMsg, result interface{}) {
	resp := &ResultVO{Code: code, Msg: msg, Success: false, Result: result}
	ctx.JSON(http.StatusOK, resp)
}
