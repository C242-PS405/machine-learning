from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import uvicorn

app = FastAPI()

class URLInput(BaseModel):
    url: str

def scrape_from_url(url: str):
    try:
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url

        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Cek status HTTP

        soup = BeautifulSoup(response.content, 'html.parser')

        # Ambil data
        title = soup.title.string.strip() if soup.title else ""
        meta_description = soup.find("meta", attrs={"name": "description"})
        description = meta_description["content"].strip() if meta_description else ""
        meta_keywords = soup.find("meta", attrs={"name": "keywords"})
        keywords = meta_keywords["content"].strip() if meta_keywords else ""

        # Gabungkan semua menjadi string
        combined_text = f"{title} {description} {keywords}".strip()

        return {"text": combined_text}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/scrape")
async def scrape(input_data: URLInput):
    result = scrape_from_url(input_data.url)
    return result

if __name__ == "__main__":
    import sys

    # port default
    port = 8000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    # Menjalankan aplikasi FastAPI menggunakan uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
