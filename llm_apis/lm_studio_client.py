from openai import OpenAI
import base64
import httpx

class LM_StudioClient:
    """Client for interacting with LM studio using a local server and openai lib."""
    def __init__(self, base_url="http://localhost:1234/v1", verbose=False):
        self.client = OpenAI(base_url=base_url, api_key="not-needed")
        self.verbose = verbose

    def stream_completion(self, messages, model, **kwargs):
        """Get completion from LM studio API.

        Args:
            messages (list): List of messages.
            model (str): Model for completion
            **kwargs: Additional keyword arguments.

        Yields:
            str: Text generated.
        """
        try:
            # Process messages to handle multimodal content
            processed_messages = []
            for message in messages:
                content = []
                
                # Handle text content
                if isinstance(message.get('content'), str):
                    content.append({"type": "text", "text": message['content']})
                # Handle multimodal content
                elif isinstance(message.get('content'), list):
                    for item in message['content']:
                        if item.get('type') == 'image':
                            content.append({
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{item['source']['media_type']};base64,{item['source']['data']}"
                                }
                            })
                        else:
                            content.append(item)
                
                processed_messages.append({
                    "role": message['role'],
                    "content": content if content else message.get('content')
                })

            stream = self.client.chat.completions.create(
                model=model,
                messages=processed_messages,
                stream=True,
                **kwargs
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            if self.verbose:
                import traceback
                traceback.print_exc()
            else:
                print(f"An error occurred streaming completion from LM studio: {e}")
            raise RuntimeError(f"An error occurred streaming completion from LM studio: {e}")

# Test the LMStudioClient
if __name__ == "__main__":
    client = LM_StudioClient(verbose=True)
    
    #test text only   
    messages = [
        {
            "role": "system",
            "content": "Be precise and concise."
        },
        {
            "role": "user",
            "content": "What is the capital of France?"
        }
    ]
    model = "your_model_name_here"  # Replace with your actual model name

    print("\nText-only Response:")
    for chunk in client.stream_completion(messages, model):
        print(chunk, end='', flush=True)
    print()  # Add a newline at the end

    
    #test multimodal
    image_url = "https://upload.wikimedia.org/wikipedia/commons/a/a7/Camponotus_flavomarginatus_ant.jpg"
    image_media_type = "image/jpeg"
    image_data = base64.b64encode(httpx.get(image_url).content).decode("utf-8")
 
    messages = [
        {
            "role": "system",
            "content": "Respond only in rhyming couplets."
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Should I eat this?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }
                }
            ]
        }
    ]
   
    print("\nMultimodal Response:")
    for chunk in client.stream_completion(messages, model):
        print(chunk, end='', flush=True)
    print()
