import pytest

from app.loader import load_prices


@pytest.fixture
def write_csv(tmp_path):
    def write(body: str):
        path = tmp_path / "prices.csv"
        path.write_text(body)
        return path

    return write


def test_groups_by_ticker_normalizes_and_sorts(write_csv):
    path = write_csv(
        "date,ticker,price\n"
        "2026-01-02,aaa,11\n"
        "2026-01-01, AAA ,10\n"
        "2026-01-01,BBB,20\n"
    )
    data = load_prices(path)
    assert sorted(data) == ["AAA", "BBB"]
    assert data["AAA"].tolist() == [10.0, 11.0]
    assert [d.isoformat() for d in data["AAA"].index.date] == ["2026-01-01", "2026-01-02"]


@pytest.mark.parametrize(
    ("body", "match"),
    [
        ("date,ticker\n2026-01-01,A\n", "price"),                  # missing column
        ("date,ticker,price\n2026-13-01,A,1\n", "2026-13-01"),     # bad date
        ("date,ticker,price\n2026-01-01,A,abc\n", "abc"),          # non-numeric price
        ("date,ticker,price\n2026-01-01,A,1\n2026-01-01,a,2\n", "duplicate"),
        ("date,ticker,price\n2026-01-01, ,1\n", "missing values"), # blank ticker
        ("date,ticker,price\n2026-01-01,A,\n", "missing values"),  # blank price
        ("date,ticker,price\n", "no data rows"),
    ],
)
def test_rejects_bad_csv(write_csv, body, match):
    with pytest.raises(ValueError, match=match):
        load_prices(write_csv(body))


def test_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_prices(tmp_path / "nope.csv")


def test_sample_csv_shape():
    from app.main import DEFAULT_CSV

    data = load_prices(DEFAULT_CSV)
    assert len(data) == 200
    assert all(len(s) == 30 and s.index.is_monotonic_increasing for s in data.values())
