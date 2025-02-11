from langsmith import Langsmith

# Initialize Langsmith
ls = Langsmith(api_key='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')

def trace_api_call(function_name, parameters, result):
    ls.log_event(
        event_type='api_call',
        function=function_name,
        parameters=parameters,
        result=result
    )
