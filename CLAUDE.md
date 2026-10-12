# FML-Racekalender – Projektgedächtnis

Motorsport-Rennkalender als Web-App (PWA) für Flo. **Vor jeder Arbeit diese Datei und `README.md` lesen.**
Am Ende jeder Arbeitssitzung diese Datei aktualisieren (Stand, Entscheidungen, offene Punkte) und mit committen.

- Repo: `langflo163/FML-Racekalender` – **öffentlich** (bewusst, wegen GitHub Pages)
- Live: https://langflo163.github.io/FML-Racekalender/ (GitHub Pages, Branch `main`, Ordner `/`)
- Läuft auf iPhone, iPad, Android, PC; als App auf dem Home-Bildschirm installiert

## Feste Regeln

- Antworten auf Deutsch, kurz und klar. **Nicht raten** – nur eintragen, was eine Quelle belegt; Unsicheres als `note`.
- **Repo ist öffentlich:** nie echte E-Mail-Adressen, private Daten oder Inhalte aus dem privaten Repo `FML-Github` hier ablegen.
  Commits immer mit `Florian Lang <langflo163@users.noreply.github.com>` (Historie wurde am 10.10.2026 bereinigt).
- **Keine Logos/fremden Bilder** von Serien, Sendern oder Strecken (rechtlich). Nur Namen, Termine, eigene Farben.
  Eigenes FML-Branding ist erlaubt: rote F-M-L-Kacheln (aus FML-ScreenView) im Header, App-Icon = roter Kalender mit „FML“ + Zielflaggen-Streifen.
- Optik: flach, Rot/Weiß/Schwarz (#d71920), Hell/Dunkel-Modus, keine Verläufe.
- Nach Änderungen an `index.html`/Icons: `CACHE`-Version in `sw.js` hochzählen (aktuell `rk-v9`), sonst sehen Geräte die alte Version.
- Vor dem Push lokal testen (Playwright/Chromium im Container, `python3 -m http.server`).

## Inhalt / Entscheidungen

- **Serien:** F1, Formel E, DTM, NLS, 24h Nürburgring (ab 2027 „ADAC 24h Nürburgring Serie“), WEC, ELMS, IMSA,
  GT World Challenge Europe, Intercontinental GT, 24H Series, IndyCar, NASCAR Cup (nur Cup), MotoGP, Moto2, Moto3,
  Superbike-WM, Truck-EM (ETRC), eNASCAR (Coca-Cola iRacing Series – Sim-Rennen, Di-Nacht; dt. Kommentar auf YouTube @BSCOMPETITION, Hinweis von Flo).
- **Aufnahmekriterium:** nur Serien/Sessions, die **live mit deutschem Kommentar** laufen.
  Bewusst nicht aufgenommen: Supercars (kein dt. Kommentar gefunden), IDM (nicht belegt).
  Bei ELMS, IGTC, 24H Series ist dt. Kommentar nicht belegt (eher Englisch) – Flo kann sie in der App ausschalten.
- **Pro Termin:** Datum, Uhrzeit in deutscher Zeit, wo auf Deutsch zu sehen. Qualifyings und Sprints immer mit dabei
  (auch bei Langstrecken-/24h-Rennen), **kein** Schalter dafür.
- **Sender von Flo** (`k: "mine"`, grün): SRF (SRF zwei / SRF info), ORF, ServusTV/ServusTV On, Sportdigital1+, Motorvision TV/Motorvision+.
  Danach kostenlos inkl. YouTube mit dt. Kommentar und DF1 (`free`, blau), dann Abo (`pay`, grau).
  **Sky nur ungern** – nur wenn es keine andere deutsche Quelle gibt. F1 schaut er bei SRF oder ORF/ServusTV.
- **Ansichten:** Nächste (Countdown), Wochenende (Heute | Wochenende, Zeitstrahl, LIVE-Markierung, Überschneidungs-Hinweis),
  Kalender (Monat), Serien (Schalter zum Ausblenden je Serie, pro Gerät gespeichert).
- **Detailansicht** beim Antippen eines Termins: alle Sessions des Wochenendes, Sender mit Direktlinks (`LINKS` in `index.html`),
  Meisterschaftsstand aus `data/standings.json`. Normale Serien komplette Tabelle; Multiclass nur Top 5 der vier höchsten Klassen.
- **Dauer** eines Termins mit Uhrzeit: Quali/Sprint 1 h, Rennen 2,5 h, sonst `dur` (z. B. 24). Danach verschwindet er aus „Nächste“.
- Von Flo **abgelehnt** (nicht bauen): Kalender-Abo .ics (vorerst), Termine merken/Stern, Ergebnisse vergangener Rennen,
  Sender-Filter, Suche, Streckeninfo, Push direkt aus der App.

## Statistik

- GoatCounter (cookielos, keine IPs), Account `fml-rennkalender` → Statistik unter https://fml-rennkalender.goatcounter.com (Login nur Flo).
  Zählt Seitenaufrufe + Tab-Wechsel als Events. Datenschutzhinweis per Link im Footer (`openInfo()` in `index.html`).

## Instagram @fmlrennkalender (aktiv seit 12.10.2026)

- Montag 9:00 Karussell Wochenübersicht (Mo–So), Freitag 12:00 **Reel** Wochenende (Fr–So, 9:16, ohne Ton),
  täglich 8:00 **Story** „Heute live“ (nur an Renntagen; bereits beendete Sessions weg, Nachtrennen vor 8:00 des Folgetags
  stehen schon in der Story des Vortags mit „Nacht auf …“ – Flo-Wunsch). Voll automatisch, Design von Flo freigegeben.
- Tests am 12.10.: Karussell, Reel, Story erfolgreich gepostet (Creator-Konto reicht auch für Storys).
- Info-Post „So läuft's hier“ am 12.10. gepostet (`insta/info_post.py`, Ordner `posts/info-zeiten`). Fertigen Ordner posten: test.json {"mode": "existing", "folder": "posts/…", "publish": true}.
- **Bonus-Storys an rennfreien Tagen** (`insta/free_story.py`, Schalter `bonus` in `insta/config.json`, **aktiv seit 12.10.2026**, Entwürfe von Flo freigegeben):
  max. 1 Story/Tag (Renntag = nur „Heute live“), max. 2 Bonus-Storys/Woche. Priorität: Titel entschieden (nur am 1. Werktag Mo–Fr nach
  Entscheidung, sonst entfällt; zählt nicht zum Wochenlimit) → Neu im Kalender (neue Saison einer Serie erkannt, Warteschlange in
  `insta/state.json`) → Saisonfinale/-start, Zeitumstellung → Heimrennen (DE/AT), Doppel-Wochenende, neue Strecke (`"new": true` am Termin),
  Winterpause (≥10 Serien 30 Tage ohne Rennen, max. alle 21 Tage) → Countdown zu Highlights (`insta/highlights.json`). Countdown/Saisonstart: **jede Veranstaltung max. 1× (Key `event:sid:datum`), höchstens 14 Tage vorher** (Flo-Wunsch, nicht übertreiben)
  → „Serie fehlt?“ (alle 14 Tage). Titel braucht `standings[sid].champion = {name, title, team?, date}` (pflegen die Claude-Updates).
- Testpost auslösen: `insta/test.json` ändern und pushen ({"mode": week|weekend|story, "date", "publish": true}).
- Umsetzung **ohne Claude-Läufe**: GitHub Action `.github/workflows/instagram.yml` → `insta/gate.py` (Zeitplan, `insta/config.json`,
  `enabled`) → `insta/make_post.py` (Bilder 1080×1350 JPEG + `caption.txt` aus `races.json`, Playwright) → Commit nach `posts/`
  → `insta/post.py` (offizielle Instagram API mit Instagram Login, Bilder per raw.githubusercontent.com-URL).
- Secret im Repo: `IG_TOKEN` (von Flo eingetragen; nie ausgeben/loggen). Konto-ID holt `post.py` selbst über `/me` (`IG_USER_ID` war falsch, wird nicht genutzt). `GH_PAT` (fine-grained, nur dieses Repo, Secrets read/write; von Flo am 12.10. eingetragen, läuft nach max. 1 Jahr ab → dann erneuern) für automatisches Speichern
  eines erneuerten Tokens. Token-Verlängerung mittwochs per Workflow (60-Tage-Token).
- Meta-App: Typ Business, Produkt Instagram, Standard Access (eigener Account, kein App Review). Instagram-Account ist Creator-Konto.
- Manuell testen: Actions → „Instagram-Posts“ → Run workflow (mode week/weekend, publish false = nur Bilder).

## Automatische Updates (geplante Aufgaben in Claude, ohne Rückfragen, mit Push)

| Aufgabe | Wann | Was |
|---|---|---|
| „Rennkalender aktualisieren“ | Montag 5:48 | Tabellen der Wochenend-Serien + neue/geänderte Saisonkalender + Startzeiten/Sessions/Sender der nächsten 4 Wochen |
| „Rennkalender Tages-Check“ | Di–So 5:50 | Nur Tabellen der Serien, die gestern gefahren sind; ohne Rennen gestern sofort Ende ohne Websuche |

Sparsam ausgelegt (Flo-Wunsch 11.10.): kein kompletter Neu-Abgleich aller Serien mehr. Kurzfristige Zeitänderungen innerhalb der Woche
werden erst am nächsten Montag erkannt.

Beide ändern nur `data/races.json` und `data/standings.json`. Bei neuen Serien/Regeln die Prompts beider Aufgaben mit anpassen.

## Stand 11.10.2026

- App fertig und live. Sonderlauf 11.10. abends: Meisterschaftstabellen für 15 Serien eingetragen.
  Noch ohne Tabelle: NLS, Intercontinental GT, 24H Series (24h Nürburgring = Einzelevent, keine Tabelle);
  IMSA nur GTP-Klasse mit Punkten, Truck-EM nur Top 6 (komplette Liste nicht gefunden).
- Offen: Startzeiten 2027 (kommen per Update), NLS 2027 + Truck-EM 2027 Kalender noch nicht veröffentlicht,
  Sender bei IMSA/NLS noch „noch zu prüfen“, MotoGP Katar 2026 Absage nur gemeldet, Motorvision+ ohne geprüften Link.
