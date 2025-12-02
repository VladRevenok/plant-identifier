import streamlit as st
import requests
from PIL import Image
import io
import os

API_KEY = "2b105FYLbg34pvfXRESKZMMKO"
API_URL = "https://my-api.plantnet.org/v2/identify/all"

st.title("🌿 Plant Identifier (PlantNet API)")
st.write("Завантаж фото рослини, і AI визначить її вид!")

upload = st.file_uploader("Завантаж зображення:", type=["jpg", "jpeg", "png"])

if upload:
    img = Image.open(upload).convert("RGB")
    st.image(img, caption="Ваше фото", width=350)

    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_bytes = buffered.getvalue()

    files = [
        ("images", ("image.jpg", img_bytes, "image/jpeg")),
    ]

    params = {
        "api-key": API_KEY,
    }

    with st.spinner("Розпізнаю рослину..."):
        resp = requests.post(API_URL, files=files, params=params)

    if resp.status_code != 200:
        st.error("Помилка API. Код: " + str(resp.status_code))
        st.text(resp.text)
    else:
        data = resp.json()

        if "results" not in data or len(data["results"]) == 0:
            st.warning("Не вдалося визначити рослину. Спробуй інше фото.")
        else:
            top = data["results"][0]
            plant_name = top["species"]["scientificName"]
            score = round(top["score"] * 100, 2)

            st.header(f"🌱 {plant_name}")
            st.subheader(f"Ймовірність: **{score}%**")

            st.write("### Інші можливі варіанти:")

            for r in data["results"][1:5]:
                nm = r["species"]["scientificName"]
                sc = round(r["score"] * 100, 2)
                st.write(f"- **{nm}** — {sc}%")

