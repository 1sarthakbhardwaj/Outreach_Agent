"""Prompt builder for generating personalized outreach emails."""

from typing import Dict, Any
import yaml


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load Labellerr configuration from YAML file.
    
    Args:
        config_path: Path to config.yaml file
        
    Returns:
        Dictionary containing Labellerr configuration
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config.get('labellerr', {})


def build_prompt(
    person_name: str,
    linkedin_url: str,
    company_name: str,
    x_profile_url: str,
    config: Dict[str, Any]
) -> str:
    """
    Build a comprehensive prompt for email generation.
    
    Args:
        person_name: Name of the prospect
        linkedin_url: LinkedIn profile URL
        company_name: Company name
        x_profile_url: X (Twitter) profile URL
        config: Labellerr configuration dictionary
        
    Returns:
        Formatted prompt string
    """
    # Extract key information from config
    capabilities = "\n".join([f"- {cap}" for cap in config.get('key_capabilities', [])])
    specializations = "\n".join([f"- {spec}" for spec in config.get('specializations', [])])
    value_props = "\n".join([f"- {vp}" for vp in config.get('value_propositions', [])])
    
    # Build prospect info section dynamically based on available fields
    prospect_lines = [f"- Name: {person_name}"]
    if company_name:
        prospect_lines.append(f"- Company Website: {company_name}")
    if linkedin_url:
        prospect_lines.append(f"- LinkedIn: {linkedin_url}")
    if x_profile_url:
        prospect_lines.append(f"- X (Twitter): {x_profile_url}")
    prospect_info = "\n".join(prospect_lines)

    prompt = f"""You are an expert B2B outreach specialist for Labellerr, a leading AI-powered data annotation platform.

PROSPECT INFORMATION:
{prospect_info}

YOUR TASK:
Using Google Search, research {person_name} and their company. Gather context about:
- What industry they operate in and current trends/challenges in that industry
- What their company does, its products, and how it uses AI/ML/data
- Their professional background, role, and any public posts or activity on LinkedIn or X/Twitter

LABELLERR OVERVIEW:
{config.get('overview', '')}

KEY CAPABILITIES:
{capabilities}

SPECIALIZATIONS:
{specializations}

VALUE PROPOSITIONS:
{value_props}

WEBSITE: {config.get('contact', {}).get('website', 'https://labellerr.com')}

INSTRUCTIONS:
Generate 3 DISTINCT emails, each with a DIFFERENT angle as described below:

**EMAIL 1 - INDUSTRY ANGLE:**
- Focus on the industry/domain {person_name} works in
- Reference a real trend, challenge, or development in their industry related to AI/ML and data
- Connect how Labellerr helps companies in that specific industry
- Keep it broad and insightful — show you understand their space

**EMAIL 2 - COMPANY ANGLE:**
- Focus specifically on {person_name}'s company
- Reference what the company does, its products, or its public AI/ML initiatives
- Identify a specific way Labellerr could help their company with data annotation needs
- Show you've done homework on their company

**EMAIL 3 - PERSONAL ANGLE:**
- Focus on {person_name} personally
- Reference their role, expertise, or any public posts/activity you found on LinkedIn or X
- Speak to them as a professional — acknowledge their work or perspective
- Make it feel like a genuine 1-on-1 conversation

REQUIREMENTS FOR ALL EMAILS:
- Each email should be 150-200 words maximum
- Professional but conversational tone
- Focus on value, not features
- Avoid being overly salesy or generic
- Include a compelling subject line for each email
- Include a clear, low-pressure call-to-action
- DO NOT include any URLs or links in the email body — no LinkedIn links, no article links, no post links
- Only reference information in plain text (e.g., "I noticed your company recently expanded into computer vision" NOT "I saw this post: https://...")

FORMAT YOUR RESPONSE EXACTLY AS:

---EMAIL 1---
SUBJECT: [subject line]

[email body]

---EMAIL 2---
SUBJECT: [subject line]

[email body]

---EMAIL 3---
SUBJECT: [subject line]

[email body]

IMPORTANT:
- Ground all emails in real information found via Google Search — do NOT make up facts
- DO NOT fabricate or hallucinate any URLs/links — keep the emails clean text only
- Each email must take a clearly different angle (industry vs company vs personal)"""

    return prompt


def parse_email_response(response_text: str) -> list[Dict[str, str]]:
    """
    Parse the model's response into structured email objects.
    
    Args:
        response_text: Raw text response from the model
        
    Returns:
        List of dictionaries, each containing 'subject' and 'body'
    """
    emails = []
    
    # Split by email markers
    email_sections = response_text.split('---EMAIL')
    
    for section in email_sections[1:]:  # Skip first empty split
        # Extract email number and content
        lines = section.strip().split('\n', 1)
        if len(lines) < 2:
            continue
            
        content = lines[1].strip()
        
        # Extract subject and body
        subject = ""
        body = ""
        
        if content.startswith('SUBJECT:'):
            parts = content.split('\n', 1)
            subject = parts[0].replace('SUBJECT:', '').strip()
            if len(parts) > 1:
                body = parts[1].strip()
        else:
            body = content
        
        emails.append({
            'subject': subject,
            'body': body
        })
    
    # If parsing failed, try alternative format
    if not emails:
        # Fallback: split by "Subject:" occurrences
        parts = response_text.split('Subject:')
        for i, part in enumerate(parts[1:], 1):  # Skip first empty
            lines = part.strip().split('\n', 1)
            subject = lines[0].strip()
            body = lines[1].strip() if len(lines) > 1 else ""
            
            emails.append({
                'subject': subject,
                'body': body
            })
    
    return emails[:3]  # Return only first 3 emails
