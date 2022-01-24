# import rai_trx.libs.error_codes as codes


class VizException(Exception):

    def __init__(self, http_code: int=400, message:str="Exception Occured", code:int=140000):
        super().__init__()
        self.http_code = http_code
        self.code = code
        self.message = message

    def __str__(self):
        return f'error_code: {self.code}, message: {self.message}'

    def to_dict(self):
        return {
            'http_code': self.http_code,
            'code': self.code,
            'message': self.message,
        }


class RaiTrxExceptionWithTrx(RaiTrxException):

    def __init__(self, message=None, error_code=None,
                 http_code=None, trx=None):
        super(RaiTrxExceptionWithTrx, self).__init__(
            message, error_code, http_code)
        self.trx = trx


class NotFound(RaiTrxException):
    http_code = 404


class Unauthorized(RaiTrxException):
    http_code = 401


class Forbidden(RaiTrxException):
    http_code = 403


class InternalError(RaiTrxException):
    http_code = 500


class ServiceUnavailable(RaiTrxException):
    http_code = 503


class UnexpectedError(InternalError):
    error_code = codes.UNEXPECTED_ERROR
    message = "Unexpected error"


class InvalidParameter(RaiTrxException):
    error_code = codes.INVALID_PARAMETER
    message = "Invalid parameter"


class InvalidImages(RaiTrxException):
    error_code = codes.INVALID_IMAGES
    message = 'Invalid layer images'


class LoginRequired(Unauthorized):
    error_code = codes.LOGIN_REQUIRED
    message = "User key not exist"


class AdminRequired(Unauthorized):
    code = 401
    error_code = codes.ADMIN_REQUIRED
    message = "Admin Token Not Provided"


class UserKeyNotExist(Forbidden):
    error_code = codes.USER_KEY_NOT_EXIST
    message = 'User key not exist'


class CabinetNotFound(NotFound):
    error_code = codes.CABINET_NOT_FOUND
    message = "Cabinet not found"


class CabinetUnavailable(ServiceUnavailable):
    error_code = codes.CABINET_UNAVAILABLE
    message = "Cabinet unavailable"


class LicenseNotFound(NotFound):
    error_code = codes.LICENSE_NOT_FOUND
    message = 'License not found'


class LicenseExpired(Forbidden):
    error_code = codes.LICENSE_EXPIRED
    message = 'License expired'


class BundleNotFound(NotFound):
    error_code = codes.BUNDLE_NOT_FOUND
    message = 'Bundle not found'


class BundleNotApproval(ServiceUnavailable):
    error_code = codes.BUNDLE_NOT_APPROVAL
    message = 'Bundle not approval'


class ModelNotFound(NotFound):
    error_code = codes.MODEL_NOT_FOUND
    message = 'Model not found'


class ModelNotReady(ServiceUnavailable):
    error_code = codes.MODEL_NOT_READY
    message = 'Model not ready'


class TrxNotFound(NotFound):
    error_code = codes.TRX_NOT_FOUND
    message = 'Transaction not found'


class TrxExceptional(InternalError):
    error_code = codes.TRX_EXCEPTIONAL
    message = 'Transaction status is exceptional'


class TrxEndedByOther(InternalError):
    error_code = codes.TRX_EXCEPTIONAL
    message = 'Transaction has been ended by another process'


class ImageDetectFailed(InternalError):
    error_code = codes.IMAGE_DETECT_FAILED
    message = 'Failed to detect image'


class AnomalyDetectFailed(InternalError):
    error_code = codes.ANOMALY_DETECT_FAILED
    message = 'Failed to anomaly detect image'


class TrxCannotAccess(Forbidden):
    error_code = codes.TRX_CANNOT_ACCESS
    message = "Transaction cannot access"


class ReplNotFound(NotFound):
    error_code = codes.REPL_NOT_FOUND
    message = 'Replenishment not found'


class ReplExceptional(InternalError):
    error_code = codes.REPL_EXCEPTIONAL
    message = 'Replenishment status is exceptional'


class ReplCannotAccess(Forbidden):
    error_code = codes.REPL_CANNOT_ACCESS
    message = "Replenishment cannot access"


class SnapshotNotFound(NotFound):
    error_code = codes.SNAPSHOT_NOT_FOUND
    message = 'Snapshot not found'


class TrxReportNotFound(NotFound):
    error_code = codes.TRX_REPORT_NOT_FOUND
    message = 'Transaction report not found'


class InventoryNotFound(NotFound):
    error_code = codes.INVENTORY_NOT_FOUND
    message = 'Inventory not found'


class CabinetIPCNotFound(NotFound):
    error_code = codes.CABINET_IPC_NOT_FOUND
    message = 'CabinetIPC not found'


class CabinetTypeNotFound(NotFound):
    error_code = codes.CABINET_TYPE_NOT_FOUND
    message = 'CabinetType not found'
