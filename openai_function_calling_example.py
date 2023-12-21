# Dependencies
# !pip install scipy
# !pip install tenacity
# !pip install tiktoken
# !pip install termcolor 
# !pip install openai
# !pip install requests

import json
import openai
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored
from dotenv import load_dotenv

GPT_MODEL = "gpt-3.5-turbo-0613"

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

