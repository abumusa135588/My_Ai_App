import os
import google.generativeai as genai
import streamlit as st
from PIL import Image

# Streamlit পেইজ কনফিগারেশন
st.set_page_config(page_title="Universal Multilingual AI App", layout="wide")

st.title("🌐 Universal Multilingual & Visual AI Assistant")
st.caption(
    "বিশ্বের যেকোনো ভাষায় প্রশ্ন করুন, টেক্সট এবং ছবির মাধ্যমে উত্তর পান!"
)

# ১. API Key রিভ্রিভ করার লজিক (Secrets অথবা Sidebar)
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

# Secrets-এ Key না থাকলে সাইডবারে ইনপুট বক্স দেখাবে
if not api_key:
    api_key = st.sidebar.text_input("Enter your Gemini API Key:", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)

        # ২. মডেল নির্বাচন (gemini-2.5-flash ব্যবহার করা নিরাপদ ও দ্রুত)
       model = genai.GenerativeModel("gemini-1.5-flash")

        # চ্যাট হিস্ট্রি ইনিশিয়ালাইজেশন
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # পূর্বের মেসেজগুলো প্রদর্শন
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # ইমেজ আপলোড অপশন (উপরে রাখা যাতে ব্যবহারকারীর সুবিধা হয়)
        uploaded_file = st.file_uploader(
            "Upload an image (optional)", type=["jpg", "png", "jpeg"]
        )

        # ইউজার ইনপুট
        user_input = st.chat_input(
            "Ask anything in any language... (যেকোনো ভাষায় প্রশ্ন করুন)"
        )

        if user_input:
            # ইউজার মেসেজ দেখান
            st.session_state.messages.append(
                {"role": "user", "content": user_input}
            )
            with st.chat_message("user"):
                st.markdown(user_input)

            # সিস্টেম প্রম্পট
            system_instruction = (
                "You are a helpful universal AI assistant. Always respond in the exact same language "
                "the user used to ask the question. Provide clear and informative answers."
            )

            prompt = f"{system_instruction}\n\nUser Question: {user_input}"

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        if uploaded_file:
                            image = Image.open(uploaded_file)
                            response = model.generate_content([prompt, image])
                        else:
                            response = model.generate_content(prompt)

                        st.markdown(response.text)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": response.text}
                        )
                    except Exception as e:
                        st.error(f"Error generating response: {str(e)}")

    except Exception as e:
        st.error(f"API Key Error: {str(e)}")

else:
    st.warning(
        "Please add your GEMINI_API_KEY in Streamlit Secrets or enter it in the sidebar."
    )
