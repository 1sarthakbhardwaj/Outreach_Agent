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
    
    prompt = f"""You are an expert B2B outreach specialist for Labellerr, a leading AI-powered data annotation platform.

PROSPECT INFORMATION:
- Name: {person_name}
- Company: {company_name}
- LinkedIn: {linkedin_url}
- X (Twitter): {x_profile_url}

YOUR TASK:
Using Google Search, research {person_name}'s recent activities on LinkedIn and X/Twitter. Look for any discussions, posts, or indicators related to:
- Data annotation challenges or needs
- Machine learning model training requirements
- Model fine-tuning projects
- AI/ML infrastructure or pipeline discussions
- Data quality or labeling pain points

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
Generate 3 DISTINCT email variations (each with a different approach/angle) that:

1. Start with a brief, personalized opener referencing their SPECIFIC recent activity or post you found
2. Acknowledge a potential challenge or interest area related to data annotation/ML training
3. Introduce Labellerr as a solution, highlighting 2-3 relevant capabilities
4. Include a clear, low-pressure call-to-action

REQUIREMENTS:
- Each email should be 150-200 words maximum
- Professional but conversational tone
- Focus on value, not features
- Avoid being overly salesy or generic
- Each variation should take a different angle (e.g., technical depth, speed/efficiency, cost savings)
- Include a compelling subject line for each email

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

Remember to ground your emails in actual, recent information you find about {person_name} through Google Search."""

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
