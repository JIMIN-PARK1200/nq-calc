import streamlit as st
import math

st.set_page_config(page_title="NQ 진입 비중 계산기", page_icon="📈")
st.title("📈 Micro E-mini NASDAQ (NQ) 진입 비중 계산기")

st.markdown("""
이 계산기는 진입가와 손절가를 입력하면 손절폭을 계산하고,
전체 자본의 **사용자 선택 손실 한도** 내에서 
진입 가능한 **최대 계약 수**, 예상 레버리지,
그리고 **진입 포지션 증거금 기준 실질 레버리지**를 계산해줍니다.

> 기준 상품: **Micro E-mini Nasdaq Futures (NQ)**  
> 1포인트당 $2 손익 발생 (1계약 기준)
""")

# 기본 설정
point_value = 2.0

# 세션 상태 초기화 및 사용자 식별
user_key = "default"

def get_initial_value(key, default):
    return st.session_state.user_data[user_key].get(key, default)

if "user_data" not in st.session_state:
    st.session_state.user_data = {}

if user_key not in st.session_state.user_data:
    st.session_state.user_data[user_key] = {
        "capital": 50000.0,
        "entry_price": 19000.0,
        "stop_price": 18900.0,
        "risk_percent": 0.05,
        "margin_per_contract": 1500.0,
    }

data = st.session_state.user_data[user_key]

# 사용자 입력
capital = st.number_input(
    "총 자본 입력 (USD)",
    min_value=1000.0,
    step=100.0,
    format="%.2f",
    value=get_initial_value("capital", 50000.0),
    key="capital",
)

entry_price = st.number_input(
    "진입가 입력",
    min_value=0.0,
    step=0.25,
    format="%.2f",
    value=get_initial_value("entry_price", 19000.0),
    key="entry_price",
)

stop_price = st.number_input(
    "손절가 입력",
    min_value=0.0,
    step=0.25,
    format="%.2f",
    value=get_initial_value("stop_price", 18900.0),
    key="stop_price",
)

risk_percent_choice = st.selectbox(
    "허용 손실 한도 (%)",
    options=[1, 2, 3, 4, 5],
    index=int(get_initial_value("risk_percent", 0.05) * 100) - 1
)

margin_per_contract = st.number_input(
    "계약당 증거금 (USD)",
    min_value=500.0,
    step=100.0,
    format="%.2f",
    value=get_initial_value("margin_per_contract", 1500.0),
    key="margin_per_contract",
    help="대부분 국내 증권사 기준 약 $1,500입니다."
)

# 입력값 저장
st.session_state.user_data[user_key]["capital"] = capital
st.session_state.user_data[user_key]["entry_price"] = entry_price
st.session_state.user_data[user_key]["stop_price"] = stop_price
st.session_state.user_data[user_key]["risk_percent"] = risk_percent_choice / 100.0
st.session_state.user_data[user_key]["margin_per_contract"] = margin_per_contract

# 계산 입력값
risk_percent = risk_percent_choice / 100.0

# 손절폭 계산
point_diff = abs(entry_price - stop_price)
stop_percent = point_diff / entry_price if entry_price > 0 else 0

# 계산 시작
risk_amount = capital * risk_percent
loss_per_contract = point_diff * point_value

if loss_per_contract == 0:
    st.warning("손절 기준이 너무 작거나 진입가가 0입니다.")
else:
    max_contracts = math.floor(risk_amount / loss_per_contract)
    position_value = max_contracts * entry_price * point_value
    leverage = position_value / capital if capital > 0 else 0
    used_margin = max_contracts * margin_per_contract
    margin_leverage = position_value / used_margin if used_margin > 0 else 0

    st.markdown("---")
    st.subheader("🧴 계산 결과")
    st.markdown(f"**✅ 최대 진입 가능 계약 수:** {max_contracts:,} 계약")
    st.markdown(f"**📊 예상 레버리지 (총 자본 기준):** {leverage:.1f}번")
    st.markdown(f"**🧩 진입 증가금 기준 리켜지:** {margin_leverage:.1f}번 (계약당 ${margin_per_contract:,.0f} 기준)")
    st.write(f"- 손절 기준: **{point_diff:.2f}pt** ({stop_percent * 100:.2f}%)")
    st.write(f"- 1계약당 손실 금액: **${loss_per_contract:,.2f}**")
    st.write(f"- 협용 손실 금액 ({risk_percent_choice}%): **${risk_amount:,.2f}**")

    if max_contracts == 0:
        st.error("⚠️ 이 조건으로는 진입 불가: 손실이 협용치를 초과합니다.")
