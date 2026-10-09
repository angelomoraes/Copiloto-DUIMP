# 🚢 DUIMP Copilot

**Assistente de IA para despachantes aduaneiros: sugere a NCM, mostra quanto custa errar e prepara os atributos do Catálogo de Produtos.**

🔗 **Teste online:** https://duimp-copilot.streamlit.app
💡 Sem arquivo ou chave de API? Marque **"Modo Demo"** na barra lateral.

---

## O problema

Na DUIMP, cada produto precisa de **NCM correta** e **atributos técnicos** preenchidos no Catálogo do Portal Único. Hoje isso é manual, lento e arriscado: classificar errado gera **multa de 1% do valor aduaneiro**, cobrança da **diferença de II/IPI** e **multa de 75% sobre essa diferença**, além de risco de canal vermelho.

## A solução

Você envia a invoice (**PDF, Excel, CSV, JSON ou XML**) e o DUIMP Copilot:

1. **Sugere um ranking de NCMs** com probabilidade, justificativa e alíquotas de II/IPI (editáveis).
2. **Calcula o risco em reais**: perda esperada e pior caso para a NCM que você escolher.
3. **Alerta sobre órgãos anuentes** (ANVISA, MAPA, DECEX) conforme a NCM.
4. **Extrai os atributos técnicos** em uma tabela editável.
5. **Exporta o JSON** revisado para o Portal Único.

A IA **apoia a decisão**, e o despachante decide, com o risco financeiro visível.

**Para quem:** despachantes, analistas de comex e importadores.

## Como funciona

```
Documento → leitor.py → motor_ia.py (Gemini → Groq → OpenRouter) → Pydantic → app.py
                                                                        └→ risco.py
```

- Saída da IA **validada por schema (Pydantic)**.
- **Fallback automático** entre provedores de IA, para a demo não cair por cota ou erro.

## Executar localmente

```bash
python -m venv venv
venv\Scripts\activate        # Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
```

Crie um `.env` na raiz (preencha só os provedores que for usar; várias chaves separadas por vírgula, sem espaços):

```env
GEMINI_API_KEYS=...
GEMINI_MODEL=...
GROQ_API_KEYS=...
GROQ_MODEL=...
OPENROUTER_API_KEYS=...
OPENROUTER_MODEL=...   # use modelos gratuitos (:free)
```

```bash
python -m streamlit run app.py
```

No Streamlit Cloud, coloque as mesmas variáveis em **Settings → Secrets**. Nunca suba o `.env` para o GitHub.

## Limitações

- NCM, probabilidades e alíquotas são **estimativas da IA**, sempre sujeitas a revisão humana.
- A **transmissão ao Siscomex é simulada** e os indicadores do topo do painel são ilustrativos.
- O risco considera só II, IPI e as multas de 1% e 75% (sem ICMS, PIS/COFINS ou juros).
- Planos gratuitos de IA podem usar os dados enviados: use documentos fictícios nos testes.

## Próximos passos

Integração real com a API do Siscomex · base oficial de NCM/TEC/TIPI · invoices com vários itens · cálculo de risco completo.

---
*Python · Streamlit · Pydantic · Pandas · Altair · Gemini / Groq / OpenRouter*
*Ferramenta de apoio: não substitui despachante, contador nem as tabelas oficiais.*
