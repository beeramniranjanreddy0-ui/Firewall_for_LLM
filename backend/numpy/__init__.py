from __future__ import annotations

from . import linalg


class NDArray:
    def __init__(self, data, dtype=None):
        self._data = self._normalize(data)
        self.dtype = dtype or float

    @staticmethod
    def _normalize(data):
        if isinstance(data, NDArray):
            return data._data
        if isinstance(data, (list, tuple)):
            if data and isinstance(data[0], (list, tuple)):
                return [NDArray._normalize(item) for item in data]
            return [float(item) if isinstance(item, (int, float)) else item for item in data]
        return float(data) if isinstance(data, (int, float)) else data

    @staticmethod
    def _as_list(data):
        if isinstance(data, NDArray):
            return data._data
        return data

    @property
    def ndim(self) -> int:
        return self._ndim(self._data)

    @property
    def shape(self):
        return self._shape(self._data)

    def _ndim(self, data) -> int:
        if isinstance(data, list):
            if data and isinstance(data[0], list):
                return 1 + self._ndim(data[0])
            return 1
        return 0

    def _shape(self, data):
        if not isinstance(data, list):
            return ()
        if not data:
            return (0,)
        if isinstance(data[0], list):
            return (len(data),) + self._shape(data[0])
        return (len(data),)

    @property
    def ndim(self) -> int:
        return self._ndim(self._data)

    def _ndim(self, data) -> int:
        if isinstance(data, list):
            if data and isinstance(data[0], list):
                return 2
            return 1
        return 0

    def astype(self, dtype):
        return NDArray(self._data, dtype=dtype)

    def sum(self):
        return self._sum(self._data)

    def _sum(self, data):
        if isinstance(data, list):
            if data and isinstance(data[0], list):
                return sum(self._sum(row) for row in data)
            return sum(float(item) for item in data)
        return float(data)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return NDArray([item / other for item in self._data], dtype=self.dtype)
        if isinstance(other, NDArray):
            return NDArray([left / right if right else 0.0 for left, right in zip(self._data, other._data)], dtype=self.dtype)
        return NDArray(self._data, dtype=self.dtype)

    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
            return NDArray([other / item for item in self._data], dtype=self.dtype)
        return NDArray(self._data, dtype=self.dtype)

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, index):
        value = self._data[index]
        if isinstance(value, list):
            return NDArray(value)
        return value

    def __setitem__(self, index, value):
        self._data[index] = value

    @property
    def size(self) -> int:
        if isinstance(self._data, list):
            if self._data and isinstance(self._data[0], list):
                return len(self._data) * len(self._data[0])
            return len(self._data)
        return 1

    def __repr__(self) -> str:
        return repr(self._data)

    def tolist(self):
        return self._data


float32 = float
ndarray = NDArray


def array(data, dtype=None):
    return NDArray(data, dtype=dtype)


def zeros(shape, dtype=None):
    if isinstance(shape, tuple):
        if len(shape) == 0:
            return NDArray(0, dtype=dtype)
        if len(shape) == 1:
            return NDArray([0] * shape[0], dtype=dtype)
        return NDArray([[0] * shape[1] for _ in range(shape[0])], dtype=dtype)
    return NDArray([0] * shape, dtype=dtype)


def expand_dims(arr, axis=0):
    if axis != 0:
        raise NotImplementedError("Only axis=0 is supported in the lightweight numpy fallback")
    if isinstance(arr, NDArray):
        arr = arr._data
    return NDArray([arr])


def dot(a, b):
    left = a._data if isinstance(a, NDArray) else a
    right = b._data if isinstance(b, NDArray) else b
    if isinstance(left, list) and isinstance(right, list) and left and isinstance(left[0], list):
        return NDArray([sum(left_row[i] * right[i] for i in range(len(right))) for left_row in left])
    if isinstance(left, list) and isinstance(right, list):
        return sum(left[i] * right[i] for i in range(min(len(left), len(right))))
    return left * right


def clip(arr, a_min, a_max):
    values = arr._data if isinstance(arr, NDArray) else arr
    if isinstance(values, list):
        if values and isinstance(values[0], list):
            return NDArray([[min(max(item, a_min), a_max) for item in row] for row in values])
        return NDArray([min(max(item, a_min), a_max) for item in values])
    return min(max(values, a_min), a_max)


class linalg_module:
    norm = staticmethod(linalg.norm)


linalg = linalg_module()

__version__ = "1.26.0"
