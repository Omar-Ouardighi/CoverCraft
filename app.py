import streamlit as st
from chatbot import Chatbot
import utils
import os


st.set_page_config(page_title="CoverCraft")
st.header("CoverCraft")

with st.sidebar:
        st.markdown(
            "## How to use\n"
            "1. Enter your [OpenAI API key](https://platform.openai.com/account/api-keys) below🔑\n" 
            "2. Upload your resume 📄\n" 
            "3. Ask to build your cover letter💬\n"
        )
        api_key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="Paste your OpenAI API key here (sk-...)",
            help="You can get your API key from https://platform.openai.com/account/api-keys.",
            value=os.environ.get("OPENAI_API_KEY", None)
            or st.session_state.get("OPENAI_API_KEY", ""),
        )

        st.session_state["OPENAI_API_KEY"] = api_key_input

openai_api_key = st.session_state.get("OPENAI_API_KEY")

if not openai_api_key:
    st.warning(
        "Enter your OpenAI API key in the sidebar. You can get a key at"
        " https://platform.openai.com/account/api-keys."
    )

if not utils.check_key(openai_api_key):
    st.stop()

file = st.file_uploader( "Upload your resume  ")
job_url = st.text_input("Enter the LinkedIn job post URL in the view mode")

    

if file:
    chatbot = Chatbot(openai_api_key)
    text = chatbot.load_document(file)
    vectorstore = chatbot.vectorize(text)
    chain = chatbot.build_chain(vectorstore,  4)
else:
    st.warning("Upload your file to get started.")

if not file or not job_url:
    st.stop()


if "conversation" not in st.session_state:
    st.session_state["conversation"] =  [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.conversation:
    if msg["role"] == "user":
        st.chat_message(msg["role"]).write(msg["content"])
    else:
        st.chat_message(msg["role"]).write(msg["content"])

if "chat_history" not in st.session_state: 
    st.session_state["chat_history"] = []



if prompt := st.chat_input():
    job_post = utils.scrape_job(job_url)
    st.session_state["conversation"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    with st.spinner("Processing"):
            combined_text = prompt + "\n" + job_post
            response = chain({"question": prompt,  "chat_history": st.session_state["chat_history"]})     
            st.session_state.conversation.append({"role": "assistant", "content": response["answer"]})
            st.session_state["chat_history"].append((prompt, response["answer"]))
            st.chat_message("assistant").write(response["answer"])