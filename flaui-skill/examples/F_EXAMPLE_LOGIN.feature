# language: es
Característica: Login de usuario
  Como usuario registrado
  Quiero iniciar sesión con mis credenciales
  Para acceder a la pantalla principal de la aplicación

  @RF-001
  Escenario: Login exitoso con credenciales válidas
    Dado que la aplicación está abierta en la pantalla de login
    Cuando ingreso el usuario "demo.qa" y la clave "Passw0rd!"
    Y hago click en "Ingresar"
    Entonces veo la ventana principal de la aplicación

  @RF-002
  Escenario: Login rechazado con clave incorrecta
    Dado que la aplicación está abierta en la pantalla de login
    Cuando ingreso el usuario "demo.qa" y la clave "clave-incorrecta"
    Y hago click en "Ingresar"
    Entonces veo el mensaje de error "Usuario o contraseña incorrectos"

  @RF-003
  Escenario: Recordar usuario mantiene el campo completado al reabrir
    Dado que la aplicación está abierta en la pantalla de login
    Cuando ingreso el usuario "demo.qa" y la clave "Passw0rd!"
    Y marco la opción "Recordarme"
    Y hago click en "Ingresar"
    Y cierro y vuelvo a abrir la aplicación
    Entonces el campo usuario aparece precargado con "demo.qa"
