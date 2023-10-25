"""Tests for the `unfccc_di_api` package."""
import os

import pytest

import unfccc_di_api
from unfccc_di_api import UNFCCCApiReader, ZenodoReader


@pytest.fixture(scope="module")
def api_reader() -> UNFCCCApiReader:
    return UNFCCCApiReader()


@pytest.fixture(scope="module")
def zenodo_reader() -> ZenodoReader:
    return ZenodoReader()


@pytest.fixture(
    scope="module",
    params=[
        pytest.param(
            "unfccc",
            marks=pytest.mark.skipif(
                "GITHUB_ACTIONS" not in os.environ, reason="UNFCCC reader not available"
            ),
        ),
        "zenodo",
    ],
)
def reader(request):
    if request.param == "unfccc":
        return UNFCCCApiReader()
    if request.param == "zenodo":
        return ZenodoReader()


def test_not_implemented(zenodo_reader):
    with pytest.raises(NotImplementedError):
        zenodo_reader.query(party_code="DEU", gases=["N2O"])
    with pytest.raises(NotImplementedError):
        zenodo_reader.query(party_code="DEU", normalize_gas_names=False)


def test_query(reader):
    res = reader.query(party_code="DEU")
    assert len(res) > 0


@pytest.mark.skip(reason="UNFCCC reader not available")
def test_non_annex_one(api_reader):
    ans = api_reader.non_annex_one_reader.query(party_codes=["MMR"])

    match = "Unknown party *"
    with pytest.raises(ValueError, match=match):
        api_reader.non_annex_one_reader.query(party_codes=["ASDF"])

    assert len(ans) > 1


@pytest.mark.skip(reason="UNFCCC reader not available")
def test_annex_one(api_reader: UNFCCCApiReader):
    ans = api_reader.annex_one_reader.query(party_codes=["DEU"], gases=["N₂O"])
    assert len(ans) > 1


def test_unified(reader):
    ans = reader.query(party_code="AFG")
    assert len(ans) > 1

    match = "Unknown party *"
    with pytest.raises(ValueError, match=match):
        reader.query(party_code="ASDF")


@pytest.mark.skip(reason="UNFCCC reader not available")
def test_unified_gases(api_reader: UNFCCCApiReader):
    ans = api_reader.query(party_code="DEU", gases=["N₂O"])
    assert len(ans) > 1


@pytest.mark.skip(reason="UNFCCC reader not available")
@pytest.mark.parametrize("normalize", [True, False])
def test_unified_as_ascii(api_reader: UNFCCCApiReader, normalize: bool):
    # assert that using standardized string ('N2O' instead of "N₂O") works
    ans = api_reader.query(
        party_code="DEU", gases=["N2O"], normalize_gas_names=normalize
    )
    assert len(ans) > 1
    assert ans.gas.unique()[0] == ("N2O" if normalize else "N₂O")


@pytest.mark.skip(reason="UNFCCC reader not available")
@pytest.mark.parametrize("category_id", [9559, 9608])
def test_category_filter(api_reader: UNFCCCApiReader, category_id):
    # this failed due to duplicate variableIds
    # see https://github.com/pik-primap/unfccc_di_api/issues/28
    df = api_reader.annex_one_reader.query(
        party_codes=["DEU"], category_ids=[category_id]
    )
    assert len(df["category"].unique()) == 1


@pytest.mark.skip(reason="UNFCCC reader not available")
def test_no_data(api_reader: UNFCCCApiReader):
    with pytest.raises(unfccc_di_api.NoDataError):
        api_reader.annex_one_reader.query(party_codes=["FIN"], category_ids=[14817])
