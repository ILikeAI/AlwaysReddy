from nltk import word_tokenize, pos_tag
from typing import Dict, Any, Optional
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import re
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from search_providers import SearchProviderFactory

class NewsSkill:
    def __init__(self, provider_type: Optional[str] = None):
        self.topic_indicators = {
            'about', 'regarding', 'on', 'related to', 'news about',
            'latest', 'recent', 'current', 'today', 'breaking', 'update'
        }
        # Expanded time indicators with more natural language expressions
        self.time_indicators = {
            'today': 1,
            'yesterday': 2,
            'last week': 7,
            'past week': 7,
            'this week': 7,
            'recent': 3,
            'latest': 3,
            'last month': 30,
            'past month': 30,
            'this month': 30,
            'past year': 365,
            'last year': 365,
            'this year': 365,
            'past few days': 3,
            'last few days': 3,
            'past couple days': 2,
            'last couple days': 2,
            'past 24 hours': 1,
            'last 24 hours': 1,
            'past hour': 1,
            'last hour': 1,
            'past few weeks': 21,
            'last few weeks': 21,
            'past couple weeks': 14,
            'last couple weeks': 14,
            'past few months': 90,
            'last few months': 90,
            'past couple months': 60,
            'last couple months': 60
        }
        # Regular expressions for relative time
        self.relative_time_patterns = [
            (r'past (\d+) days?', lambda x: int(x)),
            (r'last (\d+) days?', lambda x: int(x)),
            (r'past (\d+) weeks?', lambda x: int(x) * 7),
            (r'last (\d+) weeks?', lambda x: int(x) * 7),
            (r'past (\d+) months?', lambda x: int(x) * 30),
            (r'last (\d+) months?', lambda x: int(x) * 30),
            (r'past (\d+) years?', lambda x: int(x) * 365),
            (r'last (\d+) years?', lambda x: int(x) * 365)
        ]
        self.provider = SearchProviderFactory.get_provider(provider_type=provider_type)

    def extract_time_reference(self, text: str) -> int:
        """
        Extract a time reference from text and convert it to number of days.
        Handles both fixed and relative time expressions.
        
        Args:
            text: The text to extract the time reference from.
            
        Returns:
            Number of days to look back for news (default: 3 if no time reference found)
        """
        text_lower = text.lower()
        
        # Check for exact matches first
        for time_ref, days in self.time_indicators.items():
            if time_ref in text_lower:
                return days
        
        # Check for relative time patterns
        for pattern, converter in self.relative_time_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return converter(match.group(1))
                
        # If no time reference found, default to 3 days
        return 3

    def extract_search_topic(self, text: str) -> str:
        """
        Extract the main search topic from the query text.
        Improved to handle compound topics better.
        
        Args:
            text: The query text to extract the topic from.
            
        Returns:
            The extracted search topic or the original text if no specific topic is found.
        """
        # Tokenize and tag parts of speech
        tokens = word_tokenize(text.lower())
        tagged = pos_tag(tokens)
        
        # Look for topic after common indicators
        for i, (word, _) in enumerate(tagged):
            if word in self.topic_indicators and i + 1 < len(tagged):
                # Extract everything after the indicator as the topic
                topic_words = []
                for word, pos in tagged[i+1:]:
                    # Include nouns, adjectives, verbs, and conjunctions for compound topics
                    if pos.startswith(('NN', 'JJ', 'VB')) or word in ['and', 'or']:
                        topic_words.append(word)
                if topic_words:
                    return ' '.join(topic_words)
        
        # If no specific pattern found, use the original text with common words filtered out
        stop_words = {'what', 'is', 'are', 'the', 'tell', 'me', 'search', 'find', 'get', 'news'}
        topic_words = []
        for word, pos in tagged:
            # Include conjunctions to better handle compound topics
            if (word not in stop_words and pos.startswith(('NN', 'JJ', 'VB'))) or word in ['and', '&', 'or']:
                topic_words.append(word)
        
        return ' '.join(topic_words) if topic_words else text

    def search_news(self, query: str, provider_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for news articles using the configured search provider.
        
        Args:
            query: The search query string.
            provider_type: Optional provider type to use for this specific search
            
        Returns:
            Dict containing the search results or error information.
        """
        # Use a new provider just for this search if specified
        provider = (SearchProviderFactory.get_provider(provider_type=provider_type) 
                   if provider_type else self.provider)

        if not provider.is_configured():
            return {'error': 'Search provider not configured'}

        search_topic = self.extract_search_topic(query)
        days_to_search = self.extract_time_reference(query)
        
        return provider.search(
            search_topic,
            search_depth="basic",
            topic="news",
            max_results=5,
            include_answer=True,
            include_images=False,
            days=days_to_search
        )

# Test code
class TestNewsSkill(unittest.TestCase):
    def setUp(self):
        self.news_skill = NewsSkill()

    def test_extract_search_topic(self):
        test_cases = [
            ("What's the latest news about artificial intelligence?", "artificial intelligence"),
            ("Tell me the current news regarding climate change", "climate change"),
            ("Search for news about SpaceX launches", "spacex launches"),
            ("What's happening in technology today?", "technology"),
            ("Tell me about AI and machine learning", "ai and machine learning"),  # Test compound topic
        ]
        
        for query, expected in test_cases:
            result = self.news_skill.extract_search_topic(query)
            self.assertEqual(result.lower(), expected.lower())

    def test_extract_time_reference(self):
        test_cases = [
            ("What happened today in tech?", 1),
            ("Show me last week's news about AI", 7),
            ("What's the latest on climate change?", 3),
            ("Tell me about space news from last month", 30),
            ("What happened in politics this year?", 365),
            ("Show me news about crypto", 3),  # Default case
            ("News from past 5 days", 5),  # Test relative time
            ("Updates from last 2 weeks", 14),  # Test relative time
        ]
        
        for query, expected_days in test_cases:
            result = self.news_skill.extract_time_reference(query)
            self.assertEqual(result, expected_days)

    @patch('search_providers.factory.SearchProviderFactory.get_provider')
    def test_search_news_success(self, mock_factory):
        # Mock successful provider response
        mock_response = {
            "answer": "Recent developments in AI...",
            "articles": [
                {
                    "title": "AI Breakthrough",
                    "url": "https://example.com/ai-news",
                    "published_date": "2024-03-20",
                    "content": "Scientists have made significant progress...",
                    "score": 0.95
                }
            ],
            "time_period": "Past 3 days",
            "topic": "AI"
        }
        mock_provider = MagicMock()
        mock_provider.is_configured.return_value = True
        mock_provider.search.return_value = mock_response
        mock_factory.return_value = mock_provider

        # Create a new instance with the mocked provider
        self.news_skill = NewsSkill()
        
        result = self.news_skill.search_news("What's new in AI?")
        self.assertIn("answer", result)
        self.assertIn("articles", result)
        self.assertTrue(len(result["articles"]) > 0)
        self.assertIn("score", result["articles"][0])

    @patch('search_providers.factory.SearchProviderFactory.get_provider')
    def test_search_news_provider_not_configured(self, mock_factory):
        mock_provider = MagicMock()
        mock_provider.is_configured.return_value = False
        mock_factory.return_value = mock_provider

        # Create a new instance with the mocked provider
        self.news_skill = NewsSkill()
        
        result = self.news_skill.search_news("What's new in AI?")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Search provider not configured")

if __name__ == '__main__':
    unittest.main()
