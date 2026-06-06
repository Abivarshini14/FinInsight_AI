import streamlit as st
import google.generativeai as genai
import plotly.graph_objects as go
import time  # Added for the retry delay

# ----------------------------
# 1. API CONFIGURATION
# ----------------------------
st.set_page_config(page_title="FinInsight AI", page_icon="💰", layout="wide")

# Replace with your actual API Key
GENAI_API_KEY = "AIzaSyDgmreQDHRHhE114qDsCls5ZQLbXDbRiyI"
genai.configure(api_key=GENAI_API_KEY)

# This function prevents the 404 error by finding the best available model
@st.cache_resource
def get_best_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Check for 1.5 flash or pro as 2.5 flash is currently very restricted on free tier
        if 'models/gemini-1.5-flash' in available_models:
            return genai.GenerativeModel('gemini-1.5-flash')
        elif 'models/gemini-pro' in available_models:
            return genai.GenerativeModel('gemini-pro')
        else:
            return genai.GenerativeModel(available_models[0].split('/')[-1])
    except:
        # Fallback if list_models fails
        return genai.GenerativeModel('gemini-1.5-flash')

model = get_best_model()

def get_ai_response(user_query):
    system_prompt = f"""
    You are 'FinInsight AI', a professional financial advisor.
    Answer accurately, keep it professional, and use bullet points for clarity.
    If the question is not about finance, money, or investing, politely redirect.
    
    User Question: {user_query}
    """
    
    # ✅ FIX: Retry logic for 429 Quota Error
    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = model.generate_content(system_prompt)
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                if attempt < max_retries - 1:
                    time.sleep(12)  # Wait for the quota window to reset
                    continue
                else:
                    return "⚠️ API Quota exceeded. Please wait about 30 seconds and try again."
            return f"⚠️ API Error: {error_msg}. Please check settings."

# ----------------------------
# 2. SIDEBAR NAVIGATION
# ----------------------------
st.sidebar.title("📌 FinInsight Menu")
page = st.sidebar.radio("Go to", [
    "🏠 Dashboard", 
    "🤖 AI Financial Bot", 
    "🧮 Calculators", 
    "📊 Budget Visualizer"
])

# ----------------------------
# 3. PAGE: DASHBOARD (UNIQUE VERSION)
# ----------------------------
if page == "🏠 Dashboard":
    st.markdown("<h1 style='text-align: center; color: #00C9A7;'>🚀 FinInsight Command Center</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Welcome! Let's track your financial health in real-time.</p>", unsafe_allow_html=True)
    st.divider()

    col_input, col_gauge = st.columns([1, 1.2])

    with col_input:
        st.subheader("📊 Financial Inputs")
        income = st.number_input("Monthly Income (₹)", value=50000, step=1000)
        expenses = st.number_input("Monthly Expenses (₹)", value=30000, step=1000)
        
        savings = income - expenses
        savings_rate = (savings / income) * 100 if income > 0 else 0

        st.write("---")
        st.metric("Total Income", f"₹{income}")
        st.metric("Total Expenses", f"₹{expenses}", delta=f"{(expenses/income)*100:.1f}% Use", delta_color="inverse")
        st.metric("Net Savings", f"₹{savings}", delta=f"{savings_rate:.1f}% Rate")

    with col_gauge:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = savings_rate,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Savings Health Score", 'font': {'size': 20}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': "#00C9A7"},
                'bgcolor': "white",
                'steps': [
                    {'range': [0, 20], 'color': "#FF6B6B"},
                    {'range': [20, 45], 'color': "#FFD93D"},
                    {'range': [45, 100], 'color': "#6BCB77"}],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': 20}}))
        
        fig.update_layout(height=400, margin=dict(t=80, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info(f"**Emergency Fund Target**\n\nAim for ₹{expenses * 6} (6 months of expenses).")
    with c2:
        if savings_rate < 20:
            st.warning("**Savings Warning**\n\nYour rate is below 20%. Try reducing 'Wants' spending.")
        else:
            st.success("**Great Progress!**\n\nYour savings rate is excellent. Keep investing!")
    with c3:
        st.info("**Investment Tip**\n\nAt 12% annual return, your money doubles roughly every 6 years.")

# ----------------------------
# 4. PAGE: AI BOT
# ----------------------------
elif page == "🤖 AI Financial Bot":
    st.title("🤖 AI Financial Expert")
    st.write("Ask me about Stocks, Taxes, SIPs, or Budgeting rules.")
    
    user_input = st.text_input("Enter your financial query:", placeholder="e.g., How should I invest ₹10,000 per month?")

    if user_input:
        with st.spinner("Analyzing data..."):
            answer = get_ai_response(user_input)
            st.markdown("### 🤖 Response")
            st.info(answer)

# ----------------------------
# 5. PAGE: CALCULATORS
# ----------------------------
elif page == "🧮 Calculators":
    st.title("🧮 Finance Calculators")
    c1, c2 = st.tabs(["SIP (Wealth)", "EMI (Loan)"])

    with c1:
        amt = st.number_input("Monthly SIP Amount", value=5000)
        ret = st.number_input("Expected Return (%)", value=12.0)
        time_period = st.slider("Years", 1, 30, 10)
        if st.button("Calculate Wealth"):
            i = (ret/100)/12
            n = time_period * 12
            fv = amt * (((1+i)**n - 1)/i) * (1+i)
            st.success(f"Estimated Future Value: ₹{round(fv, 2)}")

    with c2:
        loan = st.number_input("Loan Amount", value=100000)
        rate = st.number_input("Interest Rate (%)", value=10.0)
        yrs = st.slider("Loan Tenure (Years)", 1, 30, 5)
        if st.button("Calculate EMI"):
            r = (rate/100)/12
            n = yrs * 12
            emi = (loan * r * (1+r)**n) / ((1+r)**n - 1)
            st.success(f"Monthly EMI: ₹{round(emi, 2)}")

# ----------------------------
# 6. PAGE: BUDGET VISUALIZER
# ----------------------------
elif page == "📊 Budget Visualizer":
    st.title("📊 Expense Breakdown")
    
    col_a, col_b = st.columns([1, 1])
    with col_a:
        rent = st.number_input("Rent/EMI", value=15000)
        food = st.number_input("Food", value=8000)
        bills = st.number_input("Bills", value=5000)
        other = st.number_input("Other Expenses", value=4000)
        
    with col_b:
        labels = ['Rent', 'Food', 'Bills', 'Other']
        values = [rent, food, bills, other]
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
        fig.update_layout(title_text="Visual Spending Chart")
        st.plotly_chart(fig, use_container_width=True)