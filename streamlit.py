from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import streamlit as st
import time

load_dotenv()

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI ASSISTANT",
    page_icon="🤖",
    layout="centered"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

/* Background */
.stApp {
     background-color: white !important;
}

/* Main glass container */
.block-container {
    background: rgba(255, 255, 255, 0.05);
    padding: 2rem;
    border-radius: 25px;
    backdrop-filter: blur(25px);
}

/* USER bubble */
[data-testid="stChatMessage-user"] {
    background-color: #ffffff;
    color: white !important;
    padding: 12px;
    border-radius: 15px;
}

/* ASSISTANT bubble (WHITE FOR CLEAR VISIBILITY) */
[data-testid="stChatMessage-assistant"] {
    background-color: #ffffff;
    color: #000000 !important;
    padding: 12px;
    border-radius: 15px;
}

/* Chat input container */
[data-testid="stChatInput"] {
    background-color: white !important;
    border-radius: 12px;
    padding: 5px;
}

/* Input text */
[data-testid="stChatInput"] textarea {
    color: black !important;
}

/* Placeholder */
[data-testid="stChatInput"] textarea::placeholder {
    color: gray !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(0,0,0,0.4);
}

</style>
""", unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ AI Controls")

model_name = st.sidebar.selectbox(
    "Model",
    ["llama-3.1-8b-instant", "qwen/qwen3-32b"]
)

temperature = st.sidebar.slider("Creativity", 0.0, 1.0, 0.7)

if st.sidebar.button("🗑 Clear Chat"):
    st.session_state.messages = [
        {"role": "system", "content": "You are an advanced AI assistant. Be intelligent, structured and helpful."}
    ]
    st.rerun()

if st.sidebar.button("💾 Download Chat"):
    chat_text = ""
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            chat_text += f"{msg['role'].upper()}: {msg['content']}\n\n"
    st.sidebar.download_button("Download", chat_text, file_name="chat.txt")


# ---------------- MODEL ----------------
client = ChatGroq(
    model=model_name,
    temperature=temperature
)

# ---------------- TITLE ----------------
st.title("🚀 AI Assistant")

# ---------------- MEMORY ----------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are an advanced AI assistant. Be intelligent, structured and helpful."}
    ]

# ---------------- DISPLAY CHAT ----------------
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ---------------- USER INPUT ----------------
if prompt := st.chat_input("Ask anything..."):

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    # Convert to LangChain messages
    lc_messages = []
    for msg in st.session_state.messages:
        if msg["role"] == "system":
            lc_messages.append(SystemMessage(content=msg["content"]))
        elif msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            lc_messages.append(AIMessage(content=msg["content"]))

    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        response = client.invoke(lc_messages)
        reply = response.content

        # Smooth fake streaming effect
        for word in reply.split():
            full_response += word + " "
            message_placeholder.markdown(full_response + "▌")
            time.sleep(0.02)

        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": reply})