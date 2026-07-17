# Script guidance — DuckRabbit

Scripts are thin entry points. Domain behavior belongs in `src/duckrabbit/`.
`generate_illusions.py` only resolves the project path and delegates to the
package CLI. Do not place generator math, parameter parsing, or codec logic in
this directory.

