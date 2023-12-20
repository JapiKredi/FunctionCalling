import openai
import os
import requests
import json
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

