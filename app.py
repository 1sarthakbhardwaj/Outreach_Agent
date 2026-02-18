"""
Outreach Email Generator - Streamlit Application
Generates personalized outreach emails using Gemini 3 Flash with Google Search grounding.
"""

import streamlit as st
import os
from dotenv import load_dotenv
from utils.gemini_client import GeminiClient
from utils.prompt_builder import load_config, build_prompt, parse_email_response
from utils.logger import log_request, log_feedback


def extract_resources_from_grounding(grounding_metadata):
    """Extract resource URLs and titles from Gemini grounding metadata."""
    resources = []
    if not grounding_metadata:
        return resources

    try:
        if hasattr(grounding_metadata, 'grounding_chunks'):
            chunks = grounding_metadata.grounding_chunks
            if chunks:
                for chunk in chunks:
                    if hasattr(chunk, 'web') and chunk.web:
                        web = chunk.web
                        url = getattr(web, 'uri', None) or getattr(web, 'url', None)
                        title = getattr(web, 'title', None)
                        if url:
                            resources.append({'url': url, 'title': title or url})

        if hasattr(grounding_metadata, 'web_search_queries'):
            queries = grounding_metadata.web_search_queries
            if queries:
                for query in queries:
                    if hasattr(query, 'results') and query.results:
                        for result in query.results:
                            url = getattr(result, 'url', None) or getattr(result, 'uri', None)
                            title = getattr(result, 'title', None) or getattr(result, 'name', None)
                            if url:
                                resources.append({'url': url, 'title': title or url})

        if not resources:
            try:
                import re
                metadata_str = str(grounding_metadata)
                url_pattern = r'https?://[^\s<>"{}|\\^`\[\]()]+'
                found_urls = re.findall(url_pattern, metadata_str)
                for url in found_urls:
                    url = url.rstrip('.,;:!?)')
                    if url and url not in [r['url'] for r in resources]:
                        resources.append({'url': url, 'title': url})
            except:
                pass

        seen_urls = set()
        unique_resources = []
        for resource in resources:
            url = resource.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_resources.append(resource)

        return unique_resources

    except Exception:
        return resources


load_dotenv()

st.set_page_config(
    page_title="Outreach Email Generator",
    page_icon="📧",
    layout="centered"
)

st.markdown("""
<style>
    .main { padding: 2rem; }
    .stTitle {
        text-align: center; color: #1f1f1f;
        font-size: 2.5rem !important; font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
    }
    .email-card {
        background: #f8f9fa; border-radius: 12px; padding: 1.5rem;
        margin-bottom: 1.5rem; border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .email-subject {
        font-size: 1.1rem; font-weight: 600; color: #2c3e50;
        margin-bottom: 1rem; padding-bottom: 0.5rem;
        border-bottom: 2px solid #3498db;
    }
    .email-body {
        font-size: 0.95rem; line-height: 1.6; color: #34495e;
        white-space: pre-wrap;
    }
    .metrics-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px; padding: 1.5rem; margin-top: 2rem;
        color: white; text-align: center;
    }
    .metric-item { display: inline-block; margin: 0 1.5rem; }
    .metric-label { font-size: 0.85rem; opacity: 0.9; margin-bottom: 0.25rem; }
    .metric-value { font-size: 1.5rem; font-weight: 700; }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; font-weight: 600; padding: 0.75rem 2rem;
        border-radius: 8px; border: none; font-size: 1rem;
        margin-top: 1rem; transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    .input-section {
        background: white; padding: 2rem; border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 2rem;
    }
    .stTextInput>div>div>input {
        border-radius: 8px; border: 1.5px solid #e0e0e0; padding: 0.75rem;
    }
    .stTextInput>div>div>input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
    }
    .feedback-saved {
        background: #d4edda; color: #155724; padding: 0.5rem 1rem;
        border-radius: 8px; font-size: 0.9rem; margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Title ──
st.title("📧 Outreach Email Generator")

# ── Sidebar ──
with st.sidebar:
    st.header("⚙️ Settings")

    thinking_level = st.radio(
        "Thinking Level",
        options=["low", "high"],
        index=0,
        help="Low: Faster responses. High: More thoughtful, detailed analysis."
    )

    word_limit = st.slider(
        "📏 Email Word Limit",
        min_value=50,
        max_value=500,
        value=175,
        step=25,
        help="Target word count for each generated email."
    )

    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This tool generates 3 personalized outreach emails:
    1. **Industry angle** — trends in their domain
    2. **Company angle** — based on their company
    3. **Personal angle** — from LinkedIn/X activity
    
    All grounded via Google Search research.
    """)

    st.markdown("---")
    st.markdown("### Tips")
    st.markdown("""
    - Provide at least one social profile or company website
    - Use complete URLs for profiles
    - Paste past chats for warm follow-ups
    - Add your own examples to tune the style
    """)

# ── Prospect Info ──
st.markdown("### 👤 Prospect Information")

person_name = st.text_input(
    "Person Name",
    placeholder="e.g., John Smith",
    help="Full name of the prospect"
)

col1, col2 = st.columns(2)
with col1:
    linkedin_url = st.text_input(
        "💼 LinkedIn URL (Optional)",
        placeholder="https://linkedin.com/in/johnsmith",
        help="Optional if X profile is provided"
    )
with col2:
    x_profile_url = st.text_input(
        "𝕏 X Profile URL (Optional)",
        placeholder="https://x.com/johnsmith",
        help="Optional if LinkedIn is provided"
    )

company_website = st.text_input(
    "🏢 Company Website (Optional)",
    placeholder="e.g., https://www.acmecorp.com",
    help="Company website for better context during research"
)

# ── Advanced Options ──
st.markdown("---")
st.markdown("### 🎛️ Advanced Options")

with st.expander("💬 Past Conversation (optional)", expanded=False):
    past_conversation = st.text_area(
        "Paste any prior emails, DMs, or chat history with this person",
        placeholder="e.g.,\nMe: Hey John, enjoyed your talk at the AI summit!\nJohn: Thanks! We're exploring new annotation tools right now.\nMe: Would love to show you what we're building at Labellerr...",
        height=150,
        help="This context will be used to make the emails feel like a warm follow-up instead of a cold outreach."
    )

with st.expander("✍️ Custom Instructions & Examples (optional)", expanded=False):
    custom_instructions = st.text_area(
        "Your own style instructions or example emails to follow",
        placeholder="e.g.,\n- Keep it super casual, like texting a friend\n- Always start with a compliment\n- Example email I liked:\n  'Hey [name], saw your post about [topic] — really smart take. We just shipped something that might help...'",
        height=200,
        help="The AI will match your tone and style. Paste example emails you've written that worked well."
    )

# ── Generate ──
st.markdown("---")
generate_button = st.button("🚀 Generate Emails")

if generate_button:
    if not person_name:
        st.error("⚠️ Please provide the person's name.")
    elif not any([linkedin_url, company_website, x_profile_url]):
        st.error("⚠️ Please provide at least one of: LinkedIn URL, Company Website, or X Profile URL.")
    else:
        try:
            with st.spinner("🔍 Researching prospect and generating personalized emails..."):
                config = load_config()

                prompt = build_prompt(
                    person_name=person_name,
                    linkedin_url=linkedin_url,
                    company_name=company_website,
                    x_profile_url=x_profile_url,
                    config=config,
                    word_limit=word_limit,
                    past_conversation=past_conversation,
                    custom_instructions=custom_instructions,
                )

                client = GeminiClient()
                response = client.generate_emails(
                    prompt=prompt,
                    thinking_level=thinking_level
                )

                emails = parse_email_response(response['text'])
                resources = extract_resources_from_grounding(response.get('grounding_metadata'))

                token_usage = {
                    'input': response['input_tokens'],
                    'output': response['output_tokens'],
                    'total': response['total_tokens']
                }

                # Log the request
                entry_id = log_request(
                    person_name=person_name,
                    linkedin_url=linkedin_url,
                    company_website=company_website,
                    x_profile_url=x_profile_url,
                    word_limit=word_limit,
                    thinking_level=thinking_level,
                    past_conversation=past_conversation,
                    custom_instructions=custom_instructions,
                    generated_emails=emails,
                    token_usage=token_usage,
                    resources=resources,
                )

                # Store in session state
                st.session_state.emails = emails
                st.session_state.token_usage = token_usage
                st.session_state.resources = resources
                st.session_state.log_entry_id = entry_id
                st.session_state.feedback_saved = {}

            st.success("✅ Emails generated successfully!")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("💡 Make sure your GEMINI_API_KEY is set in the .env file")

# ── Display Generated Emails ──
if 'emails' in st.session_state and st.session_state.emails:
    st.markdown("---")
    st.markdown("## 📬 Generated Email Variations")

    email_angles = {
        1: ("🌐", "Industry Angle"),
        2: ("🏢", "Company Angle"),
        3: ("👤", "Personal Angle"),
    }

    for i, email in enumerate(st.session_state.emails, 1):
        icon, angle = email_angles.get(i, ("📧", f"Variation {i}"))
        st.markdown(f"""
        <div class="email-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="margin: 0; color: #2c3e50;">{icon} Email {i} — {angle}</h3>
            </div>
            <div class="email-subject">
                Subject: {email.get('subject', 'No subject')}
            </div>
            <div class="email-body">
{email.get('body', 'No content')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        full_email = f"Subject: {email.get('subject', '')}\n\n{email.get('body', '')}"

        with st.expander("📋 View Full Email Text (for copying)"):
            st.code(full_email, language=None)
            st.caption("Select all text above (Cmd/Ctrl + A) and copy (Cmd/Ctrl + C)")

        # Feedback: what did you actually send?
        feedback_key = f"feedback_{i}"
        saved_key = f"saved_{i}"

        if st.session_state.get('feedback_saved', {}).get(i):
            st.markdown(f'<div class="feedback-saved">✅ Feedback saved for Email {i}</div>', unsafe_allow_html=True)
        
        with st.expander(f"📝 Log what you actually sent (Email {i})", expanded=False):
            actual_sent = st.text_area(
                f"Paste the email you actually sent for variation {i}",
                key=feedback_key,
                placeholder="Paste the final version of the email you ended up sending. This helps us learn your style for better future suggestions.",
                height=150,
            )
            if st.button(f"💾 Save Feedback", key=f"save_btn_{i}"):
                if actual_sent.strip():
                    entry_id = st.session_state.get('log_entry_id')
                    if entry_id:
                        log_feedback(entry_id, i - 1, actual_sent.strip())
                        if 'feedback_saved' not in st.session_state:
                            st.session_state.feedback_saved = {}
                        st.session_state.feedback_saved[i] = True
                        st.success(f"✅ Feedback for Email {i} saved!")
                    else:
                        st.warning("⚠️ No log entry found. Generate emails first.")
                else:
                    st.warning("⚠️ Please paste the email you actually sent before saving.")

    # ── Token Usage ──
    if 'token_usage' in st.session_state:
        usage = st.session_state.token_usage
        st.markdown(f"""
        <div class="metrics-box">
            <h3 style="margin-top: 0; margin-bottom: 1rem;">📊 Token Usage</h3>
            <div>
                <div class="metric-item">
                    <div class="metric-label">Input Tokens</div>
                    <div class="metric-value">{usage['input']:,}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Output Tokens</div>
                    <div class="metric-value">{usage['output']:,}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Total Tokens</div>
                    <div class="metric-value">{usage['total']:,}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Footer ──
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem; padding: 1rem;">
    Built with Streamlit • Powered by Gemini 3 Flash • Data by Labellerr
</div>
""", unsafe_allow_html=True)
