package constants

type ResponseCode int

const (
	CodeSuccess ResponseCode = 0

	// Viewer Error Code
	CodeViewerGeneral      ResponseCode = 180100
	CodeViewerDataMiss     ResponseCode = 180101
	CodeViewerInvalidParms ResponseCode = 180102
	CodeViewerRepoNotExist ResponseCode = 180103
)
