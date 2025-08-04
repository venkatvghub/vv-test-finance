# Goal-based Indian Financial Advisor Bot

A **Streamlit application** that provides **personalized financial advice** for Indian users using **OpenRouter AI models**.  
The app accepts a user’s financial profile and goals, then generates **actionable, bullet‑point‑based advice** in a **GenZ-friendly tone**.

---

## Features
- **Collects financial details**:  
  - Age  
  - Monthly Take Home (₹)  
  - Existing Loans / EMIs (₹)  
  - Additional Monthly Spends (₹)  
  - Short-term Plans (e.g., travel, gadgets)  
  - Existing Monthly Investments (₹)  
  - Financial Goal (Wealth Creation, Retirement, Tax Saving, etc.)  
  - Custom Questions
- **Generates advice in bullet points**:
  - Reality check for ambitious goals (e.g., ₹1 Cr in 2 years)  
  - Action plan with allocations & numbers  
  - Tax hacks based on **latest Indian tax laws**  
  - Quick wins for immediate action  
  - Motivational closing notes
- **GenZ tone** (uses emojis & conversational style)  
- **Multi-model fallback** to handle API rate limits:
  1. `google/gemini-2.5-pro-exp-03-25:free` – Best reasoning, newer Gemini  
  2. `openai/gpt-4o-mini` – Balanced fallback  
  3. `anthropic/claude-3-haiku` – Reliable backup
- **Spinner UI** for engaging loading state  
- Displays which model generated the response

---

## Requirements
- **Python** 3.9+
- **Streamlit**
- **Requests**

---

## Setup
1. **Clone the repository**:
   ```bash
   git clone <your_repo_url>
   cd <your_repo_folder>
   python3 -m venv venv
   source venv/bin/activate      # macOS/Linux
   ## Install Dependencies
   pip install -r requirements.txt
   ```
2. Setup Open Router API Key
```
export OPENROUTER_API_KEY="your_openrouter_key"   # macOS/Linux
```
4. Run the app
```
streamlit run simple_advisor.py
```
Then open: http://localhost:8501

## How it works
- Builds a custom prompt based on user financial details and goal
- Sends prompt to OpenRouter
- Uses fallback logic:
    - google/gemini-2.5-pro-exp-03-25:free (primary)
    - openai/gpt-4o-mini (secondary)
    - anthropic/claude-3-haiku (tertiary)
- Returns clean bullet‑point advice

Future Enhancements
- Add goal time horizon input (e.g., 1 year vs 5 years)
- Model selection dropdown in UI
- Caching & logging for analytics
   

