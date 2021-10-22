import uvicorn
from app.config import ConfigClass

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=ConfigClass.settings.host, port=ConfigClass.settings.port, log_level="info", reload=True)
