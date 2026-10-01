# Troubleshooting — tgrep

| Síntoma | Causa | Arreglo |
|---------|-------|---------|
| `warning: no index at ... - scanning every file` | No hay índice en el path que miró la búsqueda | Si el servidor/índice usa `--index-path`, pasar el mismo valor a la búsqueda; si no, `tgrep index .` o `tgrep serve .` |
| `Server unreachable, falling back to local index` | El servidor murió o `serve.json` quedó viejo | Reiniciar `tgrep serve .` |
| Un archivo nuevo no aparece, sin servidor | El índice en disco es anterior al archivo | `tgrep index .` |
| Un archivo nuevo no aparece, con servidor | Primer build en curso, o el evento del watcher sigue en cola | Esperar, o `--no-index` para esta búsqueda. Re-ejecutar `tgrep index .` **no** actualiza un servidor corriendo |
| Búsqueda lenta pese al servidor | Un flag saltea el índice (`--no-ignore`, `-a`, `--binary`, `-E`, archivo puntual) | Quitar el flag o acotar con `-g` / `-t` |
| `--stats` muestra `no index narrowing` | El patrón no tiene trigramas útiles (p. ej. `.*`, `\w+`, literales de < 3 caracteres) | Agregar un literal de 3+ caracteres al patrón, o acotar con `-t`/`-g` |
| El patrón se interpreta como subcomando (`serve`, `index`, …) | Falta `--` | `tgrep -F -- serve .` |
| Faltan archivos > 64 MiB | Límite de tamaño por defecto | `--no-max-filesize` en `index`, `serve` y búsqueda; o `--no-index --no-max-filesize` |
| El índice es más grande de lo esperado en una carpeta sin `.git` | `.gitignore` no se aplica fuera de Git | `--no-require-git` en `index`, `serve` y búsqueda |
| Un binario viejo rechaza el índice | Cambio de formato | Reconstruir con ese binario, mejor en otro `--index-path` |
| `-z` sale con código `2` | `--search-zip` no está soportado | Descomprimir antes o usar otra herramienta |
