import streamlit as st
from fer import FER
from PIL import Image
import numpy as np

# ---------------------------------------------------
# PAGE SETTINGS
# ---------------------------------------------------

st.set_page_config(
    page_title="EmotiCare AI",
    page_icon="💙"
)

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------

if "stage" not in st.session_state:
    st.session_state.stage = "first_scan"

if "first_emotion" not in st.session_state:
    st.session_state.first_emotion = None

if "second_emotion" not in st.session_state:
    st.session_state.second_emotion = None

if "chat" not in st.session_state:
    st.session_state.chat = []

# ---------------------------------------------------
# FER DETECTOR
# ---------------------------------------------------

detector = FER(mtcnn=True)

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------

st.title("💙 EmotiCare AI")

st.write(
    "This app estimates facial expressions and starts a supportive conversation."
)

# ---------------------------------------------------
# FUNCTION
# ---------------------------------------------------

def detect_emotion(image):

    image = Image.open(image)

    img_array = np.array(image)

    result = detector.detect_emotions(img_array)

    if result:

        emotions = result[0]["emotions"]

        emotion = max(emotions, key=emotions.get)

        return emotion.capitalize()

    return "Neutral"

# ---------------------------------------------------
# FIRST SCAN
# ---------------------------------------------------

if st.session_state.stage == "first_scan":

    st.header("📸 First Emotion Check")

    photo = st.camera_input("Take a photo")

    if photo:

        emotion = detect_emotion(photo)

        st.session_state.first_emotion = emotion

        st.success(
            f"Possible expression: {emotion}"
        )

        st.write(
            f"Why are you feeling {emotion.lower()}?"
        )

        st.session_state.stage = "chat"
        st.rerun()

# ---------------------------------------------------
# CHAT
# ---------------------------------------------------

elif st.session_state.stage == "chat":

    emotion = st.session_state.first_emotion

    st.header("💬 Conversation")

    if len(st.session_state.chat) == 0:

        st.session_state.chat.append(
            {
                "role": "assistant",
                "text": f"Why are you feeling {emotion.lower()}?"
            }
        )

    for msg in st.session_state.chat:

        with st.chat_message(msg["role"]):
            st.write(msg["text"])

    user_text = st.chat_input(
        "Tell me..."
    )

    if user_text:

        st.session_state.chat.append(
            {
                "role": "user",
                "text": user_text
            }
        )

        # FREE SIMPLE AI

        if "friend" in user_text.lower():

            reply = (
                "It sounds like something happened with your friend. "
                "Would you like to tell me more?"
            )

        elif "school" in user_text.lower():

            reply = (
                "School can sometimes be stressful. "
                "What happened?"
            )

        else:

            reply = (
                "Thank you for sharing that with me. "
                "Can you tell me a little more?"
            )

        st.session_state.chat.append(
            {
                "role": "assistant",
                "text": reply
            }
        )

        st.rerun()

    st.divider()

    if st.button("How I Feel Now 💙"):

        st.session_state.stage = "second_scan"

        st.rerun()

# ---------------------------------------------------
# SECOND SCAN
# ---------------------------------------------------

elif st.session_state.stage == "second_scan":

    st.header("📸 Final Check")

    st.write(
        "How do you feel now?"
    )

    photo = st.camera_input(
        "Take another photo"
    )

    if photo:

        emotion = detect_emotion(photo)

        st.session_state.second_emotion = emotion

        st.session_state.stage = "result"

        st.rerun()

# ---------------------------------------------------
# RESULT
# ---------------------------------------------------

elif st.session_state.stage == "result":

    first = st.session_state.first_emotion
    second = st.session_state.second_emotion

    st.header("💙 Result")

    st.write(f"Before: {first}")

    st.write(f"After: {second}")

    if first != second:

        st.success(
            "Your expression appears different now."
        )

    else:

        st.info(
            "Your expression appears similar."
        )

    feeling = st.radio(
        "How do YOU feel now?",
        [
            "Better",
            "A little better",
            "About the same",
            "Still sad"
        ]
    )

    if st.button("Finish"):

        st.balloons()

        st.success(
            "Thank you for checking in. "
            "Take care of yourself 💙"
        )
