import os
import google.generativeai as genai
import streamlit as st

# Streamlit পেইজ কনফিগারেশন
st.set_page_config(page_title="Universal Multilingual AI App", layout="wide")

st.title("🌐 Universal Multilingual & Visual AI Assistant")
st.caption(
    "বিশ্বের যেকোনো ভাষায় প্রশ্ন করুন, টেক্সট এবং ছবির মাধ্যমে উত্তর পান!"
)

# API Key সেটআপ
api_key = st.sidebar.text_input("Enter your Gemini API Key:", type="password")

if api_key:
    genai.configure(api_key=api_key)

    # মডেল নির্বাচন (Multilingual Text & Vision Support)
    model = genai.GenerativeModel("gemini-1.5-flash")

    # চ্যাট হিস্ট্রি ইনিশিয়ালাইজেশন
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # পূর্বের মেসেজগুলো প্রদর্শন
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ইউজার ইনপুট
    user_input = st.chat_input(
        "Ask anything in any language... (যেকোনো ভাষায় প্রশ্ন করুন)"
    )

    # ইমেজ আপলোড অপশন
    uploaded_file = st.file_uploader(
        "Upload an image (optional)", type=["jpg", "png", "jpeg"]
    )

    if user_input:
        # ইউজার মেসেজ দেখান
        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )
        with st.chat_message("user"):
            st.markdown(user_input)

        # সিস্টেম প্রম্পট (সব ভাষা এবং ছবি সম্পর্কিত নির্দেশনা)
        system_instruction = (
            "You are a helpful universal AI assistant. Always respond in the exact same language "
            "the user used to ask the question. Provide clear, informative, and visual/descriptive answers."
        )

        prompt = f"{system_instruction}\n\nUser Question: {user_input}"

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    if uploaded_file:
                        from PIL import Image

                        image = Image.open(uploaded_file)
                        response = model.generate_content([prompt, image])
                    else:
                        response = model.generate_content(prompt)

                    st.markdown(response.text)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response.text}
                    )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
else:
    st.warning(
        "Please enter your Gemini API Key in the sidebar to start using the app."
    )
