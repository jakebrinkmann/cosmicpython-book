from datetime import date, timedelta

import pytest

import model

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_prefers_current_stock_batches_to_shipments():
    RETRO_CLOCK = "RETRO-CLOCK"
    in_stock_batch = model.Batch("in-stock-batch", RETRO_CLOCK, 100, eta=None)
    shipment_batch = model.Batch("shipment-batch", RETRO_CLOCK, 100, eta=today)
    line = model.OrderLine("oref", RETRO_CLOCK, 10)

    model.allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    MINIMALIST_SPOON = "MINIMALIST-SPOON"
    earliest = model.Batch("speedy-batch", MINIMALIST_SPOON, 100, eta=today)
    medium = model.Batch("normal-batch", MINIMALIST_SPOON, 100, eta=tomorrow)
    latest = model.Batch("slow-batch", MINIMALIST_SPOON, 100, eta=later)
    line = model.OrderLine("order1", MINIMALIST_SPOON, 10)

    model.allocate(line, [medium, earliest, latest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


# NOTE: Temptation to combine tests here, and assert multiple things (e.g.
#       that the _prefers_earlier also returned the earliest.reference)
#
#       The name of the test describes the behavior.
#
# TIP: Rule of thumb: if you can't describe what your function does without using
#    words like "then" or "and," you might be violating the SRP.
def test_returns_allocated_batch_ref():
    HIGHBROW_POSTER = "HIGHBROW-POSTER"
    in_stock_batch = model.Batch("in-stock-batch-ref", HIGHBROW_POSTER, 100, eta=None)
    shipment_batch = model.Batch(
        "shipment-batch-ref", HIGHBROW_POSTER, 100, eta=tomorrow
    )
    line = model.OrderLine("oref", HIGHBROW_POSTER, 10)

    allocation = model.allocate(line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    SMALL_FORK = "SMALL-FORK"
    batch = model.Batch("batch1", SMALL_FORK, 10, eta=today)
    line1 = model.OrderLine("order1", SMALL_FORK, 10)
    line2 = model.OrderLine("order2", SMALL_FORK, 1)

    model.allocate(line1, [batch])
    with pytest.raises(model.OutOfStock, match=SMALL_FORK):
        model.allocate(line2, [batch])
