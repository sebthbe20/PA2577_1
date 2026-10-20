import os
from datetime import datetime, timezone
from typing import Optional
import uuid

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException
from falkordb import FalkorDB, Graph
from pydantic import BaseModel

from helpers import time_convert

FALKORDB_PORT = 6379
GRAPH_NAME = "notes"
FALKORDB_HOST = os.environ.get("FALKORDB_HOST", "localhost")
TOKEN_SERVICE_URL = os.environ.get("TOKEN_SERVICE_URL")


app = FastAPI(title="notes-service")


def get_graph() -> Graph:
    db = FalkorDB(host=FALKORDB_HOST, port=FALKORDB_PORT)
    return db.select_graph(GRAPH_NAME)


def require_valid_token(authorization: str = Header(...)) -> None:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    token = authorization.split(" ", 1)[1] # "Bearer abc123" -> "abc123"
    resp = httpx.post(f"{TOKEN_SERVICE_URL}/validate", json={"token": token})
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="invalid token")


class NodeCreate(BaseModel):
    title: str
    content: str = ""
    parent_id: Optional[str] = None
    expires_in: Optional[str] = None


class NodeRead(BaseModel):
    id: str
    title: str
    content: str
    expires_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/notes", dependencies=[Depends(require_valid_token)])
def create_node(payload: NodeCreate):
    expires_at = time_convert.calculate_expiry(payload.expires_in)
    node_id = str(uuid.uuid4())

    graph = get_graph()
    params = {
        "id": node_id,
        "title": payload.title,
        "content": payload.content,
        "expires_at": expires_at,
    }

    if payload.parent_id is None: # Its a category node
        graph.query(
            "CREATE (n:Node {id: $id, title: $title, content: $content, "
            "expires_at: $expires_at}) RETURN n",
            params,
        )
    else:
        params["parent_id"] = payload.parent_id # Its a note node
        result = graph.query(
            "MATCH (p:Node {id: $parent_id}) "
            "CREATE (n:Node {id: $id, title: $title, content: $content, "
            "expires_at: $expires_at})-[:CHILD_OF]->(p) RETURN n",
            params,
        )
        if not result.result_set:
            raise HTTPException(status_code=400, detail="parent_id not found")

@app.get("/notes", response_model=list[NodeRead], dependencies=[Depends(require_valid_token)])
def list_nodes():
    # TODO
    raise NotImplementedError


@app.get("/notes/{node_id}", response_model=NodeRead, dependencies=[Depends(require_valid_token)])
def get_node(node_id: str):
    graph = get_graph()



@app.delete("/notes/{node_id}", dependencies=[Depends(require_valid_token)])
def delete_node(node_id: str):
    # TODO
    raise NotImplementedError

def get_nodes():
    graph = get_graph()
    result = graph.query("MATCH (n) RETURN n")
    return result.result_set

if __name__ == "__main__":
    print("hello")
    print(get_nodes())