import requests


def get_node_by_geid(geid):
  _logger.info("get_node_by_geid".center(80, '-'))
  url = ConfigClass.NEO4J_SERVICE + f"nodes/geid/{geid}"
  _logger.info(f'Getting node: {url}')
  try:
    res = requests.get(url)
    _logger.info(f'Getting node info: {res.text}')
    result = res.json()
  except Exceptions as e:
    _logger.error(f'Error getting node by geid: {e}')
    result = None
  return result


url = "http://10.3.7.216:5062/v1/neo4j/nodes/query/geids"
payload = {
  "geids": ["2b60f036-9642-44e7-883b-c8ed247b1152-1627407935", "80c08693-9ac8-4b94-bb02-9aebe0ec9f20-16274078221", "18aff571-1669-4d39-932f-01f4d1495ec7-1626111037"],
}
geid_list = ["2b60f036-9642-44e7-883b-c8ed247b1152-1627407935", "80c08693-9ac8-4b94-bb02-9aebe0ec9f20-1627407822"]
res = requests.post(url, json=payload)
print(res.text)
res_json = res.json()
result = res_json.get('result')
query_result = {}
located_geid = []
for node in result:
  geid = node.get('global_entity_id', '')
  if geid in geid_list:
    query_result[geid] = node
    located_geid.append(geid)
for _geid in geid_list:
  if _geid not in located_geid:
    query_result[_geid] = {}
print(query_result)
