import streamlit as st
import base64
from bon_voyage_step3 import initialize_messages, get_bon_voyage_response

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

company_logo = "images/dubrovnik_image.jpg"
bon_voyage_icon = "images/plane_icon.png"
background_image = get_base64_image("images/bon_voyage_default_background.png")

#This sets up the name in the browser tab
st.set_page_config(
    page_title="Bon Voyage AI – Travel Assistance",
    layout="centered"
)

st.markdown(f"""
    <style>
    * {{
        font-family: 'Aptos Display', sans-serif;
    }}
    .stChatInput textarea {{
        font-family: 'Aptos Display', sans-serif;
    }}
    .stApp {{
        background-image: url("data:image/png;base64,{background_image}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
""", unsafe_allow_html=True)

#Add the company logo on top of the page
st.image(company_logo)
st.caption("Dubrovnik, Croatia – One of the most stunning coastal cities in the world")


#Add a title under the company logo
st.title("Bon Voyage AI – Your Personal Travel Assistant")

#Initialize conversation memory once per session
#The conversation is initialized with the system prompt
#This code is using function initialize_messages() in the other file
if "messages" not in st.session_state:
    st.session_state.messages = initialize_messages()

    #Add Ivan's greeting as the first visible message
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello there! My name is Ivan, and I’ll help you plan your next trip. Tell me your nationality, travel goal, month, budget, and trip duration whenever you're ready."
    })

# Display chat history (skip system message)
# this goes over the previous exchanges in the conversations and prints
# them in order.
# Display chat history (skip system message)
# Display chat history (skip system message and tool messages)
for msg in st.session_state.messages:
    if isinstance(msg, dict):
        if msg["role"] == "user":
            st.chat_message("user", avatar="👀").write(msg["content"])
        elif msg["role"] == "assistant" and msg.get("content"):
            st.chat_message("assistant", avatar=bon_voyage_icon).write(msg["content"])
        # skip "tool" and "system" messages — they're internal
    else:
        # handle any LangChain message objects just in case
        if hasattr(msg, "content") and msg.content:
            role = "user" if "Human" in type(msg).__name__ else "assistant"
            avatar = "👀" if role == "user" else bon_voyage_icon
            st.chat_message(role, avatar=avatar).write(msg.content)
# Chat input
# allows the user to type in a new prompt
user_input = st.chat_input("Ask Ivan a question...")

if user_input:
    # displays the new prompt as part of the conversation
    st.chat_message("user", avatar="👀").write(user_input)

    # calls function get_bon_voyage_response()
    # from the other file. The function updates the list by appending the
    # new message(s) and returns the LLM response to the latest prompt
    with st.spinner("Ivan is thinking..."):
        response, updated_messages = get_bon_voyage_response(
            st.session_state.messages,
            user_input
        )

    # replace the session_state.messages with the updated list of messages
    st.session_state.messages = updated_messages
    # display the LLMs latest response
    st.chat_message("assistant", avatar=bon_voyage_icon).write(response)