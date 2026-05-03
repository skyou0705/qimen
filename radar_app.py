import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import time

# ==========================================
# 頁面設定 (Cyberpunk UI)
# ==========================================
st.set_page_config(page_title="終極 X 光雷達 | 雙模組", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 核心邏輯區：雙模組數據引擎
# ==========================================
@st.cache_data(ttl=50, show_spinner=False)
def fetch_radar_data(ticker, mode):
    try:
        stock = yf.Ticker(ticker)
        
        # 🛡️ 根據作戰模式動態調整
        if mode == "🌊 波段模式 (持股 1~2 週)":
            hist = stock.history(period="3mo", interval="1d")
            ema_length = 20
        else:
            hist = stock.history(period="5d", interval="5m")
            ema_length = 200

        if hist.empty: 
            return None
        
        # 🧠 計算 EMA (移除嚴格的長度限制，讓 yfinance 更有彈性)
        hist['EMA'] = hist['Close'].ewm(span=ema_length, adjust=False).mean()
        
        current_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        current_ema = hist['EMA'].iloc[-1]
        pct_change = ((current_price - prev_close) / prev_close) * 100
        
        # 計算當前量能與均量比
        current_vol = hist['Volume'].iloc[-1]
        avg_vol = hist['Volume'].mean()
        vol_ratio = current_vol / avg_vol if avg_vol > 0 else 0
        
        # ⚡ 動能買賣力道演算法
        sensitivity = 8.5 
        buy_force = 50 + (pct_change * sensitivity)
        if vol_ratio > 1.3:
            buy_force += (vol_ratio * 5) if pct_change > 0 else -(vol_ratio * 5)
        buy_force = max(5, min(95, buy_force))
        
        return {
            "price": current_price, 
            "pct": pct_change, 
            "vol_ratio": vol_ratio, 
            "buy": buy_force, 
            "sell": 100 - buy_force,
            "ema": current_ema,
            "is_above_ema": current_price > current_ema,
            "ema_length": ema_length
        }
    except Exception as e:
        return None

# ==========================================
# UI 介面區：控制台
# ==========================================
st.markdown("<h3 style='color:#E0E0E0;'>📡 實體量能監控雷達 <span style='font-size:14px; color:#00FF7F;'>[KS 趨勢融合版]</span></h3>", unsafe_allow_html=True)

col_input, col_mode = st.columns([2, 2])
with col_input:
    watch_list_str = st.text_input("輸入監控清單 (逗號分隔)", value="APLD, SOUN, NVDA, TSLA, TQQQ")
    tickers = [t.strip().upper() for t in watch_list_str.split(",") if t.strip()]
with col_mode:
    combat_mode = st.radio("選擇作戰模組：", 
                          ["🌊 波段模式 (持股 1~2 週)", "⚡ 極短線當沖 (日內 / ETF)"], 
                          horizontal=True)

col1, col2 = st.columns([1, 4])
with col1:
    auto_refresh = st.toggle("啟動 60 秒自動掃描", value=True)
with col2:
    st.write(f"⏱️ 最後更新時間: `{datetime.now().strftime('%H:%M:%S')}`")

st.divider()

# ==========================================
# 動態生成卡片網格 (賽博龐克 UI)
# ==========================================
cols = st.columns(4)
for i, ticker in enumerate(tickers):
    data = fetch_radar_data(ticker, combat_mode)
    if data:
        is_up = data['pct'] >= 0
        color = "#00FF7F" if is_up else "#FF3366" 
        bg_color = "rgba(0, 255, 127, 0.1)" if is_up else "rgba(255, 51, 102, 0.1)"
        
        trend_color = "#00FF7F" if data['is_above_ema'] else "#FF3366"
        trend_text = "🟢 趨勢偏多" if data['is_above_ema'] else "🔴 趨勢偏空"
        
        if data['vol_ratio'] > 1.3:
            status = "🔥 動能爆發"
            glow = f"box-shadow: 0 0 20px {color}50, inset 0 0 10px {color}20;"
            border = f"2px solid {color}"
        elif data['vol_ratio'] < 0.7:
            status = "❄️ 量能枯竭"
            glow = "box-shadow: none;"
            border = "1px solid #222"
        else:
            status = "📊 隨波逐流"
            glow = "box-shadow: 0 4px 10px rgba(0,0,0,0.5);"
            border = "1px solid #444"

        with cols[i % 4]:
            # 壓扁 HTML 縮排，防止被解析為程式碼區塊
            st.markdown(f"""
<div style='background: linear-gradient(145deg, #1c1c1c 0%, #121212 100%); border-radius: 12px; border: {border}; {glow} padding: 20px; margin-bottom: 20px; transition: all 0.3s ease;'>
<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom: 12px;'>
<span style='font-size: 24px; font-weight: 900; color: #FFFFFF; letter-spacing: 1px;'>{ticker}</span>
<span style='font-size: 12px; font-weight: bold; padding: 4px 8px; border-radius: 4px; background: {bg_color}; color: {color};'>{status}</span>
</div>
<div style='font-size: 36px; color: {color}; font-weight: 900; font-family: "Courier New", monospace; letter-spacing: -2px; line-height: 1;'>${data['price']:.2f}</div>
<div style='font-size: 15px; color: {color}; font-weight: bold; margin-top: 4px; margin-bottom: 15px;'>{'▲' if is_up else '▼'} {abs(data['pct']):.2f}%</div>
<div style='background: #222; padding: 8px; border-radius: 6px; margin-bottom: 15px; border-left: 3px solid {trend_color};'>
<div style='font-size: 11px; color: #aaa;'>KS 趨勢防守線 (EMA {data['ema_length']})</div>
<div style='display:flex; justify-content:space-between; align-items:center; margin-top: 3px;'>
<span style='font-size: 14px; font-weight: bold; color: {trend_color};'>${data['ema']:.2f}</span>
<span style='font-size: 11px; color: {trend_color};'>{trend_text}</span>
</div>
</div>
<div style='display:flex; justify-content:space-between; font-size: 11px; color: #aaa; margin-bottom: 6px; font-weight: bold;'>
<span>買盤 {data['buy']:.0f}%</span>
<span style='color:#777; background: #222; padding: 2px 6px; border-radius: 10px;'>均量比: {data['vol_ratio']*100:.0f}%</span>
<span>賣盤 {data['sell']:.0f}%</span>
</div>
<div style="width: 100%; background-color: #222; border-radius: 6px; height: 14px; display: flex; overflow: hidden; border: 1px solid #333;">
<div style="width: {data['buy']}%; background: linear-gradient(90deg, #006400 0%, #00FF7F 100%);"></div>
<div style="width: 2px; background-color: #000;"></div>
<div style="width: {data['sell']}%; background: linear-gradient(90deg, #FF3366 0%, #8B0000 100%);"></div>
</div>
</div>
            """, unsafe_allow_html=True)
    else:
        with cols[i % 4]:
            st.error(f"⚠️ {ticker} 數據無法讀取 (可能無交易或數據不足)")

# ==========================================
# 自動刷新引擎
# ==========================================
if auto_refresh:
    time.sleep(60)
    st.rerun()
