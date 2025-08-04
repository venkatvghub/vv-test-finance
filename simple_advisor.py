import streamlit as st
import os
import requests
import json
import time

# =====================
# OpenRouter Configuration
# =====================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    st.error("OpenRouter API Key not found. Set OPENROUTER_API_KEY as an environment variable.")
    st.stop()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Primary and fallback models
MODEL_LIST = [
    "google/gemini-2.5-pro-exp-03-25:free",  # Best reasoning, newer Gemini
    "openai/gpt-4o-mini"                    # Balanced fallback
    "anthropic/claude-3-haiku"
]

# =====================
# Prompt Builder (unchanged)
# =====================
def build_prompt(age, income, loans, investments, additional_spends, short_term_plans, goal, user_query=None):
    context = f"""
You are an experienced Indian financial advisor.

User's financial profile:
- Age: {age}
- Monthly take-home: {income if income else "None"}
- Existing loans/EMIs: {loans if loans else "None"}
- Existing monthly investments: {investments if investments else "None"}
- Additional Monthly Spends: {additional_spends if additional_spends else "None"}
- Short Term Plans: {short_term_plans if short_term_plans else "None"}
- Financial goal: {goal}

Your task:
1. Understand the user's financial situation and goal (goal may be short-term, long-term, or ambitious).
2. If the goal is ambitious or time-bound (like “₹1 crore in 2 years”), include a **Reality Check** that covers feasibility and tradeoffs.
3. Build a **custom strategy** based on their profile and goal:
   - If short-term → focus on high-impact, aggressive moves, extra income ideas, or reallocating current funds.
   - If long-term → focus on stable, diversified growth, risk-adjusted strategies, and disciplined saving.
   - Work with existing data
4. Always provide **actionable, concise bullet points** (not essays). Max 20 bullet points.
5. Dont suggest, unless asked on other options around additional income sources/ideas like freelancing etc
6. Suggest strictly options available and regulated within india. In case of platforms, use from Indian content only
7. **Avoid generic investment ideas - be prescriptive with the right numbers (post taxation)**
8. **Refer to latest indian taxation laws if needed, instead of general suggestions like Check on taxation**

Your output must be structured as:
- **Understanding (2–3 bullets)** – summary of profile & goal.
- **Reality Check (if needed, 1–2 bullets)** – whether the goal is realistic and tradeoffs required.
- **Action Plan (5–7 bullets)** – investment allocation, expense optimization. Provide a growth table if possible pre and post tax for every suggestion.
- **Tax Hacks (2–3 bullets)** – quick, relevant tax optimization steps based on latest taxation norms.
- **Quick Wins (2–3 bullets)** – things user can start this week.
- **Closing Note (1–2 bullets)** – motivational and goal-aligned.
- **Summarize the above in table format wherever possible**

Style:
- Conversational, GenZ-friendly (emojis welcome like 💰🔥📈).
- Use **bullet points only**, no long paragraphs.
- Do NOT include “consult a financial advisor” disclaimers.

User Question: {user_query if user_query else "Provide a personalized financial plan"}
"""
    return context

def build_prompt1(age, income, loans, investments, additional_spends, short_term_plans, goal, user_query=None):
    context = f"""
You are an experienced Indian financial advisor.
User's financial profile:
- Age: {age}
- Monthly take-home: {income if income else "None"}
- Existing loans/EMIs: {loans if loans else "None"}
- Existing monthly investments: {investments if investments else "None"}
- Additional Monthly Spends: {additional_spends if additional_spends else "None"}
- Short Term Plans: {short_term_plans if short_term_plans else "None"}
- Financial goal: {goal}

You are a smart, energetic financial advisor who speaks like a GenZ-friendly money coach.
Your job is to:
1. Understand the user’s financial situation (age, monthly income, existing loans/EMIs, current investments, and spending habits).
2. Understand their short-term and long-term financial goals (like buying a house, FIRE, tax saving, early retirement, wealth creation, etc.).
3. Based on their profile, create a **personalized money plan** that:
   - Explains their risk profile in **1-2 simple bullet points**.
   - Suggests an **actionable investment strategy** (Mutual Funds, SIPs, Stocks, Insurance, Tax saving, EPF, NPS, PPF, UPI-linked savings, Gold, Crypto if relevant) in **bullet points** with approximate percentages.
   - Shows a **monthly allocation split** for Expenses, Debt, and Investments in **bullet points**.
   - Highlights relevant **tax hacks & government schemes** in **3-4 quick bullet points**.
   - Reviews short-term goals and suggests optimization.
   - Suggests **2–3 quick wins** for this week.
4. Make it conversational and motivational – no boring textbook finance talk.
5. Use **concise bullet points only** (no long paragraphs), use **emojis naturally (💰📈🔥)**, and keep output **under 20 bullet points total**.
6. Work with given data and supplement with relevant advice beyond what’s provided. Dont suggest "Consult a tax advisor or any external party - you are the experienced advisor"
7. If the goal is very ambitious/impractical (like “₹1 crore in 2 years”), include a **Reality Check** section with alternative paths.

Tone & Style:
- Simple, conversational, GenZ-friendly (e.g., “Treat your SIP like your Netflix subscription – but one that pays you back”)
- Be concise and impactful.
- Avoid generic disclaimers like “I’m not a financial advisor” but subtly encourage professional consultation.

Your output structure:
- **Understanding (2–3 bullets)**
- **Risk Profile (1–2 bullets)**
- **Action Plan (5–7 bullets)**
- **Tax Hacks (3–4 bullets)**
- **Quick Wins (2–3 bullets)**
- **Closing Note (1–2 short bullets)**

User Question: {user_query if user_query else "Provide a personalized financial plan"}
"""
    return context

# =====================
# OpenRouter Call with Retry & Fallback
# =====================
def get_financial_advice(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Indian Financial Advisor Bot",
    }

    for model in MODEL_LIST:
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a financial advisor specialized in Indian financial markets."},
                {"role": "user", "content": prompt},
            ],
        }

        for attempt in range(3):  # Retry 3 times for each model
            response = requests.post(
                OPENROUTER_URL, headers=headers, data=json.dumps(data), verify=False
            )

            if response.status_code == 200:
                result = response.json()
                advice = result["choices"][0]["message"]["content"]
                return advice, model  # return content and model used
            elif response.status_code == 429:
                time.sleep(2 ** attempt)  # exponential backoff
                continue
            else:
                break  # some other error, try next model

    return f"Error: {response.status_code} - {response.text}", None

# =====================
# Streamlit UI
# =====================
st.title("💰 Goal-based Indian Financial Advisor (OpenRouter)")

# Inputs
age = st.number_input("Your Age", min_value=18, max_value=100, step=1)
monthly_income = st.text_area("Monthly Take Home in Rs(₹)", placeholder="e.g., 5L")
loans = st.text_area("Existing Loans / EMIs in Rs(per month)", placeholder="e.g., Home Loan 1L, EMI(Car Loan) 7k")
additional_spends = st.text_area("Additional Monthly Spends", placeholder="e.g. Party 20k")
short_term_plans = st.text_area("Short Term Plans", placeholder="e.g. Trip to Spain in 6 months worth 2L")
investments = st.text_area("Existing Monthly Investments Rs(₹)", placeholder="SIP: 20k, FD:5k")
goal = st.selectbox(
    "Select Your Financial Goal",
    ["Retirement Planning", "Tax Saving", "Buying a House", "Emergency Fund", "Child Education", "Wealth Creation"]
)
user_message = st.text_input("Any specific question?", placeholder="e.g., Should I increase SIP in equity funds?")

if st.button("Generate Advice"):
    with st.spinner("Crunching numbers and crafting your financial plan... 🔄💸"):
        prompt = build_prompt(age, monthly_income, loans, investments, additional_spends, short_term_plans, goal, user_message)
        advice, model_used = get_financial_advice(prompt)

    st.markdown("### Personalized Financial Advice")
    st.markdown(advice)
    if model_used:
        st.caption(f"Model used: **{model_used}**")
