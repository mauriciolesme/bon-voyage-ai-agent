# tools
import requests
import os
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
EXCHANGE_API_KEY = os.getenv("EXCHANGERATE_API_KEY")


@tool
def get_weather(city: str, month: str) -> str:
    """
    Use this tool when the user has selected a destination and you need
    to retrieve the weather conditions for a specific city and travel month.
    Input: city name and month (e.g. "Tokyo", "March")
    Output: average temperature, conditions, and packing suggestions.
    """
    print(f"Agent is using get_weather tool for {city} in {month}")

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)

    if response.status_code != 200:
        return f"Could not retrieve weather data for {city}. Please check the city name."

    data = response.json()
    temp = data["main"]["temp"]
    description = data["weather"][0]["description"]
    humidity = data["main"]["humidity"]

    return (
        f"Current weather in {city}: {description}, "
        f"Temperature: {temp}°C, Humidity: {humidity}%. "
        f"Note: this reflects current conditions — for {month} travel, "
        f"consider seasonal variations when giving packing suggestions."
    )


@tool
def get_country_info(country: str) -> str:
    """
    Use this tool when the user has selected a destination and you need
    to retrieve country details such as currency, languages, and region.
    Input: country name (e.g. "Japan")
    Output: currency, official languages, region, and country info.
    """
    print(f"Agent is using get_country_info tool for {country}")

    url = f"https://restcountries.com/v3.1/name/{country}"
    response = requests.get(url)

    if response.status_code != 200:
        return f"Could not retrieve information for {country}. Please check the country name."

    data = response.json()[0]
    name = data["name"]["common"]
    region = data["region"]
    subregion = data.get("subregion", "N/A")
    capital = data.get("capital", ["N/A"])[0]
    languages = ", ".join(data.get("languages", {}).values())
    currencies = data.get("currencies", {})
    currency_info = ", ".join(
        [f"{v['name']} ({k})" for k, v in currencies.items()]
    )

    return (
        f"Country: {name} | Region: {region} | Subregion: {subregion} | "
        f"Capital: {capital} | Languages: {languages} | "
        f"Currency: {currency_info}"
    )


@tool
def get_exchange_rate(base_currency: str, target_currency: str) -> str:
    """
    Use this tool when the user wants to know the exchange rate between
    their home currency and the destination currency.
    Input: base currency code and target currency code (e.g. "USD", "JPY")
    Output: current exchange rate between the two currencies.
    """
    print(f"Agent is using get_exchange_rate tool: {base_currency} to {target_currency}")

    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/pair/{base_currency}/{target_currency}"
    response = requests.get(url)

    if response.status_code != 200:
        return f"Could not retrieve exchange rate for {base_currency} to {target_currency}."

    data = response.json()

    if data["result"] != "success":
        return f"Invalid currency codes: {base_currency} or {target_currency}."

    rate = data["conversion_rate"]

    return (
        f"1 {base_currency} = {rate} {target_currency}. "
        f"(Source: ExchangeRate-API — rates update daily)"
    )

