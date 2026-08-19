# Guía de uso — token-optimization-skill

Ejemplos de antes/después. Ninguno requiere que el alumno instale nada más allá de esta
skill — `codegraph` y `engram` son opcionales, y `caveman` ya viaja con
`postman-newman-skill`.

---

## 1. Buscar un símbolo en el código

**Sin criterio (más tokens, más lento):**
```
grep -r "calcularMonto" .
# 40 resultados, hay que abrir cada archivo para ver cuál es la definición real
```

**Con esta skill:**
- Si `codegraph` está configurado → `codegraph_search "calcularMonto"` devuelve tipo,
  ubicación y firma en una sola llamada.
- Si no está configurado → seguir con `grep`/`Grep`, pero acotado con `head_limit` y
  `output_mode: files_with_matches` primero, y recién después leer el archivo puntual.

---

## 2. Retomar un flujo que ya se investigó antes

**Sin criterio:** volver a leer 6 archivos para reconstruir por qué el equipo eligió Hurl
sobre Postman en este proyecto.

**Con esta skill:**
- Si `engram` está configurado → `mem_search "hurl vs postman"` trae la decisión guardada de
  una sesión anterior, con el motivo.
- Si no está configurado → preguntar al alumno o revisar el `CLAUDE.md` del proyecto (ahí es
  donde esta skill recomienda fijar decisiones repetidas).

---

## 3. Sesión larga corriendo varias skills del curso

**Sin criterio:** cada corrida de `/postman:fix` o `/jmeter:fix` devuelve explicaciones largas
y el historial crece hasta necesitar `/compact` a mitad de la semana 5.

**Con esta skill:** activar `/caveman` al arrancar una sesión de trabajo intensivo — las
salidas de generación, fix y CI quedan igual de precisas pero en una fracción de los tokens.
Ver `postman-newman-skill/skills/caveman/SKILL.md` para los niveles (`lite`, `full`, `ultra`).

---

## Cuándo NO aplica

Nada de esto reemplaza los pasos de verificación de cada skill (context intake, confirmación
antes de generar, escaneo de secretos en `course-pr-skill`). El objetivo es elegir la
herramienta más barata para llegar al mismo resultado correcto — nunca saltarse un paso para
ahorrar tokens.
