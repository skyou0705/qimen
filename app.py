import streamlit as st
from datetime import datetime
from time_engine import get_qimen_time_params
from qimen_matrix import generate_full_matrix

# --- 網頁基礎設定 ---
st.set_page_config(page_title="奇門遁甲 金融儀表板", layout="wide")

# --- 側邊欄：時間控制器 ---
if 'last_now' not in st.session_state:
    st.session_state.last_now = datetime.now()

with st.sidebar:
    st.header("🕰️ 盤前推演控制器")
    use_custom_time = st.toggle("開啟手動回測模式", value=False)
    if use_custom_time:
        with st.form("time_form"):
            d = st.date_input("選擇日期", st.session_state.last_now.date())
            t = st.time_input("選擇時間", st.session_state.last_now.time())
            if st.form_submit_button("🚀 執行時空推演"):
                st.session_state.last_now = datetime.combine(d, t)
        now = st.session_state.last_now
    else:
        now = datetime.now()

time_params = get_qimen_time_params(now)
matrix_result = generate_full_matrix(time_params['當前節氣'], time_params['日柱'], time_params['時柱'])
info, palace_data = matrix_result['莊家情報'], matrix_result['九宮格']
center_rel = palace_data[5]['關係']

# --- 自訂主標題 ---
st.markdown("""
<div style="font-size: 20px; font-weight: bold; color: #E0E0E0; margin-bottom: 12px; margin-top: -20px;">
    🧮 奇門遁甲：時空演算法矩陣
</div>
""", unsafe_allow_html=True)

# --- 頂部 HUD 面板 ---
st.markdown(f"""
<style>
.hud-container {{ display: flex; justify-content: space-between; background-color: #1a1a1a; padding: 10px 15px; border-radius: 8px; border: 1px solid #333; margin-bottom: 15px; }}
.hud-item {{ text-align: center; flex: 1; border-right: 1px solid #333; }}
.hud-item:last-child {{ border-right: none; }}
.hud-label {{ font-size: 10px; color: #666; margin-bottom: 2px; }}
.hud-value {{ font-size: 16px; font-weight: bold; color: #ccc; }}
</style>
<div class="hud-container">
    <div class="hud-item"><div class="hud-label">真太陽時</div><div class="hud-value">{now.strftime("%H:%M")}</div></div>
    <div class="hud-item"><div class="hud-label">時空矩陣</div><div class="hud-value" style="color:#f1c40f">{matrix_result['遁法']}遁 {matrix_result['局數']} 局</div></div>
    <div class="hud-item"><div class="hud-label">本人(日)</div><div class="hud-value">{time_params['日柱']}</div></div>
    <div class="hud-item"><div class="hud-label">標的(時)</div><div class="hud-value">{time_params['時柱']}</div></div>
    <div class="hud-item"><div class="hud-label">值符</div><div class="hud-value" style="color:#e74c3c">{info['值符']}</div></div>
    <div class="hud-item"><div class="hud-label">值使</div><div class="hud-value" style="color:#2ecc71">{info['值使']}</div></div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 🚀 左右平衡排版 (1.8 : 1)
# ==========================================
col_left, col_right = st.columns([1.8, 1])

with col_left:
    st.markdown("""
    <style>
    .qimen-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; background-color: #111; padding: 10px; border-radius: 8px; }
    .palace-box { 
        background-color: #222; border: 1px solid #333; padding: 12px; border-radius: 6px; 
        height: 160px; position: relative; display: flex; flex-direction: column; justify-content: space-between; 
    }
    .palace-box.danger { border: 1px solid #e74c3c; box-shadow: inset 0 0 8px rgba(231,76,60,0.2); }
    .palace-box.kongwang { opacity: 0.35; }
    .palace-box.center-core { border: 2px dashed #f1c40f; background: radial-gradient(circle, #2a2a2a 0%, #1a1a1a 100%); }
    .sector-tag { font-size: 11px; color: #5dade2; font-weight: bold; }
    .user-badge { background-color: #f1c40f; color: #000; font-size: 9px; padding: 1px 4px; border-radius: 3px; margin-left: 5px; }
    .rel-tag { font-size: 10px; padding: 2px 5px; border-radius: 3px; font-weight: bold; position: absolute; top: 10px; right: 10px; }
    .rel-profit { background-color: rgba(46, 204, 113, 0.2); color: #2ecc71; border: 1px solid #2ecc71; }
    .rel-risk { background-color: rgba(231, 76, 60, 0.2); color: #e74c3c; border: 1px solid #e74c3c; }
    .rel-ctrl { background-color: rgba(241, 196, 15, 0.2); color: #f1c40f; border: 1px solid #f1c40f; }
    .rel-flat { background-color: rgba(149, 165, 166, 0.2); color: #95a5a6; border: 1px solid #95a5a6; }
    .row-1 { display: flex; justify-content: space-between; color: #888; font-size: 12px; margin-top: 15px; }
    .row-2 { text-align: center; font-size: 26px; font-weight: bold; color: #f1c40f; }
    .row-3 { display: flex; justify-content: center; gap: 8px; font-size: 20px; font-weight: bold; }
    .p-num { text-align: right; font-size: 10px; color: #333; position: absolute; bottom: 5px; right: 10px; }
    .status-icon { font-size: 10px; padding: 0 2px; border-radius: 2px; margin-left: 3px; border: 1px solid currentColor; }
    </style>
    """, unsafe_allow_html=True)

    luoshu_order, html = [4, 9, 2, 3, 5, 7, 8, 1, 6], '<div class="qimen-grid">\n'
    for p in luoshu_order:
        d = palace_data[p]
        css = f"palace-box {'danger' if d['危險'] else ''} {'kongwang' if d['空亡'] else ''} {'center-core' if p==5 else ''}"
        rel_class = "rel-profit" if "生我" in d['關係'] else "rel-risk" if "剋我" in d['關係'] else "rel-ctrl" if "我剋" in d['關係'] else "rel-flat"
        icons = "".join([f'<span class="status-icon" style="color:{"#5dade2" if k=="馬" else "#e74c3c" if k=="刑" else "#f39c12" if k=="迫" else "#777"}">{k}</span>' for k, v in {"馬":d['馬星'], "刑":d['擊刑'], "迫":d['門迫'], "空":d['空亡']}.items() if v])

        if p == 5:
            html += f'<div class="{css}"><div class="rel-tag rel-flat">{d["關係"]}</div><div style="font-size:15px; font-weight:bold; color:#f1c40f; text-align:center; margin-top:20px; letter-spacing:2px;">🌐 市場中樞</div><div style="text-align:center; color:#555; font-size:11px; margin-top:10px;">MACRO INDEX</div><div class="p-num">5宮</div></div>\n'
        else:
            html += f"""<div class="{css}">
<div class="sector-tag">{d['板塊']}{'<span class="user-badge">本人</span>' if d['本人'] else ''}{icons}</div>
<div class="rel-tag {rel_class}">{d['關係'] if not d['本人'] else '📍座標'}</div>
<div class="row-1"><span>{d['神']}</span><span>{d['星']}</span></div>
<div class="row-2">{d['門']}</div>
<div class="row-3"><span style="color:#e74c3c">{d['天干']}</span><span style="color:#555">/</span><span style="color:#2ecc71">{d['地干']}</span></div>
<div class="p-num">{p}宮</div>
</div>\n"""
    st.markdown(html + '</div>', unsafe_allow_html=True)

with col_right:
    st.markdown("""
    <style>
    .right-panel { background-color: #1a1a1a; padding: 15px; border-radius: 8px; border: 1px solid #333; height: 100%; }
    .section-title { font-size: 14px; font-weight: bold; color: #888; margin-bottom: 12px; border-left: 4px solid #f1c40f; padding-left: 10px; }
    .insight-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
    .insight-item { 
        font-size: 12px; padding: 12px; background: #262626; border: 1px solid #333; border-radius: 5px; 
        display: flex; flex-direction: column; justify-content: center; min-height: 70px;
    }
    .insight-label { color: #5dade2; font-weight: bold; margin-bottom: 4px; font-size: 13px; }
    .macro-alert { font-size: 13px; font-weight: bold; padding: 12px; border-radius: 6px; border: 1px solid #e74c3c; color: #e74c3c; background: rgba(231,76,60,0.08); margin-bottom: 15px; }
    .log-item { font-size: 11px; color: #aaa; margin-bottom: 4px; padding-left: 5px; border-left: 2px solid #444; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="right-panel">', unsafe_allow_html=True)
    
    # 1. 宏觀風向
    if "剋我" in center_rel:
        st.markdown(f'<div class="macro-alert">🚨 大盤逆風警告：{center_rel}，建議縮減部位或觀望。</div>', unsafe_allow_html=True)
    elif "生我" in center_rel:
        st.markdown(f'<div class="macro-alert" style="color:#2ecc71; border-color:#2ecc71; background:rgba(46,204,113,0.08)">🚀 大盤環境順風：{center_rel}，積極尋找獲利機會。</div>', unsafe_allow_html=True)

    # 2. 系統日誌
    st.markdown('<div class="section-title" style="border-left-color:#e74c3c">📉 系統風險掃描</div>', unsafe_allow_html=True)
    if matrix_result['警報']:
        for alert in matrix_result['警報'][:3]:
            st.markdown(f'<div class="log-item">{alert}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="log-item" style="color:#2ecc71">結構穩定，無即時預警。</div>', unsafe_allow_html=True)

    # 3. 2x3 強化版板塊雷達
    st.markdown('<div class="section-title" style="margin-top: 20px;">🧭 板塊決策雷達</div>', unsafe_allow_html=True)
    insight_html = '<div class="insight-grid">'
    for p_num, d in palace_data.items():
        if p_num != 5 and not d['本人']:
            insight_html += f'<div class="insight-item"><div class="insight-label">{d["板塊"]}</div>{d["關係"]}</div>'
    st.markdown(insight_html + '</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)