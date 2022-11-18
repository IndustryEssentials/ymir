package constants

import "github.com/IndustryEssentials/ymir-hel/protos"

type ResponseCode int

const (
	CodeSuccess ResponseCode = 0

	// Viewer Error Code
	CodeViewerGeneral      ResponseCode = 180100
	CodeViewerDataMiss     ResponseCode = 180101
	CodeViewerInvalidParms ResponseCode = 180102
	CodeViewerRepoNotExist ResponseCode = 180103

	// Hel Error Code
	CodeHelGeneral      ResponseCode = 180200
	CodeHelInvalidParms ResponseCode = 180201
	CodeHelNvmlError    ResponseCode = 180210
)

func HelOpsRespMessage(code ResponseCode, request *protos.HelOpsRequest) *protos.HelOpsResponse {
	return &protos.HelOpsResponse{Code: int32(code), Request: request}
}

func HelTaskRespMessage(code ResponseCode, request *protos.HelTaskRequest) *protos.HelTaskResponse {
	return &protos.HelTaskResponse{Code: int32(code), Request: request}
}
