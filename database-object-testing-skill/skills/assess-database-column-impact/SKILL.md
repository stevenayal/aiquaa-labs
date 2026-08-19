---
name: assess-database-column-impact
description: Descubrir relaciones y evaluar el impacto funcional de ampliar columnas core en bases de datos relacionales mediante una API REST. Usar cuando Codex deba identificar tablas, vistas, triggers, stored procedures o packages que insertan, actualizan o consultan una columna; analizar riesgos de VARCHAR, VARCHAR2, CHAR o longitudes BYTE/CHAR; detectar parámetros, variables, casts o truncamientos incompatibles; generar pruebas de frontera con rollback; o demostrar que una ampliación de caracteres no afecta INSERT y UPDATE dependientes.
---

# Evaluar impacto de cambios en columnas

Usar el comando `impact` del runner `database-object-testing-skill/src/cli.mjs`. No conectarse directamente a la base de datos y no afirmar ausencia de impacto basándose solo en búsqueda de texto.

## Flujo obligatorio

1. Identificar esquema, tabla core, columna, tipo, longitud anterior, longitud nueva y semántica `CHAR` o `BYTE`.
2. Confirmar que el cambio sea una ampliación. Para reducción, cambio de tipo o semántica usar un análisis específico más estricto.
3. Leer [dependency-contract.md](references/dependency-contract.md) al integrar el endpoint REST de dependencias.
4. Exigir que la API descubra dependencias desde metadata del motor y análisis del source: FK, vistas, triggers, procedimientos, funciones y packages. Incluir sinónimos y SQL dinámico como limitaciones explícitas.
5. Crear un archivo de impacto según [impact-spec.md](references/impact-spec.md).
6. Exigir una invocación reproducible por cada operación `INSERT` o `UPDATE` detectada. Una relación sin invocación es una brecha de cobertura y bloquea el veredicto.
7. Ejecutar siempre con `transactionMode: "rollback"`:

```bash
node src/cli.mjs impact --change examples/I_CUSTOMER_NAME_LENGTH.json --output results
```

8. Validar las fronteras:
   - longitud anterior: control;
   - anterior + 1: demuestra que la ampliación atraviesa el SP/package;
   - longitud nueva: límite positivo;
   - nueva + 1: debe rechazarse sin persistir.
9. Verificar aceptación y preservación exacta del valor. Considerar truncamiento, padding o transformación como impacto funcional.
10. Entregar el mapa de dependencias y los informes PDF, JSON, Markdown y JUnit.

## Criterios de impacto

- Fallar si un SP/package referenciado no tiene prueba para la operación detectada.
- Fallar si la longitud efectiva de un parámetro o variable es menor que la nueva longitud.
- Fallar si `SUBSTR`, cast reducido u otra transformación puede truncar el valor.
- Fallar si un valor entre `anterior+1` y `nueva` se rechaza o se persiste modificado.
- Fallar si `nueva+1` se acepta.
- Tratar longitud efectiva desconocida como advertencia, pero no declarar cobertura completa sin prueba dinámica.
- Probar perfiles multibyte cuando la columna use semántica `BYTE` o acepte Unicode.

## Seguridad

- Usar ambientes aislados, datos sintéticos y rollback.
- No ejecutar DDL ni modificar producción.
- Usar usuario de privilegios mínimos y listas permitidas de esquemas/objetos en el gateway.
- No guardar tokens, respuestas sensibles ni valores reales en los informes.

## Límites

La API debe informar dependencias no resolubles, como SQL dinámico construido en runtime, enlaces remotos o invocaciones sin fixture. Reportar estas zonas como riesgo residual; no convertirlas en “sin impacto”.
