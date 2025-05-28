import streamlit as st
import requests

st.title("Word File Keyword Extractor")

uploaded_file = st.file_uploader("Upload a Word (.docx) file", type=["docx"])
n = st.number_input("Number of keywords to extract", min_value=1, max_value=100, value=5)

if uploaded_file is not None and st.button("Extract Keywords"):
    with st.spinner("Extracting keywords..."):
        files = {"file": (uploaded_file.name, uploaded_file, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        data = {"n": n}
        try:
            response = requests.post("http://localhost:8000/extract_keywords/", files=files, data=data)
            if response.status_code == 200:
                keywords = response.json().get("keywords", [])
                st.success(f"Top {n} Keywords:")
                st.write(keywords)
            else:
                st.error(f"Error: {response.json().get('error', 'Unknown error')}")
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}") 