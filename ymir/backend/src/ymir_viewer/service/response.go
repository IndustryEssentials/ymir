package service

import (
	"net/http"

	"github.com/IndustryEssentials/ymir-viewer/common/constant"
	"github.com/gin-gonic/gin"
)


type ResultVO struct {
	Code    constant.ResponseCode `json:"code"`
	Msg     constant.ResponseMsg  `json:"msg"`
	Success bool                  `json:"success"`
	Data    interface{}           `json:"data"`
}

func ViewerSuccess(ctx *gin.Context, code constant.ResponseCode, msg constant.ResponseMsg, data interface{}) {
	resp := &ResultVO{Code: code, Msg: msg, Success: true, Data: data}
	ctx.JSON(http.StatusOK, resp)
}

func ViewerFailure(ctx *gin.Context, code constant.ResponseCode, msg constant.ResponseMsg, data interface{}) {
	resp := &ResultVO{Code: code, Msg: msg, Success: false, Data: data}
	ctx.JSON(http.StatusInternalServerError, resp)
}