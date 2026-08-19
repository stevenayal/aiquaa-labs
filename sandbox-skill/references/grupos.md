# Grupos del curso → módulo → endpoints → tablas

Mapeo 1:1 entre `inscripcion-grupos-bdd2.xlsx` (asignación de alumnos) y los tags OpenAPI
del sandbox. Cada grupo trabaja su módulo durante todo el curso, en BDD, rendimiento y BD.

| Grupo | Módulo | Endpoints (grupo `api-contract.md`) | Tablas `qa_training` |
|-------|--------|--------------------------------------|------------------------|
| 1 | Autenticación y Acceso — login / logout / recuperación de contraseña | Grupo 1 | `usuarios`, `sesiones` |
| 2 | Transferencias entre Cuentas — transferencias internas (mismo banco) | Grupo 2 | `cuentas`, `transferencias` |
| 3 | Pagos de Servicios — pago de facturas (ANDE, ESSAP, telefonía) | Grupo 3 | `facturas`, `pagos` |
| 4 | Registro de Usuario / Onboarding — alta de cliente (KYC básico) | Grupo 4 | `usuarios` |
| 5 | Tarjetas de Crédito/Débito — gestión de tarjetas | Grupo 5 | `tarjetas` |
| 6 | Notificaciones y Alertas — push/email/SMS | Grupo 6 | `notificaciones` |
| 7 | Carrito de Compras / E-commerce — checkout | Grupo 7 | `ordenes`, `items_orden` |
| 8 | Reservas / Turnos — sistema de reserva de citas | Grupo 8 | `reservas` |
| 9 | Reportes y Dashboard — panel de control / reportes financieros | Grupo 9 | `movimientos` (vía `reportes/*`) |
| 10 | Administración de Roles y Permisos — backoffice | Grupo 10 | `roles`, `usuario_roles` |

Uso: al empezar el Context Intake de cualquier skill, preguntar el número de grupo y resolver
módulo + endpoints + tablas desde esta tabla en vez de volver a preguntarlos uno por uno.
