import uvicorn

url_dev_ops = "http://10.3.7.220/vre/api/vre/portal/dataops"
# url_manifests = "http://10.3.7.220/vre/api/vre/portal/v1/data/manifests"
# url_manifest_validate = "http://10.3.7.220/vre/api/vre/portal/v1/file/manifest/validate"
# url_manifest = "http://10.3.7.220/vre/api/vre/portal/v1/file/manifest"
url_file_node = "http://10.3.7.216:5062/v1/neo4j/nodes/File/query"
url_file_tag = "http://10.3.7.220/vre/api/vre/portal/dataops/v2/containers/"  # + container_id/tags or container_id/tags/validate

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=5077, log_level="info", reload=True)