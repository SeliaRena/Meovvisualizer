from __future__ import annotations

from white_cat_visualizer.runtime.latest_frame import LatestFrameSlot


def test_latest_frame_slot_has_fixed_single_item_capacity() -> None:
    slot: LatestFrameSlot[int] = LatestFrameSlot()

    assert slot.capacity == 1
    assert slot.pending_count == 0

    assert slot.publish(1) is True
    assert slot.publish(2) is False
    assert slot.publish(3) is False
    assert slot.replacement_count == 2

    assert slot.capacity == 1
    assert slot.pending_count == 1
    assert slot.take() == 3
    assert slot.pending_count == 0
    assert slot.take() is None


def test_clear_discards_the_pending_value() -> None:
    slot: LatestFrameSlot[str] = LatestFrameSlot()
    slot.publish("pending")

    slot.clear()

    assert slot.pending_count == 0
    assert slot.take() is None


def test_replacement_statistics_reset_without_discarding_pending_data() -> None:
    slot: LatestFrameSlot[int] = LatestFrameSlot()
    slot.publish(1)
    slot.publish(2)

    slot.reset_statistics()

    assert slot.replacement_count == 0
    assert slot.take() == 2
