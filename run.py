import uvicorn

url_dev_ops = "http://10.3.7.220/vre/api/vre/portal/dataops"

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=5077, log_level="info", reload=True)