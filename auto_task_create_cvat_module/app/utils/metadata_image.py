class MetadataImage:
    def __init__(self):
        self._width: int = None
        self._height: int = None
        self._bufferSizeBytes: int = None
        self._strideBytes: int = None
        self._bitsPerPixel: int = None
        self._payloadType: int = None
        self._validPayloadSizeBytes: int = None
        self._timestamp: float = None
        self._frameID: int = None
        self._imageSize: int = None

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, value: int):
        self._width = value

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, value: int):
        self._height = value

    @property
    def bufferSizeBytes(self) -> int:
        return self._bufferSizeBytes

    @bufferSizeBytes.setter
    def bufferSizeBytes(self, value: int):
        self._bufferSizeBytes = value

    @property
    def strideBytes(self) -> int:
        return self._strideBytes

    @strideBytes.setter
    def strideBytes(self, value: int):
        self._strideBytes = value

    @property
    def bitsPerPixel(self) -> int:
        return self._bitsPerPixel

    @bitsPerPixel.setter
    def bitsPerPixel(self, value: int):
        self._bitsPerPixel = value

    @property
    def payloadType(self) -> int:
        return self._payloadType

    @payloadType.setter
    def payloadType(self, value: int):
        self._payloadType = value

    @property
    def validPayloadSizeBytes(self) -> int:
        return self._validPayloadSizeBytes

    @validPayloadSizeBytes.setter
    def validPayloadSizeBytes(self, value: int):
        self._validPayloadSizeBytes = value

    @property
    def timestamp(self) -> float:
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: float):
        self._timestamp = value

    @property
    def frameID(self) -> int:
        return self._frameID

    @frameID.setter
    def frameID(self, value: int):
        self._frameID = value

    @property
    def imageSize(self) -> int:
        return self._imageSize

    @imageSize.setter
    def imageSize(self, value: int):
        self._imageSize = value
