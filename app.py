import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

try:
    from streamlit_autorefresh import st_autorefresh
    has_autorefresh = True
except ImportError:
    has_autorefresh = False

st.set_page_config(page_title="مرصد السيولة والتحليل المؤسسي (Sahm Pro)", layout="wide")

st.markdown("""
    <h1 style='text-align: center;'>🚀 مرصد السيولة والتحليل المؤسسي للأسهم السعودية (Sahm Pro - Master Edition)</h1>
    <p style='text-align: center;'>الإصدار المطور: تجميع الصناديق، مصائد السيولة (Spring)، وفلتر أسهم الزخم العالي (High-Beta).</p>
""", unsafe_allow_html=True)

st.sidebar.header("⚙️ إعدادات المنصة وإدارة المخاطر")
app_mode = st.sidebar.selectbox("اختر وضع التشغيل", [
    "🏛️ رصد التجميع المؤسسي المطور (Filtered Accumulation)",
    "🌐 مرصد السوق اللحظي المباشر (Daily Scanner)", 
    "⚡ راصد الفريمات الصغيرة للمضاربة اليومية (Scalping Scanner)",
    "📊 اختبار خلفي فردي (Single Stock Backtest)",
    "🏛️📊 اختبار خلفي لاستراتيجية التجميع ومصائد السيولة (Accumulation & Spring Backtest)",
    "🌐📊 اختبار خلفي شامل لكل السوق (Portfolio Institutional Backtest)"
], index=0)

api_key = st.sidebar.text_input("Sahm Pro API مفتاح اشتراك", type="password")

st.sidebar.markdown("---")
st.sidebar.subheader("🔄 إعدادات التحديث اللحظي التلقائي")
enable_live_refresh = st.
