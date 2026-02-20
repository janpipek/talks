import httpx
import pandas as pd

def aladin(location_id: int) -> "pd.DataFrame":
    """Download and parse aladin forecast data."""

    response = httpx.get(f"https://data-provider.chmi.cz/api/graphs/graf.meteogram/{location_id}")
    data = response.json()["data"]
    df = pd.DataFrame(data)
    df = (
        df.assign(
            validityTime=pd.to_datetime(df["validityTime"]).dt.tz_convert("Europe/Prague")
        )
        .rename(
            columns={
                "validityTime": "dateTime",
                "t2m": "temperature",
                "rh2m": "relativeHumidity",
                "prec": "precipitation",
                "mslp": "pressure",
                "cloudsTot": "clouds",
            }
        )
        .drop(columns=["windLevelIcon", "icon"])
    )
    return df


def locations() -> "pd.DataFrame":
    import pandas as pd
    import httpx
    def parse_locations(data, search: str | None = None):
        df = pd.DataFrame([row["properties"] for row in data["features"]])
        df = (
            df.assign(
                locationId=df["url"].apply(
                    lambda s: int(s.split("/")[-1].split("-")[0])
                )
            )
            .drop(columns=["url", "icon"])
            .set_index("name")
        )
        return df

    response = httpx.get("https://data-provider.chmi.cz/api/poi/data/map/obce/2")
    data = response.json()
    return parse_locations(data)


def location(name: str) -> int:
    try:
        return int(locations().loc[name, "locationId"])
    except KeyError:
        raise ValueError(f"Location '{name}' not found.")

...
# HIDE_ABOVE

if __name__ == "__main__":
    print("\n*** Welcome to my cool weather forecast app ***\n")
    ostrava = location("Ostrava")
    print(f"Ostrava location ID: {ostrava}")
