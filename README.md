# Sentinelle syndic: French condominium manager and mandate end date MCP server

**MCP server and pay-per-call API for AI agents.** From the official French condominium registry (ANAH, about 656,000 condominiums), it returns who manages a condominium and when the manager's mandate ends, and lists the condominiums of a town, postcode, department or manager portfolio whose mandate ends soon.

- **MCP endpoint (streamable HTTP):** `https://syndic.amacunia.fr/mcp`
- **REST endpoints:** `GET https://syndic.amacunia.fr/v1/syndic?immatriculations=AA0581645` and `GET https://syndic.amacunia.fr/v1/syndic/echeances?commune=44109&type_syndic=professionnel`
- **Free sample:** https://syndic.amacunia.fr/v1/exemple
- **Docs for agents:** https://syndic.amacunia.fr/llms.txt
- **Price:** 0.01 USDC per call for 1 to 50 condominiums, 0.03 USDC per call for an area list (up to 100 condominiums), paid with the [x402](https://x402.org) protocol on Base. No account, no API key, no subscription. Free trial: 3 calls per day per caller on `/v1/syndic`.
- **Official MCP Registry:** `io.github.Marcoco27/sentinelle-syndic`

## Why it exists

Every French condominium (*copropriété*) is registered with the national registry run by the Agence nationale de l'habitat (art. L711-1 Code de la construction et de l'habitation). Its manager, the *syndic*, declares its mandate there. A mandate lasts **three years at most** (art. 28 of decree 67-223 of 17 March 1967); before it ends, the co-owners' general meeting renews it or picks another manager.

Property managers who want to bid before that meeting, building insurers, contractors and real-estate software vendors need to know which mandates end when. The registry is public but only as a large daily file. This server indexes it and answers in one call.

## Tools

| Tool | Price | What it does |
|---|---|---|
| `syndic_lookup` | 0.01 USDC (x402) | Current professional manager, SIRET, mandate end date and status for 1 to 50 condominiums (registry number) |
| `syndic_echeances` | 0.03 USDC (x402) | Condominiums of an area whose mandate ends within a date window (default next 180 days), up to 100 per call, sorted by end date |
| `syndic_example` | free | Real answers (a condominium in Nantes and an extract of the Nantes list, computed as of 2026-11-09) to see the output shape |

**Input of `syndic_lookup`:** `immatriculations`, 1 to 50 registry numbers (two letters, seven digits), comma-separated.

**Input of `syndic_echeances`:** one area among `commune` (INSEE code), `code_postal`, `departement` or `siret_syndic` (a manager's portfolio); optional `apres`, `avant` (date window, at most two years), `type_syndic` (`professionnel`, `bénévole`), `lots_min`, `decalage` (paging). Invalid input is refused and never charged.

## Example output

A 421-lot condominium in Nantes whose manager's mandate ends on 13 November 2026.

```json
{
  "date_calcul": "2026-11-09",
  "mandats_finissant_sous_90_jours": 1,
  "resultats": [{
    "immatriculation": "AA0581645",
    "trouvee": true,
    "copropriete": {
      "nom_usage": "NAMET C",
      "commune": "Nantes",
      "code_insee": "44109",
      "lots_total": 421,
      "periode_construction": "De 1949 à 1974",
      "type_syndic": "professionnel",
      "syndic": "AMARA GESTION",
      "siret_syndic": "95150146900013",
      "date_fin_mandat": "2026-11-13",
      "jours_avant_fin_mandat": 4,
      "statut": "echeance_dans_90_jours",
      "date_derniere_mise_a_jour": "2026-10-17"
    }
  }],
  "donnees": { "millesime": "2026-11-07", "adresse": "https://www.data.gouv.fr/datasets/62da71c068871f4c54258c7c/" },
  "source": "Registre national d'immatriculation des copropriétés, ANAH, data.gouv.fr (Licence Ouverte 2.0) ; art. L. 711-1 du code de la construction et de l'habitation",
  "avertissement": "Information, pas un conseil juridique. Les données sont déclarées par le syndic au registre…"
}
```

Field names are in French. `statut` is one of `mandat_en_cours`, `echeance_dans_90_jours`, `echeance_depassee_fiche_a_mettre_a_jour`, `echeance_depassee_successeur_declare`, `echeance_depassee_sans_mandat_declare`, `aucune_date_de_fin_declaree`.

## Connect

Any MCP client can connect and call `syndic_example`. Calling a paid tool returns an x402 *payment required* answer: the client must support x402 payments to pay it (see below).

**Claude Code**

```bash
claude mcp add --transport http sentinelle-syndic https://syndic.amacunia.fr/mcp
```

**Claude Desktop / claude.ai:** Settings, Connectors, *Add custom connector*, URL `https://syndic.amacunia.fr/mcp`.

**Cursor** (`~/.cursor/mcp.json`)

```json
{ "mcpServers": { "sentinelle-syndic": { "url": "https://syndic.amacunia.fr/mcp" } } }
```

**VS Code** (`.vscode/mcp.json`)

```json
{ "servers": { "sentinelle-syndic": { "type": "http", "url": "https://syndic.amacunia.fr/mcp" } } }
```

## Paying with x402

The paid tools follow the x402 MCP convention: the first call returns the payment requirements (scheme `exact`, network Base `eip155:8453`, asset USDC, amount `10000` = 0.01 USDC or `30000` = 0.03 USDC); the client signs a payment, puts it in the request `_meta` under `x402/payment`, and calls again. The payment is settled only if the tool succeeds: invalid input is never charged.

A minimal Python client with the official `x402` SDK is in [`examples/pay_mcp.py`](examples/pay_mcp.py). The same service is also sold over plain HTTP (`GET /v1/syndic` and `GET /v1/syndic/echeances`, HTTP 402 then retry), which every x402 HTTP client supports.

## Data and limits

- Source: Registre national d'immatriculation des copropriétés, Agence nationale de l'habitat (ANAH), published on data.gouv.fr under the Licence Ouverte 2.0 (Etalab), refreshed daily.
- The data is declared by the managers themselves: a past end date may mean an outdated record rather than a condominium without a manager; `statut` says which case the record shows.
- Only professional managers (companies) are named. The identity of volunteer managers is not published by the registry and is never returned. No personal data is returned or stored.
- Information only, not legal advice.

## Same author

- [Sentinelle créances](https://github.com/Marcoco27/sentinelle-creances-mcp): French insolvency notices per company and the creditor claim filing deadline.
- [Sentinelle catnat](https://github.com/Marcoco27/sentinelle-catnat-mcp): French natural-disaster decrees per commune and the open insurance-claim deadline.

## About this repository

This repository holds the public documentation, the MCP Registry manifest ([`server.json`](server.json)) and client examples. The service itself runs at `syndic.amacunia.fr`. Issues and questions are welcome; contact: contact@amacunia.fr.

---

### En français

Serveur MCP et API payable à l'appel pour les agents IA : d'après le registre national d'immatriculation des copropriétés (Anah), le syndic professionnel en place et la date de fin de son mandat, copropriété par copropriété, et la liste des copropriétés d'une commune, d'un code postal, d'un département ou du portefeuille d'un syndic dont le mandat finit bientôt. Un centime de dollar la fiche, trois la liste (protocole x402, USDC sur Base). Information, pas un conseil juridique. Présentation : https://syndic.amacunia.fr
