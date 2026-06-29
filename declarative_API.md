# BIG-IP v21.1 Declarative API: Koniec éry, keď bola automatizácia BIG-IP synonymom pre AS3?

Ak ste sa posledné roky pohybovali okolo F5 BIG-IP a chceli ste konfiguráciu automatizovať, takmer s istotou ste skončili u AS3 (Application Services 3 Extension). Bol to de facto štandard — a stále je. Ale s príchodom **BIG-IP v21.1** F5 otvára novú kapitolu: priamo do jadra TMOS integrovanú **Declarative API**, ktorá ide úplne iným smerom než AS3. Pozrime sa, čo presne prináša, ako sa líši od AS3 a prečo by ste si ju (ešte) nemali nasadzovať do produkcie.

## Prečo vlastne nová API, keď máme AS3?

AS3 odviedlo za posledných pár rokov obrovský kus práce — zjednodušilo deklaratívnu konfiguráciu aplikačných služieb a stalo sa štandardným nástrojom pre CI/CD pipeline a orchestráciu tretích strán. Problém je, že AS3 je **samostatná iApps LX extenzia** s vlastným lifecyclom (treba ju nainštalovať, verzovať a udržiavať mimo samotného BIG-IP softvéru) a používa **per-tenant model**, ktorý sa pri veľkých a komplexných konfiguráciách stáva ťažko spravovateľným.

F5 reaguje na rastúci dopyt po takmer instantných konfiguračných zmenách vo veľkom merítku. Riešením je nová **BIG-IP Declarative API**, ktorá je:

- **plne integrovaná do BIG-IP** – žiadna samostatná správa lifecyclu ako pri AS3,
- postavená na **per-app modeli** namiesto per-tenant, čo umožňuje rozbiť veľké AS3 konfigurácie na menšie, opakovane použiteľné moduly,
- navrhnutá s oveľa širším pokrytím automatizácie než AS3,
- rýchlejšia – konfigurácie sa nasadzujú takmer v reálnom čase.

Dôležité je hneď na úvod povedať: **toto nie je nová verzia AS3**. Je to úplne odlišný, paralelný prístup k deklaratívnej konfigurácii BIG-IP.

## Filozofia: resource-oriented model namiesto custom syntaxe

Najväčší koncepčný rozdiel oproti AS3 je v tom, **na čom je nová API postavená**.

AS3 používa vlastnú, aplikačne orientovanú syntax – objekty a vlastnosti v AS3 deklarácii nezodpovedajú priamo objektom v tmsh alebo iControl REST. Je to abstrakcia nad BIG-IP konfiguráciou.

Nová Declarative API ide presne opačnou cestou: je to **resource-oriented model**, kde sa objekty BIG-IP LTM (nody, pooly, virtuálne servery, profily) definujú **explicitne** a ich vlastnosti zodpovedajú existujúcim iControl REST resource modelom. Inými slovami – ak poznáte `tmsh` alebo iControl REST, štruktúra deklarácie vám bude okamžite povedomá.

Každý zdroj v deklarácii má dve kľúčové časti:

- **`kind`** – typ BIG-IP zdroja, formátovaný podľa iControl REST resource kind (napr. `tm:ltm:pool`),
- **`properties`** – konfiguračné hodnoty zdroja, vychádzajúce priamo z iControl REST properties (bez systémových polí ako `kind`, `fullPath`, `generation`, `selfLink` či `*Reference`).

Príklad jednoduchého pool zdroja:

```json
{
  "kind": "tm:ltm:pool",
  "properties": {
    "name": "pool_01",
    "loadBalancingMode": "round-robin",
    "members": [
      {
        "name": "10.0.0.10:80"
      }
    ]
  }
}
```

Mapovanie medzi deklaratívnymi `kind` hodnotami a iControl REST endpointmi je priamočiare:

| Declarative `kind`   | iControl REST endpoint  |
|-----------------------|--------------------------|
| `tm:ltm:pool`         | `/mgmt/tm/ltm/pool`     |
| `tm:ltm:virtual`      | `/mgmt/tm/ltm/virtual`  |
| `tm:ltm:node`         | `/mgmt/tm/ltm/node`     |

Validácia deklarácií prebieha cez interne reprezentovanú YAML/OpenAPI-based schému, odvodenú z metadát BIG-IP LTM zdrojov – túto schému však F5 (aspoň zatiaľ) nezverejňuje pre verziu 21.1.x.

## Ako sa s API komunikuje

### Endpoint

Celá API je vystavená cez štandardné BIG-IP REST rozhranie:

```
https://<BIG-IP>/mgmt/tm/sys/app-service
```

Tento endpoint platí pre rad 21.1.x – F5 explicitne upozorňuje, že štruktúra URI je verzovo špecifická a v budúcich vydaniach sa môže zmeniť.

### Autentifikácia

Používa sa štandardná BIG-IP REST autentifikácia. Odporúčaný spôsob je token-based prístup:

```bash
curl -sk -X POST https://<BIG-IP>/mgmt/shared/authn/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "<username>",
    "password": "<password>",
    "loginProviderName": "tmos"
  }'
```

Vrátený token sa potom použije v hlavičke ďalších požiadaviek:

```bash
curl -sk -X POST https://<BIG-IP>/mgmt/tm/sys/app-service \
  -H "Content-Type: application/json" \
  -H "X-F5-Auth-Token: <token>" \
  -d @declaration.json
```

Pre rýchle testovanie je možná aj Basic autentifikácia, F5 ju však pre produkčné a automatizačné scenáre neodporúča.

### Podporované HTTP metódy

| Metóda | Účel                                                   |
|--------|---------------------------------------------------------|
| GET    | Načítanie nasadených deklarácií a zdrojov               |
| POST   | Vytvorenie novej deklarácie                              |
| PUT    | Nahradenie existujúcej deklarácie                        |
| DELETE | Odstránenie deklarácie a súvisiacich zdrojov             |

Pri `DELETE` stojí za zmienku jedna praktická drobnosť: cleanup sa snaží odstrániť všetky nasadené zdroje, ale niektoré automaticky vytvorené objekty – typicky nody vygenerované MCP procesom pre pool members – môžu zostať, pokiaľ neboli explicitne definované v pôvodnej deklarácii. F5 avizuje, že vylepšené spracovanie cleanup-u prinesú budúce vydania.

## Quick start: nasadenie HTTP služby

Poďme si to ukázať na reálnom príklade z dokumentácie – nasadenie jednoduchej HTTP aplikácie. Deklarácia vytvorí:

- dva nody (`10.0.8.10`, `10.0.8.11`),
- pool `html_pool` s round-robin load balancingom,
- HTML profil `html_profile`,
- virtuálny server `html_virtual` počúvajúci na `10.1.2.27:80`,
- pripojené HTTP a TCP profily na virtuálnom serveri.

```json
{
  "name": "html_app",
  "partition": "Common",
  "resources": [
    {
      "kind": "tm:ltm:node",
      "properties": {
        "name": "10.0.8.10",
        "address": "10.0.8.10",
        "monitor": "default"
      }
    },
    {
      "kind": "tm:ltm:node",
      "properties": {
        "name": "10.0.8.11",
        "address": "10.0.8.11",
        "monitor": "default"
      }
    },
    {
      "kind": "tm:ltm:pool",
      "properties": {
        "name": "html_pool",
        "loadBalancingMode": "round-robin",
        "members": [
          { "name": "10.0.8.10:80", "ratio": 1, "state": "user-up" },
          { "name": "10.0.8.11:80", "ratio": 1, "state": "user-up" }
        ]
      }
    },
    {
      "kind": "tm:ltm:profile:html",
      "properties": {
        "name": "html_profile",
        "defaultsFrom": "html",
        "contentDetection": "enabled"
      }
    },
    {
      "kind": "tm:ltm:virtual",
      "properties": {
        "name": "html_virtual",
        "destination": "10.1.2.27:80",
        "ipProtocol": "tcp",
        "mask": "255.255.255.255",
        "pool": "html_pool",
        "profiles": [
          { "name": "html_profile" },
          { "name": "/Common/http", "context": "all" }
        ],
        "source": "0.0.0.0/0"
      }
    }
  ]
}
```

Všimnite si dve veci, ktoré sú typické pre celý tento prístup:

1. **Žiadna abstrakcia** – `loadBalancingMode`, `defaultsFrom`, `ipProtocol` sú presne tie isté property names, na ktoré ste zvyknutí z `tmsh` alebo iControl REST.
2. **`name` a `partition`** na najvyššej úrovni určujú, do akej "aplikácie" (app-service) sa zdroje zoskupia – analogicky k tomu, ako AS3 zoskupuje zdroje do tenantov a aplikácií, len v menšom, granulárnejšom merítku.

Deklaráciu potom odošlete jediným POST požiadavkom:

```bash
curl -sku <username>:<password> \
  -X POST https://<BIG-IP>/mgmt/tm/sys/app-service \
  -H "Content-Type: application/json" \
  -d @declaration.json
```

V BIG-IP 21.1.x sa nasadenie spracúva **synchrónne** – na rozdiel od niektorých iných F5 automatizačných nástrojov tu (zatiaľ) nenájdete asynchrónne task handling.

## Spracovanie odpovedí a chýb

Úspešná odpoveď vám vráti potvrdenie vytvorených zdrojov v rovnakej štruktúre, akú ste poslali:

```json
{
  "name": "my_app",
  "partition": "Common",
  "resources": [
    {
      "kind": "tm:ltm:pool",
      "properties": {
        "loadBalancingMode": "round-robin",
        "members": [
          { "name": "/Common/10.0.0.10:443", "ratio": 1, "state": "user-up" }
        ],
        "name": "pool_01"
      }
    },
    {
      "kind": "tm:ltm:virtual",
      "properties": {
        "destination": "10.1.1.10:443",
        "ipProtocol": "tcp",
        "mask": "255.255.255.255",
        "name": "virtual_01",
        "pool": "pool_01"
      }
    }
  ]
}
```

Zoznam aktuálne nasadených aplikácií zistíte jednoduchým GET-om:

```
GET https://<BIG-IP>/mgmt/tm/sys/app-service
```

Pri chybách API vracia štandardné HTTP stavové kódy:

| Kód | Význam                                      |
|-----|-----------------------------------------------|
| 400 | Neplatná deklarácia alebo malformovaný request |
| 401 | Zlyhanie autentifikácie                       |
| 403 | Nedostatočné oprávnenia                       |
| 404 | Zdroj alebo endpoint nenájdený                |
| 409 | Konflikt zdrojov                              |
| 422 | Zlyhanie validácie alebo nasadenia            |
| 500 | Interná chyba spracovania                     |

Typický príklad – pokus o opätovné vytvorenie už existujúcej aplikácie skončí kódom 422:

```json
{
  "code": 422,
  "message": "Failed to create application service: application service my_app already exists, please use the update operation instead"
}
```

Pri troubleshootingu sa oplatí pozrieť do logov:

```
/var/log/restjavad.*
/var/log/ltm
/var/log/declared.log
```

## Čo nová API (zatiaľ) nevie

A teraz k tomu najdôležitejšiemu – prečo to nepúšťajte rovno do produkcie.

BIG-IP v21.1 predstavuje túto API ako **Early Access (EA)** funkciu, výslovne **nie určenú pre produkčné nasadenia**. Konkrétne limitácie, ktoré by mali ovplyvniť vaše rozhodnutie o adopcii:

- **Žiadna podpora WAF/security policy.** Pripojenie bezpečnostných politík cez deklaráciu jednoducho nie je v 21.1.x podporované – ak potrebujete WAF, musíte sa vrátiť k existujúcim konfiguračným postupom.
- **Žiadne formálne API verzovanie.** API momentálne nepoužíva schému ani API verzia identifikátory v klasickom zmysle.
- **Žiadna garantovaná spätná kompatibilita.** Endpointy, schémy a podporované vlastnosti zdrojov sa môžu medzi 21.1.x a budúcim major release zmeniť. F5 sľubuje "reasonable efforts", nie záruku.
- **Žiadne OpenAPI specs pre klientov.** Na rozdiel od AS3, kde máte k dispozícii verejnú schému, tu zatiaľ nie sú OpenAPI specifikácie plánované na zverejnenie pre rad 21.1.x.
- **Pokrytie zdrojov je limitované** na overené scenáre danej verzie – aktuálne najmä HTTP/HTTPS, TCP/UDP, FastL4, DNS, LDAP, RADIUS, SIP, SSL profily a šifry, analytics a persistence profily, iRules, a nasadenia v non-Common partíciách.

Pre roadmapu F5 avizuje (bez konkrétneho termínu) rozšírenie o ďalšie typy objektov, onboarding-related zdroje, service discovery integrácie, externé načítanie zdrojov z URL a alternatívne formáty obsahu ako Base64-encoded payloads.

## AS3 vs. nová Declarative API: rýchle porovnanie

| | **AS3** | **Nová Declarative API** |
|---|---|---|
| Stav | Produkčne zrelé, široko používané | Early Access (EA), nie pre produkciu |
| Lifecycle | Samostatná iApps LX extenzia | Plne integrovaná do BIG-IP |
| Model | Aplikačne orientovaný, per-tenant | Resource-oriented, per-app |
| Syntax | Vlastná, abstrahovaná | Zodpovedá tmsh / iControl REST |
| Schéma | Verejná, dokumentovaná | Interná, nezverejnená pre 21.1.x |
| WAF/security politiky | Podporované | Nepodporované |
| Asynchrónne nasadenie | Áno | Nie (len synchrónne) |

Dôležité: **AS3 aplikácie a zdroje nemožno referencovať ani spravovať cez novú Declarative API** – ide o dve oddelené, nekompatibilné cesty.

## Tak má to zmysel skúšať?

Áno – ako evaluáciu a vývoj, nie ako náhradu AS3 v produkcii. Ak vaše prostredie potrebuje:

- tesnejšie zviazanie deklarácie s natívnym tmsh/iControl REST modelom,
- možnosť po nasadení siahnuť priamo do objektov cez tmsh,
- granulárnejšie, per-app rozdelenie konfigurácie namiesto veľkých per-tenant blokov,

... oplatí sa s týmto API začať experimentovať už teraz v testovacom prostredí, aby ste boli pripravení, keď F5 (predpokladane v ďalších major release-och) prinese stabilnejšiu, plne podporovanú verziu s verejnou schémou a širším pokrytím zdrojov – vrátane bezpečnostných politík, ktoré dnes citeľne chýbajú.

Do tej doby ostáva AS3 jasnou voľbou pre produkčnú automatizáciu. Nová Declarative API je však zaujímavým signálom toho, kam F5 smeruje s modernizáciou TMOS control plane — a stojí za to ju sledovať.

---

*Zdroj: [BIG-IP Declarative API Overview and Quick Start, BIG-IP 21.1.0 Documentation](https://techdocs.f5.com/en-us/bigip-21-1-0/big-ip-declarative-api/big-ip-declarative-api.html)*
