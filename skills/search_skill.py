from nltk import word_tokenize, pos_tag
from typing import Dict, Any, Optional
import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from search_providers import SearchProviderFactory

class SearchSkill:
    def __init__(self, provider_type: Optional[str] = None):
        self.topic_indicators = {
            'about', 'for', 'on', 'related to', 'search', 
            'find', 'look up', 'information about'
        }
        self.provider = SearchProviderFactory.get_provider(provider_type=provider_type)

    def extract_search_topic(self, text: str) -> str:
        """
        Extract the main search topic from the query text.
        
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
                # Filter out common words and get only content words
                topic_words = []
                for word, pos in tagged[i+1:]:
                    if pos.startswith(('NN', 'JJ', 'VB')):  # Only include nouns, adjectives, and verbs
                        topic_words.append(word)
                if topic_words:
                    return ' '.join(topic_words)
        
        # If no specific pattern found, use the original text with common words filtered out
        stop_words = {'what', 'is', 'are', 'the', 'tell', 'me', 'can', 'you', 'please', 'for', 'about'}
        topic_words = [word for word, pos in tagged if word not in stop_words and pos.startswith(('NN', 'JJ', 'VB'))]
        
        return ' '.join(topic_words) if topic_words else text

    def search(self, query: str, provider_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform a general search using the configured search provider.
        
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
        return provider.search(
            search_topic,
            search_depth="basic",
            max_results=3,
            include_answer=True,
            include_images=False
        )

# Test code
class TestSearchSkill(unittest.TestCase):
    def setUp(self):
        self.search_skill = SearchSkill()

    def test_extract_search_topic(self):
        test_cases = [
            ("Search for quantum computing", "quantum computing"),
            ("Tell me about the history of Rome", "history rome"),
            ("Look up information about electric cars", "electric cars"),
            ("What is machine learning?", "machine learning"),
            ("Find recipes for chocolate cake", "recipes chocolate cake"),
        ]
        
        for query, expected in test_cases:
            result = self.search_skill.extract_search_topic(query)
            self.assertEqual(result.lower(), expected.lower())

    @patch('search_providers.factory.SearchProviderFactory.get_provider')
    def test_search_success(self, mock_factory):
        # Mock successful provider response
        mock_response = {
            "answer": "Here's what I found about quantum computing...",
            "results": [
                {
                    "title": "Introduction to Quantum Computing",
                    "url": "https://example.com/quantum",
                    "content": "Quantum computing is an emerging technology...",
                    "score": 0.95
                }
            ]
        }
        mock_provider = MagicMock()
        mock_provider.is_configured.return_value = True
        mock_provider.search.return_value = mock_response
        mock_factory.return_value = mock_provider

        # Create a new instance with the mocked provider
        self.search_skill = SearchSkill()
        
        result = self.search_skill.search("What is quantum computing?")
        self.assertIn("answer", result)
        self.assertIn("results", result)
        self.assertTrue(len(result["results"]) > 0)
        self.assertIn("score", result["results"][0])

    @patch('search_providers.factory.SearchProviderFactory.get_provider')
    def test_search_provider_not_configured(self, mock_factory):
        mock_provider = MagicMock()
        mock_provider.is_configured.return_value = False
        mock_factory.return_value = mock_provider

        # Create a new instance with the mocked provider
        self.search_skill = SearchSkill()
        
        result = self.search_skill.search("What is quantum computing?")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Search provider not configured")

if __name__ == '__main__':
    unittest.main()
