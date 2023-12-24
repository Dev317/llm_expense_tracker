import os
import streamlit as st
import requests
from datetime import datetime
from util.gdrive_util import get_gdrive_service, create_folder, upload_file, list_folder, delete_files

st.set_page_config(page_title="Expense Tool",
                   page_icon="💸",
                   layout="wide",
                   initial_sidebar_state="auto",
                   menu_items=None)

st.header(body="Personal Finance Tracker 💸")
st.divider()

EXTRACTION_ENDPOINT = "http://localhost:5000/api/extract"
DATA_ENDPOINT = "http://localhost:8080/api/expenses"

SCOPES = ['https://www.googleapis.com/auth/drive']
CREDENTIALS_FILE = f"{os.getcwd()}/client/sa.json"
DRIVE_SERVICE = get_gdrive_service(scopes=SCOPES, credentials_file=CREDENTIALS_FILE)

col1, col2 = st.columns(2)
with col1:
    picture = st.camera_input("Take a picture of your receipt")

with col2:
    if picture:
        st.image(picture)
        bytes_data = picture.getvalue()
        st.session_state["file_data"] = bytes_data

        if st.button("Extract", type="primary"):
            receipt_id = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
            file_name = f"{receipt_id}.png"
            files = {'images': (file_name,
                                bytes_data,
                                'multipart/form-data',
                                {'Expires': '0'})
                    }

            try:
                response = requests.post(url=EXTRACTION_ENDPOINT, files=files)
                data = response.json()['data']
                st.session_state["data"] = data

                receipt_keys = list(data.keys())[0]
                st.session_state["file_name"] = file_name
                st.session_state["businessname"] = data[receipt_keys]["businessname"]
                st.session_state["category"] = data[receipt_keys]["category"]
                st.session_state["date"] = data[receipt_keys]["date"]
                st.session_state["total"] = data[receipt_keys]["total"]
                st.toast(f"Successful extraction!", icon="✅")

            except Exception as e:
                st.toast(f"Error in extracting details from receipt. Please try again!", icon="❌")

        if "data" in st.session_state:
            with st.form(key="edit_form"):
                st.write("Edit extracted results")
                businessname = st.text_input(label="Business Name", value=st.session_state["businessname"])
                category = st.text_input(label="Category", value=st.session_state["category"])
                date = st.text_input(label="Date", value=st.session_state["date"])
                total = st.text_input(label="Total", value=st.session_state["total"])

                form_submit = st.form_submit_button(label="Submit")
                if form_submit:
                    st.session_state["businessname"] = businessname
                    st.session_state["category"] = category
                    st.session_state["date"] = date
                    st.session_state["total"] = total

                    try:
                        existing_folders = list_folder(drive_service=DRIVE_SERVICE)
                        _, month, year = map(int, st.session_state["date"].split('/'))
                        folder_name = f"{month}_{year}"
                        if folder_name not in existing_folders:
                            folder_id = create_folder(drive_service=DRIVE_SERVICE,
                                                      folder_name=folder_name)
                        else:
                            folder_id = existing_folders[folder_name]

                        file_id = upload_file(drive_service=DRIVE_SERVICE,
                                    file_name=st.session_state['file_name'],
                                    file_data=st.session_state['file_data'],
                                    mimetype="image/jpg",
                                    parent_folder_id=folder_id)

                        response = requests.post(url=DATA_ENDPOINT,
                                                 json={"business_name": st.session_state["businessname"],
                                                       "category": st.session_state["category"],
                                                       "date": st.session_state["date"],
                                                       "total": float(st.session_state["total"]),
                                                       "gdrive_id": file_id
                                                      })

                        st.toast(f"Successful submission!", icon="✅")
                    except Exception as e:
                        print(f"Error: {str(e)}")
                        delete_files(drive_service=DRIVE_SERVICE, file_or_folder_ids=[file_id])
                        st.toast(f"Error in uploading receipt. Please try again!", icon="❌")
