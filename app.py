import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="MindMirror", page_icon="🪞", layout="centered")

st.title("🪞 MindMirror")
st.caption("AI-powered journal for emotional pattern awareness")

tab1, tab2, tab3, tab4 = st.tabs(["✍️ Write", "🔍 Search", "📊 Patterns", "📋 Weekly Report"])

# --- Tab 1: Write entry ---
with tab1:
    st.subheader("Today's journal entry")
    text = st.text_area(
        "What's on your mind?",
        height=200,
        placeholder="Write freely. This is a safe space to reflect...",
        label_visibility="collapsed"
    )
    
    if st.button("Analyze entry", type="primary"):
        if len(text.strip()) < 10:
            st.warning("Please write at least a sentence or two.")
        else:
            with st.spinner("Analyzing your entry..."):
                try:
                    response = requests.post(f"{API_URL}/entry", json={"text": text})
                    result = response.json()
                    analysis = result["analysis"]
                    
                    st.success("Entry saved!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Emotional intensity", f"{analysis['intensity']}/10")
                        st.metric("Tone", analysis['valence'].capitalize())
                    with col2:
                        emotions = ", ".join(analysis['emotions'])
                        st.metric("Emotions detected", emotions)
                    
                    if analysis['distortions']:
                        st.warning(f"**Patterns noticed:** {', '.join(analysis['distortions'])}")
                        st.caption("These are thinking patterns worth reflecting on — not labels or diagnoses.")
                    else:
                        st.success("No cognitive distortions detected in this entry.")
                    
                    st.info(f"💭 {analysis['summary']}")
                    
                except Exception as e:
                    st.error(f"Could not connect to API. Is it running? Error: {e}")

# --- Tab 2: Search ---
with tab2:
    st.subheader("Search your journal")
    query = st.text_input("What would you like to find?", 
                          placeholder="e.g. times I felt anxious about work")
    
    if st.button("Search"):
        with st.spinner("Searching..."):
            try:
                response = requests.get(f"{API_URL}/search", params={"q": query, "n": 5})
                results = response.json()["results"]
                
                if not results:
                    st.info("No entries found yet. Start writing to build your journal.")
                else:
                    st.write(f"Found {len(results)} relevant entries:")
                    for r in results:
                        with st.expander(f"📅 {r['metadata']['date'][:10]} — {r['metadata']['emotions']}"):
                            st.write(r['text'])
                            st.caption(f"Tone: {r['metadata']['valence']} | Intensity: {r['metadata']['intensity']}/10")
                            
            except Exception as e:
                st.error(f"Search failed: {e}")

# --- Tab 3: Patterns ---
with tab3:
    st.subheader("Your emotional patterns")
    
    try:
        stats = requests.get(f"{API_URL}/stats").json()
        
        if stats.get("total_entries", 0) == 0:
            st.info("No entries yet. Start journaling to see your patterns.")
        else:
            st.metric("Total entries", stats["total_entries"])
            st.metric("Average intensity", f"{stats['avg_intensity']}/10")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Top emotions**")
                for emotion, count in stats.get("top_emotions", []):
                    st.write(f"- {emotion}: {count}x")
            with col2:
                st.write("**Cognitive patterns**")
                if stats.get("top_distortions"):
                    for dist, count in stats["top_distortions"]:
                        st.write(f"- {dist}: {count}x")
                else:
                    st.write("None detected yet")
                    
    except Exception as e:
        st.error(f"Could not load stats: {e}")

# --- Tab 4: Weekly report ---
with tab4:
    st.subheader("Weekly insight report")
    
    if st.button("Generate this week's report"):
        with st.spinner("Your AI coach is reflecting on your week..."):
            try:
                report = requests.get(f"{API_URL}/report/weekly").json()
                
                st.markdown(f"### 🌊 This week's theme")
                st.write(report.get("dominant_theme", ""))
                
                st.markdown(f"### 🔍 Pattern to notice")
                st.info(report.get("pattern_to_notice", ""))
                
                st.markdown(f"### 💡 Suggestion for next week")
                st.success(report.get("suggestion", ""))
                
                st.markdown(f"### 💪 Encouragement")
                st.write(report.get("encouragement", ""))
                
                trend = report.get("intensity_trend", "stable")
                trend_emoji = {"improving": "📈", "worsening": "📉", "stable": "➡️"}.get(trend, "➡️")
                st.caption(f"Intensity trend: {trend_emoji} {trend.capitalize()}")
                
            except Exception as e:
                st.error(f"Could not generate report: {e}")
    
    st.caption("⚠️ MindMirror is a self-reflection tool, not a substitute for professional mental health support.")