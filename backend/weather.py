from fastapi import APIRouter, HTTPException
import requests


router = APIRouter(
    prefix="/api",
    tags=["Weather"]
)


WEATHER_CODE = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Foggy",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Heavy Drizzle",
    61: "Light Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    71: "Light Snow",
    73: "Moderate Snow",
    75: "Heavy Snow",
    80: "Rain Showers",
    81: "Moderate Rain Showers",
    82: "Heavy Rain Showers",
    95: "Thunderstorm"
}


@router.get("/weather")
def get_weather(city: str):

    try:

        # STEP 1: Convert city name to latitude and longitude

        geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"

        geo_response = requests.get(
            geocoding_url,
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json"
            },
            timeout=10
        )

        geo_data = geo_response.json()


        if "results" not in geo_data:

            raise HTTPException(
                status_code=404,
                detail=f"City '{city}' not found"
            )


        location = geo_data["results"][0]

        latitude = location["latitude"]

        longitude = location["longitude"]

        location_name = location["name"]

        country = location.get("country", "")


        # STEP 2: Get weather data

        weather_url = "https://api.open-meteo.com/v1/forecast"


        weather_response = requests.get(
            weather_url,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "apparent_temperature",
                    "is_day",
                    "precipitation",
                    "rain",
                    "weather_code",
                    "wind_speed_10m"
                ],
                "timezone": "auto"
            },
            timeout=10
        )


        weather_data = weather_response.json()

        current = weather_data["current"]


        weather_code = current.get(
            "weather_code",
            0
        )


        return {

            "success": True,

            "location": f"{location_name}, {country}",

            "temperature": current.get(
                "temperature_2m"
            ),

            "feels_like": current.get(
                "apparent_temperature"
            ),

            "humidity": current.get(
                "relative_humidity_2m"
            ),

            "wind_speed": current.get(
                "wind_speed_10m"
            ),

            "precipitation": current.get(
                "precipitation"
            ),

            "rain": current.get(
                "rain"
            ),

            "condition": WEATHER_CODE.get(
                weather_code,
                "Unknown"
            ),

            "weather_code": weather_code

        }


    except HTTPException:

        raise


    except Exception as e:

        print("Weather API Error:", str(e))

        raise HTTPException(
            status_code=500,
            detail="Unable to fetch weather data"
        )