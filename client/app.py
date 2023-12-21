import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Expense Tool",
                   page_icon="💸",
                   layout="wide",
                   initial_sidebar_state="auto",
                   menu_items=None)

st.header(body="Personal Finance Tracker 💸")
st.divider()

EXTRACTION_ENDPOINT = "http://localhost:5000/api/extract"

col1, col2 = st.columns(2)
with col1:
    picture = st.camera_input("Take a picture of your receipt")

with col2:
    if picture:
        st.image(picture)
        bytes_data = picture.getvalue()

        if st.button("Extract", type="primary"):
            receipt_id = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
            files = {'images': (f"{receipt_id}.png",
                                bytes_data,
                                'multipart/form-data',
                                {'Expires': '0'})
                    }

            try:
                response = requests.post(url=EXTRACTION_ENDPOINT, files=files)
                data = response.json()['data']
                st.session_state["data"] = data

                receipt_keys = list(data.keys())[0]
                st.session_state["merchant"] = data[receipt_keys]["businessname"]
                st.session_state["category"] = data[receipt_keys]["category"]
                st.session_state["date"] = data[receipt_keys]["date"]
                st.session_state["total"] = data[receipt_keys]["total"]
                st.toast(f"Successful extraction!", icon="✅")

            except Exception as e:
                st.toast(f"Error in extracting details from receipt. Please try again!", icon="❌")

        if "data" in st.session_state:
            with st.form(key="edit_form"):
                st.write("Edit extracted results")
                merchant = st.text_input(label="Merchant", value=st.session_state["merchant"])
                category = st.text_input(label="Category", value=st.session_state["category"])
                date = st.text_input(label="Date", value=st.session_state["date"])
                total = st.text_input(label="Total", value=st.session_state["total"])

                form_submit = st.form_submit_button(label="Submit")
                if form_submit:
                    st.session_state["merchant"] = merchant
                    st.session_state["category"] = category
                    st.session_state["date"] = date
                    st.session_state["total"] = total
                    st.toast(f"Successful submission!", icon="✅")

