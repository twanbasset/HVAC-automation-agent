# Architectuur (voorstel)

## Overzicht

```
 Kanalen                 Platform                                Integraties
┌──────────┐     ┌────────────────────────────────────┐     ┌──────────────┐
│ E-mail   │──┐  │  Kanaal-gateway (normaliseert       │     │ Syntess      │
│ WhatsApp │──┼─▶│  berichten → Conversation/Event)    │  ┌─▶│ (projecten,  │
│ Webportal│──┤  │               │                     │  │  planning,   │
│ Monteur- │──┘  │               ▼                     │  │  werkbonnen) │
│ app      │     │  Orchestrator / Agent-runtime       │  │              │
└──────────┘     │   - workflow-agents (W1..W4)        │──┤ Exact Online │
                 │   - tools (offerte, planning, ...)   │  │ (relaties,   │
                 │   - LLM (Claude)                    │  │  facturen)   │
                 │               │                     │  │              │
                 │               ▼                     │  │ Later:       │
                 │  Goedkeuringen (HITL) dashboard     │  │ groothandel, │
                 │  Domeinmodel + DB (Postgres)        │  │ agenda, ISDE │
                 │  Audit log                          │  └──────────────┘
                 └────────────────────────────────────┘
```

## Principes

1. **Eén platform, meerdere kanalen**: elk kanaal is een adapter die berichten omzet naar
   een uniform intern formaat. Per klant (tenant) zijn kanalen aan/uit te zetten.
2. **Integraties achter interfaces**: `PlanningSystem`, `QuoteSystem`, `AccountingSystem`.
   Syntess en Exact zijn de eerste implementaties; daarnaast een **mock** zodat we kunnen
   bouwen en testen zonder pilotklant.
3. **Human-in-the-loop**: alles wat naar een klant gaat of geld raakt (offerte, factuur,
   planningsbevestiging) loopt in de MVP via een goedkeuringsstap.
4. **Multi-tenant vanaf dag 1**: elke installateur heeft eigen data, prijslijsten,
   checklists, tone-of-voice en koppelingen.
5. **Configuratie i.p.v. code**: checklists, standaardpakketten en materiaallijsten
   zijn data (YAML/DB) die per klant aanpasbaar is.
6. **Audit & AVG**: elke agent-actie gelogd; persoonsgegevens in EU-hosting.

## Technische keuzes (voorstel)

| Onderdeel | Keuze | Toelichting |
|---|---|---|
| Taal | Python 3.12 | Sterk ecosysteem voor AI en integraties |
| API | FastAPI | Webhooks (WhatsApp/mail) + dashboard-API |
| Agent | Claude API met tool use | Sonnet voor dagelijkse taken, Opus voor complexe offertes, Haiku voor classificatie |
| Database | PostgreSQL (SQLAlchemy) | Tenants, klanten, klussen, werkbonnen, goedkeuringen |
| Achtergrondtaken | Queue (bijv. Redis + worker) | Follow-ups, herinneringen, sync met Syntess/Exact |
| Bestanden | S3-compatible (EU) | Foto's, documenten |
| WhatsApp | WhatsApp Business Cloud API | Klant- en monteurkanaal |
| Dashboard | Eenvoudige web-UI | Goedkeuren, inzien, configureren |

## Integratie-aandachtspunten

- **Syntess**: API-mogelijkheden per versie/licentie verifiëren (Syntess Atrium).
  Fallback: import/export of koppeling via partner. → *te checken met pilotklant/Syntess.*
- **Exact Online**: REST API met OAuth2; relaties, artikelen, verkoopfacturen (concept).
  App-registratie in Exact App Center nodig.

## Domeinmodel (kern)

- `Tenant` (installatiebedrijf), `Customer`, `Site` (adres/installatie), `Asset` (toestel, merk, type, serienr.)
- `Lead` → `Quote` → `Job` (klus) → `WorkOrder` (werkbon) → `Invoice`
- `Technician` (vaardigheden, regio), `Appointment`
- `Checklist` (per klustype), `ChecklistItem`, `Attachment` (foto)
- `MaterialList`, `Package` (standaardpakket)
- `Approval` (HITL), `Conversation`/`Message`, `AuditEvent`
