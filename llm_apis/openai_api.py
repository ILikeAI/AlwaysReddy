from openai import OpenAI
import os

class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    
    def get_completion(self,messages,model,temperature=0.7,max_tokens=2048,**kwargs):
        try:
            full=''
            stream = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )

            for chunk in stream:
                
                content = chunk.choices[0].delta.content
                
                if content != None:
                    yield content
                    full += content


        except Exception as e:
            raise RuntimeError(f"An error occurred streaming completion from openai: {e}")
        