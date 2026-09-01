import streamlit as st
import yfinance as yf
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# ------------------------------
# 페이지 기본 설정
# ------------------------------
st.set_page_config(page_title="주가 비교", page_icon="📈", layout="centered")

st.title("📈 내 주식 주가 비교")
st.write(
    "종목 코드를 입력하면 최근 주가 흐름을 그래프로 보여드려요. "
    "두 종목을 함께 입력하면 나란히 비교할 수 있어요.\n\n"
    "예시: 삼성전자 `005930.KS`, 애플 `AAPL`, 카카오 `035720.KS`"
)

# ------------------------------
# 종목 코드 입력창 (최대 2개)
# ------------------------------
col1, col2 = st.columns(2)
with col1:
    ticker1 = st.text_input("종목 코드 1", value="005930.KS", placeholder="예: 005930.KS")
with col2:
    ticker2 = st.text_input("종목 코드 2 (선택)", value="", placeholder="예: AAPL")

# ------------------------------
# 기간 선택 버튼
# 화면에 보이는 한글 라벨과 yfinance가 요구하는 기간 문자열을 짝지어 둡니다
# ------------------------------
period_options = {
    "1개월": "1mo",
    "6개월": "6mo",
    "1년": "1y",
    "5년": "5y",
}

# 버튼으로 고른 기간을 기억해두기 위한 저장소 (기본값: 1년)
if "selected_period_label" not in st.session_state:
    st.session_state.selected_period_label = "1년"

st.write("**기간 선택**")
period_cols = st.columns(len(period_options))
for col, label in zip(period_cols, period_options.keys()):
    # 현재 선택된 기간이면 강조된 버튼(primary)으로, 아니면 기본 버튼으로 표시
    is_selected = st.session_state.selected_period_label == label
    if col.button(label, type="primary" if is_selected else "secondary", use_container_width=True):
        st.session_state.selected_period_label = label

selected_period = period_options[st.session_state.selected_period_label]


# ------------------------------
# 주가 데이터 불러오기 (캐시를 사용해 같은 요청을 반복하지 않도록 함)
# ------------------------------
@st.cache_data(ttl=3600)
def load_price_data(ticker: str, period: str) -> pd.DataFrame:
    data = yf.Ticker(ticker).history(period=period)
    return data


def show_stock_section(ticker: str, color: str, y_axis: str, fig: go.Figure):
    """종목 하나에 대한 지표 카드 + 그래프 선을 그려주는 함수"""
    data = load_price_data(ticker, selected_period)

    if data.empty:
        st.error(f"'{ticker}' 종목의 데이터를 찾을 수 없어요. 코드를 다시 확인해 주세요.")
        return None

    시작가 = data["Close"].iloc[0]
    현재가 = data["Close"].iloc[-1]
    등락률 = (현재가 - 시작가) / 시작가 * 100
    최고가 = data["Close"].max()
    최저가 = data["Close"].min()
    평균가 = data["Close"].mean()

    # 위쪽 지표 카드: 현재가와 등락률
    m1, m2 = st.columns(2)
    m1.metric(f"{ticker} 현재가", f"{현재가:,.0f}")
    m2.metric(
        f"{ticker} {st.session_state.selected_period_label} 등락률",
        f"{등락률:+.2f}%",
    )

    # 그래프에 선 추가 (두 번째 종목은 보조 y축을 사용해 가격대가 달라도 잘 보이게 함)
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["Close"],
            mode="lines",
            name=ticker,
            line=dict(color=color, width=2),
        ),
        secondary_y=(y_axis == "right"),
    )

    return {"최고가": 최고가, "최저가": 최저가, "평균가": 평균가}


# ------------------------------
# 그래프 그리기 + 통계 계산
# ------------------------------
if not ticker1:
    st.info("왼쪽 입력창에 종목 코드를 입력해 주세요.")
else:
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    st.subheader("가격 추이")
    stats1 = show_stock_section(ticker1, color="#1D9E75", y_axis="left", fig=fig)
    stats2 = None
    if ticker2:
        stats2 = show_stock_section(ticker2, color="#D85A30", y_axis="right", fig=fig)

    fig.update_layout(
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=10, t=30, b=10),
    )
    fig.update_yaxes(title_text=f"{ticker1} 가격", secondary_y=False)
    if ticker2:
        fig.update_yaxes(title_text=f"{ticker2} 가격", secondary_y=True)

    st.plotly_chart(fig, use_container_width=True)

    # ------------------------------
    # 그래프 아래 통계 카드: 최고가 · 최저가 · 평균가
    # ------------------------------
    st.subheader("기간 내 가격 통계")

    if stats1 is not None:
        st.write(f"**{ticker1}**")
        s1, s2, s3 = st.columns(3)
        s1.metric("최고가", f"{stats1['최고가']:,.0f}")
        s2.metric("최저가", f"{stats1['최저가']:,.0f}")
        s3.metric("평균가", f"{stats1['평균가']:,.0f}")

    if stats2 is not None:
        st.write(f"**{ticker2}**")
        s1, s2, s3 = st.columns(3)
        s1.metric("최고가", f"{stats2['최고가']:,.0f}")
        s2.metric("최저가", f"{stats2['최저가']:,.0f}")
        s3.metric("평균가", f"{stats2['평균가']:,.0f}")
