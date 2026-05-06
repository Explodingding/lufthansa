from airline_platform.extractors.ourairports import (
    OURAIRPORTS_AIRPORTS_CSV_URL,
    fetch_ourairports_airports,
    parse_ourairports_airports,
)

OURAIRPORTS_HEADER = (
    "id,ident,type,name,latitude_deg,longitude_deg,elevation_ft,continent,iso_country,"
    "iso_region,municipality,scheduled_service,gps_code,iata_code,local_code,home_link,"
    "wikipedia_link,keywords"
)
OURAIRPORTS_SAMPLE = "\n".join(
    [
        OURAIRPORTS_HEADER,
        (
            "1,EPGD,large_airport,Gdansk Lech Walesa Airport,54.3776,18.4662,489,"
            "EU,PL,PL-PM,Gdansk,yes,EPGD,GDN,,,"
        ),
        (
            "2,EDDF,large_airport,Frankfurt Airport,50.0333,8.5706,364,"
            "EU,DE,DE-HE,Frankfurt,yes,EDDF,FRA,,,"
        ),
        "3,XXXX,small_airport,Ignored Airport,1.0,2.0,0,EU,DE,DE-XX,Ignored,no,XXXX,IGN,,,",
    ]
)


class FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text

    def raise_for_status(self) -> None:
        return None


def test_parse_ourairports_airports_returns_selected_airports() -> None:
    airports = parse_ourairports_airports(OURAIRPORTS_SAMPLE, airport_codes=("FRA", "GDN"))

    assert airports == [
        {
            "airport_code": "FRA",
            "airport_name": "Frankfurt Airport",
            "city": "Frankfurt",
            "country": "DE",
            "latitude_deg": 50.0333,
            "longitude_deg": 8.5706,
        },
        {
            "airport_code": "GDN",
            "airport_name": "Gdansk Lech Walesa Airport",
            "city": "Gdansk",
            "country": "PL",
            "latitude_deg": 54.3776,
            "longitude_deg": 18.4662,
        },
    ]


def test_fetch_ourairports_airports_uses_configured_endpoint() -> None:
    calls = []

    def fake_get(url, timeout):
        calls.append((url, timeout))
        return FakeResponse(OURAIRPORTS_SAMPLE)

    airports = fetch_ourairports_airports(
        airport_codes=("GDN",),
        timeout_seconds=5,
        http_get=fake_get,
    )

    assert calls == [(OURAIRPORTS_AIRPORTS_CSV_URL, 5)]
    assert airports[0]["airport_code"] == "GDN"
