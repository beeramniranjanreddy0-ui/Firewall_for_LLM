from __future__ import annotations


def norm(values, axis=None, keepdims=False):
    if isinstance(values, list):
        if values and isinstance(values[0], list):
            rows = []
            for row in values:
                row_norm = sum(float(v) * float(v) for v in row) ** 0.5
                rows.append(row_norm)
            if axis == 1:
                return rows
            if axis is None:
                return rows[0] if len(rows) == 1 else rows
        else:
            return sum(float(v) * float(v) for v in values) ** 0.5
    return 0.0
