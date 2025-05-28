from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
import docx
import uvicorn
import os
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Download required NLTK data
nltk.download('punkt')
# nltk.download('punkt_tab')  # Removed as it is not a standard NLTK resource
nltk.download('wordnet')

def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def lemmatize_text(text: str) -> str:
    lemmatizer = WordNetLemmatizer()
    tokens = word_tokenize(text)
    lemmatized_tokens = [lemmatizer.lemmatize(token, pos='v') for token in tokens]
    return ' '.join(lemmatized_tokens)

@app.post("/extract_keywords/")
async def extract_keywords(file: UploadFile = File(...), n: int = Form(...)):
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        buffer.write(await file.read())
    try:
        text = extract_text_from_docx(temp_file_path)
        lemmatized_text = lemmatize_text(text)
        vectorizer = TfidfVectorizer(stop_words='english', max_features=n)
        X = vectorizer.fit_transform([lemmatized_text])
        keywords = vectorizer.get_feature_names_out()
        return JSONResponse({"keywords": list(keywords)})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    finally:
        os.remove(temp_file_path)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 