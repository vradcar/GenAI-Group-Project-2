# LaTeX Report Pack (Overleaf)

This folder contains a TikZ-native LaTeX report.

## Files

- `main.tex` — complete final report with all diagrams drawn directly using TikZ

## What Changed

- Architecture, state, and sequence diagrams are now rendered directly in LaTeX using TikZ.
- No Mermaid image export step is required.

## How to Use in Overleaf

1. Create a new Overleaf project.
2. Upload `docs/latex/main.tex`.
3. Compile.

## Notes

- The style follows the same report format used previously (compact layout, TikZ diagrams, sectioned narrative).
- Mermaid source files remain in `docs/planning/` for traceability.
