# Focus-workflows MVP

Vier workflows die samen het grootste deel van de genoemde tijdverspilling dekken.
Per workflow: huidige situatie (IST), gewenste situatie (SOLL), rol van de agent en
waar een mens moet goedkeuren (*human-in-the-loop*, HITL).

---

## W1. Offerte maken

**IST**
1. Aanvraag komt binnen (mail/telefoon/website).
2. Kantoor belt klant voor info, plant evt. schouw.
3. Monteur/adviseur doet opname (foto's, notities, soms warmteverliesberekening).
4. Werkvoorbereider stelt offerte op in Syntess: artikelen, arbeid, marges, teksten.
5. Offerte wordt gemaild; opvolging gebeurt (of niet) handmatig.

Doorlooptijd: dagen tot weken. Kosten: 1–3 uur kantoortijd per offerte.

**SOLL**
1. Agent verwerkt aanvraag en vraagt ontbrekende info uit via het kanaal van de klant
   (woningtype, bouwjaar, oppervlak, huidige installatie, foto's meterkast/cv-ketel/buitenunit-plek).
2. Agent bepaalt of een schouw nodig is of dat een offerte op afstand kan.
3. Agent kiest een **standaardpakket** (bijv. "hybride warmtepomp 4 kW + installatie"),
   berekent indicatief vermogen, vult artikelen uit de prijslijst en voegt ISDE-indicatie toe.
4. **HITL:** werkvoorbereider controleert concept, past aan, keurt goed.
5. Offerte wordt in Syntess aangemaakt en verstuurd; agent volgt op na 3/7/14 dagen.
6. Bij akkoord: opdracht aangemaakt → doorstroom naar W2 (planning) en W3 (materiaal).

**Benodigde data:** prijslijst/artikelen, standaardpakketten, arbeidsnormen, offertesjablonen, marges.

---

## W2. Monteurs inplannen

**IST:** planner puzzelt met agenda's, vaardigheden (F-gassen, warmtepomp-certificering),
regio, materiaal-beschikbaarheid en klantvoorkeuren; veel heen-en-weer bellen.

**SOLL**
1. Agent ontvangt een in te plannen klus (nieuwe installatie, onderhoud, storing) met
   duur, benodigde vaardigheden, urgentie en materiaal-status.
2. Agent stelt 1–3 planningsopties voor op basis van: bevoegdheid, reistijd/regio,
   beschikbaarheid, levertijd materiaal, klantvoorkeur.
3. **HITL:** planner kiest/bevestigt (later: automatisch voor onderhoud en eenvoudige klussen).
4. Agent bevestigt bij klant, stuurt herinnering dag ervoor, verwerkt verzetverzoeken.
5. Onderhoudscontracten: agent plant de jaarlijkse beurten proactief in (cluster per regio).

**Benodigde data:** monteurs + certificeringen, agenda's (Syntess), werkgebieden, klusduur-normen.

---

## W3. Materiaal compleet

**IST:** materiaal wordt vergeten of niet op tijd besteld → extra rit naar de groothandel,
klus niet afgerond, terugkomen.

**SOLL**
1. Bij akkoord offerte: agent maakt een **materiaallijst** uit de offerte + standaard
   "altijd-mee"-lijst per klustype (koudemiddelleiding, condensafvoer, beugels, kabel, etc.).
2. Agent vergelijkt met voorraad (bus/magazijn) en stelt bestelling voor met levertijd.
3. Planning (W2) houdt rekening met leverdatum.
4. Dag voor de klus: **paklijst** naar monteur ("check je bus").
5. Na de klus: wat is extra gebruikt? → leert de standaardlijst bij.

---

## W4. Werkbon & foto's compleet

**IST:** werkbonnen onvolledig, foto's ontbreken (nodig voor garantie, F-gassen-logboek,
ISDE, discussie met klant), kantoor moet nabellen; facturatie loopt vertraging op.

**SOLL**
1. Per klustype een **checklist** met verplichte items, bijv. warmtepomp-installatie:
   foto buitenunit + typeplaatje, foto binnenunit, foto aansluiting/leidingwerk,
   foto meterkast/groep, vacuüm/druktest-waarde, ingevulde inbedrijfstelling, klanthandtekening.
2. Monteur levert aan via app/WhatsApp (foto + spraakmemo); agent zet om naar werkbon.
3. Agent controleert **vóór de monteur vertrekt** (realtime): "typeplaatje-foto ontbreekt".
   Controle met beeldherkenning (is dit een typeplaatje? leesbaar serienummer?).
4. Compleet → werkbon naar Syntess, factuurconcept naar Exact (**HITL** goedkeuring),
   garantie/F-gassen-registratie voorbereid.

---

## Volgorde van bouwen (voorstel)

| Stap | Wat | Waarom eerst |
|---|---|---|
| 1 | Platform-kern + W4 (werkbon/foto-check) | Snelle winst, weinig integratierisico, zichtbaar voor monteurs |
| 2 | W1 Offerte-concept | Grootste tijdwinst kantoor; vraagt prijslijst-data |
| 3 | W3 Materiaal | Bouwt voort op offerte-data |
| 4 | W2 Planning | Meeste integratie met Syntess-agenda; profiteert van W1/W3 |

Alternatief: starten met W1 als de pilotklant daar de meeste pijn heeft.
