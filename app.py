import os
import streamlit as st
from datetime import datetime
from core.transcriber import MeetingTranscriber
from core.extractor import MeetingExtractor
from core.action_tracker import ActionTracker
from core.rag_engine import MeetingRAG
from models.prompts import RAG_PROMPT
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, SystemMessage

st.set_page_config(page_title="Meeting Intelligence", page_icon="🎙️", layout="wide")

try:
    mistral_key = st.secrets["MISTRAL_API_KEY"]
except KeyError:
    st.error("❌ MISTRAL_API_KEY not found in Streamlit secrets")
    st.stop()

@st.cache_resource
def get_transcriber():
    return MeetingTranscriber(model_size="base")

@st.cache_resource
def get_extractor():
    return MeetingExtractor(mistral_key)

@st.cache_resource
def get_tracker():
    return ActionTracker()

@st.cache_resource
def get_rag():
    return MeetingRAG()

@st.cache_resource
def get_llm():
    return ChatMistralAI(
        model="mistral-small-latest",
        api_key=mistral_key,
        temperature=0.3
    )

transcriber = get_transcriber()
extractor = get_extractor()
tracker = get_tracker()
rag = get_rag()
llm = get_llm()

with st.sidebar:
    st.title("🎙️ Meeting Intelligence")
    st.caption("AI-powered meeting assistant")
    st.divider()
    st.markdown("### 📊 Dashboard")
    summary = tracker.get_action_summary()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total", summary["total"])
    with col2:
        st.metric("Pending", summary["pending"])
    with col3:
        st.metric("Done", summary["done"])
    if summary["by_priority"]:
        st.markdown("**Pending by Priority:**")
        for p, c in summary["by_priority"].items():
            emoji = "🔴" if p == "HIGH" else "🟡" if p == "MEDIUM" else "🟢"
            st.write(f"{emoji} {p}: {c}")
    st.divider()
    st.markdown("### 📋 Recent Meetings")
    for m in tracker.get_meetings()[:5]:
        st.write(f"📄 {m['title']} ({m['date'][:10]})")

tab1, tab2, tab3, tab4 = st.tabs([
    "🎙️ New Meeting",
    "📋 Actions",
    "📄 Meetings",
    "💬 Chat"
])

with tab1:
    st.header("Upload a Meeting Recording")
    uploaded_file = st.file_uploader(
        "Choose audio file",
        type=["mp3", "wav", "m4a", "flac"]
    )
    if uploaded_file and st.button("🚀 Process Meeting", type="primary"):
        with st.spinner("🔄 Transcribing..."):
            result = transcriber.transcribe(uploaded_file)
            if not result["success"]:
                st.error(f"Error: {result.get('error', 'Unknown')}")
            else:
                transcript = result["text"]
                st.success("✅ Transcription complete!")
                with st.expander("📝 Transcript"):
                    st.text_area("", transcript, height=200)
                with st.spinner("🧠 Extracting..."):
                    extracted = extractor.extract(transcript)
                st.subheader("📋 Decisions")
                for d in extracted["decisions"]:
                    st.write(f"• {d}")
                st.subheader("✅ Action Items")
                for a in extracted["action_items"]:
                    st.write(f"• {a.get('action')}")
                    st.caption(f"Assigned: {a.get('assigned_to')} | Deadline: {a.get('deadline')} | Priority: {a.get('priority')}")
                st.subheader("📝 Summary")
                st.write(extracted["summary"])
                meeting_id = tracker.save_meeting(
                    f"Meeting - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    transcript,
                    extracted["summary"]
                )
                tracker.save_action_items(meeting_id, extracted["action_items"])
                rag.add_meeting(meeting_id, transcript, {
                    "title": f"Meeting - {datetime.now().strftime('%Y-%m-%d')}",
                    "date": datetime.now().isoformat()
                })
                st.success("✅ Saved!")
                st.balloons()

with tab2:
    st.header("📋 Action Items")
    status_filter = st.selectbox("Filter", ["All", "pending", "done"])
    filter_val = None if status_filter == "All" else status_filter
    for action in tracker.get_action_items(status=filter_val):
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.markdown(f"**{action['action']}**")
                st.caption(f"Meeting: {action.get('meeting_title', 'Unknown')}")
            with col2:
                st.write(f"👤 {action['assigned_to']}")
                st.write(f"📅 {action['deadline']}")
            with col3:
                emoji = "🔴" if action['priority'] == "HIGH" else "🟡" if action['priority'] == "MEDIUM" else "🟢"
                st.write(f"{emoji} {action['priority']}")
                if action['status'] == "pending" and st.button("✅ Done", key=f"done_{action['id']}"):
                    tracker.update_action_status(action['id'], "done")
                    st.rerun()
                elif action['status'] == "done":
                    st.success("✅ Done")
            st.divider()

with tab3:
    st.header("📄 Past Meetings")
    for meeting in tracker.get_meetings():
        with st.expander(f"{meeting['title']} - {meeting['date'][:16]}"):
            st.markdown("**Summary:**")
            st.write(meeting['summary'])
            actions = tracker.get_action_items(meeting_id=meeting['id'])
            if actions:
                st.markdown("**Action Items:**")
                for a in actions:
                    emoji = "✅" if a['status'] == "done" else "⬜"
                    st.write(f"{emoji} {a['action']} (→ {a['assigned_to']})")
            full = tracker.get_meeting(meeting['id'])
            if full and full.get('transcript'):
                with st.expander("📝 Full Transcript"):
                    st.text_area("", full['transcript'], height=200)

with tab4:
    st.header("💬 Chat with Your Meetings")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    query = st.text_input("Ask a question about your meetings")
    if query:
        with st.spinner("🔍 Searching..."):
            results = rag.search(query, n_results=3)
            if results:
                context = "\n\n".join([r["content"] for r in results])
                response = llm.invoke([
                    SystemMessage(content=RAG_PROMPT.format(context=context, query=query)),
                    HumanMessage(content=query)
                ])
                st.session_state.chat_history.append({"query": query, "response": response.content})
                with st.expander("📚 Sources"):
                    for r in results:
                        st.write(f"• {r['content'][:200]}...")
                        st.caption(f"From: {r['metadata'].get('title', 'Unknown')}")
            else:
                st.info("No relevant content found. Upload meetings first!")
    for item in st.session_state.chat_history:
        st.markdown(f"**Q:** {item['query']}")
        st.markdown(f"**A:** {item['response']}")
        st.divider()
