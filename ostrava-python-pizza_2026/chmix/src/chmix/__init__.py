import typer
import pandas as pd
import httpx

main = typer.Typer()


@main.command()
def aladin(location: str, json: bool = False):
    """Download and parse aladin forecast data."""
    try:
        location_id = int(location)
    except:
        location_id = get_location_id(location)
    response = httpx.get(f"https://data-provider.chmi.cz/api/graphs/graf.meteogram/{location_id}")
    data = response.json()["data"]
    if json:
        typer.echo(data)
        return
    else:
        df = pd.DataFrame(data)
        df = (
            df.assign(
                validityTime=pd.to_datetime(df["validityTime"]).dt.tz_convert("Europe/Prague").dt.strftime("%Y-%m-%d %H:%M")
            )
            .rename(
                columns={
                    "validityTime": "dateTime",
                    "t2m": "temperature",
                    "rh2m": "humidity",
                    "prec": "precipitation",
                    "mslp": "pressure",
                    "cloudsTot": "clouds",
                    "windDirection": "windDir",
                }
            )
            .drop(columns=["windLevelIcon", "icon", "windGustSpeed", "snow"], errors="ignore")
        )

    print(df.to_markdown(tablefmt="rounded_outline", index=False))


@main.command()
def locations(json: bool = typer.Option(False, help="Output in JSON format")) -> "pd.DataFrame":
    """Show available locations"""
    if json:
        typer.echo(_get_locations_data())
    else:
        df = _get_locations_df()
        _print_df(df.reset_index().drop(columns="poiType"))


def _get_locations_data():
    response = httpx.get("https://data-provider.chmi.cz/api/poi/data/map/obce/4")
    data = response.json()
    return data


def _get_locations_df():
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

    data = _get_locations_data()
    return parse_locations(data)


def _print_df(df: pd.DataFrame) -> None:
    print(df.to_markdown(tablefmt="rounded_outline", index=False))


def get_location_id(name: str) -> int:
    try:
        return int(_get_locations_df().loc[name, "locationId"])
    except KeyError:
        raise ValueError(f"Location '{name}' not found.")


if __name__ == "__main__":
    main()
