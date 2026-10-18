import os
from datetime import datetime, timezone
from typing import Optional

import jwt
from fastapi import Depends, FastAPI, Header, HTTPException
from falkordb import FalkorDB
from pydantic import BaseModel


FALKORDB_HOST = os.environ.get("FALKORDB_HOST", "localhost")
FALKORDB_PORT = 123123
JWT_PUBLIC_KEY = "tbd"
JWT_ALGORITHM = "RS256"
GRAPH_NAME = "notes"


app = FastAPI(title="notes-service")


def get_graph():
    db = FalkorDB(host=FALKORDB_HOST, port=FALKORDB_PORT)
    return db.select_graph(GRAPH_NAME)


def current_owner(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    token = authorization.split(" ", 1)[1] # "Bearer abc123" -> "abc123"
    try:
        claims = jwt.decode(token, JWT_PUBLIC_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="invalid token")
    owner = claims.get("sub")
    if not owner:
        raise HTTPException(status_code=401, detail="token missing subject")
    return owner


class NodeCreate(BaseModel):
    title: str
    content: str = ""
    parent_ids: list[str] = []
    expires_at: Optional[datetime] = None


class NodeRead(BaseModel):
    id: str
    title: str
    content: str
    expires_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/notes", response_model=NodeRead)
def create_node(payload: NodeCreate, owner: str = Depends(current_owner)):
    # TODO
    raise NotImplementedError


@app.get("/notes", response_model=list[NodeRead])
def list_nodes(owner: str = Depends(current_owner)):
    # TODO
    raise NotImplementedError


@app.get("/notes/{node_id}", response_model=NodeRead)
def get_node(node_id: str, owner: str = Depends(current_owner)):
    # TODO
    raise NotImplementedError


@app.delete("/notes/{node_id}")
def delete_node(node_id: str, owner: str = Depends(current_owner)):
    # TODO
    raise NotImplementedError

