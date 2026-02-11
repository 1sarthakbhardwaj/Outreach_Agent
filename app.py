"""
Outreach Email Generator - Streamlit Application
Generates personalized outreach emails using Gemini 3 Flash with Google Search grounding.
"""

import streamlit as st
import os
from dotenv import load_dotenv
from utils.gemini_client import GeminiClient
from utils.prompt_builder import load_config, build_prompt, parse_email_response


def extract_resources_from_grounding(grounding_metadata):
    """
    Extract resource URLs and titles from Gemini grounding metadata.
    
    Args:
        grounding_metadata: The grounding_metadata object from Gemini API response
        
    Returns:
        List of dictionaries with 'url' and 'title' keys
    """
    resources = []
    
    if not grounding_metadata:
        return resources
    
    try:
        # Check for web search chunks in grounding metadata
        if hasattr(grounding_metadata, 'web_search_queries'):
            # Handle web search queries
            pass
        
        # Check for grounding chunks which contain the actual sources
        if hasattr(grounding_metadata, 'grounding_chunks'):
            chunks = grounding_metadata.grounding_chunks
            if chunks:
                for chunk in chunks:
                    if hasattr(chunk, 'web') and chunk.web:
                        web = chunk.web
                        url = getattr(web, 'uri', None) or getattr(web, 'url', None)
                        title = getattr(web, 'title', None)
                        if url:
                            resources.append({
                                'url': url,
                                'title': title or url
                            })
        
        # Alternative structure - check for search_entry_point
        if hasattr(grounding_metadata, 'search_entry_point'):
            entry_point = grounding_metadata.search_entry_point
            if hasattr(entry_point, 'rendered_content'):
                # This might contain search results
                pass
        
        # Check for web_search_queries and their results
        if hasattr(grounding_metadata, 'web_search_queries'):
            queries = grounding_metadata.web_search_queries
            if queries:
                for query in queries:
                    if hasattr(query, 'results') and query.results:
                        for result in query.results:
                            url = getattr(result, 'url', None) or getattr(result, 'uri', None)
                            title = getattr(result, 'title', None) or getattr(result, 'name', None)
                            if url:
                                resources.append({
                                    'url': url,
                                    'title': title or url
                                })
        
        # Method 3: Fallback - try to extract URLs from string representation
        if not resources:
            try:
                import re
                # Convert to string and look for URL patterns
                metadata_str = str(grounding_metadata)
                # Look for URLs in the string representation
                url_pattern = r'https?://[^\s<>"{}|\\^`\[\]()]+'
                found_urls = re.findall(url_pattern, metadata_str)
                for url in found_urls:
                    # Clean up URL (remove trailing punctuation)
                    url = url.rstrip('.,;:!?)')
                    if url and url not in [r['url'] for r in resources]:
                        resources.append({
                            'url': url,
                            'title': url
                        })
            except:
                pass
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_resources = []
        for resource in resources:
            url = resource.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_resources.append(resource)
        
        return unique_resources
    
    except Exception as e:
        # If parsing fails, return empty list
        return resources

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Outreach Email Generator",
    page_icon="📧",
    layout="centered"
)

# Custom CSS for clean, modern UI
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    
    .stTitle {
        text-align: center;
        color: #1f1f1f;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    .email-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .email-subject {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3498db;
    }
    
    .email-body {
        font-size: 0.95rem;
        line-height: 1.6;
        color: #34495e;
        white-space: pre-wrap;
    }
    
    .metrics-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 2rem;
        color: white;
        text-align: center;
    }
    
    .metric-item {
        display: inline-block;
        margin: 0 1.5rem;
    }
    
    .metric-label {
        font-size: 0.85rem;
        opacity: 0.9;
        margin-bottom: 0.25rem;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        border: none;
        font-size: 1rem;
        margin-top: 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    .input-section {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 2rem;
    }
    
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 1.5px solid #e0e0e0;
        padding: 0.75rem;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
    }
    
    .resources-box {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 2rem;
        border: 1px solid #e0e0e0;
    }
    
    .resource-item {
        padding: 0.75rem;
        margin: 0.5rem 0;
        background: white;
        border-radius: 8px;
        border-left: 3px solid #667eea;
    }
    
    .resource-title {
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.25rem;
    }
    
    .resource-url {
        font-size: 0.85rem;
        color: #667eea;
        word-break: break-all;
    }
</style>
""", unsafe_allow_html=True)

# App title and subtitle
st.title("📧 Outreach Email Generator")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    thinking_level = st.radio(
        "Thinking Level",
        options=["low", "high"],
        index=0,
        help="Low: Faster responses. High: More thoughtful, detailed analysis."
    )
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This tool generates personalized outreach emails by:
    - Researching prospects via Google Search
    - Analyzing recent LinkedIn/X activity
    - Identifying data annotation needs
    - Crafting 3 unique email variations
    """)
    
    st.markdown("---")
    st.markdown("### Tips")
    st.markdown("""
    - Provide at least one social profile or company website
    - Use complete URLs for profiles
    - Ensure profiles are public
    - Higher thinking = better personalization
    """)

# Input section
st.markdown('<div class="input-section">', unsafe_allow_html=True)

person_name = st.text_input(
    "👤 Person Name",
    placeholder="e.g., John Smith",
    help="Full name of the prospect"
)

linkedin_url = st.text_input(
    "💼 LinkedIn Profile URL (Optional)",
    placeholder="e.g., https://linkedin.com/in/johnsmith",
    help="Complete LinkedIn profile URL - optional if X profile is provided"
)

company_website = st.text_input(
    "🏢 Company Website (Optional)",
    placeholder="e.g., https://www.acmecorp.com",
    help="Company website for better context during research"
)

x_profile_url = st.text_input(
    "𝕏 X (Twitter) Profile URL (Optional)",
    placeholder="e.g., https://x.com/johnsmith",
    help="Complete X/Twitter profile URL - optional if LinkedIn is provided"
)

generate_button = st.button("🚀 Generate Emails")

st.markdown('</div>', unsafe_allow_html=True)

# Generate emails when button is clicked
if generate_button:
    # Validate inputs - require person name and at least one optional field
    if not person_name:
        st.error("⚠️ Please provide the person's name.")
    elif not any([linkedin_url, company_website, x_profile_url]):
        st.error("⚠️ Please provide at least one of: LinkedIn URL, Company Website, or X Profile URL.")
    else:
        try:
            with st.spinner("🔍 Researching prospect and generating personalized emails..."):
                # Load configuration
                config = load_config()
                
                # Build prompt
                prompt = build_prompt(
                    person_name=person_name,
                    linkedin_url=linkedin_url,
                    company_name=company_website,
                    x_profile_url=x_profile_url,
                    config=config
                )
                
                # Initialize Gemini client and generate
                client = GeminiClient()
                response = client.generate_emails(
                    prompt=prompt,
                    thinking_level=thinking_level
                )
                
                # Parse emails
                emails = parse_email_response(response['text'])
                
                # Extract resources from grounding metadata
                resources = extract_resources_from_grounding(response.get('grounding_metadata'))
                
                # Store in session state
                st.session_state.emails = emails
                st.session_state.token_usage = {
                    'input': response['input_tokens'],
                    'output': response['output_tokens'],
                    'total': response['total_tokens']
                }
                st.session_state.resources = resources
                
            st.success("✅ Emails generated successfully!")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("💡 Make sure your GEMINI_API_KEY is set in the .env file")

# Display generated emails
if 'emails' in st.session_state and st.session_state.emails:
    st.markdown("---")
    st.markdown("## 📬 Generated Email Variations")
    
    for i, email in enumerate(st.session_state.emails, 1):
        st.markdown(f"""
        <div class="email-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="margin: 0; color: #2c3e50;">📧 Email Variation {i}</h3>
            </div>
            <div class="email-subject">
                Subject: {email.get('subject', 'No subject')}
            </div>
            <div class="email-body">
{email.get('body', 'No content')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Copy to clipboard button for each email
        full_email = f"Subject: {email.get('subject', '')}\n\n{email.get('body', '')}"
        
        # Use columns for copy button with expander
        with st.expander("📋 View Full Email Text (for copying)"):
            st.code(full_email, language=None)
            st.caption("Select all text above (Cmd/Ctrl + A) and copy (Cmd/Ctrl + C)")
    
    # Display resources/sources used
    if 'resources' in st.session_state and st.session_state.resources:
        st.markdown("---")
        st.markdown("## 🔍 Research Sources")
        st.markdown('<p style="color: #666; font-size: 0.95rem;">Sources used by Google Search to generate these emails:</p>', unsafe_allow_html=True)
        
        resources_html = '<div class="resources-box">'
        for i, resource in enumerate(st.session_state.resources, 1):
            resources_html += f'''
            <div class="resource-item">
                <div class="resource-title">{i}. {resource.get("title", "Source")}</div>
                <div class="resource-url"><a href="{resource["url"]}" target="_blank">{resource["url"]}</a></div>
            </div>
            '''
        resources_html += '</div>'
        st.markdown(resources_html, unsafe_allow_html=True)
    
    # Token usage metrics
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

# Footer
st.markdown("---")
