# Workflow-inventaris installatiebedrijf (concept)

Eerste versie op basis van een typisch Nederlands installatiebedrijf (5–50 medewerkers).
Per workflow: wat er gebeurt, waar de pijn zit, en wat een agent kan doen.
Score: **Impact** (tijdwinst/omzet) en **Haalbaarheid** (data beschikbaar, risico) op 1–5.

## Klantreis

```
Aanvraag → Intake/schouw → Offerte → Opdracht → Planning → Uitvoering (werkbon)
  → Oplevering/factuur → Subsidie/registratie → Onderhoudscontract → Storingen/service
```

| # | Workflow | Huidige pijn | Wat de agent kan doen | Impact | Haalbaarheid |
|---|----------|--------------|-----------------------|:-:|:-:|
| 1 | **Aanvragen & lead-intake** (mail, telefoon, website, WhatsApp) | Losse kanalen, informatie onvolledig, trage reactie | Aanvragen classificeren, ontbrekende info (woningtype, bouwjaar, foto's meterkast/cv) uitvragen, lead in CRM zetten | 4 | 5 |
| 2 | **Schouw / opname** | Monteur noteert op papier/foto's, kantoor moet interpreteren | Foto's + spraakmemo omzetten naar gestructureerd opnamerapport | 4 | 4 |
| 3 | **Offerte opstellen** | Kost 1–3 uur per offerte, veel copy-paste, warmteverliesberekening | Concept-offerte uit opname + prijslijst/standaardpakketten, inclusief subsidie-indicatie (ISDE) | 5 | 4 |
| 4 | **Offerte-opvolging** | Offertes vergeten na te bellen | Automatische follow-up mails, herinneringen, scoring van kans | 4 | 5 |
| 5 | **Planning & inroostering** | Puzzel met monteurs, materiaal, klantbeschikbaarheid | Voorstel planning, afspraken bevestigen/herinneren bij klant | 4 | 3 |
| 6 | **Materiaal & inkoop** | Bestellen bij groothandel (Technische Unie, Wasco, etc.), levertijden | Materiaallijst uit offerte, bestelvoorstel, levertijden checken | 3 | 3 |
| 7 | **Werkbonnen & uren** | Onvolledige werkbonnen, nawerk op kantoor | Werkbon aanvullen uit spraak/foto's, controleren op volledigheid | 4 | 4 |
| 8 | **Facturatie** | Werkbon → factuur handmatig, vertraging = cashflow | Concept-factuur uit afgeronde werkbon, betalingsherinneringen | 5 | 4 |
| 9 | **Subsidie & registraties** (ISDE, F-gassen/BRL 100 logboek, garantie-registratie fabrikant) | Foutgevoelig, klant wacht op subsidie | Checklist + documenten verzamelen, aanvraag voorbereiden voor klant | 4 | 4 |
| 10 | **Onderhoudscontracten** | Jaarlijkse onderhoudsbeurten inplannen, verlengingen | Automatisch uitnodigen, inplannen, contract verlengen | 4 | 5 |
| 11 | **Storingen & klantenservice** | Telefoon roodgloeiend in de winter | Eerste-lijns triage (foutcode uitleg, eenvoudige oplossingen), urgentie bepalen, storing inplannen | 5 | 4 |
| 12 | **Kennisbank monteurs** | Handleidingen/foutcodes zoeken op locatie | Vraag-antwoord over installatiehandleidingen en foutcodes | 3 | 5 |
| 13 | **Reviews & nazorg** | Weinig Google reviews | Na oplevering automatisch tevredenheid/review vragen | 2 | 5 |

## Beslissingen (sessie 2)

- **Doelgroep:** HVAC-installateurs: warmtepompen, airco, cv-onderhoud.
- **Software MVP:** Syntess (projecten/planning/werkbonnen) en Exact Online (boekhouding/facturatie).
- **Grootste pijnpunten:** handmatige offertes, handmatig inplannen van monteurs, vergeten materialen, ontbrekende foto's/documentatie na reparatie.
- **Kanalen:** één centraal platform met kanaal-adapters (e-mail, WhatsApp, webportaal, later telefoon), per klant aan/uit te zetten.
- **Pilotklant:** volgt.

Uitwerking van de focus-workflows: [`02-focus-workflows.md`](02-focus-workflows.md).
Architectuur: [`03-architectuur.md`](03-architectuur.md).
