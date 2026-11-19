import pandas as pd
import streamlit as st

# 1. 페이지 설정 (전체화면 와이드 레이아웃)
st.set_page_config(
    page_title="영화티켓 요금 안내 및 계산기", page_icon="🎬", layout="wide"
)

# 커스텀 CSS로 UI 스타일링 개선
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.5rem;
        color: #FF4B4B;
        text-align: center;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .sub-title {
        font-size: 1.2rem;
        color: #31333F;
        text-align: center;
        margin-bottom: 40px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 타이틀 출력
st.markdown(
    '<div class="main-title">🎬 영화티켓 요금 안내기</div>',
    unsafe_allow_html=True,
)

ex = st.expander('프로그램 설명 보기( 클릭해 보세요 )')
ex.info('**프로젝트 제목** : 부산시네마 극장의 영화티켓 요금을 안내')
ex.info('**주요 기능** : 영화티켓 요금표 안내 / 할인 혜택 안내 / 실시간 요금 계산 안내')

# 레이아웃 분할 (좌측: 요금표 및 안내 / 우측: 실시간 계산기)
col_left, col_right = st.columns([1,1], gap="large")

with col_left:
  st.subheader("📋 영화티켓 요금표")

  # 요금표 데이터프레임 구성
  pricing_data = {
      "구분": [
          "조조 (10:00 이전)",
          "일반 (10:00 이후) - 평일(월~목)",
          "일반 (10:00 이후) - 주말(금~일)",
          "일반 (10:00 이후)",
      ],
      "청소년 (~19세)": ["8,000원", "13,000원", "15,000원", "-"],
      "어른 (20세~)": ["10,000원", "15,000원", "17,000원", "-"],
      "특별관 3D ": ["-", "-", "-", "35,000원"],
  }
  df_price = pd.DataFrame(pricing_data)
  st.dataframe(df_price, use_container_width=True, hide_index=True)

  st.markdown("---")
  st.subheader("📌 할인 혜택 안내")
  st.info(
      """
        * **인원 할인**: 총 인원수(청소년, 어른) **4인 이상** 시 **총금액의 15% 할인**
        * **제휴카드 결재**: **총금액의 20% 할인**
        * ⚠️ **주의사항**: 할인 혜택은 **중복 적용이 불가**합니다 (더 큰 할인 혜택이 자동 적용됩니다).
        """
  )

with col_right:
  st.subheader("🧮 실시간 요금 계산기")

  with st.container():
    # 입력 필드 설정
    screen_type = st.radio(
        "상영관 선택", ["2D 상영관", "특별관 3D"], horizontal=True
    )

    if screen_type == "2D 상영관":
      time_slot = st.radio(
          "시간대 선택", ["조조 (10:00 이전)", "일반 (10:00 이후)"], horizontal=True
      )

      if "일반" in time_slot:
        day_type = st.radio(
            "요일 선택", ["평일 (월~목)", "주말 (금~일)"], horizontal=True
        )
      else:
        day_type = "해당없음"
    else:
      time_slot = "특별관 3D"
      day_type = "해당없음"

    st.markdown("---")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
      youth_count = st.number_input(
          "청소년 (~19세) 인원", min_value=0, max_value=20, value=0, step=1
      )
    with col_t2:
      adult_count = st.number_input(
          "어른 (20세~) 인원", min_value=0, max_value=20, value=0, step=1
      )

    discount_choice = st.selectbox(
        "적용할 할인 선택",
        [
            "자동 적용 (가장 유리한 할인)",
            "제휴카드 할인 (20%)",
            "4인 이상 다인승 할인 (15%)",
            "할인 없음",
        ],
    )

  # 요금 계산 로직
  total_people = youth_count + adult_count
  base_price = 0

  if screen_type == "특별관 3D":
    base_price = total_people * 35000
    y_price, a_price = 35000, 35000
  else:
    if "조조" in time_slot:
      y_price, a_price = 8000, 10000
    else:
      if "평일" in day_type:
        y_price, a_price = 13000, 15000
      else:
        y_price, a_price = 15000, 17000
    base_price = (youth_count * y_price) + (adult_count * a_price)

  # 할인 계산
  discount_amount = 0
  applied_discount_name = "할인 없음"

  card_discount = base_price * 0.20
  people_discount = base_price * 0.15 if total_people >= 4 else 0

  if discount_choice == "제휴카드 할인 (20%)":
    discount_amount = card_discount
    applied_discount_name = "제휴카드 결재 할인 (20%)"
  elif discount_choice == "4인 이상 다인승 할인 (15%)":
    discount_amount = people_discount
    applied_discount_name = "4인 이상 다인승 할인 (15%)"
  elif discount_choice == "자동 적용 (가장 유리한 할인)":
    if card_discount >= people_discount and card_discount > 0:
      discount_amount = card_discount
      applied_discount_name = "제휴카드 결재 할인 (20% 자동적용)"
    elif people_discount > card_discount and people_discount > 0:
      discount_amount = people_discount
      applied_discount_name = "4인 이상 다인승 할인 (15% 자동적용)"
    else:
      discount_amount = 0
      applied_discount_name = "적용 가능한 할인 없음"

  final_price = base_price - discount_amount

  # 결과 출력 영역
  st.markdown("---")
  st.subheader("💳 예매 내역 및 결제 금액")

  col_r1, col_r2, col_r3 = st.columns(3)
  col_r1.metric("총 관람 인원", f"{total_people} 명")
  col_r2.metric("기본 총금액", f"{base_price:,} 원")
  col_r3.metric(
      "최종 결제 금액",
      f"{int(final_price):,} 원",
      delta=f"-{int(discount_amount):,} 원"
      if discount_amount > 0
      else None,
      delta_color="inverse",
  )

  if discount_amount > 0:
    st.success(f"✨ 적용된 혜택: **{applied_discount_name}**")
  else:
    st.info("💡 4인 이상 관람 시 15% 또는 제휴카드 결제 시 20% 할인 혜택을 받으실 수 있습니다.")