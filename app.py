import streamlit as st
from deepface import DeepFace
from PIL import Image
import numpy as np


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="EmotiCare AI",
    page_icon="💙",
    layout="centered"
)


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "stage": "welcome",
    "first_emotion": None,
    "first_confidence": None,
    "second_emotion": None,
    "second_confidence": None,
    "messages": [],
    "user_emotion": None,
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# EMOTION INFORMATION
# ============================================================

EMOTION_INFO = {

    "happy": {
        "emoji": "😊",
        "question": "You seem to be showing a happy expression. What's making you feel happy?"
    },

    "sad": {
        "emoji": "😔",
        "question": "You seem to be showing a sad expression. Why are you feeling sad?"
    },

    "angry": {
        "emoji": "😡",
        "question": "You seem to be showing an angry expression. What's making you feel angry?"
    },

    "fear": {
        "emoji": "😨",
        "question": "You seem to be showing a worried or fearful expression. What's bothering you?"
    },

    "surprise": {
        "emoji": "😮",
        "question": "You seem surprised. What happened?"
    },

    "disgust": {
        "emoji": "🤢",
        "question": "You seem uncomfortable. What's bothering you?"
    },

    "neutral": {
        "emoji": "😐",
        "question": "You seem fairly neutral right now. How are you feeling?"
    },
}


# ============================================================
# AI EMOTION ANALYSIS
# ============================================================

@st.cache_resource
def analyze_image(image_array):

    result = DeepFace.analyze(
        img_path=image_array,
        actions=["emotion"],
        enforce_detection=False,
        detector_backend="opencv"
    )

    if isinstance(result, list):
        result = result[0]

    emotion_scores = result["emotion"]

    emotion = result["dominant_emotion"]

    confidence = float(
        emotion_scores[emotion]
    )

    return emotion.lower(), confidence


# ============================================================
# WELCOME
# ============================================================

if st.session_state.stage == "welcome":

    st.title("💙 EmotiCare AI")

    st.subheader(
        "A small moment to check in with yourself."
    )

    st.write(
        """
        EmotiCare uses AI-based facial-expression analysis
        to estimate a possible expression and then gives
        you an opportunity to talk about how you're feeling.
        """
    )

    st.info(
        """
        📸 Camera permission

        The camera is only used when you choose to take
        an emotion-check photo.
        """
    )

    st.warning(
        """
        Important: facial-expression AI cannot know exactly
        how you feel. Your own answer is more important than
        the AI's prediction.
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
# FIRST CAMERA SCAN
# ============================================================

elif st.session_state.stage == "first_scan":

    st.title("📸 First Check")

    st.write(
        "Take a photo so the AI can estimate your facial expression."
    )

    photo = st.camera_input(
        "Take your first photo"
    )

    if photo:

        image = Image.open(photo).convert("RGB")

        image_array = np.array(image)

        with st.spinner(
            "AI is analyzing your expression..."
        ):

            try:

                emotion, confidence = analyze_image(
                    image_array
                )

                st.session_state.first_emotion = emotion

                st.session_state.first_confidence = confidence

                emoji = EMOTION_INFO.get(
                    emotion,
                    {"emoji": "🙂"}
                )["emoji"]

                st.success(
                    f"{emoji} Possible expression: "
                    f"**{emotion.capitalize()}**"
                )

                st.caption(
                    f"AI confidence: {confidence:.1f}%"
                )

                st.write(
                    "Does that match how you're feeling?"
                )

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        "Yes 👍",
                        use_container_width=True
                    ):

                        st.session_state.user_emotion = emotion

                        st.session_state.stage = "conversation"

                        st.rerun()

                with col2:

                    if st.button(
                        "No, that's not right",
                        use_container_width=True
                    ):

                        st.session_state.stage = "manual_emotion"

                        st.rerun()

            except Exception as error:

                st.error(
                    "The emotion model couldn't analyze "
                    "the image."
                )

                st.caption(
                    str(error)
                )


# ============================================================
# USER CORRECTS AI
# ============================================================

elif st.session_state.stage == "manual_emotion":

    st.title("💭 Your feelings matter more")

    st.write(
        "The AI can make mistakes. Tell us what you're actually feeling."
    )

    choices = [
        "Happy",
        "Sad",
        "Angry",
        "Worried",
        "Stressed",
        "Tired",
        "Excited",
        "Confused",
        "Neutral",
    ]

    selected = st.selectbox(
        "How are you feeling?",
        choices
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

    if not st.session_state.messages:

        info = EMOTION_INFO.get(
            emotion,
            EMOTION_INFO["neutral"]
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": info["question"]
            }
        )

    for message in st.session_state.messages:

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

        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_message
            }
        )

        text = user_message.lower()

        # ----------------------------------------------------
        # FREE LOCAL CONVERSATION LOGIC
        # ----------------------------------------------------

        if any(
            word in text
            for word in [
                "friend",
                "friendship"
            ]
        ):

            response = (
                "It sounds like something involving a "
                "friend is bothering you. Would you like "
                "to tell me what happened?"
            )

        elif any(
            word in text
            for word in [
                "school",
                "teacher",
                "exam",
                "test",
                "homework"
            ]
        ):

            response = (
                "School can definitely bring a lot of "
                "pressure. What part of it is bothering "
                "you the most?"
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
                "It sounds like something involving family "
                "is on your mind. Do you want to tell me "
                "more about it?"
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
                "You sound like you might need some rest. "
                "What's been making your day so tiring?"
            )

        else:

            response = (
                "Thank you for telling me. "
                "I'm listening. Can you tell me a little "
                "more about how that made you feel?"
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
        "When you're ready to check in again:"
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
        We've talked for a moment.
        Let's take another photo and see whether
        your estimated facial expression has changed.
        """
    )

    st.caption(
        "Remember: the AI can only estimate an expression."
    )

    photo = st.camera_input(
        "Take your final photo"
    )

    if photo:

        image = Image.open(photo).convert("RGB")

        image_array = np.array(image)

        with st.spinner(
            "Checking your expression again..."
        ):

            try:

                emotion, confidence = analyze_image(
                    image_array
                )

                st.session_state.second_emotion = emotion

                st.session_state.second_confidence = confidence

                st.session_state.stage = "result"

                st.rerun()

            except Exception as error:

                st.error(
                    "The second emotion check failed."
                )

                st.caption(
                    str(error)
                )


# ============================================================
# RESULT
# ============================================================

elif st.session_state.stage == "result":

    first = st.session_state.first_emotion

    second = st.session_state.second_emotion

    st.title("📊 Your Check-in")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Before")

        st.write(
            f"{EMOTION_INFO.get(first, {'emoji': '🙂'})['emoji']} "
            f"{first.capitalize()}"
        )

        st.write(
            f"{st.session_state.first_confidence:.1f}% confidence"
        )

    with col2:

        st.subheader("Now")

        st.write(
            f"{EMOTION_INFO.get(second, {'emoji': '🙂'})['emoji']} "
            f"{second.capitalize()}"
        )

        st.write(
            f"{st.session_state.second_confidence:.1f}% confidence"
        )

    st.divider()

    if first != second:

        st.success(
            f"""
            The AI's estimated expression changed from
            **{first}** to **{second}**.
            """
        )

    else:

        st.info(
            f"""
            The AI estimated a similar expression both times:
            **{second}**.
            """
        )

    st.subheader(
        "How do YOU feel now?"
    )

    final_feeling = st.radio(
        "Choose the answer closest to how you feel:",
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

            Sometimes talking about what's bothering you
            is already a useful first step. 💙
            """
        )

    else:

        st.info(
            """
            I'm sorry you're still having a difficult moment.

            Consider talking with someone you trust if
            you need some extra support. 💙
            """
        )

    st.write(
        "Thank you for spending a moment with EmotiCare."
    )

    if st.button(
        "🔄 Start Again",
        use_container_width=True
    ):

        for key in defaults:

            st.session_state[key] = defaults[key]

        st.rerun()
