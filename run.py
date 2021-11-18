import uvicorn
from app.config import ConfigClass
from app.main import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("run:app", host=ConfigClass.settings.host, port=ConfigClass.settings.port, log_level="info", reload=True)
