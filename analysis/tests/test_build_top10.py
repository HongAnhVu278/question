"""
seam a: build(csv_path) -> dict


the fixture (fixtures/usa_mini.csv) is hand-made.
usa girls: 15 students who count. their weights add up to 100, so share = weight / 100
  bars:        2211 = 10 + 8 = 18 (2 students), 2631 = 14, 0110 = 12, 9702 = 11, 2341 = 9,
               2635 = 7, 9112 = 6, 0 = 5, 011 = 4, 3221 = 3  | cut: 2166 = 2, 9111 = 1
  didn't fit:  9704 = 5, 9705 = 3  -> 8
  out:         9999, 9998, 9995 (weights 50, 40, 30): not in the group at all (adr-013)
usa boys: 6 students who count, weights add up to 100
  bars:        2512 = 20 + 20 = 40 (2 students), 7231 = 25, 2141 = 15, 9701 = 10
  didn't fit:  9704 = 10
  out:         9997, 9996 (weights 60, 60)
plus one usa student with no gender (weight 100) and albania (weights 1000).
"""
from datetime import datetime
from pathlib import Path

import pytest

from build_top10 import build

FIXTURE = Path(__file__).parent / "fixtures" / "usa_mini.csv"


@pytest.fixture(scope="module")
def result():
    return build(FIXTURE)


@pytest.fixture(scope="module")
def usa(result):
    return next(e for e in result["entries"] if e["code"] == "USA")


def bars_by_isco(panel):
    return {b["isco"]: b for b in panel["bars"]}


# the contract

def test_top_level_shape(result):
    assert set(result) == {"year", "min_students", "generated_at", "entries"}
    assert result["year"] == 2025
    assert result["min_students"] == 30
    datetime.fromisoformat(result["generated_at"])  # raises if it isn't an iso timestamp
    assert isinstance(result["entries"], list)


def test_usa_entry_shape(usa):
    assert set(usa) == {"code", "name", "girls", "boys"}
    assert usa["name"] == "United States"
    for panel in (usa["girls"], usa["boys"]):
        assert set(panel) == {"n", "didnt_fit", "bars"}
        for bar in panel["bars"]:
            assert set(bar) == {"isco", "label", "share", "count"}
            assert isinstance(bar["isco"], str)
            assert isinstance(bar["count"], int)


# the numbers

def test_girls_weighted_shares_top_10_in_order(usa):
    got = usa["girls"]["bars"]
    assert [b["isco"] for b in got] == [
        "2211", "2631", "0110", "9702", "2341", "2635", "9112", "0", "011", "3221",
    ]
    assert [b["share"] for b in got] == pytest.approx(
        [0.18, 0.14, 0.12, 0.11, 0.09, 0.07, 0.06, 0.05, 0.04, 0.03]
    )


def test_boys_weighted_shares(usa):
    got = usa["boys"]["bars"]
    assert [b["isco"] for b in got] == ["2512", "7231", "2141", "9701"]
    assert [b["share"] for b in got] == pytest.approx([0.40, 0.25, 0.15, 0.10])


def test_at_most_10_bars_and_a_panel_can_have_fewer(usa):
    assert len(usa["girls"]["bars"]) == 10  # 12 jobs in the fixture, cut at 10
    assert len(usa["boys"]["bars"]) == 4    # only 4 jobs, nothing invented to fill it


def test_bars_descending(usa):
    for panel in (usa["girls"], usa["boys"]):
        shares = [b["share"] for b in panel["bars"]]
        assert shares == sorted(shares, reverse=True)


def test_count_is_unweighted_students(usa):
    girls, boys = bars_by_isco(usa["girls"]), bars_by_isco(usa["boys"])
    assert girls["2211"]["count"] == 2
    assert girls["2631"]["count"] == 1
    assert boys["2512"]["count"] == 2


# who is in the denominator

def test_n_counts_only_students_in_the_group(usa):
    # 9995–9999 rows and the no-gender row are in neither group
    assert usa["girls"]["n"] == 15
    assert usa["boys"]["n"] == 6


def test_didnt_fit_is_the_9704_9705_share(usa):
    assert usa["girls"]["didnt_fit"] == pytest.approx(0.08)
    assert usa["boys"]["didnt_fit"] == pytest.approx(0.10)


def test_didnt_fit_codes_are_not_bars(usa):
    for panel in (usa["girls"], usa["boys"]):
        assert not {"9704", "9705"} & set(bars_by_isco(panel))


def test_pisa_answer_codes_9701_to_9703_are_bars(usa):
    assert "9702" in bars_by_isco(usa["girls"])
    assert "9701" in bars_by_isco(usa["boys"])


# codes and labels

def test_codes_stay_strings_as_stored(usa):
    codes = set(bars_by_isco(usa["girls"]))
    assert {"0", "011", "0110"} <= codes  # not 0 / 11 / 110, not padded to "0000" / "0011"


def test_same_label_different_codes_are_separate_bars(usa):
    girls = bars_by_isco(usa["girls"])
    assert girls["011"]["label"] == "Commissioned armed forces officers"
    assert girls["0110"]["label"] == "Commissioned armed forces officers"


def test_labels_pass_through_unchanged(usa):
    girls = bars_by_isco(usa["girls"])
    assert girls["9112"]["label"] == "Cleaners and helpers in offices, hotels and other establishments"
    assert girls["9702"]["label"] == "Learning, studying"
    assert girls["2211"]["label"] == "Generalist medical practitioners"
