# GapYas Research Integration

Die vollständige Forschungsablage von **GapYas** ist hier als Git-Submodule eingebunden:

- Quelle: https://github.com/alizema700/GapYas
- Gepinnter Commit: `52a17323d9182bfe6b9aff408fa13450e68657fd`
- Zielpfad: `research/gapyas`
- Archiv-DOI aus GapYas: `10.5281/zenodo.22975868`

GapYas enthält u. a. rigorose Computer-Assisted-Proofs, Lean-Formalisationen, numerische Verifikation, erweiterte Suchläufe, asymptotische Analysen, Theorem-spezifische Prover und Paper-Artefakte.

## Einbinden

Nach dem Klonen von Daddys-Project:

```bash
git submodule update --init --recursive
```

Danach liegt die Research-Suite unter `research/gapyas/`.

## Methodischer Status

Die Ablage wird **nicht automatisch** zu bestätigten Claims. Daddys-Project behandelt GapYas als Forschungs-/Evidenzmaterial; Aussagen werden weiterhin nur über die vorhandenen Verifier, Gates und Claim-Evidenz in Daddys-Project als bestätigt übernommen.
