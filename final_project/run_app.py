import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)