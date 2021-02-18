from fastapi import Request

import jwt as pyjwt
import requests
from config import ConfigClass


async def jwt_required(request: Request):
    token = request.headers.get('Authorization')
    if token:
        token = token.replace("Bearer ", "")
    else:
        raise Exception("Token required") 
    payload = pyjwt.decode(token, verify=False)
    username: str = payload.get("preferred_username")

    # check if user is existed in neo4j
    url = ConfigClass.NEO4J_SERVICE + "nodes/User/query"
    res = requests.post(
        url=url,
        json={"name": username}
    )
    if(res.status_code != 200):
        raise Exception("Neo4j service: " + json.loads(res.text))
    users = res.json()
    if not users:
        raise Exception(f"Neo4j service: User {username} does not exist.")
    user_id = users[0]['id']
    role = users[0]['role']
    if username is None:
        raise Exception("User not found") 
    return {"user_id": user_id, "username": username, "role": role}
