# FML Rennkalender

Motorsport-Termine mit Startzeit in deutscher Zeit und deutschsprachiger Übertragung.
Läuft als Web-App auf iPhone, iPad, Android und PC (offlinefähig, zum Home-Bildschirm hinzufügbar).

**Serien:** Formel 1, Formel E, DTM, NLS, 24h Nürburgring, WEC, ELMS, IMSA, GT World Challenge Europe,
Intercontinental GT Challenge, 24H Series, IndyCar, NASCAR Cup, MotoGP

## Aufbau
- `index.html` – die komplette App (Serien lassen sich unter „Serien“ pro Gerät ausschalten)
- `data/races.json` – alle Termine und Sender (nur diese Datei wird bei Updates geändert)
- `sw.js`, `manifest.json`, `icons/` – Offline-Betrieb und App-Symbol (eigenes Design)

## Datenformat (`data/races.json`)
Ein Termin hat genau eins von:
- `start` – Rennstart mit Zeitzone der Strecke, z. B. `2026-10-25T15:00:00-05:00` (die App rechnet in deutsche Zeit um)
- `date` – nur Renntag bekannt, Uhrzeit folgt
- `from` / `to` – nur Wochenende bekannt

`tv` am Termin überschreibt die Sender der Serie. Sendertypen: `mine` (eigene Sender), `free`, `pay`, `open` (noch offen).
`hl: true` markiert Highlights.

Keine Logos oder fremden Bilder – nur Namen, Termine und eigene Farben.
Angaben ohne Gewähr.
