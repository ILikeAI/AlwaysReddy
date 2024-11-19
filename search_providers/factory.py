from typing import Optional, Dict, Type
from .base_provider import BaseSearchProvider
from .tavily_provider import TavilySearchProvider
from .bing_provider import BingSearchProvider
from .brave_provider import BraveSearchProvider
from .exa_provider import ExaSearchProvider

class SearchProviderFactory:
    """
    Factory class for creating search provider instances.
    Supports multiple provider types and handles provider configuration.
    """
    
    # Registry of available providers
    _providers: Dict[str, Type[BaseSearchProvider]] = {
        'tavily': TavilySearchProvider,
        'bing': BingSearchProvider,
        'brave': BraveSearchProvider,
        'exa': ExaSearchProvider
    }
    
    @classmethod
    def get_provider(
        cls,
        provider_type: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> BaseSearchProvider:
        """
        Get an instance of the specified search provider.
        
        Args:
            provider_type: Type of provider to create (defaults to config.SEARCH_PROVIDER)
            api_key: Optional API key for the provider
            
        Returns:
            An instance of the specified provider
            
        Raises:
            ValueError: If the specified provider type is not supported
        """
        # Import config here to avoid circular imports
        from config import SEARCH_PROVIDER
        
        # Use provided provider_type or fall back to config
        provider_type = provider_type or SEARCH_PROVIDER
        
        provider_class = cls._providers.get(provider_type.lower())
        if not provider_class:
            raise ValueError(
                f"Unsupported provider type: {provider_type}. "
                f"Available providers: {', '.join(cls._providers.keys())}"
            )
        
        return provider_class(api_key=api_key)
    
    @classmethod
    def register_provider(
        cls,
        provider_type: str,
        provider_class: Type[BaseSearchProvider]
    ) -> None:
        """
        Register a new provider type.
        
        Args:
            provider_type: Name of the provider type
            provider_class: Provider class that implements BaseSearchProvider
            
        Raises:
            TypeError: If provider_class doesn't inherit from BaseSearchProvider
        """
        if not issubclass(provider_class, BaseSearchProvider):
            raise TypeError(
                f"Provider class must inherit from BaseSearchProvider. "
                f"Got {provider_class.__name__}"
            )
        
        cls._providers[provider_type.lower()] = provider_class
