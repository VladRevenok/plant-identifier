import streamlit as st
import requests
from PIL import Image
import io
import base64
import wikipedia
import re

st.set_page_config(
    page_title="🌿 Plant Identifier",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── Стилі ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;500;600&display=swap');

/* Базові налаштування */
html, body  {
    font-family: 'Inter', sans-serif;
    
}

/* Заголовки */
.main-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.6rem;
    color: #1a3d2b;
    text-align: center;
    margin: 0.5rem 0 0.2rem 0;
}
.subtitle {
    text-align: center;
    color: #5a7a65;
    font-size: 1.05rem;
    margin-bottom: 2rem;
}

/* XP панель */
.xp-bar {
    background: linear-gradient(135deg, #1a3d2b 0%, #2e7d32 100%);
    border-radius: 16px;
    padding: 14px 22px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
    box-shadow: 0 4px 15px rgba(46,125,50,0.25);
    color: white;
}
.xp-user {
    font-size: 1.1rem;
    font-weight: 600;
}
.xp-value {
    font-size: 0.9rem;
    opacity: 0.9;
    margin-top: 3px;
}
.xp-badge {
    background: rgba(255,255,255,0.22);
    color: white;
    font-size: 1.5rem;
    font-weight: 700;
    padding: 8px 20px;
    border-radius: 50px;
}

/* Картки API та переможець */
.api-card {
    background: white;
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 12px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    border-left: 5px solid #4caf50;
    display: flex;
    align-items: center;
    gap: 16px;
}
.api-card.plantid {
    border-left-color: #2196f3;
}
.api-name {
    font-size: 0.8rem;
    font-weight: 600;
    color: #777;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}
.plant-name {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    color: #1a3d2b;
    font-weight: 700;
}
.common-name {
    font-size: 0.95rem;
    color: #6a8f75;
    margin-top: 2px;
}
.score-badge {
    margin-left: auto;
    background: #e8f5e9;
    color: #2e7d32;
    font-size: 1.35rem;
    font-weight: 700;
    padding: 8px 16px;
    border-radius: 50px;
    min-width: 80px;
    text-align: center;
}
.score-badge.blue {
    background: #e3f2fd;
    color: #1565c0;
}

/* Переможець */
.winner-card {
    background: linear-gradient(135deg, #1a3d2b 0%, #2e7d32 100%);
    border-radius: 20px;
    padding: 24px;
    color: white;
    text-align: center;
    margin: 20px 0;
    box-shadow: 0 6px 24px rgba(46,125,50,0.3);
}
.winner-label {
    font-size: 0.85rem;
    letter-spacing: 1px;
    text-transform: uppercase;
    opacity: 0.8;
    margin-bottom: 8px;
}
.winner-name {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 6px;
}
.winner-common {
    font-size: 1.1rem;
    opacity: 0.9;
    margin-bottom: 12px;
}
.winner-score {
    display: inline-block;
    background: rgba(255,255,255,0.25);
    padding: 8px 24px;
    border-radius: 50px;
    font-size: 1.4rem;
    font-weight: 700;
}

/* Інформаційний блок */
.info-block {
    background: #f9fbe7;
    border-radius: 14px;
    padding: 20px 22px;
    margin: 16px 0;
    border-left: 5px solid #aed581;
    font-size: 0.98rem;
    line-height: 1.7;
    color: #2d4a1e;
}
.info-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.25rem;
    color: #33691e;
    margin-bottom: 12px;
    font-weight: 700;
}

/* Результати відповідей */
.result-correct {
    background: #e8f5e9;
    border: 2px solid #4caf50;
    border-radius: 10px;
    padding: 14px;
    color: #1b5e20;
    font-weight: 600;
    text-align: center;
    margin: 8px 0;
}
.result-wrong {
    background: #ffebee;
    border: 2px solid #ef5350;
    border-radius: 10px;
    padding: 14px;
    color: #b71c1c;
    font-weight: 600;
    text-align: center;
    margin: 8px 0;
}

/* XP за вікторину */
.xp-gained {
    background: linear-gradient(135deg, #f9a825 0%, #f57f17 100%);
    border-radius: 14px;
    padding: 18px;
    color: white;
    text-align: center;
    margin: 16px 0;
    box-shadow: 0 4px 15px rgba(245,127,23,0.3);
}
.xp-gained-title {
    font-size: 1.05rem;
    opacity: 0.92;
    margin-bottom: 6px;
}
.xp-gained-value {
    font-family: 'Playfair Display', serif;
    font-size: 2.4rem;
    font-weight: 700;
}

/* Роздільник */
.divider {
    border: none;
    border-top: 1px solid #e0e0e0;
    margin: 20px 0;
}

/* ── КОЛЕКЦІЯ ── (оновлена, всі картки однакові) */
.plant-card {
    border: 3px solid #4caf50;
    border-radius: 16px;
    padding: 12px;
    background: white;
    text-align: center;
    box-shadow: 0 5px 18px rgba(76,175,80,0.18);
    transition: all 0.18s ease;
    height: 340px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.plant-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 28px rgba(76,175,80,0.28);
}
.plant-card img {
    width: 100%;
    height: 200px;
    object-fit: cover;
    border-radius: 10px;
    margin-bottom: 12px;
    background: #f0f4f0;
}
.plant-card .title {
    font-family: 'Playfair Display', serif;
    font-size: 1.22rem;
    font-weight: 700;
    color: #1a3d2b;
    line-height: 1.25;
    margin-bottom: 6px;
}
.plant-card .common {
    font-size: 0.94rem;
    color: #5e7a68;
    line-height: 1.3;
}

/* Адаптивність для мобілки */
@media (max-width: 768px) {
    .plant-card {
        height: 320px;
    }
    .plant-card img {
        height: 180px;
    }
    .plant-card .title {
        font-size: 1.15rem;
    }
}
</style>
""", unsafe_allow_html=True)

# ── Ключі ──────────────────────────────────────────────────────────────────────
PLANTNET_KEY = st.secrets["PLANTNET_KEY"]
PLANTID_KEY = st.secrets["PLANTID_KEY"]
GROQ_KEY = st.secrets["GROQ_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# ── Supabase ───────────────────────────────────────────────────────────────────
def sb_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

def get_or_create_user(username: str) -> dict:
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/users?username=eq.{username}&select=*",
        headers=sb_headers()
    )
    data = resp.json()
    if data:
        return data[0]
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/users",
        headers={**sb_headers(), "Prefer": "return=representation"},
        json={"username": username, "xp": 0, "plants": []}
    )
    return resp.json()[0]

def update_user_xp(username: str, new_xp: int):
    requests.patch(
        f"{SUPABASE_URL}/rest/v1/users?username=eq.{username}",
        headers=sb_headers(),
        json={"xp": new_xp}
    )

def add_plant_to_collection(username: str, plant_data: dict, current_plants: list):
    name = plant_data.get("name", "")
    exists = any(
        (isinstance(p, dict) and p.get("name") == name) or
        (isinstance(p, str) and p == name)
        for p in current_plants
    )
    if exists:
        return current_plants
    new_plants = current_plants + [plant_data]
    requests.patch(
        f"{SUPABASE_URL}/rest/v1/users?username=eq.{username}",
        headers=sb_headers(),
        json={"plants": new_plants}
    )
    return new_plants

# ── Фото з Вікіпедії (найнадійніший спосіб) ────────────────────────────────
def get_wiki_image(plant_name: str) -> str:
    """
    Бере перше придатне фото зі списку page.images
    Повертає повнорозмірне посилання або ''
    """
    for lang in ["uk", "en"]:
        wikipedia.set_lang(lang)
        try:
            page = wikipedia.page(plant_name, auto_suggest=True)

            for img_url in page.images:
                # беремо тільки ймовірно реальні фотографії
                if any(ext in img_url.lower() for ext in [".jpg", ".jpeg", ".png", ".gif"]):
                    # виключаємо очевидний непотріб
                    if any(bad in img_url.lower() for bad in ["logo", "flag", "map", "coat", "seal", "icon", "symbol", "emblem"]):
                        continue

                    # намагаємося отримати повнорозмірне зображення (без /thumb/)
                    if "/thumb/" in img_url:
                        # прибираємо частину /thumb/ і розмір
                        parts = img_url.split("/thumb/")
                        if len(parts) == 2:
                            base = parts[0] + "/"
                            filename = parts[1].split("/")[-1].split("-")[-1]
                            full_url = base + filename
                            return full_url
                    else:
                        return img_url

            # якщо жодне не підійшло — беремо перше з .jpg / .jpeg
            for img_url in page.images:
                if ".jpg" in img_url or ".jpeg" in img_url:
                    return img_url

        except wikipedia.exceptions.DisambiguationError as e:
            # якщо є варіанти — беремо перший
            if e.options:
                try:
                    return get_wiki_image(e.options[0])
                except:
                    pass
        except:
            pass

    return ""  # нічого не знайшли

# ── PlantNet ───────────────────────────────────────────────────────────────────
def identify_plantnet(image_bytes):
    try:
        files = [("images", ("image.jpg", image_bytes, "image/jpeg"))]
        params = {"api-key": PLANTNET_KEY}
        resp = requests.post(
            "https://my-api.plantnet.org/v2/identify/all",
            files=files, params=params, timeout=30
        )
        if resp.status_code != 200:
            return {"error": f"HTTP {resp.status_code}"}
        results = resp.json().get("results", [])
        if not results:
            return {"error": "Немає результатів"}
        top = results[0]
        species = top.get("species", {})
        name = species.get("scientificNameWithoutAuthor") or species.get("scientificName", "Невідомо")
        common = species.get("commonNames", [])
        return {"success": True, "name": name,
                "common_name": common[0] if common else "",
                "score": top.get("score", 0.0)}
    except Exception as e:
        return {"error": str(e)}

# ── Plant.id ───────────────────────────────────────────────────────────────────
def identify_plantid(image_bytes):
    try:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        headers = {"Content-Type": "application/json", "Api-Key": PLANTID_KEY}
        data = {"images": [b64], "modifiers": ["similar_images"],
                "plant_details": ["common_names", "taxonomy"]}
        resp = requests.post("https://api.plant.id/v2/identify",
                             json=data, headers=headers, timeout=30)
        if resp.status_code == 429:
            return {"error": "Перевищено ліміт (100/місяць)"}
        if resp.status_code != 200:
            return {"error": f"HTTP {resp.status_code}"}
        suggestions = resp.json().get("suggestions", [])
        if not suggestions:
            return {"error": "Немає результатів"}
        top = suggestions[0]
        common = top.get("plant_details", {}).get("common_names", [])
        return {"success": True, "name": top.get("plant_name", "Невідомо"),
                "common_name": common[0] if common else "",
                "score": top.get("probability", 0.0)}
    except Exception as e:
        return {"error": str(e)}

# ── Wikipedia summary ─────────────────────────────────────────────────────────
def get_wiki_raw(plant_name: str) -> str:
    for lang in ("uk", "en"):
        wikipedia.set_lang(lang)
        try:
            return wikipedia.summary(plant_name, sentences=8, auto_suggest=True)
        except wikipedia.exceptions.DisambiguationError as e:
            try:
                return wikipedia.summary(e.options[0], sentences=8)
            except:
                continue
        except:
            continue
    return ""

# ── Groq ───────────────────────────────────────────────────────────────────────
def groq_request(prompt: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    body = {"model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000}
    resp = requests.post(url, json=body, headers=headers, timeout=30)
    if resp.status_code != 200:
        raise Exception(f"Groq HTTP {resp.status_code}")
    return resp.json()["choices"][0]["message"]["content"]

def get_plant_summary(plant_name: str, wiki_text: str) -> str:
    if not wiki_text:
        prompt = (
            f"Напиши про рослину '{plant_name}' коротко — 4-5 речень українською мовою. "
            f"Розкажи що це за рослина, де росте і чим цікава. "
            f"Текст повинен бути простим і зрозумілим. Відповідай тільки текстом."
        )
    else:
        prompt = (
            f"Ось інформація з Вікіпедії про рослину '{plant_name}':\n\n{wiki_text}\n\n"
            f"Перепиши українською мовою у 4-5 простих речень. "
            f"Залиш тільки найцікавіші факти. Відповідай тільки текстом."
        )
    return groq_request(prompt)

def get_plant_questions(plant_name: str, summary: str) -> list:
    prompt = (
        f"Based on this text about plant '{plant_name}':\n\n{summary}\n\n"
        f"Write exactly 3 quiz questions in Ukrainian. "
        f"Use this EXACT format:\n\n"
        f"ПИТАННЯ1: текст питання\n"
        f"A: варіант\nB: варіант\nC: варіант\nD: варіант\n"
        f"ВІДПОВІДЬ1: A\n\n"
        f"ПИТАННЯ2: текст питання\n"
        f"A: варіант\nB: варіант\nC: варіант\nD: варіант\n"
        f"ВІДПОВІДЬ2: B\n\n"
        f"ПИТАННЯ3: текст питання\n"
        f"A: варіант\nB: варіант\nC: варіант\nD: варіант\n"
        f"ВІДПОВІДЬ3: C"
    )
    raw = groq_request(prompt)
    return parse_questions(raw)

def parse_questions(text: str) -> list:
    questions = []
    blocks = re.split(r"ПИТАННЯ\d+:", text)
    blocks = [b.strip() for b in blocks if b.strip()]
    for block in blocks:
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if len(lines) < 6:
            continue
        question_text = lines[0]
        options = []
        answer = "A"
        for line in lines[1:]:
            if re.match(r"^[ABCD]:", line):
                letter = line[0]
                text_part = line[2:].strip()
                options.append(f"{letter}) {text_part}")
            elif re.match(r"^ВІДПОВІДЬ\d+:", line):
                answer = line.split(":")[-1].strip().upper()
        if len(options) == 4:
            questions.append({"question": question_text, "options": options, "answer": answer})
    return questions[:3]

# ── XP бар ─────────────────────────────────────────────────────────────────────
def show_xp_bar():
    user = st.session_state.get("user")
    if not user:
        return
    xp = user.get("xp", 0)
    username = user.get("username", "")
    level = xp // 100 + 1
    stars = "⭐" * min(level, 5)
    st.markdown(f"""
    <div class="xp-bar">
        <div>
            <div class="xp-user">👤 {username}</div>
            <div class="xp-value">Рівень {level} {stars}</div>
        </div>
        <div class="xp-badge">✨ {xp} XP</div>
    </div>
    """, unsafe_allow_html=True)
    

# ── Діалог вікторини ───────────────────────────────────────────────────────────
@st.dialog("❓ Перевір себе!", width="large")
def show_questions_dialog(questions: list):
    st.markdown("Відповідай на питання — перевір що запам'ятав про рослину!")
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    
    answers = {}
    for i, q in enumerate(questions):
        st.markdown(
            f"""
            <div style="
                font-weight: 700;
                font-size: 1.15rem;
                color: white;
                background: #2e7d32;
                padding: 10px 14px;
                border-radius: 8px;
                margin-bottom: 12px;
                line-height: 1.4;
            ">
                Питання {i+1}: {q["question"]}
            </div>
            """,
            unsafe_allow_html=True
        )
        choice = st.radio(
            label=f"q{i}",
            options=q["options"],
            index=None,
            label_visibility="collapsed",
            key=f"radio_{i}"
        )
        answers[i] = {"choice": choice, "correct": q["answer"]}
        st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        check = st.button("✅ Перевірити відповіді", use_container_width=True, type="primary")
    with col2:
        if st.button("✕ Закрити", use_container_width=True, key="close_q"):
            st.rerun()
    
    if check:
        score = 0
        for i, q in enumerate(questions):
            user_ans = answers[i]["choice"]
            correct_letter = answers[i]["correct"]  # "A", "B", "C" або "D"
            
            correct_option = next(
                (o for o in q["options"] if o.startswith(correct_letter + ")")),
                correct_letter
            )
            
            if user_ans is None:
                st.warning(f"Питання {i+1}: відповідь не вибрана")
            elif user_ans and user_ans.startswith(correct_letter + ")"):
                score += 1
                st.markdown(
                    f'<div class="result-correct">✅ Питання {i+1}: Правильно! {correct_option}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="result-wrong">❌ Питання {i+1}: Неправильно. '
                    f'Правильна відповідь: {correct_option}</div>',
                    unsafe_allow_html=True
                )
        
        xp_gained = score * 10
        total = len(questions)
        st.markdown("<br>", unsafe_allow_html=True)
        
        if score == total:
            st.success(f"🏆 Чудово! {score}/{total} — всі відповіді правильні!")
        elif score >= total // 2:
            st.info(f"👍 Непогано! {score}/{total} правильних відповідей")
        else:
            st.warning(f"📖 {score}/{total} — варто ще раз перечитати про рослину")
        
        # ── НАРАХУВАННЯ XP ТА ДОДАВАННЯ В КОЛЕКЦІЮ ──
        plant_name = st.session_state.get("last_plant_name", "")
        
        if xp_gained > 0 and st.session_state.get("user"):
            user = st.session_state["user"]
            new_xp = user["xp"] + xp_gained
            username = user["username"]
            
            update_user_xp(username, new_xp)
            
            current_plants = user.get("plants", []) or []
            
            image_url = get_wiki_image(plant_name)
            plant_data = {
                "name": plant_name,
                "common_name": st.session_state.get("last_common_name", ""),
                "image_url": image_url
            }
            
            # Додаємо тільки якщо немає в колекції
            if not any(
                (isinstance(p, dict) and p.get("name") == plant_name) or
                (isinstance(p, str) and p == plant_name)
                for p in current_plants
            ):
                new_plants = current_plants + [plant_data]
                requests.patch(
                    f"{SUPABASE_URL}/rest/v1/users",
                    headers=sb_headers(),
                    params={"username": f"eq.{username}"},
                    json={"plants": new_plants}
                )
                st.session_state.user["plants"] = new_plants
                st.success(f"🌿 Рослина **{plant_name}** додана до твоєї колекції!")
            else:
                new_plants = current_plants
            
            # Оновлюємо сесію
            st.session_state["user"]["xp"] = new_xp
            st.session_state["user"]["plants"] = new_plants
            
            # Показуємо блок з XP
            st.markdown(f"""
            <div class="xp-gained">
                <div class="xp-gained-title">Зароблено XP за цю вікторину</div>
                <div class="xp-gained-value">+{xp_gained} ✨</div>
                <div style="margin-top:6px;opacity:0.9;font-size:0.9rem;">
                    Загальний рахунок: {new_xp} XP
                </div>
            </div>
            """, unsafe_allow_html=True)
# ── Діалог результатів сканування ─────────────────────────────────────────────
@st.dialog("🌿 Результат сканування", width="large")
def show_results_dialog(pnet: dict, pid: dict):
    def api_card(data, label, icon, css_class="", badge_class=""):
        if data.get("success"):
            common_html = f'<div class="common-name">{data["common_name"]}</div>' if data.get("common_name") else ""
            st.markdown(f"""
            <div class="api-card {css_class}">
                <div style="font-size:1.8rem">{icon}</div>
                <div>
                    <div class="api-name">{label}</div>
                    <div class="plant-name">{data['name']}</div>
                    {common_html}
                </div>
                <div class="score-badge {badge_class}">{data['score']*100:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning(f"{label}: {data.get('error', 'Помилка')}")

    api_card(pnet, "PlantNet", "🌿", "")
    api_card(pid, "Plant.id", "🤖", "plantid", "blue")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    candidates = {}
    if pnet.get("success"): candidates["PlantNet"] = pnet
    if pid.get("success"): candidates["Plant.id"] = pid
    if not candidates:
        st.error("Жоден API не розпізнав рослину 😔")
        return

    best_api, best = max(candidates.items(), key=lambda x: x[1]["score"])
    st.session_state["last_common_name"] = best.get("common_name", "")

    common_html = f'<div class="winner-common">{best["common_name"]}</div>' if best.get("common_name") else ""
    st.markdown(f"""
    <div class="winner-card">
        <div class="winner-label">Найвища впевненість · {best_api}</div>
        <div class="winner-name">{best['name']}</div>
        {common_html}
        <div class="winner-score">{best['score']*100:.1f}% впевненості</div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Готуємо інформацію про рослину..."):
        wiki_raw = get_wiki_raw(best["name"])
        try:
            summary = get_plant_summary(best["name"], wiki_raw)
        except Exception as e:
            summary = wiki_raw[:600] if wiki_raw else "Не вдалося отримати інформацію."
            st.warning(f"Groq недоступний: {e}")
    st.session_state["last_summary"] = summary
    st.session_state["last_plant_name"] = best["name"]
    st.session_state["questions"] = None
    st.markdown(f"""
    <div class="info-block">
        <div class="info-title">📚 Про рослину</div>
        {summary.replace('\n', '<br>')}
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("❓ Перевірити знання", use_container_width=True, type="primary"):
            with st.spinner("Генеруємо питання..."):
                try:
                    qs = get_plant_questions(
                        st.session_state["last_plant_name"],
                        st.session_state["last_summary"]
                    )
                    st.session_state["questions"] = qs
                    st.session_state["open_questions"] = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Помилка генерації питань: {e}")
    with col2:
        if st.button("✕ Закрити", use_container_width=True, key="close_main"):
            st.rerun()

# ── Діалог колекції ────────────────────────────────────────────────────────────
@st.dialog("🌿 Моя колекція рослин", width="large")
def show_collection_dialog():
    plants = st.session_state["user"].get("plants", []) or []
    if not plants:
        st.info("🌱 Колекція порожня. Скануй рослини, щоб наповнити її!")
        return
    
    st.markdown(f"### 🌿 Твоя колекція — {len(plants)} рослин")
    
    # Кнопка очистки
    if st.button("🗑️ Очистити всю колекцію", type="secondary"):
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/users",
            headers=sb_headers(),
            params={"username": f"eq.{st.session_state.user['username']}"},
            json={"plants": []}
        )
        st.session_state.user["plants"] = []
        st.success("Колекцію очищено!")
        st.rerun()

    # По 4 рослини в рядок (маленькі картки)
    for i in range(0, len(plants), 4):
        cols = st.columns(4)
        for j, plant in enumerate(plants[i:i+4]):
            with cols[j]:
                if isinstance(plant, str):
                    name = plant
                    common = ""
                    url = ""
                else:
                    name = plant.get("name", "Без назви")
                    common = plant.get("common_name", "")
                    url = plant.get("image_url", "")

                placeholder = f"https://placehold.co/300x200/4caf50/white/png?text={name.replace(' ', '+')[:15]}"
                img_src = url or placeholder

                html = f"""
                <div class="plant-card">
                    <img src="{img_src}" 
                         onerror="this.src='{placeholder}'"
                         style="width:100%; height:200px; object-fit:cover; border-radius:10px;">
                    <div class="title">{name}</div>
                    {f'<div class="common">{common}</div>' if common else ''}
                </div>
                """
                st.markdown(html, unsafe_allow_html=True)

# ── Логін ──────────────────────────────────────────────────────────────────────
def show_login():
    st.markdown('<div class="main-title">🌿 Plant Identifier</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Введи своє ім\'я щоб почати</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name = st.text_input("Твоє ім'я:", placeholder="Наприклад: Name123", max_chars=30)
        if st.button("▶ Почати", use_container_width=True, type="primary"):
            name = name.strip()
            if not name:
                st.warning("Введи своє ім'я!")
            else:
                with st.spinner("Завантажуємо твій профіль..."):
                    try:
                        user = get_or_create_user(name)
                        st.session_state["user"] = user
                        st.rerun()
                    except Exception as e:
                        st.error(f"Помилка підключення до бази даних: {e}")

# ── Головна логіка ─────────────────────────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state["user"] = None
if "questions" not in st.session_state:
    st.session_state["questions"] = None
if "open_questions" not in st.session_state:
    st.session_state["open_questions"] = False
if "last_common_name" not in st.session_state:
    st.session_state["last_common_name"] = ""
if "quiz_completed_for_plant" not in st.session_state:
    st.session_state.quiz_completed_for_plant = set()   # множина пройдених рослин

if not st.session_state["user"]:
    show_login()
    st.stop()

if st.session_state.get("open_questions") and st.session_state.get("questions"):
    st.session_state["open_questions"] = False
    show_questions_dialog(st.session_state["questions"])

show_xp_bar()
st.markdown('<div class="main-title">🌿 Plant Identifier</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Завантаж фото — дізнайся що за рослина</div>', unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Оберіть фото рослини:",
    type=["jpg", "jpeg", "png"],
    label_visibility="collapsed"
)

if uploaded:
    img = Image.open(uploaded).convert("RGB")
    st.image(img, caption="Завантажене фото", use_container_width=True)
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_bytes = buffered.getvalue()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 Сканувати рослину", use_container_width=True, type="primary"):
            with st.spinner("Розпізнаємо рослину..."):
                pnet_result = identify_plantnet(img_bytes)
                pid_result = identify_plantid(img_bytes)
            show_results_dialog(pnet_result, pid_result)

# ── Сайдбар ────────────────────────────────────────────────────────────────────
with st.sidebar:
    user = st.session_state["user"]
    st.markdown(f"👤 **{user['username']}**")
    st.markdown(f"✨ **{user['xp']} XP**")
    plants = user.get("plants", []) or []
    st.markdown(f"🌿 **{len(plants)} рослин** у колекції")
    st.markdown("---")
    if st.button("📖 Переглянути колекцію", use_container_width=True):
        show_collection_dialog()
    if st.button("🚪 Вийти"):
        st.session_state["user"] = None
        st.rerun()
