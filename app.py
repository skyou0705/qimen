import streamlit as st
import yfinance as yf
from datetime import datetime
import os
from time_engine import get_qimen_time_params
from qimen_matrix import generate_full_matrix

# ==========================================
# 頁面基本設定與快取引擎
# ==========================================
st.set_page_config(page_title="奇門遁甲 金融儀表板", layout="wide")

if 'last_now' not in st.session_state: 
    st.session_state.last_now = datetime.now()

@st.cache_data(ttl=60, show_spinner=False)
def fetch_stock_data(ticker):
    """取得 yfinance 數據並快取 60 秒"""
    stock = yf.Ticker(ticker)
    return stock.history(period="5d")

def write_snapshot_to_log(filename, content):
    """寫入日誌邏輯"""
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(content + "\n" + "-"*50 + "\n")
        return True
    except Exception as e:
        st.error(f"寫入失敗：{e}")
        return False

# ==========================================
# 側邊欄：控制器與 X 光機
# ==========================================
with st.sidebar:
    st.header("🕰️ 盤前推演控制器")
    use_custom_time_state = st.toggle("開啟手動回測模式", value=False)
    
    if use_custom_time_state:
        d = st.date_input("選擇日期", st.session_state.last_now.date())
        t = st.time_input("選擇時間", st.session_state.last_now.time())
        new_dt = datetime.combine(d, t)
        if new_dt != st.session_state.last_now:
            st.session_state.last_now = new_dt
            st.rerun()
        now = st.session_state.last_now
    else:
        now = datetime.now()
                
    st.divider()
    
    st.header("📈 個股 X 光機")
    st.caption("驗證奇門板塊與個股實體量能的共振狀態")
    
    ticker_input = st.text_input("輸入美股代號", key="target_ticker").upper()
    
    if ticker_input:
        with st.spinner("掃描即時量價數據中..."):
            try:
                hist = fetch_stock_data(ticker_input)
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                    pct_change = ((current_price - prev_close) / prev_close) * 100
                    
                    current_vol = hist['Volume'].iloc[-1]
                    avg_vol = hist['Volume'].mean()
                    vol_ratio = current_vol / avg_vol if avg_vol > 0 else 0
                    
                    # 模擬買賣力道演算法
                    sensitivity = 8.5 
                    buy_force = 50 + (pct_change * sensitivity)
                    if vol_ratio > 1.3 and pct_change < 0:
                        buy_force -= (vol_ratio * 5)
                    elif vol_ratio > 1.3 and pct_change > 0:
                        buy_force += (vol_ratio * 5)
                        
                    buy_force = max(5, min(95, buy_force))
                    sell_force = 100 - buy_force
                    
                    color = "#2ecc71" if pct_change >= 0 else "#e74c3c"
                    if vol_ratio > 1.3:
                        vol_status, vol_color = "🔥 動能爆發 (主升段警示)", "#e74c3c"
                    elif vol_ratio < 0.7:
                        vol_status, vol_color = "❄️ 量能枯竭 (虛假突破/盤整)", "#3498db"
                    else:
                        vol_status, vol_color = "📊 量能平穩 (跟隨大盤)", "#f1c40f"

                    # 修正：移除HTML前的多餘空白，避免被解析為程式碼區塊
                    html_content = f"""
<div style='background-color: #1a1a1a; padding: 12px; border-radius: 8px; border: 1px solid #333; border-left: 4px solid {color};'>
<div style='font-size: 18px; font-weight: bold; color: #E0E0E0;'>{ticker_input}</div>
<div style='font-size: 26px; color: {color}; font-weight: bold;'>${current_price:.2f} <span style='font-size: 14px;'>({pct_change:+.2f}%)</span></div>
<div style='font-size: 11px; color: #888; margin-top:5px;'>5日均量比: <span style='color: #ccc; font-weight: bold;'>{(vol_ratio*100):.0f}%</span></div>
<div style="margin-top: 15px; margin-bottom: 5px; display: flex; justify-content: space-between; font-size: 10px; color: #aaa;">
<span>主動買入力道</span>
<span>主動賣出力道</span>
</div>
<div style="width: 100%; background-color: #333; border-radius: 10px; height: 18px; display: flex; overflow: hidden; border: 1px solid #444;">
<div style="width: {buy_force:.2f}%; background-color: #2ecc71; text-align: center; color: white; font-size: 10px; line-height: 18px; font-weight: bold;">{buy_force:.0f}%</div>
<div style="width: {sell_force:.2f}%; background-color: #e74c3c; text-align: center; color: white; font-size: 10px; line-height: 18px; font-weight: bold;">{sell_force:.0f}%</div>
</div>
<div style='font-size: 12px; color: {vol_color}; font-weight: bold; margin-top: 10px;'>{vol_status}</div>
</div>
"""
                    st.markdown(html_content, unsafe_allow_html=True)

                    st.write("") 
                    if st.button("📓 紀錄當前時空快照", use_container_width=True):
                        temp_params = get_qimen_time_params(now)
                        temp_matrix = generate_full_matrix(temp_params['當前節氣'], temp_params['日柱'], temp_params['時柱'])
                        log_entry = (
                            f"【時空快照】 {now.strftime('%Y-%m-%d %H:%M:%S')} ({temp_params['時柱'][1]}時)\n"
                            f"► 矩陣: {temp_matrix['遁法']}遁{temp_matrix['局數']}局 | 值符: {temp_matrix['莊家情報']['值符']} | 值使: {temp_matrix['莊家情報']['值使']}\n"
                            f"► 標的: {ticker_input} | 價格: ${current_price:.2f} ({pct_change:+.2f}%)\n"
                            f"► 動能: {vol_status} (買盤:{buy_force:.0f}% 賣盤:{sell_force:.0f}%)\n"
                            f"► 大盤中樞關係: {temp_matrix['九宮格'][5]['關係']}"
                        )
                        if write_snapshot_to_log("trading_diary.txt", log_entry):
                            st.toast("✅ 數據已寫入日誌", icon="📝")
                else:
                    st.error("⚠️ 找不到數據。")
            except Exception as e:
                st.error(f"⚠️ 讀取失敗: {e}")

# ==========================================
# 奇門遁甲矩陣運算 (主畫面)
# ==========================================
time_params = get_qimen_time_params(now)
matrix_result = generate_full_matrix(time_params['當前節氣'], time_params['日柱'], time_params['時柱'])
info, palace_data = matrix_result['莊家情報'], matrix_result['九宮格']
center_rel = palace_data[5]['關係']
shichen_name = time_params['時柱'][1] + "時"

# ==========================================
# 主視覺 HUD 面板
# ==========================================
st.markdown("""<div style="font-size: 20px; font-weight: bold; color: #E0E0E0; margin-bottom: 12px; margin-top: -20px;">🧮 奇門遁甲：時空演算法矩陣</div>""", unsafe_allow_html=True)
st.markdown(f"""
<style>
.hud-container {{ display: flex; justify-content: space-between; background-color: #1a1a1a; padding: 10px 15px; border-radius: 8px; border: 1px solid #333; margin-bottom: 12px; }}
.hud-item {{ text-align: center; flex: 1; border-right: 1px solid #333; }}
.hud-item:last-child {{ border-right: none; }}
.hud-label {{ font-size: 9px; color: #666; margin-bottom: 1px; }}
.hud-value {{ font-size: 14px; font-weight: bold; color: #ccc; }}
</style>
<div class="hud-container">
    <div class="hud-item"><div class="hud-label">真太陽時</div><div class="hud-value">{now.strftime("%H:%M")} <span style="font-size: 11px; color: #f1c40f; font-weight: normal;">({shichen_name})</span></div></div>
    <div class="hud-item"><div class="hud-label">時空矩陣</div><div class="hud-value" style="color:#f1c40f">{matrix_result['遁法']}遁 {matrix_result['局數']} 局</div></div>
    <div class="hud-item"><div class="hud-label">本人(日)</div><div class="hud-value">{time_params['日柱']}</div></div>
    <div class="hud-item"><div class="hud-label">標的(時)</div><div class="hud-value">{time_params['時柱']}</div></div>
    <div class="hud-item"><div class="hud-label">值符</div><div class="hud-value" style="color:#e74c3c">{info['值符']}</div></div>
    <div class="hud-item"><div class="hud-label">值使</div><div class="hud-value" style="color:#2ecc71">{info['值使']}</div></div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 左右平衡排版 (1.8 : 1)
# ==========================================
col_left, col_right = st.columns([1.8, 1])

with col_left:
    st.markdown("""<style>
    .qimen-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; background-color: #111; padding: 8px; border-radius: 8px; }
    .palace-box { background-color: #222; border: 1px solid #333; padding: 10px; border-radius: 4px; height: 160px; position: relative; display: flex; flex-direction: column; justify-content: space-between; overflow: hidden; }
    .sector-tag { font-size: 11px; color: #5dade2; font-weight: bold; }
    .rel-tag { font-size: 9px; padding: 2px 5px; border-radius: 3px; font-weight: bold; }
    .status-icon { font-size: 9px; padding: 0 2px; border-radius: 2px; border: 1px solid currentColor; margin-left: 2px; }
    .rel-profit { background-color: rgba(46, 204, 113, 0.2); color: #2ecc71; border: 1px solid #2ecc71; }
    .rel-risk { background-color: rgba(231, 76, 60, 0.2); color: #e74c3c; border: 1px solid #e74c3c; }
    .rel-ctrl { background-color: rgba(241, 196, 15, 0.2); color: #f1c40f; border: 1px solid #f1c40f; }
    .rel-flat { background-color: rgba(149, 165, 166, 0.2); color: #95a5a6; border: 1px solid #95a5a6; }
    </style>""", unsafe_allow_html=True)

    luoshu_order, html = [4, 9, 2, 3, 5, 7, 8, 1, 6], '<div class="qimen-grid">\n'
    for p in luoshu_order:
        d = palace_data[p]
        css = f"palace-box {'danger' if d['危險'] else ''} {'kongwang' if d['空亡'] else ''} {'center-core' if p==5 else ''}"
        icons_html = "".join([f'<span class="status-icon" style="color:{c}; border-color:{c};">{t}</span>' for t, c in [("🐎馬","#5dade2"), ("⚡刑","#e74c3c"), ("🚧迫","#f39c12"), ("空","#777")] if d.get(t[1:]) or (t=="空" and d['空亡'])])
        rel_class = "rel-profit" if "生我" in d['關係'] else "rel-risk" if "剋我" in d['關係'] else "rel-ctrl" if "我剋" in d['關係'] else "rel-flat"
        
        if p == 5:
            html += f'<div class="{css}"><div style="display:flex;justify-content:space-between;"><div class="sector-tag">🌐 市場中樞</div><div class="rel-tag rel-flat">{d["關係"]}</div></div><div style="text-align:center;color:#555;font-size:10px;margin-top:30px;">MACRO INDEX</div><div style="position:absolute;bottom:4px;right:8px;font-size:9px;color:#333;">5宮</div></div>'
        else:
            html += f"""<div class="{css}">
                <div style="display:flex;justify-content:space-between;"><div class="sector-tag">{d['板塊']}{'<span style="background:#f1c40f;color:#000;font-size:8px;padding:1px 3px;border-radius:2px;margin-left:3px;">本人</span>' if d['本人'] else ''}</div><div class="rel-tag {rel_class}">{d['關係'] if not d['本人'] else "📍座標"}</div></div>
                <div style="display:flex;gap:3px;margin-bottom:6px;">{icons_html}</div>
                <div style="display:flex;justify-content:space-between;color:#888;font-size:11px;"><span>{d['神']}</span><span>{d['星']}</span></div>
                <div style="text-align:center;font-size:24px;font-weight:bold;color:#f1c40f;">{d['門']}</div>
                <div style="display:flex;justify-content:center;gap:6px;font-size:18px;font-weight:bold;"><span style="color:#e74c3c">{d['天干']}</span><span style="color:#555">/</span><span style="color:#2ecc71">{d['地干']}</span></div>
                <div style="position:absolute;bottom:4px;right:8px;font-size:9px;color:#333;">{p}宮</div>
            </div>"""
    st.markdown(html + '</div>', unsafe_allow_html=True)

    # 🤖 自動白話文翻譯引擎
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True) 
    QIMEN_DICT = {
        "神": {"值符": "主力大資本 (護盤力量)：大機構重倉。", "騰蛇": "虛假與震盪 (高波動)：容易出現騙線。", "太陰": "暗盤與隱蔽 (潛伏期)：主力悄悄吸籌。", "六合": "併購與平穩 (合作)：走勢溫和。", "白虎": "暴漲暴跌 (高壓)：動能極強，風險極大。", "玄武": "投機與假消息 (洗盤)：熱錢為主，防割韭菜。", "九地": "底部與盤整 (長線)：適合長線佈局。", "九天": "主升段與泡沫 (新高)：情緒狂熱，隨時見頂。"},
        "星": {"天蓬": "高風險大波動", "天任": "穩健慢牛", "天沖": "動能突破 (軋空)", "天輔": "穩步向上", "天英": "情緒化高熱度 (見光死)", "天芮": "問題股與套牢", "天柱": "突發利空破壞", "天心": "核心權重資產"},
        "門": {"休門": "觀望盤整", "生門": "絕對利潤 (多頭)", "傷門": "激烈競爭耗損", "杜門": "隱藏停滯 (掛單潛伏)", "景門": "消息面驅動 (獲利了結)", "死門": "資金死水", "驚門": "恐慌拋售", "開門": "突破順暢"},
        "干": {"乙": "散戶資金", "丙": "熱錢暴漲跌", "丁": "精準小資金", "戊": "主力大本金", "己": "陷阱陰跌", "庚": "強大阻力", "辛": "錯誤套牢", "壬": "量化流動性", "癸": "天網枯竭"}
    }
    with st.expander("🤖 深度解析：各板塊底層邏輯", expanded=False):
        for p in [8, 3, 4, 1, 9, 2, 6, 7]:
            d = palace_data[p]
            if d['空亡']: continue
            border_color = '#2ecc71' if '生我' in d['關係'] else '#e74c3c' if '剋我' in d['關係'] else '#f1c40f'
            st.markdown(f"""<div style="background-color:#1e1e1e;padding:10px;border-radius:5px;margin-bottom:10px;border-left:4px solid {border_color};">
                <div style="font-size:14px;font-weight:bold;color:#5dade2;">{p}宮 - {d['板塊']} ({d['關係']})</div>
                <div style="font-size:12px;color:#ccc;">[{d['神']}] {QIMEN_DICT['神'].get(d['神'], '')}<br>[{d['星']}] {QIMEN_DICT['星'].get(d['星'], '')}<br>[{d['門']}] {QIMEN_DICT['門'].get(d['門'], '')}<br>[{d['天干']}/{d['地干']}] {QIMEN_DICT['干'].get(d['天干'], '')} 遇上 {QIMEN_DICT['干'].get(d['地干'], '')}</div>
            </div>""", unsafe_allow_html=True)

with col_right:
    st.markdown('<div style="background:#1a1a1a;padding:12px;border-radius:8px;border:1px solid #333;height:100%;">', unsafe_allow_html=True)
    if "剋我" in center_rel: st.markdown(f'<div style="font-size:12px;font-weight:bold;padding:10px;border-radius:5px;border:1px solid #e74c3c;color:#e74c3c;background:rgba(231,76,60,0.05);margin-bottom:15px;">🚨 大盤逆風：{center_rel}，建議觀望。</div>', unsafe_allow_html=True)
    elif "生我" in center_rel: st.markdown(f'<div style="font-size:12px;font-weight:bold;padding:10px;border-radius:5px;border:1px solid #2ecc71;color:#2ecc71;background:rgba(46,204,113,0.05);margin-bottom:15px;">🚀 大盤環境順風：{center_rel}，積極尋找機會。</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:13px;font-weight:bold;color:#888;margin-bottom:10px;border-left:4px solid #e74c3c;padding-left:10px;">📉 系統日誌</div>', unsafe_allow_html=True)
    for alert in matrix_result['警報'][:3]: st.markdown(f'<div style="font-size:10px;color:#aaa;margin-bottom:3px;padding-left:5px;border-left:2px solid #444;">{alert}</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:13px;font-weight:bold;color:#888;margin-top:20px;border-left:4px solid #f1c40f;padding-left:10px;">🧭 板塊資金流向雷達</div>', unsafe_allow_html=True)
    insight_html = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px;">'
    for p_num, d in palace_data.items():
        if p_num != 5 and not d['本人']: insight_html += f'<div style="font-size:11px;padding:8px;background:#262626;border:1px solid #333;border-radius:5px;">{d["板塊"]}<br><span style="color:#5dade2;">{d["關係"]}</span></div>'
    st.markdown(insight_html + '</div></div>', unsafe_allow_html=True)
