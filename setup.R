# -------------------------------------------------------------------------
# Einmaliges Setup: kopiert die von webexercises benötigten Dateien
# (webex.css und webex.js) in den Ordner include/.
#
# Aus dem Projektordner heraus ausführen:  source("setup.R")
# (Voraussetzung: install.packages("webexercises") wurde bereits ausgeführt.)
# -------------------------------------------------------------------------

if (!requireNamespace("webexercises", quietly = TRUE)) {
  stop("Bitte zuerst installieren: install.packages('webexercises')")
}

dir.create("include", showWarnings = FALSE)

# Die Dateien liegen irgendwo im installierten Paket – wir suchen sie robust,
# unabhängig vom genauen Unterordner der jeweiligen Paketversion.
pkg_root <- system.file(package = "webexercises")

css <- list.files(pkg_root, pattern = "webex\\.css$", recursive = TRUE, full.names = TRUE)[1]
js  <- list.files(pkg_root, pattern = "webex\\.js$",  recursive = TRUE, full.names = TRUE)[1]

if (is.na(css) || is.na(js)) {
  stop("webex.css / webex.js wurden im Paket nicht gefunden. ",
       "Alternativ: webexercises::add_to_quarto() ausprobieren.")
}

file.copy(css, "include/webex.css", overwrite = TRUE)
file.copy(js,  "include/webex.js",  overwrite = TRUE)

message("Fertig. Kopiert nach include/:")
message("  - include/webex.css")
message("  - include/webex.js")
message("Jetzt kann die Website gerendert werden (Quarto -> Render).")
