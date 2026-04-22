# MOSIP Auth - Local Setup

## 1. Create and activate virtual environment
```
python -m venv env
.\env\Scripts\activate
```

## 2. Install dependencies
```
pip install fastapi uvicorn mosip-auth-sdk dynaconf pydantic
```

## 3. Start the server
```
uvicorn MOSIP_Auth:app --reload
```

## 4. Test
Open `http://localhost:8000/docs` in your browser.
