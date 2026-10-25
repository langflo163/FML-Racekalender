# FML Rennkalender

Motorsport-Termine mit Startzeit in deutscher Zeit und deutschsprachiger Übertragung.
Läuft als Web-App auf iPhone, iPad, Android und PC (offlinefähig, zum Home-Bildschirm hinzufügbar).

**Serien:** Formel 1, Formel E, DTM, NLS, 24h Nürburgring, WEC, ELMS, IMSA, GT World Challenge Europe,
Intercontinental GT Challenge, 24H Series, IndyCar, NASCAR Cup, MotoGP, Moto2, Moto3, Superbike-WM, Truck-EM, eNASCAR

## Aufbau
- `index.html` – die komplette App (Serien lassen sich unter „Serien“ pro Gerät ausschalten)
- `data/races.json` – alle Termine und Sender (nur diese Datei wird bei Updates geändert)
- `insta/`, `.github/workflows/instagram.yml`, `posts/` – automatische Instagram-Posts (siehe CLAUDE.md)
- `sw.js`, `manifest.json`, `icons/` – Offline-Betrieb und App-Symbol (eigenes Design)

## Datenformat (`data/races.json`)
Ein Termin hat genau eins von:
- `start` – Rennstart mit Zeitzone der Strecke, z. B. `2026-10-25T15:00:00-05:00` (die App rechnet in deutsche Zeit um)
- `date` – nur Renntag bekannt, Uhrzeit folgt
- `from` / `to` – nur Wochenende bekannt

`dur` – Dauer in Stunden (optional, z. B. `24` für 24h-Rennen). Ohne Angabe: Qualifying/Sprint 1 h, Rennen = Richtwert der Serie (`dur` an der Serie, z. B. NASCAR 3,5, MotoGP 0,75, NLS 4), sonst 2,5 h. Danach verschwindet der Termin aus „Nächste“; solange er läuft, steht er oben unter „Läuft gerade“.

`tv` am Termin überschreibt die Sender der Serie. Sendertypen: `mine` (eigene Sender), `free`, `pay`, `open` (noch offen).
`hl: true` markiert Highlights.

Keine Logos oder fremden Bilder – nur Namen, Termine und eigene Farben.
Angaben ohne Gewähr.

## Meisterschaftsstand (`data/standings.json`)
Pro Serien-ID ein Eintrag, angezeigt in der Detailansicht eines Termins:
```json
"f1": { "title": "Fahrer-WM 2026", "asof": "nach GP USA",
        "tables": [ { "name": null, "rows": [[1, "Name", "Team", "325"]] } ] }
```
Normale Serien: komplette Tabelle. Multiclass-Serien (WEC, IMSA, ELMS, GTWC, NLS, 24H Series …):
je Klasse eine Tabelle (`"name": "Hypercar", "top": 5`) – nur die Top 5 der vier höchsten Klassen.

`champion` (optional): `{"name", "title", "team", "date": "YYYY-MM-DD"}` sobald der Titel entschieden ist (für Instagram-Story).
Termine können `"new": true` haben (neue Strecke im Kalender).

Sender-Links ergänzt die App automatisch anhand des Sendernamens; abweichend kann ein Sender `"url"` haben.
