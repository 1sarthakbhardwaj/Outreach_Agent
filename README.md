# Outreach Email Generator

An AI-powered outreach email generator that creates personalized B2B emails using Gemini 3 Flash with Google Search grounding.

## Features

- **Google Search Grounding**: Automatically researches prospects' recent LinkedIn and X (Twitter) activities
- **3 Email Variations**: Generates three distinct email approaches for each prospect
- **Token Usage Tracking**: Displays input, output, and total token consumption
- **Configurable Thinking**: Toggle between low (faster) and high (more thoughtful) thinking levels
- **Clean UI**: Modern, minimal Streamlit interface with card-based email previews
- **Easy Configuration**: Labellerr company info stored in editable YAML config

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API key:
   - Copy `.env.example` to `.env`
   - Add your Gemini API key to `.env`:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

## Usage

1. Start the Streamlit app:
```bash
streamlit run app.py
```

2. Open your browser to the provided URL (typically `http://localhost:8501`)

3. Fill in the prospect information:
   - Person Name
   - LinkedIn Profile URL
   - Company Name
   - X (Twitter) Profile URL

4. (Optional) Adjust thinking level in sidebar:
   - **Low**: Faster responses, good for most cases
   - **High**: More thoughtful analysis, better personalization

5. Click "Generate Emails" and wait for results

6. Review the 3 generated email variations

7. Copy emails using the expandable text sections

## Project Structure

```
outreach-agent/
├── app.py                    # Main Streamlit application
├── config.yaml               # Labellerr company info (editable)
├── requirements.txt          # Python dependencies
├── .env                      # API key (create from .env.example)
├── .env.example              # Template for environment variables
├── README.md                 # This file
└── utils/
    ├── __init__.py
    ├── gemini_client.py     # Gemini API wrapper
    └── prompt_builder.py    # Prompt construction logic
```

## Configuration

Edit `config.yaml` to customize Labellerr's company information, capabilities, and pitch points. The configuration includes:

- Company overview and tagline
- Key capabilities
- Specializations
- Value propositions
- Success stories
- Contact information
- Call-to-action options

## How It Works

1. **User Input**: You provide prospect details (name, LinkedIn, X profile, company)

2. **Google Search Grounding**: Gemini uses Google Search to research the prospect's recent activities on LinkedIn and X

3. **AI Analysis**: The model identifies potential data annotation needs, ML challenges, or relevant pain points

4. **Email Generation**: Creates 3 distinct email variations, each with:
   - Personalized opener referencing recent activity
   - Acknowledgment of their challenge/need
   - Introduction to Labellerr as solution
   - Clear call-to-action

5. **Display**: Shows all emails with subject lines, token usage metrics, and easy copy functionality

## Tips

- Use complete, public profile URLs
- Ensure LinkedIn and X profiles are publicly accessible
- Higher thinking level = better personalization (but slower)
- Each email variation takes a different angle (technical, efficiency, cost savings, etc.)

## Technology Stack

- **Frontend**: Streamlit
- **AI Model**: Gemini 3 Flash Preview
- **API**: google-genai Python SDK
- **Configuration**: YAML
- **Environment**: python-dotenv

## Requirements

- Python 3.8+
- Gemini API key (get from [Google AI Studio](https://aistudio.google.com/))
- Internet connection for API calls

## License

This project is for internal use. Customize as needed for your organization.

## Support

For issues or questions, please contact your development team.
