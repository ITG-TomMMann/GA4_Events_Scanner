from langsmith_tracing import trace_api_call

def process_hypothesis(md_path, output_dir):
    # Read the hypothesis from the Markdown file
    with open(md_path, 'r') as file:
        hypothesis = file.read()
    
    # Define processing steps based on O1 model
    processing_steps = [
        "Outline comparison of defender vs classic defender performance.",
        "Aggregate data to compare the two config types.",
        "Define enquiry and config completion rates as enquiries/total visitors.",
        "Compare the two values according to the hypothesis and provide an answer."
    ]
    
    # Write the processed hypothesis to output
    processed_hypothesis_path = os.path.join(output_dir, 'processed_hypothesis.md')
    with open(processed_hypothesis_path, 'w') as file:
        file.write(hypothesis)
        for step in processing_steps:
            file.write(f"\n\n- {step}")
    
    trace_api_call('process_hypothesis', {'md_path': md_path, 'output_dir': output_dir}, processed_hypothesis_path)
    
    return processed_hypothesis_path
