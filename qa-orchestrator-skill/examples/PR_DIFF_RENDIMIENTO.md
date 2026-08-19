# Ejemplo — historia de rendimiento (esperado: `jmeter-skill`, confianza alta)

Sin PR — historia de usuario directa (sin diff de código, sin archivos tocados).

**Historia:** "Como responsable de infraestructura, necesito saber cuántos usuarios
concurrentes soporta el endpoint `/api/v1/orders` antes del Black Friday. El SLA acordado es
p95 < 800ms con 200 usuarios concurrentes sostenidos por 10 minutos, sin superar 1% de error
rate. Necesitamos comparar contra el baseline actual."

**Señales esperadas:** keywords "usuarios concurrentes" (peso 8), "SLA" (peso 8), "p95" (peso
6) → `jmeter-skill`, puntaje ≥15 solo por historia (sin señales de ruta porque no hay diff) →
confianza alta igual, porque la suma de keywords supera el umbral. Sin señales de otra capa →
única skill seleccionada. Prerrequisito a verificar antes de `/qa:ejecutar`: JMeter instalado
y confirmación explícita de que el entorno destino no es producción.
