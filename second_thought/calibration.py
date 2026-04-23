"""Confidence calibration helpers."""

from __future__ import annotations

import math


def calibrate_confidence(raw: float, slope: float = 1.0, intercept: float = 0.0) -> float:
    raw = max(1e-6, min(1 - 1e-6, raw))
    logit = math.log(raw / (1.0 - raw))
    adjusted = (logit * slope) + intercept
    calibrated = 1.0 / (1.0 + math.exp(-adjusted))
    return max(0.01, min(0.99, calibrated))
