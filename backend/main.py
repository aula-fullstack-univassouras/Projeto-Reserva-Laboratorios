from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

import database
import services
from models import ReservaAtualizacao, ReservaEntrada, ReservaSaida


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Prepara a persistência uma vez, ao iniciar a aplicação.
    database.criar_tabela()
    yield


app = FastAPI(title="Sistema de Reservas de Laboratórios", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/status")
def consultar_status():
    """Rota de saúde usada para comprovar a integração inicial (Encontro 1)."""
    return {"status": "online", "mensagem": "API em execução"}


@app.post("/api/reservas", response_model=ReservaSaida, status_code=201)
def criar(dados: ReservaEntrada):
    try:
        return services.criar_reserva(dados)
    except services.ConflitoReserva as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/api/reservas", response_model=list[ReservaSaida])
def listar(
    status_reserva: Literal["confirmada", "pendente", "cancelada"] | None = None,
    laboratorio: str | None = None,
    status: Literal["confirmada", "pendente", "cancelada"] | None = None,
):
    # status_reserva é o nome ensinado no roteiro; status fica como alias compatível.
    return services.listar_reservas(status_reserva or status, laboratorio)


@app.get("/api/reservas/{reserva_id}", response_model=ReservaSaida)
def obter(reserva_id: int):
    try:
        return services.obter_reserva(reserva_id)
    except services.ReservaNaoEncontrada as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.put("/api/reservas/{reserva_id}", response_model=ReservaSaida)
def atualizar(reserva_id: int, dados: ReservaAtualizacao):
    try:
        return services.atualizar_reserva(reserva_id, dados)
    except services.ReservaNaoEncontrada as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except services.ConflitoReserva as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.delete("/api/reservas/{reserva_id}", status_code=204)
def excluir(reserva_id: int):
    try:
        services.excluir_reserva(reserva_id)
        return Response(status_code=204)
    except services.ReservaNaoEncontrada as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
