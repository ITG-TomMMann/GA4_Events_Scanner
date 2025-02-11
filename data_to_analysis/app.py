import streamlit as st
from GA4_events_scaner import GA4EventCollector

def main():
    st.title("GA4 Events Scanner")
    
    url = st.text_input("Enter the URL to scan:", "")
    section_selector = st.text_input("Section Selector (CSS):", "body")
    target_text = st.text_input("Filter by Target Text (optional):", "")
    wait_time = st.slider("Wait Time for Page Load (seconds):", 1, 10, 5)
    
    if st.button("Start Scanning"):
        if not url:
            st.error("Please enter a valid URL.")
            return
        collector = GA4EventCollector()
        with st.spinner("Collecting events..."):
            events = collector.collect_events_from_url(
                url,
                wait_time=wait_time,
                section_selector=section_selector,
                target_text=target_text
            )
            collector.export_events("streamlit_output/events")
            collector.close()
        st.success("Scanning completed.")
        st.write(f"Collected {len(events['dataLayer'])} dataLayer events and {len(events['ga4'])} GA4 events.")
        st.download_button(
            label="Download DataLayer JSON",
            data=open("streamlit_output/events_dataLayer.json").read(),
            file_name="dataLayer.json",
            mime="application/json"
        )
        st.download_button(
            label="Download GA4 JSON",
            data=open("streamlit_output/events_GA4.json").read(),
            file_name="GA4.json",
            mime="application/json"
        )

if __name__ == "__main__":
    main()
