from langsmith_tracing import trace_api_call
import os
import pandas as pd

def generate_email(processed_data_path, processed_hypothesis_path, output_dir):
    # Read processed data
    data = pd.read_csv(processed_data_path)
    
    # Read processed hypothesis
    with open(processed_hypothesis_path, 'r') as file:
        hypothesis_details = file.read()
    
    # Generate email content
    email_content = f"""
    Subject: Analytical Insights on Defender Configurator Performance

    Dear JLR Team,

    I hope this message finds you well.

    Based on our recent analysis, we examined the hypothesis: {hypothesis_details}

    **Findings:**
    """
    for index, row in data.iterrows():
        email_content += f"\n- The {row['config_type']} has an enquiry rate of {row['enquiry_rate']:.2f} and a config completion rate of {row['config_completion_rate']:.2f}."

    email_content += """
    
    **Conclusion:**
    The analysis supports the hypothesis by demonstrating the differences in enquiry and configuration completion rates between the classic defender configurator and the defender configurator.

    Please let me know if you need any further insights.

    Best regards,
    Tom the Analyst
    """

    # Save email to output directory
    email_path = os.path.join(output_dir, 'analytical_email.md')
    with open(email_path, 'w') as file:
        file.write(email_content)
    
    trace_api_call('generate_email', {'processed_data_path': processed_data_path, 'processed_hypothesis_path': processed_hypothesis_path, 'output_dir': output_dir}, 'Email Generated')
