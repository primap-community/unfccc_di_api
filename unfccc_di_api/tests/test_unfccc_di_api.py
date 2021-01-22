"""Tests for the `unfccc_di_api` package."""

import pytest

from unfccc_di_api import UNFCCCApiReader


@pytest.fixture(scope="module")
def api_reader() -> UNFCCCApiReader:
    return UNFCCCApiReader()


def test_non_annex_one(api_reader: UNFCCCApiReader):
    api_reader.non_annex_one_reader.query(party_codes=["MMR"])


def test_annex_one(api_reader: UNFCCCApiReader):
    api_reader.annex_one_reader.query(party_codes=["DEU"], gases=["N₂O"])


def test_unified(api_reader: UNFCCCApiReader):
    api_reader.query(party_code="AFG")
