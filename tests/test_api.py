import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/"backend"))
import database
from fastapi.testclient import TestClient
from main import app
client=TestClient(app)
BASE={"laboratorio":"Lab 01","responsavel":"Ana","data":"2026-10-10","turno":"manha","finalidade":"Aula prática","quantidade_alunos":20,"status":"confirmada"}
def setup_function():
    database.criar_tabela()
    with database.conectar() as c: c.execute("DELETE FROM reservas")
def test_criar_listar_consultar():
    r=client.post('/api/reservas',json=BASE); assert r.status_code==201; rid=r.json()['id']; assert client.get('/api/reservas').status_code==200; assert client.get(f'/api/reservas/{rid}').status_code==200
def test_conflito_409():
    assert client.post('/api/reservas',json=BASE).status_code==201; assert client.post('/api/reservas',json=BASE).status_code==409
def test_turno_invalido_422():
    d={**BASE,"turno":"madrugada"}; assert client.post('/api/reservas',json=d).status_code==422
def test_filtro_laboratorio():
    client.post('/api/reservas',json=BASE); r=client.get('/api/reservas?laboratorio=01'); assert len(r.json())==1
def test_excluir_204_depois_404():
    rid=client.post('/api/reservas',json=BASE).json()['id']; assert client.delete(f'/api/reservas/{rid}').status_code==204; assert client.delete(f'/api/reservas/{rid}').status_code==404


def test_quantidade_alunos_valida():
    r=client.post("/api/reservas",json=BASE); assert r.status_code==201; assert r.json()["quantidade_alunos"]==20

def test_quantidade_alunos_fora_do_intervalo():
    for valor in (0, 41):
        d={**BASE,"quantidade_alunos":valor}
        assert client.post("/api/reservas",json=d).status_code==422

def test_quantidade_alunos_obrigatoria():
    d={k:v for k,v in BASE.items() if k!="quantidade_alunos"}
    assert client.post("/api/reservas",json=d).status_code==422

def test_limites_quantidade_alunos():
    for valor in (1, 40):
        d={**BASE,"laboratorio":f"Lab {valor}","quantidade_alunos":valor}
        assert client.post("/api/reservas",json=d).status_code==201

def test_status_api():
    r=client.get("/api/status")
    assert r.status_code==200 and r.json()["status"]=="online"

def test_filtro_status_reserva():
    client.post("/api/reservas",json=BASE)
    assert len(client.get("/api/reservas?status_reserva=confirmada").json())==1

def test_atualizar_e_consultar_inexistente():
    rid=client.post("/api/reservas",json=BASE).json()["id"]
    atualizado={**BASE,"quantidade_alunos":30,"responsavel":"Beatriz"}
    r=client.put(f"/api/reservas/{rid}",json=atualizado)
    assert r.status_code==200 and r.json()["quantidade_alunos"]==30
    assert client.get("/api/reservas/999999").status_code==404

def test_persistencia_sqlite_fora_do_backend():
    r=client.post("/api/reservas",json=BASE)
    assert r.status_code==201
    assert database.CAMINHO_BANCO.parent.name=="dados"
    with database.conectar() as conn:
        gravada=conn.execute("SELECT quantidade_alunos FROM reservas WHERE id=?",(r.json()["id"],)).fetchone()
    assert gravada["quantidade_alunos"]==20
