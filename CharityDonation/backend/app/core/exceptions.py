class AppError(Exception):
    def __init__(self, message: str, code: str, status_code: int):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found", code: str = "not_found"):
        super().__init__(message, code, 404)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized", code: str = "unauthorized"):
        super().__init__(message, code, 401)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden", code: str = "forbidden"):
        super().__init__(message, code, 403)


class ConflictError(AppError):
    def __init__(self, message: str = "Conflict", code: str = "conflict"):
        super().__init__(message, code, 409)


class BadRequestError(AppError):
    def __init__(self, message: str = "Bad request", code: str = "bad_request"):
        super().__init__(message, code, 400)
