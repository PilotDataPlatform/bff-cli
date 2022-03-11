from app.resources.helpers import query_node
import asyncio


paylod =  {'query': {'name': 'fake_file', 'display_path': 'fake_file', 'archived': False, 'project_code': 'cli', 'labels': ['File', 'gr']}}
result = asyncio.run(query_node(payload=paylod))
print(result)
