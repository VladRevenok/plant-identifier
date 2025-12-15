import streamlit as st
import requests
from PIL import Image
import io
import base64
from typing import Dict, List

# ==============
# Налаштування сторінки
# ==============
st.set_page_config(page_title="Plant Identifier - 3 API", layout="centered")
st.title("🌿 Plant Identifier - Три API")

# -------------------------------
# API KEYS
# -------------------------------
PLANTNET_KEY = "2b105FYLbg34pvfXRESKZMMKO"
PLANTID_KEY = "HxlpPMRKG5HxLVhO9ug43DXFQfJ6LsLF6T4TKj9BCuyWVKzhmJ"
PERENUAL_KEY = "sk-oQbZ693ec348b4aa213954"  # <<< Отримай на https://perenual.com/docs/api

# -------------------------------
# 1. PlantNet API
# -------------------------------
def identify_plantnet(image_bytes):
    """PlantNet API"""
    try:
        files = [("images", ("image.jpg", image_bytes, "image/jpeg"))]
        params = {"api-key": PLANTNET_KEY}
        
        resp = requests.post(
            "https://my-api.plantnet.org/v2/identify/all",
            files=files,
            params=params,
            timeout=30
        )
        
        if resp.status_code != 200:
            return {"error": f"Помилка HTTP {resp.status_code}"}
        
        data = resp.json()
        results = []
        
        for item in data.get("results", [])[:5]:
            species = item.get("species", {})
            name = species.get("scientificNameWithoutAuthor") or species.get("scientificName", "Невідомо")
            common = species.get("commonNames", [])
            common_name = common[0] if common else ""
            score = item.get("score", 0.0)
            
            results.append({
                "name": name,
                "common_name": common_name,
                "score": score
            })
        
        return {"results": results, "success": True}
    
    except Exception as e:
        return {"error": str(e)}

# -------------------------------
# 2. Plant.id (Kindwise) API
# -------------------------------
def identify_plantid(image_bytes):
    """Plant.id API"""
    try:
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        headers = {
            "Content-Type": "application/json",
            "Api-Key": PLANTID_KEY
        }
        
        data = {
            "images": [base64_image],
            "modifiers": ["similar_images"],
            "plant_details": ["common_names", "taxonomy"]
        }
        
        resp = requests.post(
            "https://api.plant.id/v2/identify",
            json=data,
            headers=headers,
            timeout=30
        )
        
        if resp.status_code == 429:
            return {"error": "Перевищено ліміт запитів (100/місяць)"}
        
        if resp.status_code != 200:
            return {"error": f"Помилка HTTP {resp.status_code}"}
        
        result = resp.json()
        suggestions = result.get("suggestions", [])[:5]
        
        results = []
        for item in suggestions:
            name = item.get("plant_name", "Невідомо")
            probability = item.get("probability", 0.0)
            common = item.get("plant_details", {}).get("common_names", [])
            common_name = common[0] if common else ""
            
            results.append({
                "name": name,
                "common_name": common_name,
                "score": probability
            })
        
        return {"results": results, "success": True}
    
    except Exception as e:
        return {"error": str(e)}

# -------------------------------
# 3. Perenual API
# -------------------------------
def identify_perenual(image_bytes):
    """Perenual Plant ID API"""
    
    if not PERENUAL_KEY:
        return {"error": "API ключ не налаштований. Отримай на https://perenual.com/docs/api"}
    
    try:
        # Конвертуємо зображення в base64
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        # Perenual Identification API endpoint
        url = "https://perenual.com/api/v1/identify"
        
        # Формат запиту (можна відправити або URL, або base64)
        # Спробуємо multipart/form-data як у PlantNet
        files = {
            'image': ('plant.jpg', image_bytes, 'image/jpeg')
        }
        
        params = {
            'key': PERENUAL_KEY
        }
        
        resp = requests.post(
            url,
            files=files,
            params=params,
            timeout=30
        )
        
        if resp.status_code == 401:
            return {"error": "Неправильний API ключ або немає доступу до Identification API. Приєднайся до waitlist на https://perenual.com/docs/identify/api"}
        
        if resp.status_code == 429:
            return {"error": "Перевищено ліміт (100 запитів/день у безкоштовній версії)"}
        
        if resp.status_code != 200:
            return {"error": f"Помилка HTTP {resp.status_code}. Можливо API ще в waitlist - спробуй запросити доступ"}
        
        data = resp.json()
        
        # Обробка результатів Perenual
        results_list = data.get("results", [])
        
        if not results_list:
            return {"error": "Не знайдено результатів"}
        
        results = []
        for item in results_list[:5]:
            name = item.get("scientific_name", item.get("name", "Невідомо"))
            score = item.get("score", 0.0)
            
            # Perenual може давати links до деталей
            resources = item.get("resources", {})
            
            results.append({
                "name": name,
                "common_name": "",
                "score": score
            })
        
        return {"results": results, "success": True}
    
    except Exception as e:
        return {"error": f"Perenual помилка: {str(e)}"}

# -------------------------------
# Функція: показати горизонтальні кольорові блоки
# -------------------------------
def show_color_bars(results: List[Dict], api_name: str, color_scheme: str):
    """Відображення результатів у вигляді кольорових барів"""
    
    if len(results) == 0:
        st.info(f"**{api_name}**: Немає результатів")
        return
    
    color_palettes = {
        "blue": ["#0d47a1", "#1565c0", "#1e88e5", "#2196f3", "#42a5f5"],
        "green": ["#1b5e20", "#2e7d32", "#388e3c", "#43a047", "#66bb6a"],
        "purple": ["#4a148c", "#6a1b9a", "#7b1fa2", "#8e24aa", "#9c27b0"]
    }
    
    colors = color_palettes.get(color_scheme, color_palettes["blue"])
    max_score = max([r["score"] for r in results]) or 1.0
    
    st.markdown(f"### {api_name}")
    
    for i, r in enumerate(results):
        name = r["name"]
        common_name = r.get("common_name", "")
        score = r["score"]
        width_pct = (score / max_score) * 90
        color = colors[i % len(colors)]
        
        display_name = f"{name}" + (f" ({common_name})" if common_name else "")
        
        html = f"""
        <div style="
            display:flex;
            align-items:center;
            margin-bottom:10px;
            gap:12px;
        ">
            <div style="
                background:{color};
                width:{width_pct}%;
                min-width:100px;
                padding:12px 16px;
                border-radius:8px;
                color:white;
                font-weight:600;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                font-size:14px;
            ">
                {display_name}
            </div>
            <div style="min-width:70px; color:#90a4ae; font-weight:600; font-size:16px;">
                {score*100:.1f}%
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)
    
    st.markdown("---")

# -------------------------------
# Функція: визначити найточніший результат
# -------------------------------
def show_best_result(all_results: Dict):
    """Показати API з найвищим score"""
    
    # Збираємо топові результати від кожного API
    top_scores = {}
    
    for api_name, data in all_results.items():
        if data.get("success") and data.get("results"):
            top = data["results"][0]
            top_scores[api_name] = {
                "name": top["name"],
                "score": top["score"],
                "common_name": top.get("common_name", "")
            }
    
    if not top_scores:
        st.warning("❌ Жоден API не повернув результатів")
        return
    
    # Знаходимо API з найвищим score
    best_api = max(top_scores.items(), key=lambda x: x[1]["score"])
    api_name = best_api[0]
    plant_data = best_api[1]
    
    st.markdown("---")
    st.header("🏆 Найточніший результат")
    
    # Іконки для API
    api_icons = {
        "PlantNet": "🌿",
        "Plant.id": "🤖",
        "Perenual": "🌱"
    }
    
    icon = api_icons.get(api_name, "🎯")
    display_name = f"{plant_data['name']}" + (f" ({plant_data['common_name']})" if plant_data['common_name'] else "")
    
    # Красива плашка з переможцем
    html = f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        text-align: center;
        margin-bottom: 20px;
    ">
        <div style="font-size: 48px; margin-bottom: 10px;">
            {icon}
        </div>
        <div style="color: white; font-size: 24px; font-weight: 700; margin-bottom: 8px;">
            {api_name}
        </div>
        <div style="color: #f0f0f0; font-size: 18px; margin-bottom: 5px;">
            {display_name}
        </div>
        <div style="
            background: rgba(255,255,255,0.2);
            display: inline-block;
            padding: 8px 20px;
            border-radius: 20px;
            color: white;
            font-size: 22px;
            font-weight: 700;
            margin-top: 10px;
        ">
            {plant_data['score']*100:.1f}% впевненості
        </div>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)
    
    # Показати порівняння всіх API
    st.subheader("📊 Порівняння всіх API")
    
    cols = st.columns(len(top_scores))
    for i, (api, plant) in enumerate(top_scores.items()):
        with cols[i]:
            is_best = api == api_name
            border = "3px solid #667eea" if is_best else "1px solid #ddd"
            
            html_card = f"""
            <div style="
                border: {border};
                border-radius: 10px;
                padding: 15px;
                background: {'#f8f9ff' if is_best else 'white'};
                text-align: center;
            ">
                <div style="font-size: 32px; margin-bottom: 5px;">
                    {api_icons.get(api, '🎯')}
                </div>
                <div style="font-weight: 700; font-size: 14px; margin-bottom: 5px; color: #333;">
                    {api}
                </div>
                <div style="font-size: 20px; font-weight: 700; color: #667eea;">
                    {plant['score']*100:.0f}%
                </div>
                <div style="font-size: 11px; color: #666; margin-top: 5px;">
                    {plant['name'].split()[0] if plant['name'] != "Невідомо" else "❓"}
                </div>
            </div>
            """
            st.markdown(html_card, unsafe_allow_html=True)

# -------------------------------
# ГОЛОВНИЙ ІНТЕРФЕЙС
# -------------------------------

uploaded = st.file_uploader("Завантаж фото рослини (jpg, png, jpeg):", type=["jpg","jpeg","png"])

if uploaded:
    # Показати оригінал
    img = Image.open(uploaded).convert("RGB")
    st.image(img, caption="Завантажене фото", use_container_width=True)
    
    # Отримати байти
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_bytes = buffered.getvalue()
    
    st.markdown("---")
    st.header("🔍 Результати розпізнавання")
    
    all_results = {}
    
    # PlantNet
    with st.spinner("PlantNet розпізнає..."):
        result1 = identify_plantnet(img_bytes)
        all_results["PlantNet"] = result1
        
        if result1.get("success"):
            show_color_bars(result1["results"], "🌿 PlantNet", "blue")
        else:
            st.error(f"**PlantNet**: {result1.get('error', 'Помилка')}")
    
    # Plant.id
    with st.spinner("Plant.id розпізнає..."):
        result2 = identify_plantid(img_bytes)
        all_results["Plant.id"] = result2
        
        if result2.get("success"):
            show_color_bars(result2["results"], "🤖 Plant.id (AI)", "green")
        else:
            st.warning(f"**Plant.id**: {result2.get('error', 'Помилка')}")
    
    # Perenual
    with st.spinner("Perenual розпізнає..."):
        result3 = identify_perenual(img_bytes)
        all_results["Perenual"] = result3
        
        if result3.get("success"):
            show_color_bars(result3["results"], "🌱 Perenual", "purple")
        else:
            st.warning(f"**Perenual**: {result3.get('error', 'Помилка')}")
    
    # Показати найточніший результат
    show_best_result(all_results)


