import streamlit as st
import yfinance as yf
from datetime import datetime
import time

# ==========================================
# 頁面設定 (適合放在副螢幕全螢幕顯示)
# ==========================================
st.set_page_config(page_title="終極 X 光雷達", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 核心邏輯區
# ==========================================
@st.cache_data(ttl=50, show_spinner=False) # 快取 50 秒，配合 60 秒刷新
def fetch_radar_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        if hist.empty: return None
        
        current_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        pct_change = ((current_price - prev_close) / prev_close) * 100
        
        current_vol = hist['Volume'].iloc[-1]
        avg_vol = hist['Volume'].mean()
        vol_ratio = current_vol / avg_vol if avg_vol > 0 else 0
        
        # 買賣力道演算法
        sensitivity = 8.5 
        buy_force = max(5, min(95, 50 + (pct_change * sensitivity)))
        if vol_ratio > 1.3:
            buy_force += (vol_ratio * 5) if pct_change > 0 else -(vol_ratio * 5)
        buy_force = max(5, min(95, buy_force))
        
        return {
            "price": current_price, "pct": pct_change, 
            "vol_ratio": vol_ratio, "buy": buy_force, "sell": 100 - buy_force
        }
    except:
        return None

# ==========================================
# UI 介面區
# ==========================================
st.markdown("<h3 style='color:#E0E0E0;'>📡 實體量能監控雷達</h3>", unsafe_allow_html=True)

# 讓你自己輸入要監控的股票 (用逗號隔開)
default_tickers = "APLD, SOUN, NVDA, TSLA"
watch_list_str = st.text_input("輸入監控清單 (逗號分隔)", value=default_tickers)
tickers = [t.strip().upper() for t in watch_list_str.split(",") if t.strip()]

# 頂部控制列
col1, col2 = st.columns([1, 4])
with col1:
    auto_refresh = st.toggle("啟動 60 秒自動掃描", value=True)
with col2:
    st.write(f"⏱️ 最後更新時間: `{datetime.now().strftime('%H:%M:%S')}`")

st.divider()

# 動態生成卡片網格 (每排顯示 3 到 4 個)
cols = st.columns(4)
for i, ticker in enumerate(tickers):
    data = fetch_radar_data(ticker)
    if data:
        color = "#2ecc71" if data['pct'] >= 0 else "#e74c3c"
        status = "🔥 爆發" if data['vol_ratio'] > 1.3 else "❄️ 枯竭" if data['vol_ratio'] < 0.7 else "📊 平穩"
        
        with cols[i % 4]:
            st.markdown(f"""
            <div style='background-color: #1a1a1a; padding: 15px; border-radius: 8px; border-top: 4px solid {color}; border-left: 1px solid #333; border-right: 1px solid #333; border-bottom: 1px solid #333; margin-bottom: 15px;'>
                <div style='display:flex; justify-content:space-between;'>
                    <span style='font-size: 20px; font-weight: bold; color: #E0E0E0;'>{ticker}</span>
                    <span style='font-size: 14px; color: #888;'>{status}</span>
                </div>
                <div style='font-size: 24px; color: {color}; font-weight: bold; margin-top: 5px;'>
                    ${data['price']:.2f} <span style='font-size: 12px;'>({data['pct']:+.2f}%)</span>
                </div>
                <div style='font-size: 10px; color: #888; margin-top: 8px;'>主動買賣力道 (均量比: {data['vol_ratio']*100:.0f}%)</div>
                <div style="width: 100%; background-color: #333; border-radius: 5px; height: 12px; display: flex; overflow: hidden; margin-top: 3px;">
                    <div style="width: {data['buy']:.0f}%; background-color: #2ecc71;"></div>
                    <div style="width: {data['sell']:.0f}%; background-color: #e74c3c;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        with cols[i % 4]:
            st.error(f"{ticker} 讀取失敗")

# ==========================================
# 自動刷新引擎
# ==========================================
if auto_refresh:
    time.sleep(60) # 暫停 60 秒
    st.rerun()     # 重新執行整個腳本，達到畫面刷新效果
