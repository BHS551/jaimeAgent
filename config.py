import os
import sys

# Load API credentials and model name from environment
defined_api_key = os.getenv('OPENAI_API_KEY')
if not defined_api_key:
    sys.exit("ERROR: Please set the OPENAI_API_KEY environment variable.")
OPENAI_API_KEY = defined_api_key

# You can override the model via OPENAI_MODEL; default to gpt-4\OPENAI_MODEL default: 
MODEL_NAME = "gpt-4o-mini"