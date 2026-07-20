from __future__ import annotations

import math

import numpy as np
import pytest

from white_cat_visualizer.analysis.smoothing import AttackReleaseSmoother


def test_attack_changes_faster_than_release() -> None:
    smoother = AttackReleaseSmoother(1, attack=0.8, release=0.2)
    rise = float(smoother.process(np.array([1.0]))[0])

    smoother.reset(1.0)
    fall = float(smoother.process(np.array([0.0]))[0])

    assert math.isclose(rise, 0.8)
    assert math.isclose(1.0 - fall, 0.2)
    assert rise > 1.0 - fall


def test_smoother_rejects_out_of_range_target() -> None:
    smoother = AttackReleaseSmoother(2)
    with pytest.raises(ValueError, match="between 0 and 1"):
        smoother.process(np.array([0.0, 1.1]))
