# Statistik als Modellierung – Flipped-Classroom-Website

Quarto-Website mit Selbsttest (webexercises) und interaktiver Grafik (OJS) zum
einfachen linearen Modell.

## Erste Schritte

1. **Pakete installieren** (einmalig, in R):

   ```r
   install.packages(c("webexercises", "ggplot2"))
   ```

2. **Dateien ins Projekt legen.** Alle Dateien dieses Ordners in ein
   Quarto-Website-Projekt kopieren (z. B. ein neues Projekt via
   *File → New Project → Quarto Website* in RStudio anlegen und die Dateien
   dort hineinlegen bzw. ersetzen).

3. **Setup einmalig ausführen** (legt `include/webex.css` und
   `include/webex.js` an – diese werden von `_quarto.yml` referenziert):

   ```r
   source("setup.R")
   ```

4. **Rendern:** in RStudio auf **Render** klicken, oder im Terminal:

   ```bash
   quarto render
   ```

   Die fertige Seite liegt danach im Ordner `_site/`.

## Dateien

| Datei | Zweck |
|---|---|
| `_quarto.yml` | Website-Konfiguration, bindet webex- und image-quiz-CSS/JS ein |
| `index.qmd` | Startseite |
| `vorbereitung-lineares-modell.qmd` | Selbsttest + interaktive Grafik |
| `setup.R` | Kopiert die webexercises-Dateien nach `include/` |
| `include/` | Wird durch `setup.R` befüllt (webex.\*) und enthält zusätzlich `image-quiz.css`/`image-quiz.js` für die klickbaren Diagramm-Kacheln |
| `images/` | Wird beim Rendern automatisch erzeugt (einzelne PNGs der fünf Diagramme A–E für den Bild-Quiz) |

## Hinweise

- Der Selbsttest läuft vollständig im Browser – kein Server nötig, damit auch
  auf GitLab Pages problemlos hostbar.
- Die Lösungen stehen im HTML-Quelltext; für einen echten (bewerteten) Test ist
  webexercises daher nicht gedacht, für Selbstkontrolle aber ideal.
- Die interaktive Grafik nutzt ObservableJS, das Quarto bereits mitbringt – auch
  hierfür ist kein zusätzliches Paket und kein Server erforderlich.
