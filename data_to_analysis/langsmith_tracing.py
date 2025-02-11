import os
from langsmith import Langsmith

# Get API key from environment variable
api_key = os.getenv('LANGSMITH_API_KEY')

# Initialize Langsmith
ls = Langsmith(api_key=api_key)

def trace_api_call(function_name, parameters, result):
    ls.log_event(
        event_type='api_call',
        function=function_name,
        parameters=parameters,
        result=result
    )
