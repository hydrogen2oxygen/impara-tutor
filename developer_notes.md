# Impara-Tutor – User Registrierung & Login (ohne Passwort)

Diese App soll lokal laufen (Python + Angular) und mehrere Lernende sauber voneinander trennen können, z.B. in einer Familie, einer Schulklasse oder einem kleinen Betrieb. Es geht nicht um sensible Daten und nicht um hohe Sicherheit, sondern um ein leichtes “Profil auswählen” mit optionaler Neuregistrierung direkt auf der Loginseite.

## Zielbild

Beim Start landet man auf einer Loginseite, die gleichzeitig als “User-Auswahl” dient. Dort sieht man bereits vorhandene Profile als Buttons/Karten (Avatar + Name; später auch kleine öffentliche Details). Auf derselben Seite gibt es eine einfache Registrierung mit Name, Email, Bio und Avatar-Bild. Nach erfolgreicher Registrierung erscheint sofort ein neuer Button/Karte für das neue Profil – ohne Seitenwechsel.

Es gibt kein Passwort. Ein Profil ist eine Identität innerhalb dieser lokalen App-Instanz.

## Begriffe

**User / Profil**  
Ein User ist ein lokales Profil mit eindeutiger ID. Der User ist die Einheit, an die Lernfortschritt, Texte, Vokabeln, Wiederholungen, Statistiken usw. gebunden werden.

**Login**  
Login bedeutet: “Aktiven User auswählen”. Der ausgewählte User wird zur aktuellen Session, damit alle Aktionen klar zugeordnet sind.

**Öffentliches Profil (in der App)**  
Ein kleiner Teil der Profildaten kann in der App sichtbar sein (z.B. Bio, Avatar und später Lern-Highlights), damit in einer Klasse sichtbar wird, woran andere arbeiten. Das ist “öffentlich” nur innerhalb der App-Instanz, nicht im Internet.

## Anforderungen (Funktional)

### Registrierung (auf der Loginseite)

Ein neues Profil kann angelegt werden mit:
- Name (Pflicht)
- Email (optional, aber empfohlen)
- Bio (optional, kurze Beschreibung)
- Avatar (optional, Bilddatei oder später URL)

Nach dem Speichern:
- erscheint das neue Profil sofort in der User-Liste als auswählbarer Button/Karte
- das neue Profil kann direkt ausgewählt werden und startet eine Session

Fehlerfälle:
- Name fehlt → klare Fehlermeldung
- Email ist vorhanden und bereits vergeben (falls wir Email als eindeutig festlegen) → klare Fehlermeldung
- Avatar-Datei zu groß oder falsches Format → klare Fehlermeldung

### Login / User-Auswahl (ohne Passwort)

Auf der Loginseite gibt es eine Liste vorhandener User:
- Jeder User wird als Button/Karte angezeigt (mindestens Avatar + Name)
- Klick auf Button/Karte setzt den aktiven User und navigiert in die App (z.B. Dashboard / Home)
- Der aktive User wird in der App UI sichtbar gemacht (z.B. oben rechts Avatar + Name)

Zusätzlich:
- “Logout” ist ein einfacher Wechsel zurück zur Loginseite und das Entfernen des aktiven Users aus der Session.

### Sichtbarkeit von User-Details (später erweiterbar)

Die Loginseite soll bereits so gebaut werden, dass später weitere Info pro User angezeigt werden kann, z.B.:
- aktuell gelernte Sprache(n)
- aktueller “Baum”-Knoten / Kurs
- kurze Aktivitätsinfo (“zuletzt aktiv”, “aktuelle Streak”, “gerade gelesen: …”)

Wichtig: Diese Details sind innerhalb der App sichtbar, nicht öffentlich im Web.

## Anforderungen (Nicht-funktional)

- Kein Passwort, keine 2FA, keine komplexe Sicherheit.
- Daten sind lokal (SQLite/Datei/IndexedDB – je nach Architektur), nicht Cloud by default.
- Datensparsamkeit: nur speichern, was die App wirklich braucht.
- Avatar möglichst effizient speichern (z.B. Thumbnail), damit die UI schnell bleibt.

## Datenmodell (Vorschlag)

`User`
- `id` (UUID oder int)
- `displayName` (string, required)
- `email` (string, optional; optional unique)
- `bio` (string, optional)
- `avatarRef` (string, optional; Verweis auf Datei/Blob/URL)
- `createdAt` (timestamp)
- `lastActiveAt` (timestamp)

`Session`
- `activeUserId`
- `startedAt`
- `lastSeenAt`

Hinweis: Wenn mehrere Geräte/Browser getrennte Instanzen sind, ist “lokal” auch wirklich lokal pro Gerät. Das ist gewollt.

## UI Verhalten (Definition)

### Loginseite

Bereiche auf einer Seite:
- Profil-Auswahl: Grid/Liste aller User als Karten/Buttons
- Registrierung: kleines Formular am Rand oder als Dialog auf derselben Seite

Interaktionen:
- Klick auf User-Karte → Login (active user setzen) → App Startseite
- Klick auf “Neues Profil” → Formular öffnen
- Speichern → User-Karte erscheint sofort ohne Reload
- Optional: “Profil bearbeiten” (später), “Profil löschen” (später)

### App Shell

- Aktiver User ist ständig sichtbar.
- “User wechseln” führt zurück zur Loginseite.
- Beim Start der App: Wenn eine Session mit aktivem User existiert, direkt in die App; sonst Loginseite.

## API / Storage (Vorschlag)

Backend (Python) sollte einfache Endpunkte bieten:

- `GET /api/users` → Liste aller User (für Loginseite)
- `POST /api/users` → neuen User anlegen
- `PATCH /api/users/{id}` → Profil aktualisieren (später)
- `POST /api/session/login` → active user setzen
- `POST /api/session/logout` → active user entfernen
- `GET /api/session` → aktuelle Session abfragen

Avatar Handling (einfach):
- Entweder als Upload-Endpunkt `POST /api/users/{id}/avatar`
- Oder als DataURL/Blob lokal im Frontend speichern und nur Referenz im Backend ablegen

## Datenschutz / Erwartungsmanagement

Diese App ist bewusst “leichtgewichtig” und nicht für sensible Daten gedacht. In Schul-/Betriebsumgebungen sollte klar kommuniziert werden, welche Profilinformationen andere sehen können. Optional sollte es später pro User eine Einstellung geben: “Profil-Details für andere anzeigen: ja/nein”.

## Umsetzungsaufgaben (konkret)

### Phase 1: Minimal lauffähig
- Datenmodell `User` + Migration/Storage
- `GET /api/users`, `POST /api/users`
- Session-Konzept: active user setzen/lesen
- Angular Loginseite: User-Liste + Registrierung auf derselben Seite
- App Shell: active user anzeigen, “User wechseln”

Akzeptanzkriterien:
- Ohne User: Loginseite zeigt Registrierung, keine User-Karten
- User registriert: Karte erscheint sofort
- Klick auf Karte: App startet unter diesem User
- Reload: User bleibt erhalten; Session optional persistent

### Phase 2: Komfort & Robustheit
- Optional eindeutige Email-Regel (konfigurierbar)
- Avatar Upload + Thumbnail
- “Zuletzt aktiv” pflegen (bei jeder Aktivität)
- Profil bearbeiten (Name/Bio/Avatar)

### Phase 3: Sichtbarkeit in Klasse/Gruppe
- Öffentliche Profilfelder definieren (Preview)
- Loginseite zeigt pro User kleine Lern-Highlights
- Optional Privatsphäre-Toggle pro User

---





# Workflow
I want to learn a new language. My workflow will be as follows:
1. Import card lessons from external sources (e.g., Anki, Memrise).
2. After one session with imported card lessons, create a text according to my learning progress, using the vocabulary I have learned so far and identifying my weak points during the learning process.
3. Use the text to read and learn new vocabulary. Reading is essential for language acquisition, by exposing me to context and usage of words.
4. As a user I can mark unknown words in the text.
5. Unknown words from the text will be added to my vocabulary list, receiving definitions and example sentences from the dictionary database.
5. Create new card lessons from the updated vocabulary list.
6. Repeat steps 2-5 until I reach my desired proficiency level.
7. Additionally give me the option to learn vocabulary through spaced repetition flashcards, writing exercises, and quizzes.
8. Track my progress over time, including words learned, lessons completed, and proficiency levels achieved.
9. Provide analytics and insights on my learning patterns to help optimize my study sessions.

# Components
## Lesson Importer
- Anki Importer
- Memrise Importer
- CSV Importer
- JSON Importer

## Text Generator
- Vocabulary Analyzer
- Weak Point Identifier
- Contextual Text Creator
- Reading Module
- Unknown Word Marker
- Vocabulary Updater
- Definition Fetcher
- Example Sentence Fetcher
- Card Lesson Creator

## Database
- Dictionary DB
- Vocabulary DB
- User Data DB
- Settings DB
- Lessons DB

## Interface APIs
- Import Lessons API
- Export Lessons API (secondary priority)
- Text Generation API
- Vocabulary Management API
- Progress Tracking API

## Progress Tracking
- Progress Logger
- Analytics Module
- Insights Generator

