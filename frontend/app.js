// URL base da API; a interface é servida separadamente do backend.
const API_BASE = "http://127.0.0.1:8000";
const API = `${API_BASE}/api/reservas`;
const $ = (id) => document.getElementById(id);
let reservas = [];

function dadosFormulario() {
  const dados = Object.fromEntries(["laboratorio", "responsavel", "data", "turno", "finalidade", "status"]
    .map((campo) => [campo, $(campo).value.trim()]));
  dados.quantidade_alunos = Number($("quantidade_alunos").value);
  return dados;
}
function mensagem(texto, sucesso = true) {
  $("msg").textContent = texto;
  $("msg").className = sucesso ? "success" : "error";
}
function textoSeguro(valor) {
  return String(valor).replace(/[&<>"']/g, (caractere) => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[caractere]));
}
async function verificarStatus() {
  try {
    const resposta = await fetch(`${API_BASE}/api/status`);
    if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`);
    const dados = await resposta.json();
    $("api-status").textContent = `API ${dados.status}: ${dados.mensagem}`;
    $("api-status").className = "api-online";
  } catch (erro) {
    $("api-status").textContent = "API offline: não foi possível conectar ao servidor.";
    $("api-status").className = "api-offline";
  }
}
async function listar() {
  try {
    const parametros = new URLSearchParams();
    if ($("fstatus").value) parametros.set("status_reserva", $("fstatus").value);
    if ($("busca").value.trim()) parametros.set("laboratorio", $("busca").value.trim());
    const resposta = await fetch(`${API}?${parametros}`);
    if (!resposta.ok) throw new Error(`API respondeu HTTP ${resposta.status}`);
    reservas = await resposta.json();
    $("lista").innerHTML = reservas.map((r) => `<tr><td>${textoSeguro(r.laboratorio)}</td><td>${textoSeguro(r.data)}</td><td>${textoSeguro(r.turno)}</td><td>${textoSeguro(r.responsavel)}</td><td>${textoSeguro(r.quantidade_alunos)}</td><td>${textoSeguro(r.status)}</td><td><button type="button" data-editar="${r.id}">Editar</button><button type="button" class="delete" data-excluir="${r.id}">Excluir</button></td></tr>`).join("");
    $("vazio").hidden = reservas.length !== 0;
  } catch (erro) {
    mensagem(`Não foi possível carregar as reservas. Verifique se a API está ligada. (${erro.message})`, false);
  }
}
function limparFormulario() { $("form").reset(); $("id").value = ""; $("form-title").textContent = "Nova reserva"; }
$("form").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const id = $("id").value;
  try {
    const resposta = await fetch(id ? `${API}/${id}` : API, {
      method: id ? "PUT" : "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(dadosFormulario())
    });
    if (!resposta.ok) {
      const erro = await resposta.json();
      const detalhe = Array.isArray(erro.detail) ? erro.detail.map((x) => `${x.loc?.join(".")}: ${x.msg}`).join("; ") : erro.detail;
      throw new Error(`${resposta.status}: ${detalhe || "Erro ao guardar"}`);
    }
    mensagem(id ? "Reserva atualizada com sucesso." : "Reserva criada com sucesso.");
    limparFormulario(); await listar();
  } catch (erro) { mensagem(erro.message, false); }
});
$("lista").addEventListener("click", async (evento) => {
  const editarId = evento.target.dataset.editar;
  if (editarId) {
    const reserva = reservas.find((r) => r.id === Number(editarId));
    if (!reserva) return;
    for (const campo of ["id", "laboratorio", "responsavel", "data", "turno", "finalidade", "quantidade_alunos", "status"]) $(campo).value = reserva[campo];
    $("form-title").textContent = `Editar reserva #${reserva.id}`; window.scrollTo({top:0,behavior:"smooth"}); return;
  }
  const excluirId = evento.target.dataset.excluir;
  if (excluirId && window.confirm("Tem certeza de que deseja excluir esta reserva?")) {
    try {
      const resposta = await fetch(`${API}/${excluirId}`, {method:"DELETE"});
      if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`);
      mensagem("Reserva excluída com sucesso."); await listar();
    } catch (erro) { mensagem(`Falha ao excluir: ${erro.message}`, false); }
  }
});
$("cancelar").addEventListener("click", limparFormulario);
$("filtrar").addEventListener("click", listar);
listar();
verificarStatus();
