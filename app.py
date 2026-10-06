"""UAE Loan EMI Calculator - Streamlit UI."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import plotly.graph_objects as go
import streamlit as st

from emi_calculator.core import LOAN_TYPES, amortization_schedule, calculate_emi

st.set_page_config(page_title="UAE Loan EMI Calculator", page_icon="🏦", layout="wide")

ICONS = {"Personal Loan": "👤", "Home Loan": "🏠", "Auto Loan": "🚗"}
ACCENTS = {"Personal Loan": "#6366F1", "Home Loan": "#0F766E", "Auto Loan": "#D97706"}

# ---------------------------------------------------------------- styles
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; }

/* Page background: soft gradient + subtle dot grid + skyline glow */
.stApp {
  background:
    radial-gradient(circle at 10% 0%, rgba(15,118,110,.14) 0, transparent 40%),
    radial-gradient(circle at 95% 10%, rgba(217,119,6,.12) 0, transparent 35%),
    radial-gradient(circle at 50% 100%, rgba(99,102,241,.10) 0, transparent 45%),
    radial-gradient(rgba(15,23,42,.06) 1px, transparent 1px),
    linear-gradient(180deg, #F8FAFC 0%, #EEF3F9 100%);
  background-size: auto, auto, auto, 22px 22px, auto;
  background-attachment: fixed;
}
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.5rem; max-width: 1400px; }

/* Hero banner */
.hero {
  position: relative; overflow: hidden; text-align: center;
  padding: 2.6rem 1.5rem 2.2rem; margin-bottom: 1.8rem; border-radius: 22px;
  background: linear-gradient(120deg, #0B3B3A 0%, #0F766E 45%, #115E59 70%, #1E293B 100%);
  box-shadow: 0 18px 40px -18px rgba(15,118,110,.55);
  color: #fff;
}
.hero::before, .hero::after {
  content: ""; position: absolute; border-radius: 50%;
  background: rgba(255,255,255,.07);
}
.hero::before { width: 320px; height: 320px; top: -140px; left: -80px; }
.hero::after  { width: 420px; height: 420px; bottom: -260px; right: -120px;
                background: rgba(251,191,36,.12); }
.hero .badge {
  display: inline-block; padding: .3rem .9rem; border-radius: 999px;
  background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.25);
  font-size: .78rem; letter-spacing: .08em; text-transform: uppercase; font-weight: 600;
}
.hero h1 {
  color: #fff; font-size: 2.9rem; font-weight: 800; margin: .7rem 0 .4rem;
  letter-spacing: -.02em; line-height: 1.1; padding: 0;
}
.hero h1 span { color: #FBBF24; }
.hero p { color: rgba(255,255,255,.85); font-size: 1.05rem; margin: 0 auto; max-width: 760px; }
.hero .chips { margin-top: 1.1rem; display: flex; gap: .6rem; justify-content: center; flex-wrap: wrap; }
.hero .chip {
  background: rgba(255,255,255,.12); border-radius: 10px; padding: .45rem .8rem;
  font-size: .85rem; border: 1px solid rgba(255,255,255,.18);
}

/* Cards (bordered containers) */
div[data-testid="stVerticalBlockBorderWrapper"]:has(> div .loan-head),
div[data-testid="stVerticalBlock"]:has(> div .loan-head) {
  background: #FFFFFF;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
  background: rgba(255,255,255,.92); border-radius: 18px !important;
  border: 1px solid #E2E8F0 !important;
  box-shadow: 0 10px 30px -15px rgba(15,23,42,.25);
  transition: transform .2s ease, box-shadow .2s ease;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
  transform: translateY(-3px); box-shadow: 0 18px 38px -16px rgba(15,23,42,.32);
}
.loan-head { display: flex; align-items: center; gap: .7rem; margin-bottom: .4rem; }
.loan-head .ico {
  width: 44px; height: 44px; border-radius: 12px; display: grid; place-items: center;
  font-size: 1.4rem;
}
.loan-head h3 { margin: 0; padding: 0; font-size: 1.2rem; font-weight: 700; color: #0F172A; }
.loan-head small { color: #64748B; font-size: .78rem; }

.emi-box {
  border-radius: 14px; padding: 1rem 1.1rem; margin: .6rem 0 .8rem; color: #fff;
}
.emi-box .lbl { font-size: .78rem; opacity: .85; text-transform: uppercase; letter-spacing: .06em; }
.emi-box .val { font-size: 1.9rem; font-weight: 800; letter-spacing: -.01em; }
.stats { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: .5rem; }
.stat { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: .55rem .6rem; }
.stat .lbl { font-size: .68rem; color: #64748B; text-transform: uppercase; letter-spacing: .05em; }
.stat .val { font-size: .9rem; font-weight: 700; color: #0F172A; }

/* Section title */
.section-title { display: flex; align-items: center; gap: .6rem; margin: 2rem 0 .8rem; }
.section-title h2 { margin: 0; padding: 0; font-size: 1.5rem; font-weight: 800; color: #0F172A; }
.section-title .bar { width: 6px; height: 28px; border-radius: 4px;
  background: linear-gradient(#0F766E, #FBBF24); }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  gap: .4rem; background: #fff; padding: .35rem; border-radius: 14px;
  border: 1px solid #E2E8F0; width: fit-content;
}
.stTabs [data-baseweb="tab"] { border-radius: 10px; padding: .45rem 1.1rem; font-weight: 600; }
.stTabs [aria-selected="true"] { background: #0F766E !important; color: #fff !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

.summary-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: .8rem; margin: 1rem 0; }
.summary-row .card {
  background: #fff; border: 1px solid #E2E8F0; border-radius: 14px; padding: .9rem 1rem;
  box-shadow: 0 6px 18px -12px rgba(15,23,42,.25);
}
.summary-row .lbl { font-size: .72rem; color: #64748B; text-transform: uppercase; letter-spacing: .05em; }
.summary-row .val { font-size: 1.25rem; font-weight: 800; color: #0F172A; }

[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; border: 1px solid #E2E8F0; }
.footer { text-align: center; color: #94A3B8; font-size: .8rem; margin: 2.5rem 0 1rem; }
</style>
""", unsafe_allow_html=True)


def fmt(x: float) -> str:
    return f"AED {x:,.2f}"


def short(x: float) -> str:
    if x >= 1_000_000:
        return f"AED {x/1_000_000:,.2f}M"
    if x >= 1_000:
        return f"AED {x/1_000:,.1f}K"
    return f"AED {x:,.0f}"


# ---------------------------------------------------------------- hero
st.markdown("""
<div class="hero">
  <div class="badge">🇦🇪 Central Bank of UAE guidelines</div>
  <h1>UAE Loan <span>EMI</span> Calculator</h1>
  <p>Plan your Personal, Home and Auto loans in seconds. Adjust the amount, rate and tenure,
     then see exactly where every dirham goes, month by month.</p>
  <div class="chips">
    <div class="chip">👤 Personal · up to 48 months</div>
    <div class="chip">🚗 Auto · up to 60 months</div>
    <div class="chip">🏠 Home · up to 25 years</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------- inputs
def loan_card(key: str):
    d = LOAN_TYPES[key]
    accent = ACCENTS[key]
    st.markdown(f"""
    <div class="loan-head">
      <div class="ico" style="background:{accent}1A;">{ICONS[key]}</div>
      <div><h3>{key}</h3><small>Default tenure: {d.tenure_months} months</small></div>
    </div>""", unsafe_allow_html=True)

    amount = st.slider("Loan Amount (AED)", int(d.min_amount), int(d.max_amount),
                       int(d.amount), step=5_000, key=f"{key}_amt")
    rate = st.slider("Interest Rate (% p.a.)", 0.0, 20.0, d.rate, step=0.05, key=f"{key}_rate")
    use_default = st.toggle("Use UAE default tenure", value=True, key=f"{key}_def")
    tenure = d.tenure_months
    if not use_default:
        tenure = st.slider("Tenure (months)", 6, d.max_tenure_months, d.tenure_months,
                           step=1 if d.max_tenure_months <= 60 else 6, key=f"{key}_ten")

    emi = calculate_emi(amount, rate, tenure)
    total = emi * tenure
    st.markdown(f"""
    <div class="emi-box" style="background:linear-gradient(135deg,{accent} 0%,{accent}CC 100%);">
      <div class="lbl">Monthly EMI</div><div class="val">{fmt(emi)}</div>
    </div>
    <div class="stats">
      <div class="stat"><div class="lbl">Tenure</div><div class="val">{tenure} m</div></div>
      <div class="stat"><div class="lbl">Interest</div><div class="val">{short(total-amount)}</div></div>
      <div class="stat"><div class="lbl">Total</div><div class="val">{short(total)}</div></div>
    </div>""", unsafe_allow_html=True)
    return amount, rate, tenure, emi, total


cols = st.columns(3, gap="large")
inputs = {}
for col, key in zip(cols, LOAN_TYPES):
    with col:
        with st.container(border=True):
            inputs[key] = loan_card(key)

# ---------------------------------------------------------------- schedule
st.markdown('<div class="section-title"><div class="bar"></div><h2>Amortization Schedule</h2></div>',
            unsafe_allow_html=True)

tabs = st.tabs([f"{ICONS[k]}  {k}" for k in LOAN_TYPES])
for tab, key in zip(tabs, LOAN_TYPES):
    with tab:
        amount, rate, tenure, emi, total = inputs[key]
        df = amortization_schedule(amount, rate, tenure, key)
        accent = ACCENTS[key]

        st.markdown(f"""
        <div class="summary-row">
          <div class="card"><div class="lbl">Principal</div><div class="val">{fmt(amount)}</div></div>
          <div class="card"><div class="lbl">Monthly EMI</div><div class="val" style="color:{accent}">{fmt(emi)}</div></div>
          <div class="card"><div class="lbl">Total Interest</div><div class="val">{fmt(total-amount)}</div></div>
          <div class="card"><div class="lbl">Total Payable</div><div class="val">{fmt(total)}</div></div>
        </div>""", unsafe_allow_html=True)

        with st.container(border=True):
            c1, c2 = st.columns([2.2, 1])
            with c1:
                fig = go.Figure()
                fig.add_bar(x=df["Month"], y=df["Principal Paid (AED)"], name="Principal",
                            marker_color=accent)
                fig.add_bar(x=df["Month"], y=df["Interest Paid (AED)"], name="Interest",
                            marker_color="#FBBF24")
                fig.add_scatter(x=df["Month"], y=df["Left-over Principal (AED)"],
                                name="Left-over Principal", yaxis="y2", mode="lines",
                                line=dict(color="#0F172A", width=2.5))
                fig.update_layout(
                    barmode="stack", height=360, margin=dict(t=20, b=10, l=10, r=10),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter"),
                    xaxis=dict(title="Month", gridcolor="#EEF2F7"),
                    yaxis=dict(title="Monthly split (AED)", gridcolor="#EEF2F7"),
                    yaxis2=dict(title="Balance (AED)", overlaying="y", side="right", showgrid=False),
                    legend=dict(orientation="h", y=1.12, x=0),
                )
                st.plotly_chart(fig, width="stretch", key=f"{key}_bar")
            with c2:
                donut = go.Figure(go.Pie(
                    labels=["Principal", "Interest"], values=[amount, max(total - amount, 0)],
                    hole=.68, marker=dict(colors=[accent, "#FBBF24"]), textinfo="percent",
                    sort=False))
                donut.update_layout(
                    height=360, margin=dict(t=20, b=10, l=10, r=10), showlegend=True,
                    legend=dict(orientation="h", y=-0.05), paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter"),
                    annotations=[dict(text=f"<b>{short(total)}</b><br>Total", showarrow=False,
                                      font=dict(size=15))])
                st.plotly_chart(donut, width="stretch", key=f"{key}_pie")

        st.dataframe(df, hide_index=True, width="stretch", height=430,
                     column_config={c: st.column_config.NumberColumn(format="%.2f")
                                    for c in df.columns if c != "Month"})
        st.download_button("⬇️  Download schedule (CSV)", df.to_csv(index=False),
                           file_name=f"{key.replace(' ', '_').lower()}_schedule.csv",
                           key=f"{key}_dl", type="primary")

st.markdown('<div class="footer">Rates shown are indicative only. Actual EMI depends on your bank\'s '
            'offer, fees and eligibility.</div>', unsafe_allow_html=True)
