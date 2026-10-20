# HVAC Automation Agent

AI-agent voor installatiebedrijven (W-installaties, warmtepompen, airco, ventilatie)
die terugkerende kantoor- en serviceprocessen automatiseert.

## Aanpak

1. **Workflows in kaart brengen** — zie [`docs/01-workflow-inventaris.md`](docs/01-workflow-inventaris.md)
2. **Prioriteren** — waar zit de meeste tijdwinst en de minste risico?
3. **MVP-agent bouwen** voor 1–2 workflows
4. **Integraties** met bestaande software (planning, boekhouding, e-mail)
5. **Pilot** bij een installatiebedrijf, meten, uitbreiden

## Status

- Fase 1 (workflow-inventarisatie) — afgerond, zie `docs/`
- Fase 3 (MVP) — **W4 Werkbon & foto's compleet** werkt end-to-end met mock-Syntess/Exact

## Projectstructuur

```
config/checklists/        Checklists per klustype (YAML, per installateur aanpasbaar)
src/hvac_agent/
  app.py                  HTTP-API (kanaalberichten, werkbonnen, goedkeuringen)
  container.py            Samenstellen van LLM, integraties en kanalen
  models.py               Domeinmodel (Tenant, Job, WorkOrder, Approval, ...)
  channels/               Kanaal-gateway (uniform berichtformaat)
  integrations/           Interfaces + mocks voor Syntess en Exact
  llm/                    Claude-implementatie + nep-LLM voor tests
  workflows/work_order.py W4: werkbon- en fotocheck
tests/                    End-to-end en unit tests
```

## Lokaal draaien

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pytest                                  # tests (geen API-sleutel nodig)

cp .env.example .env                    # vul ANTHROPIC_API_KEY in voor echte AI
python -m hvac_agent.seed               # demo-klus + monteur +31600000001
uvicorn hvac_agent.app:create_app --factory --reload
```

Zonder `ANTHROPIC_API_KEY` draait een regelgebaseerde nep-LLM (handig voor demo's/tests).

### Voorbeeld: monteur stuurt een foto

```bash
curl -X POST localhost:8000/tenants/1/channels/app/inbound -H 'Content-Type: application/json' -d '{
  "sender": "+31600000001",
  "text": "typeplaatje buitenunit",
  "attachments": [{"filename": "IMG_1.jpg", "media_type": "image/jpeg", "data_b64": "'$(base64 -w0 foto.jpg)'"}]
}'
```

Antwoord: wat is herkend en wat nog ontbreekt. Bij een complete werkbon gaat deze naar Syntess en
staat er een factuurconcept klaar in `GET /tenants/1/approvals` (goedkeuren → Exact).
