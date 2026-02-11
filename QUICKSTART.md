# Quick Start Guide

Get your Outreach Email Generator running in 5 minutes!

## Step 1: Get Your API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Get API Key" or "Create API Key"
4. Copy the generated API key

## Step 2: Configure the Application

1. Navigate to the `outreach-agent` folder
2. Create a `.env` file (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```
3. Open `.env` and paste your API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

If you prefer using a virtual environment (recommended):

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 4: Run Tests (Optional)

Verify everything is working:

```bash
python test_app.py
```

You should see: "All tests passed! Ready to run: streamlit run app.py"

## Step 5: Launch the App

```bash
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

## Step 6: Generate Your First Email

1. Fill in the prospect information:
   - **Person Name**: e.g., "Sarah Chen"
   - **LinkedIn URL**: Full profile URL (e.g., `https://linkedin.com/in/sarahchen`)
   - **Company Name**: e.g., "TechCorp AI"
   - **X Profile URL**: Full Twitter/X URL (e.g., `https://x.com/sarahchen`)

2. (Optional) Adjust thinking level in the sidebar:
   - **Low** (default): Faster, good for most cases
   - **High**: More thorough research and personalization

3. Click "🚀 Generate Emails"

4. Wait 10-30 seconds for the AI to:
   - Research the prospect's recent activities
   - Identify data annotation needs
   - Generate 3 personalized email variations

5. Review and copy your emails!

## Tips for Best Results

✅ **Use Public Profiles**: Ensure LinkedIn and X profiles are publicly visible

✅ **Complete URLs**: Use full profile URLs, not shortened links

✅ **Active Profiles**: Prospects with recent activity yield better personalization

✅ **Try Different Variations**: The 3 emails take different angles - test to see which works best

## Troubleshooting

### "GEMINI_API_KEY not found"
- Make sure you created the `.env` file
- Verify your API key is correctly pasted (no extra spaces)
- Restart the Streamlit app after adding the key

### "Rate limit exceeded"
- Gemini API has usage limits
- Wait a few minutes and try again
- Check your [API quota](https://aistudio.google.com/)

### "No recent activities found"
- The prospect's profiles might be private
- Try a different prospect with public, active profiles
- Ensure URLs are correct and accessible

### Import errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Verify you're using Python 3.8 or higher: `python --version`

## Customization

### Edit Company Information

Edit `config.yaml` to customize:
- Company overview
- Key capabilities
- Specializations
- Value propositions
- Contact information

Changes take effect immediately (no need to restart the app).

### Adjust Email Format

Edit `utils/prompt_builder.py` to modify:
- Email structure
- Tone and style
- Focus areas
- Call-to-action options

## Need Help?

- Review the full [README.md](README.md) for detailed documentation
- Check the [test_app.py](test_app.py) output for specific errors
- Ensure your API key is valid and has available quota

## What's Next?

Once you're comfortable with the basics:

1. **Experiment with thinking levels** - High mode provides deeper personalization
2. **A/B test email variations** - Track which style gets better responses
3. **Customize config.yaml** - Tailor the pitch to your specific offerings
4. **Batch processing** - Generate emails for multiple prospects

---

**Happy Outreaching! 📧**
