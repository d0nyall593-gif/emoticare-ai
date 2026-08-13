import streamlit as st
from PIL import Image
import numpy as np
import torch
from transformers import pipeline


# ============================================================
# PAGE SETTINGS
# ============================================================

st.set_page_config(
    page_title="EmotiCare AI",
    page_icon="💙",
    layout="centered"
)


# ============================================================
# SESSION STATE
# ============================================================

if "stage" not in st.session_state:
    st.session_state.stage = "welcome"

if "first_emotion" not in st.session_state:
    st.session_state.first_emotion = None

if "first_confidence" not in st.session_state:
    st.session_state.first_confidence = 0.0

if "second_emotion" not in st.session_state:
    st.session_state.second_emotion = None

if "second_confidence" not in st.session_state:
    st.session_state.second_confidence = 0.0

if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_emotion" not in st.session_state:
    st.session_state.user_emotion = None

if "final_feeling" not in st.session_state:
    st.session_state.final_feeling = None


# ============================================================
# EMOTION MODEL
# ============================================================

@st.cache_resource
def load_emotion_model():

    return pipeline(
        "image-classification",
        model="trpakov/vit-face-expression"
    )


emotion_model = load_emotion_model()


# ============================================================
# EMOTION DISPLAY
# ============================================================

EMOTION_EMOJIS = {
    "happy": "😊",
    "sad": "😔",
    "angry": "😡",
    "fear": "😨",
    "surprise": "😮",
    "disgust": "🤢",
    "neutral": "😐"
}


# ============================================================
# ANALYZE PHOTO
# ============================================================

def analyze_emotion(photo):

    image = Image.open(photo).convert("RGB")

    results = emotion_model(image)

    if not results:
        return None, 0.0

    best = results[0]

    emotion = best["label"].lower()

    confidence = float(best["score"]) * 100

    return emotion, confidence


# ============================================================
# WELCOME
# ============================================================

if st.session_state.stage == "welcome":

    st.title("💙 EmotiCare AI")

    st.subheader(
        "A little space to check in with yourself."
    )

    st.write(
        """
        EmotiCare uses AI to estimate a possible
        facial expression and then gives you a chance
        to talk about how you're feeling.
        """
    )

    st.info(
        """
        📸 Camera permission

        Your camera is only used when you choose to
        take a photo for the emotion check.
        """
    )

    st.warning(
        """
        ⚠️ Important

        Facial-expression AI cannot actually know exactly
        how someone feels. The AI's result is only an
        estimate, and your own answer is more important.
        """
    )

    if st.button(
        "💙 Start Check-in",
        use_container_width=True,
        type="primary"
    ):

        st.session_state.stage = "first_scan"

        st.rerun()


# ============================================================
# FIRST SCAN
# ============================================================

elif st.session_state.stage == "first_scan":

    st.title("📸 First Emotion Check")

    st.write(
        "Take a photo so the AI can estimate your expression."
    )

    photo = st.camera_input(
        "Take your first photo"
    )

    if photo:

        with st.spinner(
            "AI is analyzing your expression..."
        ):

            try:

                emotion, confidence = analyze_emotion(photo)

                if emotion is None:
                    st.error(
                        "I couldn't analyze the photo."
                    )

                else:

                    st.session_state.first_emotion = emotion

                    st.session_state.first_confidence = confidence

                    emoji = EMOTION_EMOJIS.get(
                        emotion,
                        "🙂"
                    )

                    st.success(
                        f"{emoji} Possible expression: "
                        f"**{emotion.capitalize()}**"
                    )

                    st.caption(
                        f"AI confidence: {confidence:.1f}%"
                    )

                    st.write(
                        f"Do you actually feel **{emotion}**?"
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        if st.button(
                            "✅ Yes",
                            use_container_width=True
                        ):

                            st.session_state.user_emotion = emotion

                            st.session_state.stage = "conversation"

                            st.rerun()

                    with col2:

                        if st.button(
                            "❌ No",
                            use_container_width=True
                        ):

                            st.session_state.stage = "manual_emotion"

                            st.rerun()

            except Exception as error:

                st.error(
                    "The AI could not analyze this photo."
                )

                st.exception(error)


# ============================================================
# MANUAL EMOTION
# ============================================================

elif st.session_state.stage == "manual_emotion":

    st.title("💭 You know yourself best")

    st.write(
        "The AI can be wrong. Tell me how you're actually feeling."
    )

    emotion_choices = [
        "Happy",
        "Sad",
        "Angry",
        "Worried",
        "Stressed",
        "Tired",
        "Excited",
        "Confused",
        "Neutral"
    ]

    selected = st.selectbox(
        "How are you feeling?",
        emotion_choices
    )

    if st.button(
        "Continue 💙",
        use_container_width=True,
        type="primary"
    ):

        st.session_state.user_emotion = selected.lower()

        st.session_state.stage = "conversation"

        st.rerun()


# ============================================================
# CONVERSATION
# ============================================================

elif st.session_state.stage == "conversation":

    emotion = st.session_state.user_emotion

    st.title("💬 Let's talk")

    if len(st.session_state.messages) == 0:

        if emotion == "sad":

            question = (
                "You seem to be feeling sad. "
                "Why are you feeling sad?"
            )

        elif emotion == "angry":

            question = (
                "You seem to be feeling angry. "
                "Why are you feeling angry?"
            )

        elif emotion == "happy":

            question = (
                "You seem to be feeling happy. "
                "What's making you feel happy?"
            )

        elif emotion == "worried":

            question = (
                "You seem worried. "
                "What's making you feel worried?"
            )

        elif emotion == "stressed":

            question = (
                "You seem stressed. "
                "What's been stressing you out?"
            )

        elif emotion == "tired":

            question = (
                "You seem tired. "
                "What's been making you feel tired?"
            )

        elif emotion == "excited":

            question = (
                "You seem excited. "
                "What's making you feel excited?"
            )

        elif emotion == "confused":

            question = (
                "You seem confused. "
                "What's confusing you?"
            )

        else:

            question = (
                "How are you feeling right now? "
                "What's on your mind?"
            )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": question
            }
        )

    # Display conversation

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.write(
                message["content"]
            )

    # User response

    user_message = st.chat_input(
        "Tell me what's going on..."
    )

    if user_message:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_message
            }
        )

        text = user_message.lower()

        # Simple free local conversation

        if any(
            word in text
            for word in [
                "school",
                "exam",
                "test",
                "homework",
                "teacher"
            ]
        ):

            response = (
                "It sounds like school might be part "
                "of what's bothering you. "
                "What happened?"
            )

        elif any(
            word in text
            for word in [
                "friend",
                "friends"
            ]
        ):

            response = (
                "It sounds like something involving "
                "your friend is on your mind. "
                "Would you like to tell me more?"
            )

        elif any(
            word in text
            for word in [
                "family",
                "mom",
                "dad",
                "brother",
                "sister"
            ]
        ):

            response = (
                "Things involving family can sometimes "
                "be difficult. What happened?"
            )

        elif any(
            word in text
            for word in [
                "tired",
                "sleep",
                "sleepy"
            ]
        ):

            response = (
                "It sounds like you've had a tiring time. "
                "What's been making you feel this way?"
            )

        else:

            response = (
                "Thank you for sharing that with me. "
                "I'm listening. Can you tell me a little "
                "more about what happened?"
            )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )

        st.rerun()

    st.divider()

    st.write(
        "When you're ready to finish:"
    )

    if st.button(
        "💙 How do I feel now?",
        use_container_width=True,
        type="primary"
    ):

        st.session_state.stage = "second_scan"

        st.rerun()


# ============================================================
# SECOND SCAN
# ============================================================

elif st.session_state.stage == "second_scan":

    st.title("💙 How do you feel now?")

    st.write(
        """
        Before we finish, take one more photo.
        We'll compare the AI's estimate with the first check.
        """
    )

    st.caption(
        "Remember: the AI can only estimate facial expression."
    )

    photo = st.camera_input(
        "Take your final photo"
    )

    if photo:

        with st.spinner(
            "Checking your expression again..."
        ):

            try:

                emotion, confidence = analyze_emotion(photo)

                st.session_state.second_emotion = emotion

                st.session_state.second_confidence = confidence

                st.session_state.stage = "result"

                st.rerun()

            except Exception as error:

                st.error(
                    "The final emotion check failed."
                )

                st.exception(error)


# ============================================================
# RESULT
# ============================================================

elif st.session_state.stage == "result":

    first = st.session_state.first_emotion

    second = st.session_state.second_emotion

    st.title("📊 Your Emotion Check")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Before")

        st.write(
            f"{EMOTION_EMOJIS.get(first, '🙂')} "
            f"**{first.capitalize()}**"
        )

        st.caption(
            f"{st.session_state.first_confidence:.1f}% confidence"
        )

    with col2:

        st.subheader("Now")

        st.write(
            f"{EMOTION_EMOJIS.get(second, '🙂')} "
            f"**{second.capitalize()}**"
        )

        st.caption(
            f"{st.session_state.second_confidence:.1f}% confidence"
        )

    st.divider()

    if first != second:

        st.success(
            f"""
            The AI's estimated facial expression changed
            from **{first}** to **{second}**.
            """
        )

    else:

        st.info(
            f"""
            The AI estimated a similar facial expression
            both times: **{second}**.
            """
        )

    st.subheader(
        "But how do YOU feel now?"
    )

    final_feeling = st.radio(
        "Choose the answer that feels closest:",
        [
            "😊 I feel better",
            "🙂 I feel a little better",
            "😐 I feel about the same",
            "😔 I still don't feel good"
        ]
    )

    if st.button(
        "Finish 💙",
        use_container_width=True,
        type="primary"
    ):

        st.session_state.final_feeling = final_feeling

        st.session_state.stage = "goodbye"

        st.rerun()


# ============================================================
# GOODBYE
# ============================================================

elif st.session_state.stage == "goodbye":

    st.title("💙 Thank you for checking in")

    feeling = st.session_state.final_feeling

    if "better" in feeling.lower():

        st.success(
            """
            I'm glad you're feeling better.

            Remember to be kind to yourself. 💙
            """
        )

    elif "same" in feeling.lower():

        st.info(
            """
            That's okay. You don't have to feel better
            immediately.

            Talking about what's bothering you can be
            a good first step. 💙
            """
        )

    else:

        st.info(
            """
            I'm sorry you're still having a difficult moment.

            Consider talking to someone you trust if you
            need some extra support. 💙
            """
        )

    st.write(
        "Thank you for spending a moment with EmotiCare."
    )

    if st.button(
        "🔄 Start Again",
        use_container_width=True
    ):

        st.session_state.clear()

        st.rerun()
