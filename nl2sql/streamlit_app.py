import streamlit as st
import requests

# Initialize session state variables
if 'session_id' not in st.session_state:
    st.session_state['session_id'] = None
if 'conversation' not in st.session_state:
    st.session_state['conversation'] = []

st.set_page_config(page_title="Text-to-SQL Chat Interface", page_icon="💬")

st.title("💬 Text-to-SQL Chat Interface")

# Function to send user query to FastAPI
def send_query(message):
    api_url = "http://127.0.0.1:8000/query" if st.session_state['session_id'] is None else "http://127.0.0.1:8000/followup"
    payload = {
        "query": message
    }
    if st.session_state['session_id']:
        payload["session_id"] = st.session_state['session_id']
    
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        data = response.json()
        st.session_state['session_id'] = data.get('session_id')
        ai_response = data.get('response')
        st.session_state['conversation'].append({"role": "assistant", "message": ai_response})
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with the server: {e}")

# User input section
with st.form(key='chat_form', clear_on_submit=True):
    user_input = st.text_input("You:", "")
    submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        st.session_state['conversation'].append({"role": "user", "message": user_input})
        send_query(user_input)
        st.experimental_rerun()

# Display conversation
st.markdown("### Conversation")
for chat in st.session_state['conversation']:
    if chat['role'] == 'user':
        st.markdown(f"**You:** {chat['message']}")
    else:
        st.markdown(f"**Assistant:** {chat['message']}")

# Clear Memory Button
if st.button("🧹 Clear Memory"):
    if st.session_state['session_id']:
        try:
            clear_response = requests.post("http://127.0.0.1:8000/clear_memory", json={"session_id": st.session_state['session_id']})
            clear_response.raise_for_status()
            st.session_state['session_id'] = None
            st.session_state['conversation'] = []
            st.success("Memory cleared successfully.")
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to clear memory: {e}")
    else:
        st.warning("No active session to clear.")
