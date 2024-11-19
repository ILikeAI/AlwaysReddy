import requests
import os
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.tree import Tree
from typing import Dict, Any, Optional
from config_loader import config
import unittest
from unittest.mock import patch

class WeatherSkill:
    def __init__(self):
        self.time_indicators = {
            'today', 'tomorrow', 'tonight', 'morning', 'afternoon',
            'evening', 'week', 'weekend', 'monday', 'tuesday',
            'wednesday', 'thursday', 'friday', 'saturday', 'sunday'
        }
        self.location_labels = {'GPE', 'LOC'}

    def extract_location(self, text: str) -> Optional[str]:
        """
        Extract a location from a text using named entity recognition.

        Args:
            text: The text to extract the location from.

        Returns:
            The location found in the text, or None if no location was found.
        """
        tokens = word_tokenize(text)
        tagged = pos_tag(tokens)
        chunks = ne_chunk(tagged)

        locations = []
        if isinstance(chunks, Tree):
            for subtree in chunks:
                if isinstance(subtree, Tree) and subtree.label() in self.location_labels:
                    location = ' '.join([token for token, pos in subtree.leaves()])
                    locations.append(location)

        return locations[0] if locations else None

    def extract_time_reference(self, text: str) -> Optional[str]:
        """
        Extract a time reference from a text using a set of predefined time indicators.

        Args:
            text: The text to extract the time reference from.

        Returns:
            The time reference found in the text, or None if no time reference was found.
        """
        tokens = word_tokenize(text.lower())
        for token in tokens:
            if token in self.time_indicators:
                return token
        return None
 
    def condense_json(self, input_json):
        """
        Condense a JSON object by rounding all floating point numbers to integers
        and removing specific weather elements (sea_level, grnd_level, pressure, visibility, temp_kf).
        
        Args:
            input_json: The JSON object to condense.
            
        Returns:
            The condensed JSON object with rounded numbers and removed elements.
        """
        def round_numbers_and_filter(obj):
            if isinstance(obj, dict):
                filtered_dict = {}
                for k, v in obj.items():
                    # Skip specific weather elements
                    if k not in ['sea_level', 'grnd_level', 'pressure', 'visibility','temp_kf']:
                        filtered_dict[k] = round_numbers_and_filter(v)
                return filtered_dict
            elif isinstance(obj, list):
                return [round_numbers_and_filter(item) for item in obj]
            elif isinstance(obj, float):
                return int(obj)
            else:
                return obj

        # Create a deep copy of the input JSON, round the numbers, and filter elements
        condensed_json = round_numbers_and_filter(input_json)
        
        return condensed_json

    def getLocationWeather(self, query: str) -> Dict[str, Any]:
        """
        Retrieve weather information for a given location from a query string.

        This function uses OpenWeatherMap API to fetch the current weather data
        for a location extracted from the query. If the query includes a time 
        reference other than 'today', it also fetches the weather forecast.

        Args:
            query (str): The query string containing the location and optionally a time reference.

        Returns:
            Dict[str, Any]: A dictionary containing the weather data. If an error occurs,
                            the dictionary contains an 'error' key with the error message.
        """
        try:
            location_name = self.extract_location(query) or str(config.DEFAULT_LOCATION)
            if not location_name:
                return {'error': 'No location found in query and DEFAULT_LOCATION is not set'}
            time_ref = self.extract_time_reference(query)

            apiKey = "34805111fe90be66c8b6923016ef27c0"

           
            #if the query implies a time reference, get the forecast
            if time_ref and time_ref != 'today':
                forecastUrl = "https://api.openweathermap.org/data/2.5/forecast?q=" + location_name + "&units=" + str(config.DEFAULT_UNITS) + "&appid=" + apiKey
                forecast_response = requests.get(forecastUrl)
                forecast_response.raise_for_status()
                weather_data = self.condense_json(forecast_response.json())

            else:
            #get the current weather
                completeUrl = "https://api.openweathermap.org/data/2.5/weather?q=" + location_name + "&units=" + str(config.DEFAULT_UNITS) + "&appid=" + apiKey
                response = requests.get(completeUrl)
                response.raise_for_status()
                weather_data = self.condense_json(response.json())
            
            return weather_data
        except requests.exceptions.RequestException as e:
            return {'error': f'Error fetching weather data: {e}'}
        except Exception as e:
            return {'error': f'An unexpected error occurred: {e}'}

# Test code
class TestWeatherSkill(unittest.TestCase):
    def setUp(self):
        self.weather_skill = WeatherSkill()

    def test_extract_location(self):
        self.assertEqual(self.weather_skill.extract_location("What's the weather like in New York?"), "New York")
        self.assertIsNone(self.weather_skill.extract_location("What's the weather like today?"))

    def test_extract_time_reference(self):
        self.assertEqual(self.weather_skill.extract_time_reference("What's the weather like tomorrow?"), "tomorrow")
        self.assertIsNone(self.weather_skill.extract_time_reference("What's the weather like in London?"))

    def test_condense_json(self):
        test_json = {
            "temp": 20.5,
            "humidity": 45.7,
            "pressure": 1013,
            "sea_level": 1014,
            "grnd_level": 1012,
            "forecast": [
                {
                    "temp": 22.3,
                    "wind": 5.8,
                    "pressure": 1015,
                    "sea_level": 1016,
                    "grnd_level": 1014
                },
                {
                    "temp": 21.7,
                    "wind": 6.2,
                    "pressure": 1014,
                    "sea_level": 1015,
                    "grnd_level": 1013
                }
            ]
        }
        expected = {
            "temp": 20,
            "humidity": 45,
            "forecast": [
                {
                    "temp": 22,
                    "wind": 5
                },
                {
                    "temp": 21,
                    "wind": 6
                }
            ]
        }
        result = self.weather_skill.condense_json(test_json)
        self.assertEqual(result, expected)

    @patch('requests.get')
    def test_getLocationWeather_current(self, mock_get):
        # Mock response for current weather
        mock_current = unittest.mock.Mock()
        mock_current.json.return_value = {"weather": [{"description": "clear sky"}], "main": {"temp": 20}}
        mock_current.raise_for_status = lambda: None
        mock_get.return_value = mock_current

        result = self.weather_skill.getLocationWeather("What's the weather like in London?")
        self.assertIn("weather", result)
        self.assertIn("main", result)

    @patch('requests.get')
    def test_getLocationWeather_forecast(self, mock_get):
        # Mock responses for both current weather and forecast
        mock_current = unittest.mock.Mock()
        mock_current.json.return_value = {"weather": [{"description": "clear sky"}], "main": {"temp": 20}}
        mock_current.raise_for_status = lambda: None

        mock_forecast = unittest.mock.Mock()
        mock_forecast.json.return_value = {
            "list": [
                {"main": {"temp": 22.5, "pressure": 1013}, "weather": [{"description": "sunny"}]},
                {"main": {"temp": 21.3, "pressure": 1014}, "weather": [{"description": "cloudy"}]}
            ]
        }
        mock_forecast.raise_for_status = lambda: None

        # Configure mock_get to return different responses for different URLs
        def side_effect(url):
            if "forecast" in url:
                return mock_forecast
            return mock_current

        mock_get.side_effect = side_effect

        result = self.weather_skill.getLocationWeather("What's the weather like tomorrow in London?")
        self.assertIn("list", result)
        # Verify pressure was removed from the response
        self.assertNotIn("pressure", result["list"][0]["main"])

    def test_getLocationWeather_no_location(self):
        result = self.weather_skill.getLocationWeather("What's the weather like?")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "No location found in query")

    @patch('requests.get')
    def test_getLocationWeather_api_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        result = self.weather_skill.getLocationWeather("What's the weather like in London?")
        self.assertIn("error", result)
        self.assertTrue(result["error"].startswith("Error fetching weather data"))

if __name__ == '__main__':
    unittest.main()
