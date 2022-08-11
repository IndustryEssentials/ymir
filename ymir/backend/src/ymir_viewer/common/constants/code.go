package constants

type ResponseCode int
type ResponseMsg string

const (
	ViewerSuccessCode ResponseCode = 0
	ViewerSuccessMsg  ResponseMsg  = "Success"

	FailGeneralCode ResponseCode = 180100
	FailGeneralMsg  ResponseMsg  = "Viewer Failure"

	FailDataMissCode ResponseCode = 180101
	FailDataMissMsg  ResponseMsg  = "Data not exist"

	FailInvalidParmsCode ResponseCode = 180102
	FailInvalidParmsMsg  ResponseMsg  = "Invalid parameters"
)
