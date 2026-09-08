import os
import io
import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import PyPDF2

# ১. পেজ কনফিগারেশন
st.set_page_config(
    page_title="Universal AI Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Universal AI Assistant")
st.caption("কথা বলুন, ফাইল ও ছবি আপলোড করুন এবং যেকোনো ভাষায় দ্রুত উত্তর পান!")

# ২. API Key লোড করা (Secrets অথবা Sidebar)
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    api_key = st.sidebar.text_input("🔑 Enter your Gemini API Key:", type="password")

if not api_key:
    st.warning("অনুগ্রহ করে আপনার Gemini API Key-টি সাইডবারে দিন বা Streamlit Secrets-এ সেভ করুন।")
    st.stop()

# API কনফিগারেশন
genai.configure(api_key=api_key)

# ৩. সাইডবার সেটিংস ও শেয়ার অপশন (Share Application)
st.sidebar.header("⚙️ Settings & Share")
enable_voice = st.sidebar.checkbox("🔊 Enable Voice Output (TTS)", value=True)
clear_chat = st.sidebar.button("🗑️ Clear Chat History")

st.sidebar.markdown("---")
st.sidebar.subheader("🔗 Share App")
# অ্যাপ শেয়ারের জন্য ডাইরেক্ট লিংক বা বাটন
st.sidebar.info("আপনার বন্ধুদের সাথে অ্যাপটি শেয়ার করতে নিচের লিংকটি কপি করুন:")
st.sidebar.code(st.sidebar.text_input("App URL", "https://share.streamlit.io", disabled=True), language="text")

# ৪. চ্যাট হিস্ট্রি ব্যবস্থাপনা
if "messages" not in st.session_state or clear_chat:
    st.session_state.messages = []

# পূর্বের চ্যাট দেখানো (ChatGPT / Gemini Style UI)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "audio" in message and enable_voice:
            st.audio(message["audio"], format="audio/mp3")

# ৫. মাল্টিমিডিয়া ও ফাইল ইনপুট
with st.expander("📎 Attach Image or PDF Document (Optional)"):
    uploaded_image = st.file_uploader("Upload Image (JPG, PNG)", type=["jpg", "png", "jpeg"], key="img")
    uploaded_pdf = st.file_uploader("Upload PDF Document", type=["pdf"], key="pdf")

# ৬. ইউজার ইনপুট গ্রহণ
user_input = st.chat_input("Ask anything... (যেকোনো কিছু জিজ্ঞাসা করুন)")

if user_input:
    # পিডিএফ ফাইল থেকে টেক্সট পড়া
    pdf_text = ""
    if uploaded_pdf:
        try:
            reader = PyPDF2.PdfReader(uploaded_pdf)
            for page in reader.pages:
                pdf_text += page.extract_text() or ""
            pdf_text = f"\n\n[Attached PDF Content]:\n{pdf_text[:3000]}"
        except Exception as e:
            st.error(f"PDF পড়তে সমস্যা হয়েছে: {str(e)}")

    full_prompt = user_input + pdf_text

    # ইউজার মেসেজ চ্যাটে দেখানো
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        if uploaded_image:
            st.image(uploaded_image, caption="Uploaded Image", width=250)

    # ৭. AI মডেল কল ও উত্তর জেনারেট
    with st.chat_message("assistant"):
        with st.spinner("AI চিন্তা করছে..."):
            try:
                # অফিশিয়াল স্ট্যাবল মডেল
                model = genai.GenerativeModel("gemini-1.5-flash")

                if uploaded_image:
                    img = Image.open(uploaded_image)
                    response = model.generate_content([full_prompt, img])
                else:
                    response = model.generate_content(full_prompt)

                bot_reply = response.text
                st.markdown(bot_reply)

                # ৮. ভয়েস রেসপন্স (Text-to-Speech)
                audio_bytes = None
                if enable_voice:
                    try:
                        tts = gTTS(text=bot_reply[:500], lang='bn' if any(ch in bot_reply for ch in 'অআইঈউঊএঐওঔকখগঘ') else 'en')
                        audio_fp = io.BytesIO()
                        tts.write_to_fp(audio_fp)
                        audio_fp.seek(0)
                        audio_bytes = audio_fp.read()
                        st.audio(audio_bytes, format="audio/mp3")
                    except Exception:
                        pass

                # হিস্ট্রিতে সেভ
                msg_data = {"role": "assistant", "content": bot_reply}
                if audio_bytes:
                    msg_data["audio"] = audio_bytes
                st.session_state.messages.append(msg_data)

            except Exception as e:
                st.error(f"ত্রুটি ঘটেছে: {str(e)}")
