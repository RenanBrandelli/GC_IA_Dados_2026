# 🧃 Casa de Sucos API

API desenvolvida com **FastAPI** que se integra à API pública [Fruityvice](https://www.fruityvice.com/api/fruit/)
para consultar informações nutricionais de frutas e cadastrar sucos com o total de calorias e açúcar.

> Os cálculos consideram **100 g de cada fruta** informada. Os nomes das frutas devem ser em **inglês**
> (ex.: `banana`, `strawberry`, `apple`), pois é o padrão da Fruityvice.

## Funcionalidades

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/frutas/{nome}` | Consulta uma fruta e retorna `nome`, `calorias` e `acucar` |
| POST | `/sucos` | Cadastra um suco e calcula o total de calorias e açúcar |
| GET | `/sucos` | Lista todos os sucos cadastrados |
| PUT | `/sucos/{id}` | **(Bônus)** Atualiza as frutas de um suco e recalcula os valores |

### Tratamento de erros

- **404**: fruta não encontrada na Fruityvice (mensagem amigável) ou suco inexistente.
- **422**: corpo da requisição inválido (ex.: lista de frutas vazia).
- **503**: Fruityvice indisponível / timeout.
- Se qualquer fruta de um suco não existir, **nada é salvo/alterado**.

## Como executar

```bash
# 1. Entrar na pasta
cd aula_14

# 2. Criar e ativar o ambiente virtual
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Iniciar a API
uvicorn main:app --reload
```

Acesse o Swagger em: <http://127.0.0.1:8000/docs>

## Exemplos

**GET /frutas/banana**
```json
{ "nome": "Banana", "calorias": 96, "acucar": 17.2 }
```

**POST /sucos**
```json
{
  "nome": "Vitamina Tropical",
  "frutas": ["banana", "strawberry"],
  "tem_gosto_de": "Tamarindo"
}
```
Resposta (201):
```json
{
  "id": 1,
  "nome": "Vitamina Tropical",
  "frutas": ["banana", "strawberry"],
  "tem_gosto_de": "Tamarindo",
  "total_calorias": 128,
  "total_acucar": 22.6
}
```

**PUT /sucos/1**
```json
{ "frutas": ["banana", "apple"] }
```

**Fruta inexistente** (`GET /frutas/xyz`) → 404
```json
{ "detail": "Fruta 'xyz' não encontrada. Verifique o nome (em inglês) e tente novamente." }
```

## Estrutura

```
aula_14/
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Observações

Os sucos ficam armazenados **em memória**; ao reiniciar a API, a lista é zerada.
