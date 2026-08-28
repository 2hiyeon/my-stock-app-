import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

# ----------------------------
# 기본 페이지 설정
# ----------------------------
st.set_page_config(
    page_title="주가 조회 앱",
    page_icon="📈",
    layout="centered"
)

# ----------------------------
# 따뜻한 톤을 위한 간단한 커스텀 스타일
# ----------------------------
st.markdown(
    """
    <style>
    .main {
        background-color: #FFF8E7;
    }
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(122, 92, 46, 0.08);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# 제목과 간단한 설명
# ----------------------------
st.title("📈 내 손안의 주가 조회")
st.write(
    "종목 코드를 입력하면 최근 1년 동안의 주가 흐름을 그래프로 보여드려요. "
    "예: 삼성전자 → **005930.KS**, 애플 → **AAPL**"
)

# ----------------------------
# 종목 코드 입력창
# ----------------------------
ticker_input = st.text_input(
    "종목 코드를 입력하세요",
    value="AAPL",
    placeholder="예: 005930.KS 또는 AAPL"
)

# 검색 버튼 (엔터로도 동작하지만, 명확하게 버튼도 하나 둡니다)
search_clicked = st.button("조회하기", type="primary")

# ----------------------------
# 실제 조회 로직
# ----------------------------
# 버튼을 누르거나, 입력값이 있으면 바로 조회하도록 처리
if ticker_input:
    ticker = ticker_input.strip().upper()  # 앞뒤 공백 제거 + 대문자로 통일

    try:
        # 오늘 날짜 기준으로 최근 1년 데이터 범위 계산
        end_date = datetime.today()
        start_date = end_date - timedelta(days=365)

        # yfinance로 주가 데이터 불러오기
        with st.spinner("주가 데이터를 불러오는 중이에요..."):
            data = yf.download(
                ticker,
                start=start_date.strftime("%Y-%m-%d"),
                end=end_date.strftime("%Y-%m-%d"),
                progress=False
            )

        # 데이터가 비어있으면 잘못된 종목 코드로 안내
        if data.empty:
            st.error("데이터를 찾을 수 없어요. 종목 코드를 다시 확인해 주세요. (예: 005930.KS, AAPL)")
        else:
            # yfinance가 여러 종목을 받을 때 컬럼이 다중 인덱스로 나올 수 있어서 정리해줌
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            # 종가(Close) 기준으로 계산
            close_prices = data["Close"].dropna()

            current_price = close_prices.iloc[-1]     # 가장 최근 종가 (현재가로 사용)
            start_price = close_prices.iloc[0]         # 1년 전 종가

            # 1년 등락률 계산 (%)
            change_rate = (current_price - start_price) / start_price * 100

            # ----------------------------
            # 종목명 가져오기 (실패해도 앱이 멈추지 않도록 처리)
            # ----------------------------
            try:
                info = yf.Ticker(ticker).info
                company_name = info.get("longName") or info.get("shortName") or ticker
            except Exception:
                company_name = ticker

            st.subheader(f"🏷️ {company_name} ({ticker})")

            # ----------------------------
            # 지표 카드: 현재가, 1년 등락률
            # ----------------------------
            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    label="현재가",
                    value=f"{current_price:,.2f}"
                )

            with col2:
                st.metric(
                    label="1년 등락률",
                    value=f"{change_rate:,.2f}%",
                    delta=f"{change_rate:,.2f}%"  # 색깔로 상승/하락 표시
                )

            # ----------------------------
            # Plotly 꺾은선 그래프 그리기
            # ----------------------------
            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=close_prices.index,
                    y=close_prices.values,
                    mode="lines",
                    name="종가",
                    line=dict(color="#FFB800", width=2),  # 따뜻한 노란색 톤
                    fill="tozeroy",
                    fillcolor="rgba(255, 184, 0, 0.1)"
                )
            )

            fig.update_layout(
                title="최근 1년 주가 흐름",
                xaxis_title="날짜",
                yaxis_title="가격",
                plot_bgcolor="#FFF8E7",
                paper_bgcolor="#FFFFFF",
                font=dict(color="#7A5C2E"),
                hovermode="x unified"
            )

            st.plotly_chart(fig, use_container_width=True)

            # ----------------------------
            # 원본 데이터 표로도 확인할 수 있게 (접어두기)
            # ----------------------------
            with st.expander("📋 원본 데이터 보기"):
                st.dataframe(data)

    except Exception as e:
        # 예상치 못한 오류가 나도 앱이 멈추지 않고 안내 메시지를 보여줌
        st.error(f"데이터를 불러오는 중 문제가 발생했어요: {e}")

else:
    st.info("종목 코드를 입력하면 주가 정보를 보여드려요.")
