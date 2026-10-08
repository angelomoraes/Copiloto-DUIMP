DUIMP Copilot - Catálogo de Produtos
Aplicação em Streamlit que lê uma invoice em PDF, usa IA para identificar o produto, sugerir a NCM e extrair os atributos técnicos, e permite a revisão humana antes de exportar o resultado em JSON (carga para o Portal Único / Siscomex).
> A NCM e os atributos sugeridos pela IA são apenas uma sugestão. Sempre revise antes de usar em um processo real.
Como funciona
Você envia a invoice (PDF) na tela.
O texto é extraído do PDF com `pdfplumber`.
O texto é enviado para a IA, que devolve os dados no formato definido em `modelos.py` (Pydantic).
Você revisa e edita os atributos em uma tabela interativa.
Ao aprovar, o app gera o JSON para download.
Fallback automático entre provedores
Para não depender de uma única chave ou serviço, o `motor_ia.py` tenta os provedores em ordem de prioridade e passa para o próximo se um falhar (erro 503, cota esgotada, chave inválida etc.):
Gemini (Google)
Groq
OpenRouter
Provedores sem chave ou sem modelo configurado no `.env` são ignorados. Se todos falharem, o app exibe o motivo de cada falha.
Estrutura do projeto
```
├── app.py             # Interface Streamlit
├── leitor.py          # Extração de texto do PDF
├── modelos.py         # Estrutura dos dados (Pydantic)
├── motor_ia.py        # Comunicação com a IA e fallback entre provedores
├── requirements.txt   # Dependências
├── .env               # Chaves de API (Crie seu arquivo e insira suas API Keys aqui)
└── .gitignore
```
Como executar
1. Instale as dependências
Recomendado usar um ambiente virtual:
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
2. Configure as chaves de API
Crie um arquivo chamado `.env` na pasta raiz do projeto (junto do `app.py`) com o conteúdo abaixo. Preencha apenas os provedores que for usar:
```
GEMINI_API_KEYS=chave_gemini
GEMINI_MODEL=id_do_modelo_gemini

GROQ_API_KEYS=sua_chave_groq
GROQ_MODEL=id_do_modelo_groq

OPENROUTER_API_KEYS=sua_chave_openrouter
OPENROUTER_MODEL=id_do_modelo_gratuito
```
Observações:
Sem aspas e sem espaços ao redor do `=`.
Várias chaves do mesmo provedor ficam na mesma linha, separadas por vírgula, sem espaços.
Os IDs de modelo mudam com frequência. Confira o ID exato no console de cada provedor.
No Gemini, o limite gratuito vale por projeto do Google Cloud. Para ter cotas separadas, crie cada chave em um projeto diferente.
No OpenRouter, use apenas modelos gratuitos (terminados em `:free`).
Nunca envie o `.env` para o GitHub. Ele já está no `.gitignore`.
3. Rode o projeto
No terminal (Ctrl + '), dentro da pasta do projeto:
```
python -m streamlit run app.py
```
Sempre que alterar o `.env`, reinicie o Streamlit.
Privacidade
Os planos gratuitos de alguns provedores podem usar o conteúdo enviado para melhorar seus produtos. Leia a política de dados de cada plano antes de enviar invoices reais de clientes. Para testes, use documentos fictícios.
