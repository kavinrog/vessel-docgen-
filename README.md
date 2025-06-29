# Vessel DocGen

**Vessel DocGen** is a FastAPI-based service that accepts JSON input describing vessel, owner, and registration details, and maps the data to the official USCG CG-1258 PDF form. It returns a completed, downloadable PDF. Useful for automating vessel documentation workflows.

---

## 🚀 Features
- JSON to PDF mapping for USCG CG-1258 form
- FastAPI backend with Swagger UI
- Returns filled PDF for download

---

## 🧰 Requirements
- Python 3.8+

---

## 📦 Installation
```bash
# Clone the repository
https://github.com/kavinrog/vessel-docgen-.git
cd vessel-docgen

# Install dependencies
pip install -r requirements.txt
```

---

## ▶️ Run the App
```bash
uvicorn main:app --reload
```
Visit Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📤 Example Request (via Swagger UI)
Use the `POST /fill-pdf` endpoint and paste the example JSON provided in the `Technical Test` file.

---

## 📄 File Structure
```
project/
├── main.py            # FastAPI app logic
├── uscg.pdf           # Blank CG-1258 form
├── filled_uscg.pdf    # Output file (auto-generated)
├── requirements.txt
└── README.md
```

---

## 📋 License
MIT License