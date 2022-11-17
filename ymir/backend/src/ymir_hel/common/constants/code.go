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
	CodeHelGeneral   ResponseCode = 180200
	CodeHelNvmlError ResponseCode = 180201
)

func HelRespMessage(code ResponseCode) *protos.HelResponse {
	return &protos.HelResponse{Code: int32(code)}
}
