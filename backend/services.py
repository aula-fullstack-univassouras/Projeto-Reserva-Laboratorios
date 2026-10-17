from datetime import datetime
from database import conectar
from models import ReservaEntrada, ReservaAtualizacao

class ReservaNaoEncontrada(Exception): pass
class ConflitoReserva(Exception): pass

def _dict(row): return dict(row) if row else None

def _conflita(conn, dados, ignorar_id=None):
    sql = """SELECT id FROM reservas WHERE laboratorio=? AND data=? AND turno=?
             AND status <> 'cancelada' AND ? <> 'cancelada'"""
    params=[dados.laboratorio, dados.data.isoformat(), dados.turno, dados.status]
    if ignorar_id is not None:
        sql += " AND id <> ?"; params.append(ignorar_id)
    return conn.execute(sql, params).fetchone() is not None

def criar_reserva(dados: ReservaEntrada):
    with conectar() as conn:
        if _conflita(conn, dados): raise ConflitoReserva("Horário já reservado para este laboratório.")
        criado=datetime.now().isoformat(timespec="seconds")
        cur=conn.execute("""INSERT INTO reservas(laboratorio,responsavel,data,turno,finalidade,quantidade_alunos,status,data_criacao)
        VALUES(?,?,?,?,?,?,?,?)""",(dados.laboratorio,dados.responsavel,dados.data.isoformat(),dados.turno,dados.finalidade,dados.quantidade_alunos,dados.status,criado))
        return obter_reserva(cur.lastrowid, conn)

def listar_reservas(status=None, laboratorio=None):
    sql="SELECT * FROM reservas WHERE 1=1"; params=[]
    if status: sql += " AND status=?"; params.append(status)
    if laboratorio: sql += " AND lower(laboratorio) LIKE ?"; params.append(f"%{laboratorio.lower()}%")
    sql += " ORDER BY data, turno, laboratorio"
    with conectar() as conn: return [_dict(r) for r in conn.execute(sql,params).fetchall()]

def obter_reserva(reserva_id, conn=None):
    own=conn is None; conn=conn or conectar()
    row=conn.execute("SELECT * FROM reservas WHERE id=?",(reserva_id,)).fetchone()
    if own: conn.close()
    if not row: raise ReservaNaoEncontrada("Reserva não encontrada.")
    return _dict(row)

def atualizar_reserva(reserva_id: int, dados: ReservaAtualizacao):
    with conectar() as conn:
        if not conn.execute("SELECT id FROM reservas WHERE id=?",(reserva_id,)).fetchone(): raise ReservaNaoEncontrada("Reserva não encontrada.")
        if _conflita(conn,dados,reserva_id): raise ConflitoReserva("Horário já reservado para este laboratório.")
        conn.execute("""UPDATE reservas SET laboratorio=?,responsavel=?,data=?,turno=?,finalidade=?,quantidade_alunos=?,status=? WHERE id=?""",
                     (dados.laboratorio,dados.responsavel,dados.data.isoformat(),dados.turno,dados.finalidade,dados.quantidade_alunos,dados.status,reserva_id))
        return obter_reserva(reserva_id,conn)

def excluir_reserva(reserva_id:int):
    with conectar() as conn:
        cur=conn.execute("DELETE FROM reservas WHERE id=?",(reserva_id,))
        if cur.rowcount==0: raise ReservaNaoEncontrada("Reserva não encontrada.")
