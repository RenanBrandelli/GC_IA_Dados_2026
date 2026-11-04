"""API da Casa de Sucos.

Consome a API pública Fruityvice para obter informações nutricionais
das frutas e expõe endpoints para consultar frutas e gerenciar sucos.
"""

from typing import List, Optional

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

FRUITYVICE_URL = "https://www.fruityvice.com/api/fruit"
TIMEOUT_SEGUNDOS = 10

app = FastAPI(
    title="Casa de Sucos API",
    description="API de sucos integrada à Fruityvice (valores nutricionais por 100 g de fruta).",
    version="1.0.0",
)

# "Banco de dados" em memória
sucos_db: List[dict] = []
proximo_id = 1


# ---------------------------------------------------------------------------
# Modelos (Pydantic)
# ---------------------------------------------------------------------------
class FrutaResposta(BaseModel):
    nome: str
    calorias: float
    acucar: float


class SucoCriar(BaseModel):
    nome: str = Field(..., min_length=1, examples=["Vitamina Tropical"])
    frutas: List[str] = Field(..., min_length=1, examples=[["banana", "strawberry"]])
    tem_gosto_de: str = Field(..., examples=["Tamarindo"])


class SucoAtualizar(BaseModel):
    frutas: List[str] = Field(..., min_length=1, examples=[["banana", "apple"]])


class SucoResposta(BaseModel):
    id: int
    nome: str
    frutas: List[str]
    tem_gosto_de: str
    total_calorias: float
    total_acucar: float


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------
def buscar_fruta(nome: str) -> dict:
    """Consulta uma fruta na Fruityvice e devolve nome, calorias e açúcar."""
    nome_limpo = nome.strip().lower()

    try:
        resposta = requests.get(f"{FRUITYVICE_URL}/{nome_limpo}", timeout=TIMEOUT_SEGUNDOS)
    except requests.RequestException:
        raise HTTPException(
            status_code=503,
            detail="Não foi possível acessar a API Fruityvice no momento. Tente novamente mais tarde.",
        )

    if resposta.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail=f"Fruta '{nome}' não encontrada. Verifique o nome (em inglês) e tente novamente.",
        )
    if resposta.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="A API Fruityvice retornou uma resposta inesperada.",
        )

    dados = resposta.json()
    nutricao = dados.get("nutritions", {})
    return {
        "nome": dados.get("name", nome_limpo),
        "calorias": nutricao.get("calories", 0),
        "acucar": nutricao.get("sugar", 0),
    }


def calcular_totais(frutas: List[str]) -> dict:
    """Soma calorias e açúcar das frutas (100 g de cada).

    Todas as frutas são consultadas antes de qualquer gravação; se alguma
    não existir, o erro 404 é levantado e nada é salvo.
    """
    total_calorias = 0.0
    total_acucar = 0.0
    for nome in frutas:
        fruta = buscar_fruta(nome)
        total_calorias += fruta["calorias"]
        total_acucar += fruta["acucar"]
    return {
        "total_calorias": round(total_calorias, 2),
        "total_acucar": round(total_acucar, 2),
    }


def encontrar_suco(suco_id: int) -> dict:
    for suco in sucos_db:
        if suco["id"] == suco_id:
            return suco
    raise HTTPException(status_code=404, detail=f"Suco com id {suco_id} não encontrado.")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/frutas/{nome}", response_model=FrutaResposta, tags=["Frutas"])
def consultar_fruta(nome: str):
    """Consulta uma fruta na Fruityvice (nome, calorias e açúcar por 100 g)."""
    return buscar_fruta(nome)


@app.post("/sucos", response_model=SucoResposta, status_code=201, tags=["Sucos"])
def cadastrar_suco(suco: SucoCriar):
    """Cadastra um suco e calcula calorias e açúcar totais (100 g por fruta)."""
    global proximo_id

    totais = calcular_totais(suco.frutas)
    novo = {
        "id": proximo_id,
        "nome": suco.nome,
        "frutas": [f.strip().lower() for f in suco.frutas],
        "tem_gosto_de": suco.tem_gosto_de,
        **totais,
    }
    sucos_db.append(novo)
    proximo_id += 1
    return novo


@app.get("/sucos", response_model=List[SucoResposta], tags=["Sucos"])
def listar_sucos():
    """Lista todos os sucos cadastrados com seus valores nutricionais."""
    return sucos_db


@app.put("/sucos/{suco_id}", response_model=SucoResposta, tags=["Sucos"])
def atualizar_suco(suco_id: int, dados: SucoAtualizar):
    """(Bônus) Atualiza as frutas de um suco e recalcula os valores nutricionais."""
    suco = encontrar_suco(suco_id)
    totais = calcular_totais(dados.frutas)  # falha antes de alterar o suco
    suco["frutas"] = [f.strip().lower() for f in dados.frutas]
    suco.update(totais)
    return suco
