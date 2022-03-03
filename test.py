import requests


payload = {
        "query": {
            "folder_relative_path": 'jzhang7',
            "display_path": 'jzhang7/sample_data2',
            "name": 'sample_data2',
            "project_code": 'indoctestproject',
            "archived": False,
            "labels": ['Folder', 'Core']}
    }
node_query_url = "http://10.3.7.216:5062/v2/neo4j/nodes/query"
response = requests.post(node_query_url, json=payload)
print(response.text)
