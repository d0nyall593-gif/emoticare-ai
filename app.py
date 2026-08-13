import streamlit as st
from fer import FER
from PIL import Image
import numpy as np


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="EmotiCare AI",
    page_icon="💙",
    layout="centered"
)


# =========================================================
# SESSION STATE
# =========================================================

if "stage" not in st.session_state:
    st.session_state.stage = "welcome"

if "first_emotion" not in st.session_state:
    st.session_state.first_emotion = None

if "first_confidence" not in st.session_state:
    st.session_state.first_confidence = 0

if "second_emotion" not in st.session_state:
    st.session_state.second_emotion = None

if "second_confidence" not in st.session_state:
    st.session_state.second_confidence = 0

if "conversation" not in st.session_state:
    st.session_state.conversation = []

if "final_feeling" not in st.session_state:
    st.session_state.final_feeling = None


# =========================================================
# EMOTION DETECTOR
# =========================================================

@st.cache_resource
def load_detector():
    return FER()


detector = load_detector()


# =========================================================
# EMOTION EMOJIS
# =========================================================

EMOTION_EMOJIS = {
    "happy": "😊",
    "sad": "😔",
    "angry": "😡",
    "fear": "😨",
    "surprise": "😮",
    "disgust": "🤢",
    "neutral": "😐",
}


# =========================================================
# DETECT EMOTION
# =========================================================

def analyze_face(photo):

    image = Image.open(photo).convert("RGB")

    image_array = np.array(image)

    result = detector.detect_emotions(image_array)

    if not result:
        return None, 0

    emotions = result[0]["emotions"]

    emotion = max(
        emotions,
        key=emotions.get
    )

    confidence = emotions[emotion]

    return emotion, confidence


# =========================================================
# RESET
# =========================================================

def reset_app():

    st.session_state.stage = "welcome"

    st.session_state.first_emotion = None
    st.session_state.first_confidence = 0

    st.session_state.second_emotion = None
    st.session_state.second_confidence = 0

    st.session_state.conversation = []

    st.session_state.final_feeling = None


# =========================================================
# WELCOME
# =========================================================

if st.session_state.stage == "welcome":

    st.title("💙 EmotiCare AI")

    st.subheader(
        "Take a moment to check in with yourself."
    )

    st.write(
        """
        EmotiCare uses facial-expression analysis to
        estimate a possible expression and then gives
        you a chance to talk about how you're feeling.
        """
    )

    st.info(
        """
        🔒 Privacy notice

        Your camera is used only for the emotion check.
        This school-project prototype does not intentionally
        save your photos.
        """
    )

    st.warning(
        """
        Facial expressions cannot tell us exactly how
        someone feels. Your own answer is always more
        important than the camera's estimate.
        """
    )

    if st.button(
        "📸 Start Emotion Check",
        use_container_width=True,
        type="primary"
    ):

        st.session_state.stage = "first_scan"

        st.rerun()


# =========================================================
# FIRST SCAN
# =========================================================

elif st.session_state.stage == "first_scan":

    st.title("📸 Let's check in")

    st.write(
        "Give me a moment to analyze your facial expression."
    )

    photo = st.camera_input(
        "Take a photo"
    )

    if photo:

        with st.spinner(
            "Analyzing your expression..."
        ):

            emotion, confidence = analyze_face(photo)

        if emotion is None:

            st.error(
                "I couldn't detect a face clearly. "
                "Please try again with your face clearly visible."
            )

        else:

            st.session_state.first_emotion = emotion

            st.session_state.first_confidence = confidence

            emoji = EMOTION_EMOJIS.get(
                emotion,
                "🙂"
            )

            percentage = round(
                confidence * 100
            )

            st.success(
                f"{emoji} Possible facial expression: "
                f"**{emotion.capitalize()}**"
            )

            st.write(
                f"Model confidence: **{percentage}%**"
            )

            st.subheader(
                f"Do you feel {emotion}?"
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "✅ Yes",
                    use_container_width=True
                ):

                    st.session_state.stage = "conversation"

                    st.rerun()

            with col2:

                if st.button(
                    "❌ No",
                    use_container_width=True
                ):

                    st.session_state.stage = "choose_emotion"

                    st.rerun()


# =========================================================
# MANUAL CORRECTION
# =========================================================

elif st.session_state.stage == "choose_emotion":

    st.title("💭 Tell me how you really feel")

    st.write(
        "That's completely okay. The camera can be wrong."
    )

    emotions = [
        "Happy",
        "Sad",
        "Angry",
        "Anxious",
        "Stressed",
        "Tired",
        "Excited",
        "Confused",
        "Neutral",
    ]

    selected = st.selectbox(
        "Choose your emotion",
        emotions
    )

    if st.button(
        "Continue",
        use_container_width=True,
        type="primary"
    ):

        st.session_state.first_emotion = selected.lower()

        st.session_state.stage = "conversation"

        st.rerun()


# =========================================================
# CONVERSATION
# =========================================================

elif st.session_state.stage == "conversation":

    emotion = st.session_state.first_emotion

    st.title("💬 Let's talk")

    if len(st.session_state.conversation) == 0:

        first_message = (
            f"You seem to be feeling {emotion}. "
            f"Why are you feeling {emotion}?"
        )

        st.session_state.conversation.append(
            {
                "role": "assistant",
                "content": first_message
            }
        )

    for message in st.session_state.conversation:

        with st.chat_message(
            message["role"]
        ):

            st.write(
                message["content"]
            )

    user_message = st.chat_input(
        "Tell me what's going on..."
    )

    if user_message:

        st.session_state.conversation.append(
            {
                "role": "user",
                "content": user_message
            }
        )

        # -------------------------------------------------
        # TEMPORARY FREE CONVERSATION LOGIC
        # -------------------------------------------------

        text = user_message.lower()

        if "friend" in text:

            response = (
                "It sounds like something happened "
                "with your friend. Would you like "
                "to tell me a little more about it?"
            )

        elif "school" in text:

            response = (
                "It sounds like school may have "
                "played a part in how you're feeling. "
                "What happened?"
            )

        elif "family" in text:

            response = (
                "Things involving family can sometimes "
                "be difficult. What happened?"
            )

        elif "tired" in text:

            response = (
                "It sounds like you've had a tiring "
                "time. What's been making you feel "
                "so tired?"
            )

        else:

            response = (
                "Thank you for sharing that with me. "
                "Can you tell me a little more about "
                "what happened?"
            )

        st.session_state.conversation.append(
            {
                "role": "assistant",
                "content": response
            }
        )

        st.rerun()

    st.divider()

    st.write(
        "When you're ready to finish the conversation:"
    )

    if st.button(
        "💙 Check how I feel now",
        use_container_width=True,
        type="primary"
    ):

        st.session_state.stage = "second_scan"

        st.rerun()


# =========================================================
# SECOND SCAN
# =========================================================

elif st.session_state.stage == "second_scan":

    st.title("💙 How do you feel now?")

    st.write(
        """
        Before we finish, let's take one more look
        at your facial expression.
        """
    )

    st.caption(
        "Remember: your own feelings are more important "
        "than what the camera detects."
    )

    photo = st.camera_input(
        "Take your second photo"
    )

    if photo:

        with st.spinner(
            "Checking your expression again..."
        ):

            emotion, confidence = analyze_face(photo)

        if emotion is None:

            st.error(
                "I couldn't detect a face clearly. "
                "Please try again."
            )

        else:

            st.session_state.second_emotion = emotion

            st.session_state.second_confidence = confidence

            st.session_state.stage = "comparison"

            st.rerun()


# =========================================================
# COMPARISON
# =========================================================

elif st.session_state.stage == "comparison":

    first = st.session_state.first_emotion

    second = st.session_state.second_emotion

    st.title("📊 Your check-in")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Before")

        st.write(
            f"{EMOTION_EMOJIS.get(first, '🙂')} "
            f"**{first.capitalize()}**"
        )

        st.write(
            f"{round(st.session_state.first_confidence * 100)}%"
        )

    with col2:

        st.subheader("Now")

        st.write(
            f"{EMOTION_EMOJIS.get(second, '🙂')} "
            f"**{second.capitalize()}**"
        )

        st.write(
            f"{round(st.session_state.second_confidence * 100)}%"
        )

    st.divider()

    if first != second:

        st.success(
            f"""
            Your estimated facial expression changed
            from **{first}** to **{second}**.
            """
        )

    else:

        st.info(
            """
            Your estimated facial expression appears
            similar to your first check.
            """
        )

    st.subheader(
        "But how do YOU actually feel now?"
    )

    feeling = st.radio(
        "Choose the answer that feels closest:",
        [
            "😊 I feel better",
            "🙂 I feel a little better",
            "😐 I feel about the same",
            "😔 I still don't feel good",
        ]
    )

    if st.button(
        "Finish 💙",
        use_container_width=True,
        type="primary"
    ):

        st.session_state.final_feeling = feeling

        st.session_state.stage = "goodbye"

        st.rerun()


# =========================================================
# GOODBYE
# =========================================================

elif st.session_state.stage == "goodbye":

    st.title("💙 Thank you for checking in")

    feeling = st.session_state.final_feeling

    if "better" in feeling.lower():

        st.success(
            """
            I'm glad you're feeling a little better.

            Take care of yourself and remember that
            it's okay to talk when something is bothering you. 💙
            """
        )

    elif "same" in feeling.lower():

        st.info(
            """
            That's okay. You don't have to feel better
            immediately.

            Sometimes talking about what's bothering you
            is already a good first step. 💙
            """
        )

    else:

        st.info(
            """
            I'm sorry you're still having a difficult moment.

            Be gentle with yourself, and consider talking
            with someone you trust if you need support. 💙
            """
        )

    st.write(
        "Thank you for spending a moment with EmotiCare."
    )

    if st.button(
        "Start another check-in",
        use_container_width=True
    ):

        reset_app()

        st.rerun()
