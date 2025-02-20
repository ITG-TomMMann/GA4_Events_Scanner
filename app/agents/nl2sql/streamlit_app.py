import streamlit as st
import requests

# Initialize session state variables
if "session_id" not in st.session_state:
    st.session_state["session_id"] = None
if "conversation" not in st.session_state:
    st.session_state["conversation"] = []
if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""

st.set_page_config(page_title="Text-to-SQL Chat", page_icon="💬")

st.title("💬 Text-to-SQL Chat")

# Function to send query or follow-up message
def send_query(message):
    """Send user input to FastAPI and store response."""
    if st.session_state["session_id"] is None:
        # First message, start a new session
        api_url = "http://127.0.0.1:8000/query"
        payload = {"query": message}
    else:
        # Follow-up message
        api_url = "http://127.0.0.1:8000/followup"
        payload = {"follow_up_query": message, "session_id": st.session_state["session_id"]}

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        data = response.json()

        # Save session ID
        st.session_state["session_id"] = data.get("session_id")

        # Extract AI response
        ai_response = data.get("response") or data.get("sql")

        if ai_response:
            st.session_state["conversation"].append({"role": "assistant", "message": ai_response})
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with the server: {e}")

# Function to handle user input
def handle_send():
    input_text = st.session_state["user_input"].strip()
    if input_text:
        # Append user message
        st.session_state["conversation"].append({"role": "user", "message": input_text})
        send_query(input_text)
        st.session_state["user_input"] = ""  # Clear input field

# Chat interface
st.markdown("### 🗨️ Conversation")
chat_container = st.container()
with chat_container:
    for chat in st.session_state["conversation"]:
        if chat["role"] == "user":
            st.markdown(f"**🧑 You:** {chat['message']}")
        else:
            st.markdown(f"**🤖 Assistant:** {chat['message']}")

# User input field with Enter key support
user_input = st.text_input("Type your message here...", key="user_input", on_change=handle_send)

# "Send" button (useful for mobile users)
st.button("Send", on_click=handle_send)

# Clear Memory Button
if st.button("🧹 Clear Memory"):
    if st.session_state["session_id"]:
        try:
            clear_response = requests.post(
                "http://127.0.0.1:8000/clear_memory",
                json={"session_id": st.session_state["session_id"]}
            )
            clear_response.raise_for_status()
            st.session_state["session_id"] = None
            st.session_state["conversation"] = []
            st.success("Memory cleared successfully.")
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to clear memory: {e}")
    else:
        st.warning("No active session to clear.")
