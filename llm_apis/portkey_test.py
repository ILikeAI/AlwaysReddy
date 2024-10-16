from portkey_ai import Portkey

client = Portkey(
  base_url="https://api.portkey.ai/v1",
  api_key="ul3h7nwcLc4ckKUXnmn1NP8hGssz"  # defaults to os.environ.get("PORTKEY_API_KEY")
)

# Make the prompt creation call with the variables
prompt_completion = client.prompts.completions.create(
  prompt_id="pp-pirate-bf8dcd",
  variables={"role":"user","content":"Hello, how are you?"}
)

# Make the prompt creation call with the variables - stream mode
stream_prompt_completion = client.prompts.completions.create(
  prompt_id="pp-pirate-bf8dcd",
  variables={"role":"user","content":"Hello, how are you?"},
  stream=True
)
