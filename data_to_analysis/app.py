import streamlit as st
from data_to_analysis.GA4_events_scaner import GA4EventCollector
import os
import re
import json

def sanitize_url(url: str) -> str:
    """Sanitize the URL to create a valid directory name."""
    return re.sub(r'[^a-zA-Z0-9]', '_', url)

def sanitize_url(url: str) -> str:
    """Sanitize the URL to create a valid directory name."""
    return re.sub(r'[^a-zA-Z0-9]', '_', url)
    st.title("GA4 Events Scanner")

    url = st.text_input("Enter the URL to scan:", "")
    section_selector = st.text_input("Section Selector (CSS):", "body")
    target_text = st.text_input("Filter by Target Text (optional):", "")
    wait_time = st.slider("Wait Time for Page Load (seconds):", 1, 10, 5)

    if st.button("Start Scanning"):
        if not url:
            st.error("Please enter a valid URL.")
            return

        # Sanitize URL to determine output directory
        sanitized_url = sanitize_url(url)
        output_dir = os.path.join(os.getcwd(), sanitized_url)

        # Ensure output directory exists (optional, as script creates it)
        os.makedirs(output_dir, exist_ok=True)

        # Execute the GA4EventCollector directly
        with st.spinner("Collecting events..."):
            try:
                collector = GA4EventCollector()
                events = collector.collect_events_from_url(
                    url=url,
                    section_selector=section_selector,
                    target_text=target_text,
                    wait_time=wait_time
                )
                collector.export_events(os.path.join(output_dir, 'gtm_and_ga4_events'))
                st.success("Scanning completed.")
            except subprocess.CalledProcessError as e:
                st.error(f"An error occurred while collecting events: {e}")
                return

        # Define paths to the output files
        data_layer_json_path = os.path.join(output_dir, 'gtm_and_ga4_events_dataLayer.json')
        ga4_json_path = os.path.join(output_dir, 'gtm_and_ga4_events_GA4.json')

        # Check if output files exist
        if not os.path.exists(data_layer_json_path) or not os.path.exists(ga4_json_path):
            st.error("Output files not found. Please ensure the GA4_events_scaner.py script ran successfully.")
            return

        # Load and display the number of events
        try:
            with open(data_layer_json_path, 'r', encoding='utf-8') as f:
                data_layer_events = json.load(f)
            with open(ga4_json_path, 'r', encoding='utf-8') as f:
                ga4_events = json.load(f)

            st.write(f"**Collected {len(data_layer_events)} DataLayer events and {len(ga4_events)} GA4 events.**")
        except json.JSONDecodeError as e:
            st.error(f"Failed to decode JSON output: {e}")
            return

        # Provide download buttons for the JSON files
        try:
            with open(data_layer_json_path, 'r', encoding='utf-8') as f:
                data_layer_content = f.read()
            with open(ga4_json_path, 'r', encoding='utf-8') as f:
                ga4_content = f.read()

            st.download_button(
                label="Download DataLayer JSON",
                data=data_layer_content,
                file_name="events_dataLayer.json",
                mime="application/json"
            )
            st.download_button(
                label="Download GA4 JSON",
                data=ga4_content,
                file_name="events_GA4.json",
                mime="application/json"
            )
        except Exception as e:
            st.error(f"Error preparing download buttons: {e}")

    # Optional: Display the output files if they exist
    if st.checkbox("Show Output Files"):
        if st.button("Refresh Output"):
            sanitized_url = sanitize_url(url)
            output_dir = os.path.join(os.getcwd(), sanitized_url)
            data_layer_json_path = os.path.join(output_dir, 'events_dataLayer.json')
            ga4_json_path = os.path.join(output_dir, 'events_GA4.json')

            if os.path.exists(data_layer_json_path):
                st.subheader("DataLayer Events")
                with open(data_layer_json_path, 'r', encoding='utf-8') as f:
                    data_layer_events = json.load(f)
                st.json(data_layer_events)

            if os.path.exists(ga4_json_path):
                st.subheader("GA4 Events")
                with open(ga4_json_path, 'r', encoding='utf-8') as f:
                    ga4_events = json.load(f)
                st.json(ga4_events)

if __name__ == "__main__":
    main()
