import config
from llm_apis.openai_api import OpenAIClient
import re
from utils import to_clipboard
import os

class CompletionManager:
    def __init__(self, TTS_client):
        self.client = None
        self.setup_client()
        self.model = None
        self.TTS_client = TTS_client

    def setup_client(self):
        """Instantiates the appropriate AI client based on configuration file."""
        if config.COMPLETIONS_API == "openai":
            self.client = OpenAIClient()

        ##TODO add these apis:
        # elif config.COMPLETIONS_API == "together":
        #     self.client = TogetherClient(api_key=config.TOGETHER_API_KEY, model_name=config.TOGETHER_MODEL)
        # elif config.COMPLETIONS_API == "anthropic":
        #     self.client = AnthropicsClient(api_key=config.ANTHROPIC_API_KEY, model_name=config.ANTHROPIC_MODEL)
        else:
            raise ValueError("Unsupported completion API service configured")
        
    def get_completion(self,messages,model,**kwargs):
        response = ''
        stream = self.client.get_completion(messages,model,**kwargs)
        for type, content in self.stream_sentences_from_chunks(stream, clip_start_marker=config.START_SEQ,clip_end_marker=config.END_SEQ):
            if type == "sentence":
                self.TTS_client.run_tts(content)
                    
            elif type == "clipboard_text":
                to_clipboard(content)
            response += content

        return response


    def stream_sentences_from_chunks(self,chunks_stream, clip_start_marker="-CLIPSTART-", clip_end_marker="-CLIPEND-"):
        buffer = ''
        sentence_endings = re.compile(r'(?<=[.!?])\s+|(?<=\n)')
        in_marker = False
        
        for chunk in chunks_stream:
            buffer += chunk

            # Check for clip_start_marker without clip_end_marker
            if clip_start_marker in buffer and not in_marker:
                pre, match, post = buffer.partition(clip_start_marker)
                if pre.strip():
                    yield "sentence", pre.strip()
                buffer = post
                in_marker = True
            
            # Check for clip_end_marker without clip_start_marker
            if clip_end_marker in buffer and in_marker:
                marked_section, _, post_end = buffer.partition(clip_end_marker)
                
                yield "clipboard_text", marked_section.strip()
                buffer = post_end  # Remaining text after the end marker
                in_marker = False  # Reset the marker flag
            
            # Process sentences outside of marked sections
            if not in_marker:
                while True:
                    match = sentence_endings.search(buffer)
                    if match:
                        sentence = buffer[:match.end()]
                        buffer = buffer[match.end():]
                        if sentence.strip():
                            yield "sentence", sentence.strip()
                    else:
                        break
        
        # Yield any remaining content in the buffer as a sentence
        if buffer.strip() and not in_marker:
            yield "sentence", buffer.strip()
        elif buffer.strip() and in_marker:  # Handle any remaining marked text
            yield "clipboard_text", buffer.strip()
