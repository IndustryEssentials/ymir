package services

import (
	"net/http"

	"github.com/IndustryEssentials/ymir-viewer/common/constants"
	"github.com/gin-gonic/gin"
)

type ResultVO struct {
	Code    constants.ResponseCode `json:"code"`
	Msg     constants.ResponseMsg  `json:"msg"`
	Success bool                  `json:"success"`
	Data    interface{}           `json:"data"`
}

func ViewerSuccess(ctx *gin.Context, code constants.ResponseCode, msg constants.ResponseMsg, data interface{}) {
	resp := &ResultVO{Code: code, Msg: msg, Success: true, Data: data}
	ctx.JSON(http.StatusOK, resp)
}

func ViewerFailure(ctx *gin.Context, code constants.ResponseCode, msg constants.ResponseMsg, data interface{}) {
	resp := &ResultVO{Code: code, Msg: msg, Success: false, Data: data}
	ctx.JSON(http.StatusInternalServerError, resp)
}
