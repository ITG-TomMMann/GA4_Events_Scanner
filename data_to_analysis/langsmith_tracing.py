from langsmith import Langsmith

# Initialize Langsmith
ls = Langsmith(api_key='YOUR_API_KEY')

def trace_api_call(function_name, parameters, result):
    ls.log_event(
        event_type='api_call',
        function=function_name,
        parameters=parameters,
        result=result
    )
