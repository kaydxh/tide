from google.protobuf import descriptor_pb2 as _descriptor_pb2
from types import error_pb2 as _error_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NowRequest(_message.Message):
    __slots__ = ("request_id", "data")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    data: bytes
    def __init__(self, request_id: _Optional[str] = ..., data: _Optional[bytes] = ...) -> None: ...

class NowResponse(_message.Message):
    __slots__ = ("request_id", "date", "error")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    date: str
    error: _error_pb2.Error
    def __init__(self, request_id: _Optional[str] = ..., date: _Optional[str] = ..., error: _Optional[_Union[_error_pb2.Error, _Mapping]] = ...) -> None: ...

class NowErrorRequest(_message.Message):
    __slots__ = ("request_id",)
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    def __init__(self, request_id: _Optional[str] = ...) -> None: ...

class NowErrorResponse(_message.Message):
    __slots__ = ("request_id", "date", "error")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    date: str
    error: _error_pb2.Error
    def __init__(self, request_id: _Optional[str] = ..., date: _Optional[str] = ..., error: _Optional[_Union[_error_pb2.Error, _Mapping]] = ...) -> None: ...
