package constant

type ResponseCode int
type ResponseMsg string

const (
	ViewerSuccessCode ResponseCode = 0
	ViewerSuccessMsg  ResponseMsg  = "Success"

	FailDataMissCode ResponseCode = 180100
	FailDataMissMsg  ResponseMsg  = "Data not exist"
)
