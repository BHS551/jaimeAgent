import os
import sys

# Load API credentials and model name from environment
defined_api_key = "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"
if not defined_api_key:
    sys.exit("ERROR: Please set the OPENAI_API_KEY environment variable.")
OPENAI_API_KEY = defined_api_key

# You can override the model via OPENAI_MODEL; default to gpt-4\OPENAI_MODEL default: 
MODEL_NAME = "gpt-4o-mini"
