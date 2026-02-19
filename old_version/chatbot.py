"""
Chatbot Interface for Dataset Search
Handles natural language interactions for searching datasets using LLM web search
"""

import re
import logging
from typing import Dict, Any, Optional, List, Tuple
from tools.web_search import LLMWebSearcher
from tools.download import DatasetDownloader

logger = logging.getLogger(__name__)


class DataProcessingChatbot:
    """Chatbot interface for dataset search using LLM web search"""
    
    def __init__(
        self,
        llm_api_key: Optional[str] = None,
        llm_model: str = "gpt-4o-mini",
        llm_provider: str = "openai"
    ):
        """
        Initialize the chatbot
        
        Args:
            llm_api_key: API key for LLM service
            llm_model: LLM model name
            llm_provider: LLM provider ('openai', 'anthropic')
        """
        self.searcher = LLMWebSearcher(
            api_key=llm_api_key,
            model=llm_model,
            provider=llm_provider
        )
        self.downloader = DatasetDownloader(work_dir="./data")
        self.last_downloaded_path = None
        self.conversation_history = []
        self.last_search_results = []
        
        logger.info("DataProcessingChatbot initialized (LLM web search)")
    
    def parse_intent(self, user_input: str) -> Tuple[str, Dict[str, Any]]:
        """
        Parse user input to extract intent and parameters
        
        Args:
            user_input: User's natural language input
            
        Returns:
            Tuple of (intent, parameters)
        """
        user_input_lower = user_input.lower().strip()
        
        # Search intent
        if any(keyword in user_input_lower for keyword in ['search', 'search for', 'find', 'look for', 'give me', 'do you know']):
            # Extract query
            query = self._extract_query(user_input)
            source = self._extract_source(user_input)
            limit = self._extract_number(user_input) or 10
            
            return "search", {
                "query": query,
                "source": source,
                "limit": limit
            }
        
        # Download intent
        if any(keyword in user_input_lower for keyword in ['download', 'get', 'fetch', 'pull', 'save']):
            # Extract URL
            url = self._extract_url(user_input)
            # Extract source type
            source = self._extract_source(user_input) or 'auto'
            
            return "download", {
                "url_or_id": url,
                "source": source
            }
        
        # Show/List intent
        if any(keyword in user_input_lower for keyword in ['show', 'list', 'display', 'what']):
            if 'result' in user_input_lower or 'dataset' in user_input_lower:
                return "show_results", {}
        
        # Help intent
        if any(keyword in user_input_lower for keyword in ['help', 'what can you do', 'commands']):
            return "help", {}
        
        return "unknown", {}
    
    def _extract_query(self, text: str) -> str:
        """Extract search query from text"""

        return text.strip()
    
    def _extract_source(self, text: str) -> Optional[str]:
        """Extract data source from text"""
        text_lower = text.lower()
        if 'huggingface' in text_lower or 'hugging face' in text_lower or 'hf' in text_lower:
            return 'huggingface'
        if 'kaggle' in text_lower:
            return 'kaggle'
        if 'url' in text_lower or 'http' in text_lower:
            return 'url'
        return None

    def _extract_number(self, text: str) -> Optional[int]:
        """Extract a number from text"""
        numbers = re.findall(r'\b(\d+)\b', text)
        if numbers:
            return int(numbers[0])

        # Try to convert English words to numbers
        try:
            from word2number import w2n
            # Extract potential number phrases
            text_lower = text.lower()
            # Common patterns: "five", "ten datasets", "first five", etc.
            number_phrases = re.findall(r'\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|hundred|thousand)\b', text_lower)
            if number_phrases:
                # Try to convert the first number phrase found
                number_str = ' '.join(number_phrases[:3])  # Take up to 3 words
                return w2n.word_to_num(number_str)
        except (ImportError, ValueError):
            pass

        return None
    
    def _extract_dataset_id(self, text: str) -> Optional[str]:
        """Extract dataset ID from text"""
        # Extract quoted text
        quoted = re.findall(r'"([^"]+)"', text)
        if quoted:
            return quoted[0]
        
        # Extract common dataset names
        common_datasets = ['imdb', 'glue', 'squad', 'mnist', 'cifar']
        for dataset in common_datasets:
            if dataset in text.lower():
                return dataset
        
        return None
    
    def _extract_index(self, text: str) -> Optional[int]:
        """Extract index/number from text (e.g., 'first', 'second', '1', '2')"""
        text_lower = text.lower()
        
        # Number words
        number_words = {
            'first': 0, 'second': 1, 'third': 2, 'fourth': 3, 'fifth': 4,
            '1st': 0, '2nd': 1, '3rd': 2, '4th': 3, '5th': 4
        }
        
        for word, idx in number_words.items():
            if word in text_lower:
                return idx
        
        # Numeric
        numbers = re.findall(r'\b(\d+)\b', text)
        if numbers:
            return int(numbers[0]) - 1  # Convert to 0-based index
        
        return None
    
    def _extract_path(self, text: str) -> Optional[str]:
        """Extract file path from text"""
        # Look for path-like strings
        paths = re.findall(r'[./\w]+(?:/[\w.]+)+', text)
        if paths:
            return paths[0]
        return None

    def _extract_url(self, text: str) -> Optional[str]:
        """Extract URL from text"""
        # Look for HTTP/HTTPS URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        if urls:
            return urls[0]
        
        # Look for HuggingFace dataset URLs
        hf_pattern = r'huggingface\.co/datasets/[^\s<>"{}|\\^`\[\]]+'
        hf_urls = re.findall(hf_pattern, text)
        if hf_urls:
            return 'https://' + hf_urls[0]
        return None
    
    def _extract_processing_config(self, text: str) -> Dict[str, Any]:
        """Extract processing configuration from text"""
        text_lower = text.lower()
        config = {}
        clean_config = {}
        transform_config = {}
        
        # Cleaning options
        if any(word in text_lower for word in ['remove duplicates', 'deduplicate']):
            clean_config['remove_duplicates'] = True
        if any(word in text_lower for word in ['remove missing', 'drop na', 'drop missing']):
            clean_config['remove_missing'] = True
        if any(word in text_lower for word in ['fill missing', 'fill na']):
            clean_config['fill_missing'] = True
        if any(word in text_lower for word in ['remove outliers', 'filter outliers']):
            clean_config['remove_outliers'] = True
        
        # Transformation options
        if any(word in text_lower for word in ['normalize', 'normalization']):
            transform_config['normalize'] = True
        if any(word in text_lower for word in ['encode', 'encoding', 'categorical']):
            transform_config['encode_categorical'] = True
        
        # Output format
        if 'parquet' in text_lower:
            config['output_format'] = 'parquet'
        elif 'json' in text_lower:
            config['output_format'] = 'json'
        else:
            config['output_format'] = 'csv'
        
        if clean_config:
            config['clean'] = True
            config['clean_config'] = clean_config
        
        if transform_config:
            config['transform'] = True
            config['transform_config'] = transform_config
        
        return config if config else None
    
    def handle_search(self, params: Dict[str, Any]) -> str:
        """Handle search intent"""
        query = params.get('query')
        if not query:
            return "I need a search query. For example: 'search for sentiment analysis datasets'"
        
        limit = params.get('limit', 10)
        
        try:
            results = self.searcher.search(query, limit=limit)
            self.last_search_results = results
            
            if not results:
                return f"I couldn't find any datasets matching '{query}'. Try a different search term."
            
            response = f"I found {len(results)} dataset(s) for '{query}':\n\n"
            for i, result in enumerate(results, 1):
                name = result.get('name', 'Unknown')
                description = result.get('description', 'No description available')
                source = result.get('source', 'Unknown')
                response += f"{i}. **{name}**\n"
                response += f"   Description: {description}\n"
                response += f"   Source: {source}\n\n"
            
            return response
            
        except Exception as e:
            error_msg = str(e)
            return f"❌ Sorry, I encountered an error while searching: {error_msg}"

    def handle_download(self, params: Dict[str, Any]) -> str:
        """Handle download intent"""
        url_or_id = params.get('url_or_id')
        source = params.get('source', 'auto')
        
        if not url_or_id:
            return "I need a URL or dataset identifier to download. For example:\n- 'download https://example.com/data.csv'\n- 'download from https://huggingface.co/datasets/imdb'"
        
        try:
            result = self.downloader.download(source=source, url_or_id=url_or_id)
            
            if result['success']:
                self.last_downloaded_path = result['path']
                size_mb = result.get('size', 0) / (1024 * 1024)
                
                response = f"✅ Successfully downloaded!\n\n"
                response += f"📁 Location: {result['path']}\n"
                response += f"📊 Size: {size_mb:.2f} MB\n"
                
                if result.get('extracted'):
                    response += f"📦 Extracted from: {result.get('original_path')}\n"
                
                return response
            else:
                return f"❌ Download failed: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            return f"❌ Sorry, I encountered an error: {str(e)}"
    
    def handle_show_results(self, params: Dict[str, Any]) -> str:
        """Handle show results intent"""
        if not self.last_search_results:
            return "No search results to show. Please search for datasets first."
        
        response = f"I found {len(self.last_search_results)} dataset(s):\n\n"
        for i, result in enumerate(self.last_search_results, 1):
            name = result.get('name', 'Unknown')
            description = result.get('description', 'No description available')
            source = result.get('source', 'Unknown')
            response += f"{i}. **{name}**\n"
            response += f"   Description: {description}\n"
            response += f"   Source: {source}\n\n"
        return response
    
    def handle_help(self, params: Dict[str, Any]) -> str:
        """Handle help intent"""

        return """
        🤖 **Dataset Search Chatbot Help**

        I can help you search for datasets! Here's what I can do:

        **Search:**
            - "search for sentiment analysis datasets"
            - "find text classification datasets"
            - "show me computer vision datasets"
            - "search flood datasets"

        **Other:**
            - "show results" - Show last search results
            - "help" - Show this help message

        **Examples:**
            - "search for sentiment analysis"
            - "find image classification datasets"
            - "show me text datasets"

        Just tell me what kind of datasets you're looking for! 🚀
        """
    
    def chat(self, user_input: str) -> str:
        """
        Process user input and return response
        
        Args:
            user_input: User's natural language input
            
        Returns:
            Bot's response
        """
        # Store conversation
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Parse intent
        intent, params = self.parse_intent(user_input)
        print(f"Intent: {intent}, Params: {params}")
        
        # Handle intent
        if intent == "search":
            response = self.handle_search(params)
        elif intent == "download":  
            response = self.handle_download(params)
        elif intent == "show_results":
            response = self.handle_show_results(params)
        elif intent == "help":
            response = self.handle_help(params)
        elif intent == "unknown":
            response = "I'm not sure what you want me to do. Try saying:\n- 'search for [topic] datasets'\n- 'show results'\n- 'help' for more options"
        else:
            response = "I didn't understand that. Type 'help' to see what I can do."
        
        # Store response
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def start_chat(self):
        """Start interactive chat session"""
        print("=" * 60)
        print("🤖 Dataset Search Chatbot")
        print("=" * 60)
        print("\nHi! I can help you search for datasets.")
        print("\nType 'help' to see what I can do, or 'quit' to exit.\n")
        
        while True:
            try:
                user_input = input(">>> You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("\n👋 Goodbye! Happy data processing!")
                    break
                
                response = self.chat(user_input)
                print(f"\n>>> Bot: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Happy data processing!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")
