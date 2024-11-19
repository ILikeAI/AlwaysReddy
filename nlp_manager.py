import spacy
from config_loader import config
from typing import List, Dict, Any, Tuple, Optional
from skills.weather_skill import WeatherSkill
from skills.news_skill import NewsSkill
from skills.search_skill import SearchSkill

class NLPManager:
    def __init__(self):
        # Load spaCy model
        """
        Initialize the NLPManager.

        This method loads the spaCy model and stores it in the class instance.
        It also sets up the intent keywords and initializes the entity extractor.
        """
        try:
            self.nlp = spacy.load('en_core_web_md')
        except OSError:
            # Download if not available
            spacy.cli.download('en_core_web_md')
            self.nlp = spacy.load('en_core_web_md')
        
        # Intent keywords
        self.intents = {
            'weather': ['weather', 'temperature', 'forecast', 'rain', 'snow', 'sunny', 'cloudy', 'humidity', 'heat', 'cold', 'hot',
                       'wind', 'storm', 'precipitation', 'celsius', 'fahrenheit', 'degrees', 'sunrise', 'sunset'],
            'news': ['news', 'update', 'latest', 'current', 'happening', 'event', 'story', 'article', 'report'],
            'search': ['search', 'find', 'look up', 'lookup', 'research', 'information about', 'tell me about', 'what is', 'who is']
        }
        
        self.entity_extractor = EntityExtractor(self.nlp)

    def preprocess_text(self, text: str) -> List[str]:
        # Process text using spaCy
        """
        Process text using spaCy.

        This method takes a string of text and preprocesses it using the spaCy library.
        It first converts the text to lowercase and then processes it using the
        English language model.

        The method then filters out the tokens using spaCy's built-in attributes:
        - is_stop: Stop words (e.g. "the", "a", etc.)
        - is_punct: Punctuation (e.g. periods, commas, etc.)
        - len(token.text) > 1: Tokens with more than one character
        - token.text.isalpha(): Tokens that are alphabetic

        The method returns a list of lemmatized tokens (root words).

        :param text: The text to preprocess
        :type text: str
        :return: A list of lemmatized tokens
        :rtype: List[str]
        """
        doc = self.nlp(text.lower())
        
        # Filter tokens using spaCy's built-in attributes
        processed_tokens = [
            token.lemma_ for token in doc
            if not token.is_stop 
            and not token.is_punct
            and len(token.text) > 1
            and token.text.isalpha()
        ]
        
        return processed_tokens

    def classify_intent(self, text: str) -> Tuple[str, float, Optional[Dict[str, Any]]]:
        """
        Classify the intent of a given text.

        This method takes a string of text and classifies its intent into one of the
        following categories: information_query, weather, news, search.

        The method preprocesses the text using the preprocess_text method and then
        checks if any of the intent keywords are present in the tokens. If a keyword
        is found, it calculates the confidence of the classification by dividing the
        number of keywords found by the total number of tokens. If no keyword is found,
        it defaults to an information_query intent with a confidence of 0.3.

        :param text: The text to classify
        :type text: str
        :return: A tuple containing the intent, confidence, and optional entity dictionary
        :rtype: Tuple[str, float, Optional[Dict[str, Any]]]
        """
        tokens = self.preprocess_text(text)
        
        # Intent classification
        for intent, keywords in self.intents.items():
            # Special handling for multi-word keywords
            text_lower = text.lower()
            keyword_matches = sum(1 for keyword in keywords if keyword in text_lower)
            if keyword_matches > 0:
                confidence = keyword_matches / len(tokens)
                return intent, confidence, None
        
        return 'information_query', 0.3, None


class EntityExtractor:
    def __init__(self, nlp):
        """
        Initialize the EntityExtractor.

        This method sets up the entity extractor with the provided spaCy NLP model.

        :param nlp: The spaCy NLP model used for entity extraction.
        :type nlp: spacy.language.Language
        """
        self.nlp = nlp

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        doc = self.nlp(text)
        entities = {}
        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            entities[ent.label_].append(ent.text)
        return entities

def get_nlp_context(AR, message_content: str) -> str:
    """
    Add contextual information to a message based on the user's intent.

    If the intent is 'weather', add information about the user's preferred unit of measurement
    for weather information, and the user's location if it can be detected.

    If the intent is 'news', add news search results related to the query.

    If the intent is 'search', add general search results related to the query.

    :param AR: The AlwaysReddy object
    :param message_content: The message content
    :return: The message content with additional context
    :rtype: str
    """
    nlp_manager = NLPManager()
    intent, confidence, additional_info = nlp_manager.classify_intent(message_content)
    
    if intent == 'weather':
        weather_skill = WeatherSkill()
        message_content += f"\n\nTHE USER APPEARS TO HAVE A QUESTION ABOUT THE WEATHER, USE THIS DATA TO HELP YOU ANSWER IT:\n```{weather_skill.getLocationWeather(message_content)}```"
        unit = str(config.DEFAULT_UNITS) or 'METRIC'
        message_content += f"\n\nTHE USER PREFERS TO RECEIVE WEATHER INFORMATION IN A {unit} FORMAT. DO NOT ABBREVIATE UNITS OF MEASURE eg. USE 'CELSIUS' INSTEAD OF 'C'. KEEP THE FORECAST SOUNDING NATURAL AND NOT ROBOTIC."
    
    elif intent == 'news':
        news_skill = NewsSkill(provider_type=config.NEWS_PROVIDER)
        news_results = news_skill.search_news(message_content)
        if 'error' not in news_results:
            message_content += f"\n\nTHE USER APPEARS TO HAVE A QUESTION ABOUT NEWS, USE THIS DATA TO HELP YOU ANSWER IT:\n```{news_results}```"
            message_content += "\n\nPLEASE PROVIDE A NATURAL SUMMARY OF THE NEWS, INCLUDING THE MOST RELEVANT AND RECENT INFORMATION. PROVIDE 5 SENTENCES OF DETAIL."
    
    elif intent == 'search':
        search_skill = SearchSkill(provider_type=config.SEARCH_PROVIDER)
        search_results = search_skill.search(message_content)
        if 'error' not in search_results:
            message_content += f"\n\nTHE USER APPEARS TO BE SEARCHING FOR INFORMATION, USE THIS DATA TO HELP YOU ANSWER IT:\n```{search_results}```"
            message_content += "\n\nPLEASE PROVIDE A CLEAR AND CONCISE ANSWER BASED ON THE SEARCH RESULTS AND YOUR EXISTING KNOWLEDGE, FOCUSING ON THE MOST RELEVANT INFORMATION TO ANSWER THEIR QUESTION."
   
    return message_content
    
   

def main():
    classifier = NLPManager()
    
    test_queries = [
        "What is the best restaurant in town?",
        "Book a flight to New York",
        "Compare iPhone and Android phones",
        "Recommend a good book to read",
        "What's the weather like in Buffalo today?",
        "Will it rain tomorrow in New York?",
        "How's the temperature in Los Angeles this weekend?",
        "How's the weather in Los Angeles this weekend?",
        "What is the weather in Miami?",
        "Describe the wind conditions in Los Angeles for the rest of the week.",
        "Give me a weather update for New York",
        "Search for quantum computing",
        "Look up the history of Rome",
        "Find information about electric cars"
    ]
    
    import time
    for query in test_queries:
        #start_time = time.time()
        intent, confidence, additional_info = classifier.classify_intent(query)
        entities = classifier.entity_extractor.extract_entities(query)
        print(f"Query: '{query}'")
        print(f"Intent: {intent}")
        print(f"Confidence: {confidence:.2f}")
        print(f"Entities: {entities}")
        if additional_info:
            print("Additional Information:")
            for key, value in additional_info.items():
                print(f"  {key}: {value}")
        print()
        start_time = time.time()
        if intent == 'weather':
            weather_skill = WeatherSkill()
            print(str(weather_skill.getLocationWeather(query))[:200])
        elif intent == 'search':
            search_skill = SearchSkill()
            print(str(search_skill.search(query))[:200])
        print()
        end_time = time.time()
        print(f"Time taken: {end_time - start_time} seconds")
        print()

if __name__ == "__main__":
    main()
