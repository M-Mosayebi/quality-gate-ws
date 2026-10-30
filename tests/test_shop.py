import pytest
from app.shop import (
    calculate_total,
    apply_discount,
    shipping_cost,
    loyalty_points,
)


def test_calculate_total():
    assert calculate_total([10, 20, 30]) == 60


def test_apply_discount():
    assert apply_discount(100, 10) == 90


def test_apply_discount_invalid_percent():
    with pytest.raises(ValueError):
        apply_discount(100, 150)


def test_shipping_cost_basic():
    assert shipping_cost(10, 50, False) == 20


def test_shipping_cost_far_distance():
    assert shipping_cost(10, 200, False) == 40


def test_shipping_cost_very_far_distance():
    assert shipping_cost(10, 600, False) == 90


def test_shipping_cost_express():
    assert shipping_cost(10, 50, True) == 40


def test_shipping_cost_invalid_weight():
    with pytest.raises(ValueError):
        shipping_cost(0, 10, False)


def test_loyalty_points_gold():
    assert loyalty_points(100, "gold") == 300


def test_loyalty_points_silver():
    assert loyalty_points(100, "silver") == 200


def test_loyalty_points_default():
    assert loyalty_points(100, "bronze") == 100
