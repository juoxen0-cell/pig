"""남은 한 끼: Streamlit Community Cloud에서 app.py를 실행하세요.
저장소 루트에 app.py와 requirements.txt를 함께 업로드합니다.
외부 API, API 키, 데이터베이스 없이 동작합니다.
"""
import io
import re
from urllib.parse import urlparse

import qrcode
import streamlit as st

st.set_page_config(page_title="남은 한 끼", page_icon="🥗", layout="centered")

FOODS = {
    "밥": {
        "title": "채소 달걀 볶음밥",
        "extra": "달걀, 잘게 썬 채소, 식용유 (있는 재료만 사용)",
        "steps": ["손과 조리도구를 씻고, 채소를 잘게 썰어 주세요.", "팬에 기름을 두르고 채소를 먼저 익혀 주세요.", "달걀을 넣었다면 완전히 익힌 뒤 밥을 넣어 골고루 볶아 주세요.", "음식 중심부까지 충분히 뜨겁게 익혀 주세요. 가능하면 식품용 온도계로 74°C 이상인지 확인하세요.", "먹을 만큼만 덜어 바로 먹고, 재가열한 음식은 다시 보관하지 않는 편이 안전해요."],
        "tip": "밥은 상온에 둔 시간이 특히 중요해요. 잘못 보관한 밥은 다시 가열해도 안전해지지 않을 수 있어요.",
    },
    "치킨·익힌 고기": {
        "title": "잘게 찢은 고기 덮밥",
        "extra": "밥, 양파, 물 약간, 간장 소량 (선택)",
        "steps": ["손과 조리도구를 씻고 뼈와 먹지 못하는 부분을 제거해 주세요.", "고기를 작게 찢고, 양파가 있다면 얇게 썰어 주세요.", "팬에 양파와 물을 조금 넣어 익힌 뒤 고기를 넣어 주세요.", "고기 중심부까지 충분히 뜨겁게 가열하세요. 가능하면 식품용 온도계로 74°C 이상인지 확인하세요.", "따뜻한 밥 위에 올려 바로 먹고, 재가열한 음식은 다시 보관하지 않는 편이 안전해요."],
        "tip": "뼈와 두꺼운 살 주변은 차갑게 남기 쉬워요. 작은 크기로 나누어 고르게 데우세요.",
    },
    "국·찌개": {
        "title": "국물로 만드는 한 그릇 국수",
        "extra": "국수 또는 우동 면, 물 약간 (선택)",
        "steps": ["손을 씻고 깨끗한 냄비에 먹을 만큼만 덜어 주세요.", "국물이 너무 짜면 물을 조금 넣어 주세요.", "국물과 건더기를 저어 가며 전체가 충분히 끓도록 가열해 주세요.", "제품 조리법에 맞게 따로 익힌 면을 넣고, 전체를 다시 충분히 뜨겁게 가열해 주세요.", "한 번 데운 양은 바로 먹고, 재가열한 음식은 다시 보관하지 않는 편이 안전해요."],
        "tip": "끓이기는 잘못된 보관을 되돌리는 방법이 아니에요. 안전하게 보관된 국물에만 적용하세요.",
    },
    "피자": {
        "title": "팬으로 바삭하게 데운 피자",
        "extra": "뚜껑 있는 팬, 물 몇 방울",
        "steps": ["깨끗한 팬에 먹을 만큼의 피자를 겹치지 않게 놓아 주세요.", "약한 불에서 바닥을 데워 주세요.", "피자에 직접 닿지 않는 팬 가장자리에 물 몇 방울을 넣고 뚜껑을 덮어 주세요. 증기에 데이지 않도록 주의하세요.", "토핑과 중심부까지 충분히 뜨겁게 익혀 주세요. 가능하면 식품용 온도계로 74°C 이상인지 확인하세요.", "바로 먹고, 재가열한 음식은 다시 보관하지 않는 편이 안전해요."],
        "tip": "치즈만 녹았다고 속까지 안전하게 데워진 것은 아니에요.",
    },
    "익힌 채소": {
        "title": "채소 달걀전",
        "extra": "달걀, 식용유, 밀가루 또는 부침가루 약간 (선택)",
        "steps": ["손과 도구를 씻고 익힌 채소를 잘게 잘라 주세요.", "깨끗한 그릇에 채소와 달걀을 넣어 섞어 주세요. 필요하면 가루를 조금 넣어 주세요.", "기름을 두른 팬에 반죽을 얇게 펼쳐 주세요.", "양면을 익히고 달걀이 흐르지 않도록 속까지 충분히 익혀 주세요. 가능하면 중심부 74°C 이상인지 확인하세요.", "먹을 만큼만 조리해 바로 먹고, 재가열한 음식은 다시 보관하지 않는 편이 안전해요."],
        "tip": "알레르기가 있다면 달걀·밀가루 등 추가 재료를 반드시 확인하세요.",
    },
    "속 없는 식빵·바게트": {
        "title": "바삭한 크루통",
        "extra": "식용유 또는 버터 소량 (선택)",
        "steps": ["빵 전체에 곰팡이·이상한 냄새가 없는지 살펴보세요. 이상이 있으면 조리를 멈추고 빵 전체를 버리세요.", "깨끗한 도구로 빵을 한입 크기로 잘라 주세요.", "팬에 기름이나 버터를 소량 넣고 약한 불에서 빵을 뒤집으며 바삭하게 구워 주세요.", "수프나 샐러드에 올려 바로 먹어 주세요."],
        "tip": "곰팡이가 핀 빵은 그 부분만 떼어 먹지 마세요. 크림·고기·달걀 등이 들어간 빵은 이 안내의 대상이 아니에요.",
    },
}

st.markdown("""<style>
.stApp {background: #f7faf7;}
.block-container {max-width: 760px; padding-top: 2rem; padding-bottom: 3rem;}
h1, h2, h3 {color: #205844;}
.stButton > button {border-radius: 12px; min-height: 48px;}
div[data-testid="stVerticalBlockBorderWrapper"] {border-radius: 16px;}
</style>""", unsafe_allow_html=True)

st.title("🥗 남은 한 끼")
st.write("남은 음식, 버리기 전에 확인해요. **안전 확인 → 활용 또는 처리 → 하나씩 체크!**")
st.caption("로그인·사진 업로드 없이 사용하는 간단한 앱 · 입력 내용은 별도 데이터베이스에 저장하지 않아요.")

with st.expander("먼저 알아두세요 · 식품 안전 기준과 한계"):
    st.markdown("""
- 냄새와 겉모습이 정상이어도 안전한 것은 아닙니다. **맛을 봐서 확인하지 마세요.**
- 이 앱은 진단 도구가 아닙니다. 보관 이력이 불확실하면 먹지 않는 쪽으로 안내합니다.
- 조리된 음식은 일반적으로 **2시간 이내**, 기온이 **32°C를 넘는 환경에서는 1시간 이내** 냉장하는 것이 기본 원칙입니다. 이 앱은 기준 시간에 도달한 경우에도 보수적으로 폐기를 권합니다.
- 냉장고는 **4°C 이하**를 기준으로 합니다. 일반 조리 잔반의 냉장 보관은 통상 3~4일 이내가 권장되지만, 이 앱은 보수적으로 **3일 이내**만 활용 후보로 안내합니다. 안전을 보증하는 기간은 아닙니다.
- 밥은 특히 빨리 식혀 냉장하고 **24시간 이내** 사용하는 보수적인 기준을 적용합니다. 가열해도 일부 독소는 없어지지 않을 수 있습니다.
- 냉동·해동한 음식, 생고기·생선·회, 유아식, 크림빵 등은 이 앱에서 판정하지 않습니다. 제품 표시와 별도 안전 지침을 확인하세요.
- 임신부·영유아·고령자·면역저하자는 더욱 주의하고, 조금이라도 의심되면 먹지 마세요.

참고: [USDA 잔반 보관·재가열](https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/leftovers-and-food-safety), [영국 FSA 밥 안전 안내](https://www.food.gov.uk/safety-hygiene/home-food-fact-checker)
""")

st.subheader("1. 음식과 보관 상태를 알려주세요")
with st.form("food_form"):
    food = st.selectbox("어떤 음식이 남았나요?", list(FOODS) + ["그 외 음식·판단하기 어려움"])
    condition = st.radio("현재 상태는 어떤가요?", ["이상 징후는 보이지 않아요", "곰팡이·이상한 냄새·끈적임·변색 등이 있어요", "잘 모르겠어요"])
    storage = st.radio("보관 상태를 골라 주세요", ["조리 후 신속히 냉장했고 계속 4°C 이하로 보관했어요", "상온에 두었거나 냉장 온도를 확신할 수 없어요", "냉동·해동했거나 보관 이력을 잘 모르겠어요"])
    exposure = st.radio("조리 후 냉장하기 전과 꺼내 둔 시간을 합치면?", ["2시간 미만이며, 32°C 초과 환경에서는 1시간 미만이에요", "2시간 이상이거나, 32°C 초과 환경에서 1시간 이상이에요", "정확히 모르겠어요"])
    age = st.radio("조리 후 얼마나 지났나요?", ["24시간 이내", "24시간 초과 ~ 3일 이내", "3일 초과", "잘 모르겠어요"])
    reheated = st.checkbox("이미 한 번 재가열한 음식이에요")
    submitted = st.form_submit_button("활용·처리 방법 확인하기", type="primary", use_container_width=True)

if submitted:
    reasons = []
    unsupported = food not in FOODS
    if condition != "이상 징후는 보이지 않아요":
        reasons.append("이상 징후가 있거나 상태를 확신할 수 없어요.")
    if storage != "조리 후 신속히 냉장했고 계속 4°C 이하로 보관했어요":
        reasons.append("안전한 냉장 보관 이력을 확인할 수 없어요.")
    if exposure != "2시간 미만이며, 32°C 초과 환경에서는 1시간 미만이에요":
        reasons.append("상온 노출이 길거나 정확한 시간을 알 수 없어요.")
    if age in ["3일 초과", "잘 모르겠어요"]:
        reasons.append("이 앱의 보수적인 보관 기간 기준을 충족하지 못해요.")
    if food == "밥" and age != "24시간 이내":
        reasons.append("밥은 냉장 후 24시간 이내 사용 기준으로 안내해요.")
    if reheated:
        reasons.append("이미 재가열한 음식은 이 앱에서 추가 활용을 권하지 않아요.")
    if unsupported:
        reasons.append("이 음식은 앱의 개별 안전 안내 범위 밖이에요. 제품 표시나 별도 지침으로 안전을 확인할 수 없다면 먹지 마세요.")
    st.session_state["result"] = {"food": food, "reasons": reasons, "unsupported": unsupported}
    st.session_state["check_version"] = st.session_state.get("check_version", 0) + 1

result = st.session_state.get("result")
if result:
    st.divider()
    st.subheader("2. 결과와 실행 체크리스트")
    st.caption("아래 결과는 마지막으로 ‘활용·처리 방법 확인하기’를 누른 내용이에요. 위 선택을 바꿨다면 다시 눌러 주세요.")
    reasons = result["reasons"]
    if reasons:
        st.warning("안전을 확인하기 어려워요. 이 앱에서는 재활용 조리를 권하지 않습니다.")
        for reason in reasons:
            st.write(f"• {reason}")
        title = "안전하게 처리하기"
        steps = [
            "맛을 보거나 반려동물에게 주지 말고, 먹을 음식과 분리해 주세요.",
            "뼈·껍데기·포장재 등 이물질을 분리하고, 국물은 식혀 건더기와 나눠 주세요.",
            "기름이나 음식물을 싱크대·변기·빗물받이에 붓지 마세요. 액체와 기름의 배출 방법은 지자체 안내를 확인하세요.",
            "음식물류 폐기물과 일반쓰레기의 구분은 지역마다 다를 수 있어요. 거주지 지자체 안내에 따라 전용 수거함이나 지정 봉투 등으로 배출하세요.",
            "음식이 닿은 용기와 조리대, 손을 깨끗하게 씻어 주세요.",
        ]
        extra = None
    else:
        recipe = FOODS[result["food"]]
        st.success("입력한 조건에서는 활용을 고려할 수 있어요. 안전을 보증하는 판정은 아니며, 의심되면 먹지 마세요.")
        title, steps, extra = recipe["title"], recipe["steps"], recipe["extra"]
        st.info(recipe["tip"])
    st.markdown(f"### {'🗑️' if reasons else '🍳'} {title}")
    st.write(f"선택한 음식: **{result['food']}**")
    if extra:
        st.write(f"추가 재료: {extra}")
        st.caption("추가 재료의 알레르기·소비기한도 확인해 주세요.")
    version = st.session_state.get("check_version", 0)
    if st.button("체크만 초기화", key="reset_checks"):
        version += 1
        st.session_state["check_version"] = version
    checks = [st.checkbox(f"{idx + 1}. {step}", key=f"step_{version}_{idx}") for idx, step in enumerate(steps)]
    completed = sum(checks)
    st.progress(completed / len(steps))
    st.caption(f"{len(steps)}단계 중 {completed}단계 완료")
    if all(checks):
        st.success("모든 단계를 완료했어요! 다음에는 먹을 만큼 덜고 남은 음식은 신속히 냉장해 주세요. 🌱")
    text = f"남은 한 끼 | {result['food']}\n{title}\n\n"
    text += "\n".join(f"{'[완료]' if checks[i] else '[ ]'} {i+1}. {step}" for i, step in enumerate(steps))
    st.download_button("📄 현재 체크리스트 저장", data=text.encode("utf-8-sig"), file_name="leftover_checklist.txt", mime="text/plain")
else:
    st.info("위에서 음식을 고르고 보관 상태를 입력하면 단계별 체크리스트가 나타나요.")

st.divider()
with st.expander("📱 QR코드로 이 앱 공유하기 · 배포 안내"):
    st.markdown("""
**GitHub → Streamlit Community Cloud → QR 접속**
1. GitHub 저장소의 같은 폴더에 `app.py`와 `requirements.txt`를 업로드하세요.
2. Streamlit Community Cloud에 로그인하고 **Create app**에서 저장소·브랜치를 선택하세요.
3. 실행 파일을 `app.py`로 지정하고 배포하세요. 공개 앱으로 배포하면 방문자의 로그인 없이 사용할 수 있어요.
4. 발급된 앱 주소를 아래에 붙여 넣고 QR 이미지를 다운로드하세요.
5. 휴대전화 카메라로 QR을 스캔하면 웹 앱이 열려요. 별도의 앱 설치는 필요 없어요.

로컬 실행: `pip install -r requirements.txt` 후 `streamlit run app.py`

QR에는 입력한 주소만 담깁니다. QR 생성 자체가 앱을 배포하거나 공개하지는 않아요. 로컬 주소는 다른 휴대전화에서 접근되지 않을 수 있어요.
""")
    url = st.text_input("배포된 앱의 https 주소", placeholder="https://your-app.streamlit.app", max_chars=2048)
    if url:
        clean_url = url.strip()
        try:
            parsed = urlparse(clean_url)
            valid = parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password and not re.search(r"\s", clean_url)
        except ValueError:
            valid = False
        if valid:
            try:
                image = qrcode.make(clean_url)
                buffer = io.BytesIO()
                image.save(buffer, format="PNG")
                png = buffer.getvalue()
                st.image(png, caption="휴대전화 카메라로 스캔하세요", width=240)
                st.download_button("QR 이미지 다운로드", data=png, file_name="leftover_app_qr.png", mime="image/png")
                st.caption("인쇄 전에 휴대전화에서 직접 스캔하고 앱 주소가 맞는지 확인하세요.")
            except (ValueError, qrcode.exceptions.DataOverflowError):
                st.error("QR로 만들기에는 주소가 너무 길어요. 배포된 앱의 기본 주소만 입력해 주세요.")
        else:
            st.warning("공백이나 로그인 정보 없이 https://로 시작하는 올바른 배포 주소를 입력해 주세요.")

st.caption("남은 한 끼 · 재사용보다 식품 안전이 먼저입니다. 체크 결과는 브라우저를 새로 열거나 세션이 종료되면 초기화될 수 있어요.")
