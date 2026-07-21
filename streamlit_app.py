"""Streamlit test UI for the affiliate support bot.

Run with:
    streamlit run streamlit_app.py
"""

import streamlit as st

from assistant_manager import SupportAssistant

st.set_page_config(page_title="Affiliate support bot", page_icon="🤖")
st.title("🤖 Affiliate support bot")
st.caption("Answers strictly from the uploaded knowledge base PDF.")

with st.sidebar:
    st.header("Session")
    if st.button("New chat", icon=":material/refresh:"):
        st.session_state.messages = []
        st.session_state.previous_response_id = None
        st.rerun()

if "assistant" not in st.session_state:
    try:
        with st.spinner("Preparing the knowledge base (first run may take a moment)..."):
            assistant = SupportAssistant()
            assistant.ensure_vector_store()
            st.session_state.assistant = assistant
    except Exception as exc:
        st.error(f"Failed to prepare the knowledge base: {exc}")
        st.stop()

st.session_state.setdefault("messages", [])
st.session_state.setdefault("previous_response_id", None)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask a question about the affiliate program..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.assistant.ask(
                    prompt,
                    previous_response_id=st.session_state.previous_response_id,
                )
                answer = response.output_text
            except Exception as exc:
                answer = f"An error occurred while contacting OpenAI: {exc}"
                response = None
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    if response is not None:
        st.session_state.previous_response_id = response.id
