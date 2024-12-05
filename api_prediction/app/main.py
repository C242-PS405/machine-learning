from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import re
import os
import uvicorn

# Inisialisasi aplikasi FastAPI
app = FastAPI()

# Load model dan tokenizer
model = load_model('gambling_detection_model.h5')

with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

# Maksimal panjang sequence (harus sesuai dengan model training)
maxlen = 100

# Fungsi untuk membersihkan teks
def clean_text(text):
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = re.sub(r'[^\w\s]', ' ', text)  
    text = re.sub(r'\s+', ' ', text).strip()  
    text = text.lower()  
    return text

# Fungsi untuk prediksi teks
def predict_text(text):
    text_cleaned = clean_text(text)
    
    # Tokenisasi dan padding
    sequence = tokenizer.texts_to_sequences([text_cleaned])  
    padded = pad_sequences(sequence, maxlen=maxlen)  
    
    prediction = model.predict(padded)[0][0]
    
    return {
        'text': text,
        'probability': float(prediction),
        'prediction': 'Judi Online' if prediction > 0.5 else 'Bukan Judi Online'
    }

# Model untuk input JSON
class PredictionInput(BaseModel):
    text: str

# Endpoint untuk prediksi
@app.post("/predict")
def predict_endpoint(input: PredictionInput):
    try:
        result = predict_text(input.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Jalankan aplikasi dengan port fleksibel untuk Cloud Run
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Baca port dari lingkungan atau gunakan 8000
    uvicorn.run(app, host="0.0.0.0", port=port)