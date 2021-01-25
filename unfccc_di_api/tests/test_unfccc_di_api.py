"""Tests for the `unfccc_di_api` package."""

import pytest

from unfccc_di_api import UNFCCCApiReader


@pytest.fixture(scope="module")
def api_reader() -> UNFCCCApiReader:
    return UNFCCCApiReader()


def test_non_annex_one(api_reader: UNFCCCApiReader):
    ans = api_reader.non_annex_one_reader.query(party_codes=["MMR"])

    match = "Unknown party *"
    with pytest.raises(ValueError, match=match):
        api_reader.non_annex_one_reader.query(party_codes=["ASDF"])

    assert len(ans) > 1


def test_annex_one(api_reader: UNFCCCApiReader):
    ans = api_reader.annex_one_reader.query(party_codes=["DEU"], gases=["N₂O"])
    assert len(ans) > 1


def test_unified(api_reader: UNFCCCApiReader):
    ans = api_reader.query(party_code="AFG")
    assert len(ans) > 1
    ans = api_reader.query(party_code="DEU", gases=["N₂O"])
    assert len(ans) > 1

    match = "Unknown party *"
    with pytest.raises(ValueError, match=match):
        api_reader.query(party_code="ASDF")
