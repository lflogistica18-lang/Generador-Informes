"""
clients.py — Router de FastAPI para gestión de clientes y sucursales
Usa almacenamiento simple en JSON (sin BD) para uso interno localhost.
"""
import json
import os
import uuid
from fastapi import APIRouter, HTTPException
from typing import List

from models.schemas import Cliente, Sucursal

router = APIRouter()

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "clients.json")


def _load_clients() -> List[dict]:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_clients(clients: List[dict]):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(clients, f, ensure_ascii=False, indent=2)


@router.get("/", response_model=List[Cliente])
async def get_clients():
    """Lista todos los clientes."""
    return _load_clients()


@router.post("/", response_model=Cliente)
async def create_client(cliente: Cliente):
    """Crea un nuevo cliente."""
    clients = _load_clients()
    new_client = cliente.model_dump()
    new_client["id"] = str(uuid.uuid4())[:8]
    clients.append(new_client)
    _save_clients(clients)
    return new_client


@router.post("/{client_id}/sucursales", response_model=Sucursal)
async def add_sucursal(client_id: str, sucursal: Sucursal):
    """Agrega una sucursal a un cliente existente."""
    clients = _load_clients()
    for c in clients:
        if c["id"] == client_id:
            if "sucursales" not in c:
                c["sucursales"] = []
            new_suc = sucursal.model_dump()
            new_suc["id"] = str(uuid.uuid4())[:8]
            c["sucursales"].append(new_suc)
            _save_clients(clients)
            return new_suc
    raise HTTPException(status_code=404, detail="Cliente no encontrado")


@router.delete("/{client_id}")
async def delete_client(client_id: str):
    """Elimina un cliente."""
    clients = _load_clients()
    clients = [c for c in clients if c["id"] != client_id]
    _save_clients(clients)
    return {"message": "Cliente eliminado"}
