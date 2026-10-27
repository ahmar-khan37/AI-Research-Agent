import random
import requests
import streamlit as st

st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔎",
    layout="wide"
)

START_URL = "https://ahmarnexora.app.n8n.cloud/webhook/ai-research"
STATUS_URL = "https://ahmarnexora.app.n8n.cloud/webhook/research-status"

API_KEY = st.secrets["RESEARCH_API_KEY"]
HEADERS = {"X-Research-API-Key": API_KEY}

PAIRS = ["🤖", "🚀", "🧠", "🌎", "💡", "🔬"]


def reset_game():
    cards = PAIRS * 2
    random.shuffle(cards)
    st.session_state.cards = cards
    st.session_state.matched = set()
    st.session_state.selected = []
    st.session_state.moves = 0


def flip(index):
    if index in st.session_state.matched:
        return

    selected = st.session_state.selected

    if index in selected:
        return

    if len(selected) == 2:
        selected.clear()

    selected.append(index)

    if len(selected) == 2:
        first, second = selected
        st.session_state.moves += 1

        if st.session_state.cards[first] == st.session_state.cards[second]:
            st.session_state.matched.update([first, second])
            selected.clear()


if "cards" not in st.session_state:
    reset_game()

st.title("🔎 AI Research Agent")
st.caption("Research smarter. Play while you wait!")

with st.form("research_form"):
    topic = st.text_input(
        "What do you want to research?",
        placeholder="Top AI automation companies in Pakistan"
    )
    start = st.form_submit_button("🚀 Start Research")

if start:
    if topic.strip():
        st.session_state.pop("report", None)
        st.session_state.pop("job_id", None)
        st.session_state.started = False
        st.session_state.research_status = "starting"

        try:
            response = requests.post(
                START_URL,
                json={"topic": topic.strip()},
                headers=HEADERS,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            st.session_state.topic = topic.strip()
            st.session_state.job_id = result["job_id"]
            st.session_state.started = True
            st.session_state.research_status = "running"

            st.success("🚀 Research started successfully!")

        except Exception as e:
            st.error(f"Could not start research: {e}")
    else:
        st.warning("Please enter a research topic.")

left, right = st.columns([1, 1.4])

with left:
    st.subheader("📡 Research Status")

    if st.session_state.get("started", False):
        st.write("**Topic:**", st.session_state.topic)
        st.write("**Job ID:**", st.session_state.job_id)

        status = st.session_state.get("research_status", "running")
        st.info(f"Research status: {status}")
    else:
        st.write("Enter a topic and start your research.")

    if st.session_state.get("job_id"):
        if st.button("🔄 Check Research Status"):
            try:
                response = requests.get(
                    STATUS_URL,
                    params={"job_id": st.session_state.job_id},
                    headers=HEADERS,
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()

                status = data.get("status", "unknown")
                st.session_state.research_status = status

                if status == "completed":
                    st.session_state.report = data.get("report", "")
                    st.success("✅ Research completed!")
                else:
                    st.info(f"Research status: {status}")

            except Exception as e:
                st.error(f"Status check failed: {e}")

    if st.session_state.get("report"):
        st.subheader("📄 Your Research Report")
        st.markdown(st.session_state.report)

with right:
    st.subheader("🃏 Memory Match")
    st.write("Find all six matching pairs.")

    a, b = st.columns(2)
    a.metric("Moves", st.session_state.moves)
    b.metric("Pairs found", len(st.session_state.matched) // 2)

    if st.button("🔄 Restart Game"):
        reset_game()
        st.rerun()

    for r in range(3):
        cols = st.columns(4)

        for c in range(4):
            i = r * 4 + c

            if i in st.session_state.matched or i in st.session_state.selected:
                label = st.session_state.cards[i]
            else:
                label = "❔"

            cols[c].button(
                label,
                key=f"card_{i}",
                use_container_width=True,
                disabled=i in st.session_state.matched,
                on_click=flip,
                args=(i,)
            )

    if len(st.session_state.matched) == 12:
        st.success(
            f"🎉 All pairs matched in {st.session_state.moves} moves!"
        )
