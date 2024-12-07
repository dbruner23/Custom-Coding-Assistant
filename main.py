import os
import streamlit as st
import anthropic
from anthropic.types import TextBlock
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if prompt := st.chat_input():
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    model_id="claude-3-5-sonnet-20241022"

    try:
        response = client.messages.create(
            model=model_id,
            max_tokens=3000,
            messages=st.session_state.messages,
        )

        content = response.content

        for block in content:
            if isinstance(block, TextBlock):
                assistant_message = block.text

                st.session_state.messages.append({"role": "assistant", "content": assistant_message})

                with st.chat_message("assistant"):
                    # Parse the message to handle transitions between text and code
                    lines = assistant_message.splitlines()
                    is_code_block = False
                    code_language = None
                    code_content = []

                    for line in lines:
                        if line.startswith("```") and not is_code_block:
                            # Start of a code block
                            is_code_block = True
                            code_language = line[3:].strip()  # Extract language (if specified)
                            code_content = []
                        elif line.startswith("```") and is_code_block:
                            # End of a code block
                            is_code_block = False
                            st.code("\n".join(code_content), language=code_language or "plaintext")
                        elif is_code_block:
                            # Inside a code block
                            code_content.append(line)
                        else:
                            # Normal text
                            st.write(line)


    except Exception as e:
        error_msg = f"Error: {e}"
        print(error_msg)
        st.error(f"Error: {e}")


if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()