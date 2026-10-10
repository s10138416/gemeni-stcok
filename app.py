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
    <p style='text-align: center;'>الإصدار المحسّن: تجميع الصناديق، مصائد السيولة (Spring)، ومضاعفات إدارة مخاطر متوازنة.</p>
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
enable_live_refresh = st.sidebar.checkbox("تفعيل التحديث اللحظي التلقائي أثناء الجلسة", value=True)
refresh_interval_sec = st.sidebar.slider("فترة التحديث اللحظي (بالثواني)", min_value=10, max_value=60, value=20, step=5)

if enable_live_refresh and has_autorefresh:
    st_autorefresh(interval=refresh_interval_sec * 1000, key="sahm_live_updater")
elif enable_live_refresh and not has_autorefresh:
    st.sidebar.warning("⚠️ مكتبة التحديث التلقائي غير مثبتة.")

st.sidebar.markdown("---")
st.sidebar.subheader("⏱️ إعدادات الفريمات الصغيرة (للمضاربة السريعة)")
scalp_interval = st.sidebar.selectbox("اختر الفريم الزمني للمضاربة", ["5m", "15m", "30m", "60m"], index=1)

st.sidebar.markdown("---")
st.sidebar.subheader("💰 إدارة المخاطر ووقف الخسارة المتحرك المشروط")
total_capital = st.sidebar.number_input("إجمالي رأس المال (ريال سعودي)", min_value=1000, max_value=10000000, value=50000, step=5000)
risk_percentage = st.sidebar.slider("نسبة المخاطرة المقبولة لكل صفقة (%)", min_value=0.5, max_value=3.0, value=1.0, step=0.5)

enable_trailing = st.sidebar.checkbox("تفعيل وقف الخسارة المتحرك المشروط", value=True)
trailing_atr_mult = st.sidebar.slider("مضاعف وقف الخسارة المتحرك (ATR)", min_value=0.5, max_value=3.0, value=2.0, step=0.1)

st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ معايير تصفية الإشارات الوهمية والذكية (المحسنة)")
vol_threshold = st.sidebar.slider("عتبة تضخم الحجوم المطورة", min_value=1.2, max_value=3.0, value=1.8, step=0.1)
min_rsi_filter = st.sidebar.slider("الحد الأدنى لمؤشر الزخم (RSI)", min_value=45, max_value=60, value=50, step=1)
min_acc_score = st.slider("مستوى مؤشر التجميع الأدنى للمسح والاختبار (%)", 50, 95, 80)
sl_multiplier = st.sidebar.slider("مضاعف وقف الخسارة الابتدائي (ATR)", min_value=0.8, max_value=2.5, value=1.5, step=0.1)
target_multiplier = st.sidebar.slider("مضاعف الهدف (تم تعديله لسرعة التحقق)", min_value=1.5, max_value=4.0, value=2.2, step=0.1)

stocks_dict = {
    "أرامكو السعودية (2222)": 2222, "أديس القابضة (2382)": 2382, "مصرف الراجحي (1120)": 1120,
    "البنك الأهلي السعودي (1180)": 1180, "مصرف الإنماء (1150)": 1150, "بنك الرياض (1010)": 1010,
    "البنك السعودي الأول (1060)": 1060, "بنك الجزيرة (1020)": 1020, "مصرف البلاد (1140)": 1140,
    "البنك السعودي الفرنسي (1050)": 1050, "سابك (2010)": 2010, "معادن (1211)": 1211,
    "سابك للمغذيات الزراعية (2020)": 2020, "ينساب (2290)": 2290, "سبكيم العالمية (2310)": 2310,
    "كيان السعودية (2350)": 2350, "الاتصالات السعودية STC (7010)": 7010, "موبايلي (7020)": 7020,
    "زين السعودية (7030)": 7030, "الكهرباء السعودية (5110)": 5110, "اكوا باور (2082)": 2082,
    "مرافقي (2083)": 2083, "أسواق العثيم (4001)": 4001, "مكتبة جرير (4190)": 4190,
    "إكسترا (4003)": 4003, "مجموعة الدكتور سليمان الحبيب (4013)": 4013, "المواساة (4002)": 4002,
    "دلة الصحية (4004)": 4004, "دار الأركان (4300)": 4300, "جبل عمر (4250)": 4250
}

if 'bt_results_df' not in st.session_state:
    st.session_state['bt_results_df'] = None
    st.session_state['bt_metrics'] = None

if 'acc_bt_results' not in st.session_state:
    st.session_state['acc_bt_results'] = None
    st.session_state['acc_bt_metrics'] = None

if 'portfolio_bt_df' not in st.session_state:
    st.session_state['portfolio_bt_df'] = None
    st.session_state['portfolio_metrics'] = None

if app_mode == "🏛️ رصد التجميع المؤسسي المطور (Filtered Accumulation)":
    st.subheader("🏛️ رصد التجميع المؤسسي المطور ومصائد السيولة (الفرص الحية)")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.info(f"مستوى التجميع الأدنى الحالي: {min_acc_score}% (معايير محسنة)")
    with col_f2:
        only_winners = st.checkbox("🟢 فلترة: عرض الأسهم ذات الزخم الإيجابي فقط", value=True)
    run_inst_scan = st.button("تشغيل المسح المؤسسي الحي الآن", type="primary")
    if run_inst_scan or enable_live_refresh:
        with st.spinner("جاري فحص السيولة وتكتيكات المضارب الكبير (Spring & VWAP)..."):
            inst_results = []
            for name, code in stocks_dict.items():
                try:
                    df_i = yf.download(f"{code}.SR", period="2mo", interval="1d", progress=False)
                    if not df_i.empty and len(df_i) > 30:
                        if isinstance(df_i.columns, pd.MultiIndex):
                            df_i.columns = df_i.columns.get_level_values(0)
                        curr_price = float(df_i['Close'].iloc[-1])
                        prev_price = float(df_i['Close'].iloc[-2])
                        change_pct = ((curr_price - prev_price) / prev_price) * 100
                        df_i['SMA50'] = df_i['Close'].rolling(window=50).mean()
                        df_i['OBV'] = (np.sign(df_i['Close'].diff()) * df_i['Volume']).fillna(0).cumsum()
                        df_i['OBV_Slope'] = df_i['OBV'].diff(3)
                        delta = df_i['Close'].diff()
                        rs = delta.clip(lower=0).rolling(14).mean() / (-delta.clip(upper=0)).rolling(14).mean()
                        df_i['RSI'] = 100 - (100 / (1 + rs))
                        
                        is_spring = (df_i['Low'].iloc[-1] < df_i['Low'].rolling(10).min().shift(1).iloc[-1]) and (curr_price > float(df_i['Open'].iloc[-1]))
                        min_idx = df_i['Low'].iloc[-20:].idxmin()
                        sub_df = df_i.loc[min_idx:]
                        tp = (sub_df['High'] + sub_df['Low'] + sub_df['Close']) / 3
                        avwap = float((tp * sub_df['Volume']).sum() / sub_df['Volume'].sum()) if sub_df['Volume'].sum() > 0 else curr_price

                        rsi_val = float(df_i['RSI'].iloc[-1])
                        sma50_val = float(df_i['SMA50'].iloc[-1]) if not pd.isna(df_i['SMA50'].iloc[-1]) else curr_price
                        
                        if curr_price > sma50_val and rsi_val >= min_rsi_filter:
                            vol_mean = df_i['Volume'].rolling(window=15).mean().iloc[-1]
                            recent_vol = df_i['Volume'].iloc[-1]
                            base_score = 50 + (float(df_i['OBV_Slope'].iloc[-1]) / (vol_mean + 1)) * 10 + (recent_vol / vol_mean) * 10
                            if is_spring:
                                base_score += 15.0
                            acc_score = round(min(max(base_score, 45), 98.5), 1)
                            
                            inst_results.append({
                                "الرمز والشركة": name, "السعر الحالي": round(curr_price, 2),
                                "التغير (%)": round(change_pct, 2), "مؤشر RSI": round(rsi_val, 1),
                                "مؤشر التكلفة AVWAP": round(avwap, 2),
                                "مؤشر التجميع (%)": acc_score,
                                "الحالة المؤسسية": "تجميع احترافي + مصيدة 🟢🔥" if is_spring else ("تجميع مؤسسي مؤكد 🟢🟢" if acc_score >= 82 else "تراكم سيولة ذكية 🟢")
                            })
                except Exception:
                    continue
            df_inst = pd.DataFrame(inst_results)
            if not df_inst.empty:
                df_inst = df_inst[df_inst["مؤشر التجميع (%)"] >= min_acc_score]
                if only_winners:
                    df_inst = df_inst[df_inst["التغير (%)"] > 0]
                df_inst = df_inst.sort_values(by="مؤشر التجميع (%)", ascending=False)
                st.dataframe(df_inst, use_container_width=True)
            else:
                st.info("⚠️ لا توجد نتائج مطابقة لشروط التجميع الحالية.")

elif app_mode == "🌐 مرصد السوق اللحظي المباشر (Daily Scanner)":
    st.subheader("🌐 مرصد السوق اليومي المباشر")
    run_live_alerts = st.button("تشغيل الماسح اليومي الآن", type="primary")
    if run_live_alerts or enable_live_refresh:
        risk_amount = total_capital * (risk_percentage / 100.0)
        alert_results = []
        for name, code in stocks_dict.items():
            try:
                df_live = yf.download(f"{code}.SR", period="1mo", interval="1d", progress=False)
                if not df_live.empty:
                    if isinstance(df_live.columns, pd.MultiIndex):
                        df_live.columns = df_live.columns.get_level_values(0)
                    current_price = float(df_live['Close'].iloc[-1])
                    df_live['SMA50'] = df_live['Close'].rolling(window=50).mean()
                    prev_high = float(df_live['High'].iloc[-2])
                    prev_volume = float(df_live['Volume'].iloc[-2])
                    avg_volume = float(df_live['Volume'].rolling(window=20).mean().iloc[-1])
                    sma50_val = float(df_live['SMA50'].iloc[-1]) if not pd.isna(df_live['SMA50'].iloc[-1]) else current_price
                    atr = current_price * 0.025
                    if (prev_volume > (vol_threshold * avg_volume)) and (current_price > sma50_val):
                        optimal_entry = round(prev_high + 0.02, 2)
                        stop_loss = round(optimal_entry - (sl_multiplier * atr), 2)
                        target = round(optimal_entry + (target_multiplier * atr), 2)
                        shares = int(risk_amount / (optimal_entry - stop_loss)) if optimal_entry > stop_loss else 0
                        alert_results.append({
                            "السهم": name, "السعر الحالي": round(current_price, 2), "سعر الزناد": optimal_entry,
                            "وقف الخسارة": stop_loss, "الهدف": target, "الأسهم المقترحة": shares
                        })
            except Exception:
                continue
        df_alerts = pd.DataFrame(alert_results)
        if not df_alerts.empty:
            st.dataframe(df_alerts, use_container_width=True)
        else:
            st.info("⚠️ لا توجد صفقات مطابقة حالياً.")

elif app_mode == "⚡ راصد الفريمات الصغيرة للمضاربة اليومية (Scalping Scanner)":
    st.subheader(f"⚡ راصد الفريمات الصغيرة ({scalp_interval}) للمضاربة اليومية السريعة")
    run_scalp = st.button("تشغيل راصد المضاربة اللحظية الآن", type="primary")
    if run_scalp or enable_live_refresh:
        risk_amount = total_capital * (risk_percentage / 100.0)
        scalp_results = []
        for name, code in stocks_dict.items():
            try:
                df_s = yf.download(f"{code}.SR", period="5d", interval=scalp_interval, progress=False)
                if not df_s.empty and len(df_s) > 20:
                    if isinstance(df_s.columns, pd.MultiIndex):
                        df_s.columns = df_s.columns.get_level_values(0)
                    df_s['EMA9'] = df_s['Close'].ewm(span=9, adjust=False).mean()
                    df_s['Vol_MA'] = df_s['Volume'].rolling(window=15).mean()
                    df_s['ATR'] = (df_s['High'] - df_s['Low']).rolling(window=14).mean()
                    cur_price = float(df_s['Close'].iloc[-1])
                    cur_vol = float(df_s['Volume'].iloc[-1])
                    avg_vol = float(df_s['Vol_MA'].iloc[-1])
                    ema9_val = float(df_s['EMA9'].iloc[-1])
                    cur_atr = float(df_s['ATR'].iloc[-1]) if not pd.isna(df_s['ATR'].iloc[-1]) else (cur_price * 0.01)
                    if (cur_vol > (vol_threshold * avg_vol)) and (cur_price > ema9_val):
                        trigger = round(float(df_s['High'].iloc[-2]) + 0.02, 2)
                        stop_loss = round(trigger - (sl_multiplier * cur_atr), 2)
                        target = round(trigger + (target_multiplier * cur_atr), 2)
                        shares = int(risk_amount / (trigger - stop_loss)) if trigger > stop_loss else 0
                        scalp_results.append({
                            "السهم": name, "السعر اللحظي": round(cur_price, 2), "سعر الزناد": trigger,
                            "وقف الخسارة": stop_loss, "الهدف": target, "الكمية المقترحة": shares
                        })
            except Exception:
                continue
        df_scalp = pd.DataFrame(scalp_results)
        if not df_scalp.empty:
            st.dataframe(df_scalp, use_container_width=True)
        else:
            st.info(f"⚠️ لا توجد فرص سكالبينغ على الفريم ({scalp_interval}) حالياً.")

elif app_mode == "📊 اختبار خلفي فردي (Single Stock Backtest)":
    st.subheader("📊 اختبار خلفي فردي مع وقف خسارة متحرك مشروط (Single Stock Backtest)")
    col_c1, col_c2, col_c3 = st.columns([2, 2, 1])
    with col_c1:
        bt_stock_name = st.selectbox("اختر السهم للاختبار", list(stocks_dict.keys()))
    with col_c2:
        period_label = st.selectbox("فترة الاختبار التاريخي", ["6 أشهر", "سنة كاملة", "سنتان"])
        selected_period = {"6 أشهر": "6mo", "سنة كاملة": "1y", "سنتان": "2y"}[period_label]
    with col_c3:
        st.markdown("<br>", unsafe_allow_html=True)
        run_backtest = st.button("تشغيل الاختبار الفردي", type="primary")
    
    bt_code = stocks_dict[bt_stock_name]

    if run_backtest:
        with st.spinner("جاري تشغيل الاختبار الفردي للسهم..."):
            try:
                df = yf.download(f"{bt_code}.SR", period=selected_period, interval="1d", progress=False)
                if not df.empty and len(df) > 50:
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    df['SMA50'] = df['Close'].rolling(window=50).mean()
                    df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
                    df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
                    df['OBV_Slope'] = df['OBV'].diff(3)
                    rs = df['Close'].diff().clip(lower=0).rolling(14).mean() / (-df['Close'].diff().clip(upper=0)).rolling(14).mean()
                    df['RSI'] = 100 - (100 / (1 + rs))
                    df['ATR'] = (df['High'] - df['Low']).rolling(window=14).mean()
                    df['Signal'] = np.where((df['OBV_Slope'] > 0) & (df['Volume'] > vol_threshold * df['Volume_MA']) & (df['Close'] > df['SMA50']) & (df['RSI'] >= min_rsi_filter), 1, 0)
                    
                    trades, in_pos, entry_p, sl, target_p, highest, e_date = [], False, 0, 0, 0, 0, ""
                    for i in range(50, len(df) - 5):
                        if not in_pos and df['Signal'].iloc[i] == 1:
                            trigger_price = round(float(df['High'].iloc[i]) + 0.02, 2)
                            for offset in range(1, 4):
                                if i + offset < len(df):
                                    if float(df['High'].iloc[i+offset]) >= trigger_price:
                                        e_date = str(df.index[i+offset]).split()[0]
                                        entry_p = trigger_price
                                        c_atr = float(df['ATR'].iloc[i]) or (entry_p * 0.01)
                                        sl = round(entry_p - (sl_multiplier * c_atr), 2)
                                        target_p = round(entry_p + (target_multiplier * c_atr), 2)
                                        highest = entry_p
                                        in_pos = True
                                        break
                        elif in_pos:
                            h_p, l_p, c_atr = float(df['High'].iloc[i]), float(df['Low'].iloc[i]), float(df['ATR'].iloc[i]) or (entry_p * 0.01)
                            if enable_trailing and h_p > entry_p + (1.0 * c_atr) and h_p > highest:
                                highest = h_p
                                new_sl = round(highest - (trailing_atr_mult * c_atr), 2)
                                if new_sl > sl: sl = new_sl
                            if h_p >= target_p:
                                trades.append({"السهم": bt_stock_name, "تاريخ الدخول": e_date, "سعر الدخول": entry_p, "النتيجة": "ربح 🟢", "العائد (%)": round(((target_p - entry_p) / entry_p) * 100, 2)})
                                in_pos = False
                            elif l_p <= sl:
                                trades.append({"السهم": bt_stock_name, "تاريخ الدخول": e_date, "سعر الدخول": entry_p, "النتيجة": "خسارة 🔴", "العائد (%)": round(((sl - entry_p) / entry_p) * 100, 2)})
                                in_pos = False
                            elif i == len(df) - 6:
                                final_c = float(df['Close'].iloc[i])
                                trades.append({"السهم": bt_stock_name, "تاريخ الدخول": e_date, "سعر الدخول": entry_p, "النتيجة": "ربح 🟢" if final_c > entry_p else "خسارة 🔴", "العائد (%)": round(((final_c - entry_p) / entry_p) * 100, 2)})
                                in_pos = False
                    
                    df_t = pd.DataFrame(trades)
                    if not df_t.empty:
                        w_t = len(df_t[df_t['النتيجة'].str.contains("ربح")])
                        wr = w_t / len(df_t)
                        exp = (wr * df_t[df_t['النتيجة'].str.contains("ربح")]['العائد (%)'].mean()) - ((1 - wr) * abs(df_t[df_t['النتيجة'] == "خسارة 🔴"]['العائد (%)'].mean()))
                        st.session_state['bt_results_df'] = df_t
                        st.session_state['bt_metrics'] = (len(df_t), wr, exp)
                    else:
                        st.session_state['bt_results_df'] = pd.DataFrame()
            except Exception as e:
                st.error(f"خطأ: {e}")

    if st.session_state['bt_results_df'] is not None and not st.session_state['bt_results_df'].empty:
        tot, wr, exp = st.session_state['bt_metrics']
        m1, m2, m3 = st.columns(3)
        m1.metric("إجمالي الصفقات", tot)
        m2.metric("معدل النجاح", f"{round(wr * 100, 1)}%")
        m3.metric("العائد المتوقع", f"{round(exp, 2)}%")
        st.download_button("📥 تحميل السجل (Excel/CSV)", st.session_state['bt_results_df'].to_csv(index=False).encode('utf-8-sig'), "trades.csv", "text/csv")
        st.dataframe(st.session_state['bt_results_df'], use_container_width=True)
    elif st.session_state['bt_results_df'] is not None and st.session_state['bt_results_df'].empty:
        st.warning("⚠️ لا توجد صفقات مطابقة لهذا السهم في الفترة المحددة.")

elif app_mode == "🏛️📊 اختبار خلفي لاستراتيجية التجميع ومصائد السيولة (Accumulation & Spring Backtest)":
    st.subheader("🏛️📊 اختبار خلفي محسن لاستراتيجية التجميع ومصائد السيولة (Spring & Accumulation Backtest)")
    st.markdown(f"اختبار أداء الشروط بدعم مصائد السيولة (Spring Detection)، وعتبة تجميع $\\ge$ {min_acc_score}%، ومضاعف هدف محسّن ({target_multiplier}x).")
    
    col_ab1, col_ab2, col_ab3 = st.columns([2, 2, 1])
    with col_ab1:
        acc_bt_stock = st.selectbox("اختر السهم للاختبار المؤسسي", list(stocks_dict.keys()), key="acc_stock_sel")
    with col_ab2:
        acc_period_label = st.selectbox("فترة الاختبار التاريخي", ["6 أشهر", "سنة كاملة", "سنتان"], key="acc_per_sel")
        acc_period = {"6 أشهر": "6mo", "سنة كاملة": "1y", "سنتان": "2y"}[acc_period_label]
    with col_ab3:
        st.markdown("<br>", unsafe_allow_html=True)
        run_acc_bt = st.button("تشغيل الاختبار المحسّن", type="primary")
        
    acc_code_val = stocks_dict[acc_bt_stock]
    
    if run_acc_bt:
        with st.spinner("جاري محاكاة وتطبيق استراتيجية التجميع ومصائد السيولة المحسنة..."):
            try:
                df_a = yf.download(f"{acc_code_val}.SR", period=acc_period, interval="1d", progress=False)
                if not df_a.empty and len(df_a) > 50:
                    if isinstance(df_a.columns, pd.MultiIndex):
                        df_a.columns = df_a.columns.get_level_values(0)
                    
                    df_a['SMA50'] = df_a['Close'].rolling(window=50).mean()
                    df_a['OBV'] = (np.sign(df_a['Close'].diff()) * df_a['Volume']).fillna(0).cumsum()
                    df_a['OBV_Slope'] = df_a['OBV'].diff(3)
                    
                    delta_a = df_a['Close'].diff()
                    gain_a = delta_a.clip(lower=0)
                    loss_a = -delta_a.clip(upper=0)
                    rs_a = gain_a.rolling(14).mean() / loss_a.rolling(14).mean()
                    df_a['RSI'] = 100 - (100 / (1 + rs_a))
                    df_a['ATR'] = (df_a['High'] - df_a['Low']).rolling(window=14).mean()
                    
                    vol_mean_s = df_a['Volume'].rolling(window=15).mean()
                    
                    spring_cond = (df_a['Low'] < df_a['Low'].rolling(10).min().shift(1)) & (df_a['Close'] > df_a['Open'])
                    
                    score_c = 50 + (df_a['OBV_Slope'] / (vol_mean_s + 1)) * 10 + (df_a['Volume'] / vol_mean_s) * 10
                    score_c = np.where(spring_cond, score_c + 15, score_c)
                    df_a['Acc_Score'] = np.clip(score_c, 45, 98.5).round(1)
                    
                    df_a['Signal'] = np.where(
                        (df_a['Acc_Score'] >= min_acc_score) & 
                        (df_a['Close'] > df_a['SMA50']) & 
                        (df_a['RSI'] >= min_rsi_filter), 1, 0
                    )
                    
                    trades_a, in_pos_a, entry_pa, sl_a, target_pa, high_a, date_a = [], False, 0, 0, 0, 0, ""
                    for i in range(50, len(df_a) - 5):
                        if not in_pos_a and df_a['Signal'].iloc[i] == 1:
                            trigger_price_a = round(float(df_a['High'].iloc[i]) + 0.02, 2)
                            entered_a = False
                            for offset in range(1, 4):
                                if i + offset < len(df_a):
                                    if float(df_a['High'].iloc[i+offset]) >= trigger_price_a:
                                        date_a = str(df_a.index[i+offset]).split()[0]
                                        entry_pa = trigger_price_a
                                        c_atr_a = float(df_a['ATR'].iloc[i]) or (entry_pa * 0.01)
                                        sl_a = round(entry_pa - (sl_multiplier * c_atr_a), 2)
                                        target_pa = round(entry_pa + (target_multiplier * c_atr_a), 2)
                                        high_a = entry_pa
                                        in_pos_a = True
                                        entered_a = True
                                        break
                        elif in_pos_a:
                            hp_a, lp_a, c_atr_a = float(df_a['High'].iloc[i]), float(df_a['Low'].iloc[i]), float(df_a['ATR'].iloc[i]) or (entry_pa * 0.01)
                            if enable_trailing and hp_a > entry_pa + (1.0 * c_atr_a) and hp_a > high_a:
                                high_a = hp_a
                                new_sla = round(high_a - (trailing_atr_mult * c_atr_a), 2)
                                if new_sla > sl_a: sl_a = new_sla
                            if hp_a >= target_pa:
                                trades_a.append({"السهم": acc_bt_stock, "تاريخ الدخول": date_a, "سعر الدخول": entry_pa, "النتيجة": "ربح 🟢", "العائد (%)": round(((target_pa - entry_pa) / entry_pa) * 100, 2)})
                                in_pos_a = False
                            elif lp_a <= sl_a:
                                trades_a.append({"السهم": acc_bt_stock, "تاريخ الدخول": date_a, "سعر الدخول": entry_pa, "النتيجة": "خسارة 🔴", "العائد (%)": round(((sl_a - entry_pa) / entry_pa) * 100, 2)})
                                in_pos_a = False
                            elif i == len(df_a) - 6:
                                final_ca = float(df_a['Close'].iloc[i])
                                trades_a.append({"السهم": acc_bt_stock, "تاريخ الدخول": date_a, "سعر الدخول": entry_pa, "النتيجة": "ربح 🟢" if final_ca > entry_pa else "خسارة 🔴", "العائد (%)": round(((final_ca - entry_pa) / entry_pa) * 100, 2)})
                                in_pos_a = False
                                
                    df_ta = pd.DataFrame(trades_a)
                    if not df_ta.empty:
                        w_ta = len(df_ta[df_ta['النتيجة'].str.contains("ربح")])
                        wra = w_ta / len(df_ta)
                        exp_a = (wra * df_ta[df_ta['النتيجة'].str.contains("ربح")]['العائد (%)'].mean()) - ((1 - wra) * abs(df_ta[df_ta['النتيجة'] == "خسارة 🔴"]['العائد (%)'].mean()))
                        st.session_state['acc_bt_results'] = df_ta
                        st.session_state['acc_bt_metrics'] = (len(df_ta), wra, exp_a)
                    else:
                        st.session_state['acc_bt_results'] = pd.DataFrame()
            except Exception as ex:
                st.error(f"خطأ في الاختبار: {ex}")
                
    # تم تصحيح الأقواس هنا لتفادي خطأ الـ SyntaxError الموضح في الصورة
    if st.session_state.get('acc_bt_results') is not None and not st.session_state.get('acc_bt_results').empty:
        tot_a, wra, exp_a = st.session_state['acc_bt_metrics']
        am1, am2, am3 = st.columns(3)
        am1.metric("إجمالي الصفقات المحسنة", tot_a)
        am2.metric("معدل النجاح الإجمالي", f"{round(wra * 100, 1)}%")
        am3.metric("العائد المتوقع الاستراتيجي", f"{round(exp_a, 2)}%")
        st.download_button("📥 تحميل سجل الصفقات (Excel/CSV)", st.session_state['acc_bt_results'].to_csv(index=False).encode('utf-8-sig'), "accumulation_spring_trades.csv", "text/csv")
        st.dataframe(st.session_state['acc_bt_results'], use_container_width=True)
    elif st.session_state.get('acc_bt_results') is not None and st.session_state.get('acc_bt_results').empty:
        st.warning("⚠️ لا توجد صفقات مطابقة في الفترة المحددة.")

else:
    st.subheader("🌐📊 اختبار خلفي شامل لكل السوق (Portfolio Institutional Backtest)")
    st.markdown("تشغيل الاختبار الخلفي لجميع أسهم السوق السعودي المدرجة وفق المعايير المحسنة.")
    run_port = st.button("تشغيل الاختبار الشامل لكل السوق", type="primary")
    if run_port:
        with st.spinner("جاري فحص السوق الشامل..."):
            all_t = []
            for name, code in stocks_dict.items():
                try:
                    df_p = yf.download(f"{code}.SR", period="1y", interval="1d", progress=False)
                    if not df_p.empty and len(df_p) > 50:
                        if isinstance(df_p.columns, pd.MultiIndex):
                            df_p.columns = df_p.columns.get_level_values(0)
                        df_p['SMA50'] = df_p['Close'].rolling(window=50).mean()
                        df_p['Volume_MA'] = df_p['Volume'].rolling(window=20).mean()
                        df_p['OBV'] = (np.sign(df_p['Close'].diff()) * df_p['Volume']).fillna(0).cumsum()
                        df_p['OBV_Slope'] = df_p['OBV'].diff(3)
                        rs = df_p['Close'].diff().clip(lower=0).rolling(14).mean() / (-df_p['Close'].diff().clip(upper=0)).rolling(14).mean()
                        df_p['RSI'] = 100 - (100 / (1 + rs))
                        df_p['ATR'] = (df_p['High'] - df_p['Low']).rolling(window=14).mean()
                        df_p['Signal'] = np.where((df_p['OBV_Slope'] > 0) & (df_p['Volume'] > vol_threshold * df_p['Volume_MA']) & (df_p['Close'] > df_p['SMA50']) & (df_p['RSI'] >= min_rsi_filter), 1, 0)
                        
                        in_pos, entry_p, sl, target_p, highest, e_date = False, 0, 0, 0, 0, ""
                        for i in range(50, len(df_p) - 5):
                            if not in_pos and df_p['Signal'].iloc[i] == 1:
                                trigger_price_p = round(float(df_p['High'].iloc[i]) + 0.02, 2)
                                for offset in range(1, 4):
                                    if i + offset < len(df_p):
                                        if float(df_p['High'].iloc[i+offset]) >= trigger_price_p:
                                            e_date = str(df_p.index[i+offset]).split()[0]
                                            entry_p = trigger_price_p
                                            c_atr = float(df_p['ATR'].iloc[i]) or (entry_p * 0.01)
                                            sl = round(entry_p - (sl_multiplier * c_atr), 2)
                                            target_p = round(entry_p + (target_multiplier * c_atr), 2)
                                            highest = entry_p
                                            in_pos = True
                                            break
                            elif in_pos:
                                h_p, l_p, c_atr = float(df_p['High'].iloc[i]), float(df_p['Low'].iloc[i]), float(df_p['ATR'].iloc[i]) or (entry_p * 0.01)
                                if enable_trailing and h_p > entry_p + (1.0 * c_atr) and h_p > highest:
                                    highest = h_p
                                    new_sl = round(highest - (trailing_atr_mult * c_atr), 2)
                                    if new_sl > sl: sl = new_sl
                                if h_p >= target_p:
                                    all_t.append({"السهم": name, "تاريخ الدخول": e_date, "سعر الدخول": entry_p, "النتيجة": "ربح 🟢", "العائد (%)": round(((target_p - entry_p) / entry_p) * 100, 2)})
                                    in_pos = False
                                elif l_p <= sl:
                                    all_t.append({"السهم": name, "تاريخ الدخول": e_date, "سعر الدخول": entry_p, "النتيجة": "خسارة 🔴", "العائد (%)": round(((sl - entry_p) / entry_p) * 100, 2)})
                                    in_pos = False
                                elif i == len(df_p) - 6:
                                    final_c = float(df_p['Close'].iloc[i])
                                    all_t.append({"السهم": name, "تاريخ الدخول": e_date, "سعر الدخول": entry_p, "النتيجة": "ربح 🟢" if final_c > entry_p else "خسارة 🔴", "العائد (%)": round(((final_c - entry_p) / entry_p) * 100, 2)})
                                    in_pos = False
                except Exception:
                    continue
            df_port = pd.DataFrame(all_t)
            if not df_port.empty:
                tot_t = len(df_port)
                w_t = len(df_port[df_port['النتيجة'].str.contains("ربح")])
                w_rate = w_t / tot_t
                p_exp = (w_rate * df_port[df_port['النتيجة'].str.contains("ربح")]['العائد (%)'].mean()) - ((1 - w_rate) * abs(df_port[df_port['النتيجة'] == "خسارة 🔴"]['العائد (%)'].mean()))
                st.session_state['portfolio_bt_df'] = df_port
                st.session_state['portfolio_metrics'] = (tot_t, w_rate, p_exp)
            else:
                st.session_state['portfolio_bt_df'] = pd.DataFrame()

    if st.session_state['portfolio_bt_df'] is not None and not st.session_state['portfolio_bt_df'].empty:
        tot_t, w_rate, p_exp = st.session_state['portfolio_metrics']
        pm1, pm2, pm3 = st.columns(3)
        pm1.metric("إجمالي صفقات السوق", tot_t)
        pm2.metric("معدل النجاح العام", f"{round(w_rate * 100, 1)}%")
        pm3.metric("العائد المتوقع للسوق", f"{round(p_exp, 2)}%")
        st.download_button("📥 تحميل السجل الشامل (Excel/CSV)", st.session_state['portfolio_bt_df'].to_csv(index=False).encode('utf-8-sig'), "portfolio_trades.csv", "text/csv")
        st.dataframe(st.session_state['portfolio_bt_df'], use_container_width=True)
    elif st.session_state['portfolio_bt_df'] is not None and st.session_state['portfolio_bt_df'].empty:
        st.warning("⚠️ لم يتم العثور على صفقات مطابقة في نطاق السوق الحالي.")
