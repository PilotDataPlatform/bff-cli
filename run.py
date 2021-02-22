import uvicorn
from app.main import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("run:app", host="127.0.0.1", port=5077, log_level="info", reload=True)
