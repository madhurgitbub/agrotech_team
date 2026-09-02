async function loadWeather() {

    const cityInput =
        document.getElementById("weatherCity");

    const city =
        cityInput.value.trim() || "Indore";


    const loading =
        document.getElementById("weatherLoading");

    const errorBox =
        document.getElementById("weatherError");

    const weatherCard =
        document.getElementById("weatherCard");


    console.log(
        "Fetching weather for:",
        city
    );


    if (loading) {

        loading.style.display = "block";

    }


    if (errorBox) {

        errorBox.style.display = "none";

    }


    if (weatherCard) {

        weatherCard.style.display = "none";

    }


    try {

        const response =
            await fetch(
                `http://127.0.0.1:8000/api/weather?city=${encodeURIComponent(city)}`
            );


        console.log(
            "Response status:",
            response.status
        );


        if (!response.ok) {

            throw new Error(
                "Unable to fetch weather data"
            );

        }


        const data =
            await response.json();


        console.log(
            "Weather data:",
            data
        );


        if (!data.success) {

            throw new Error(
                "Weather data not available"
            );

        }


        // Location

        const locationElement =
            document.getElementById(
                "weatherLocation"
            );

        if (locationElement) {

            locationElement.innerText =
                data.location;

        }


        // Temperature

        const temperatureElement =
            document.getElementById(
                "weatherTemperature"
            );

        if (temperatureElement) {

            temperatureElement.innerText =
                Math.round(
                    data.temperature
                );

        }


        // Feels Like

        const feelsLikeElement =
            document.getElementById(
                "weatherFeelsLike"
            );

        if (feelsLikeElement) {

            feelsLikeElement.innerText =
                Math.round(
                    data.feels_like
                );

        }


        // Humidity

        const humidityElement =
            document.getElementById(
                "weatherHumidity"
            );

        if (humidityElement) {

            humidityElement.innerText =
                data.humidity + "%";

        }


        // Wind

        const windElement =
            document.getElementById(
                "weatherWind"
            );

        if (windElement) {

            windElement.innerText =
                data.wind_speed + " km/h";

        }


        // Rain

        const rainElement =
            document.getElementById(
                "weatherRain"
            );

        if (rainElement) {

            rainElement.innerText =
                data.rain + " mm";

        }


        // Precipitation

        const precipitationElement =
            document.getElementById(
                "weatherPrecipitation"
            );

        if (precipitationElement) {

            precipitationElement.innerText =
                data.precipitation + " mm";

        }


        // Weather Condition

        const conditionElement =
            document.getElementById(
                "weatherCondition"
            );

        if (conditionElement) {

            conditionElement.innerText =
                data.condition;

        }


        // Weather Icon

        const iconElement =
            document.getElementById(
                "weatherIcon"
            );

        if (iconElement) {

            iconElement.innerText =
                getWeatherIcon(
                    data.weather_code
                );

        }


        // Hide loading

        if (loading) {

            loading.style.display =
                "none";

        }


        // Show card

        if (weatherCard) {

            weatherCard.style.display =
                "block";

        }


    }

    catch (error) {

        console.error(
            "Weather Error:",
            error
        );


        if (loading) {

            loading.style.display =
                "none";

        }


        if (errorBox) {

            errorBox.innerText =
                "⚠️ Unable to load weather. Please try again.";

            errorBox.style.display =
                "block";

        }

    }

}


function getWeatherIcon(code) {

    if (code === 0) {

        return "☀️";

    }


    if (
        code === 1 ||
        code === 2
    ) {

        return "🌤️";

    }


    if (code === 3) {

        return "☁️";

    }


    if (
        code >= 45 &&
        code <= 48
    ) {

        return "🌫️";

    }


    if (
        code >= 51 &&
        code <= 67
    ) {

        return "🌧️";

    }


    if (
        code >= 71 &&
        code <= 77
    ) {

        return "❄️";

    }


    if (
        code >= 80 &&
        code <= 82
    ) {

        return "🌦️";

    }


    if (code >= 95) {

        return "⛈️";

    }


    return "🌤️";

}


document.addEventListener(
    "DOMContentLoaded",
    function () {

        loadWeather();

    }
);