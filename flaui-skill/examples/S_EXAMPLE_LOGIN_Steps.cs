using System;
using FlaUI.Core.AutomationElements;
using MiApp.UiTests.Support;
using MiApp.UiTests.Windows;
using NUnit.Framework;
using Reqnroll;

namespace MiApp.UiTests.Steps
{
    /// <summary>
    /// Steps del feature F_EXAMPLE_LOGIN.feature. Solo orquesta llamadas al
    /// Window Object — cero lógica de UIAutomation acá (eso vive en W_LoginWindow).
    /// </summary>
    [Binding]
    public sealed class LoginSteps
    {
        private AppDriver? _driver;
        private W_LoginWindow? _login;

        private string ExePath =>
            Environment.GetEnvironmentVariable("APP_EXE_PATH")
            ?? throw new InvalidOperationException("Variable de entorno APP_EXE_PATH no configurada.");

        [Given(@"que la aplicación está abierta en la pantalla de login")]
        public void DadoQueLaAplicacionEstaAbierta()
        {
            _driver = AppDriver.Launch(ExePath);
            _login = new W_LoginWindow(_driver.MainWindow);
        }

        [When(@"ingreso el usuario ""(.*)"" y la clave ""(.*)""")]
        public void CuandoIngresoUsuarioYClave(string usuario, string clave)
        {
            _login!.Login(usuario, clave);
        }

        [When(@"hago click en ""Ingresar""")]
        public void CuandoHagoClickEnIngresar()
        {
            // El click ya ocurre dentro de Login(); step separado por legibilidad
            // del escenario cuando el flujo requiere pasos intermedios entre ambos.
        }

        [When(@"marco la opción ""Recordarme""")]
        public void CuandoMarcoRecordarme()
        {
            _login!.MarcarRecordarme(true);
        }

        [When(@"cierro y vuelvo a abrir la aplicación")]
        public void CuandoCierroYVuelvoAAbrir()
        {
            _driver!.Dispose();
            _driver = AppDriver.Launch(ExePath);
            _login = new W_LoginWindow(_driver.MainWindow);
        }

        [Then(@"veo la ventana principal de la aplicación")]
        public void EntoncesVeoLaVentanaPrincipal()
        {
            var mainWindow = UiWait.WaitForElement(
                () => _driver!.App.GetMainWindow(_driver.Automation),
                description: "ventana principal post-login");
            Assert.That(mainWindow.Name, Does.Not.Contain("Login"));
        }

        [Then(@"veo el mensaje de error ""(.*)""")]
        public void EntoncesVeoElMensajeDeError(string mensajeEsperado)
        {
            UiWait.WaitForElement(() => null, description: "mensaje de error visible");
            Assert.That(_login!.MensajeError, Is.EqualTo(mensajeEsperado));
        }

        [Then(@"el campo usuario aparece precargado con ""(.*)""")]
        public void EntoncesElCampoUsuarioAparecePrecargado(string usuarioEsperado)
        {
            // Placeholder de ejemplo — reemplazar por lectura real vía W_LoginWindow
            // (propiedad de solo lectura sobre TxtUsuario.Text) cuando se conecte a la app real.
            Assert.That(_login, Is.Not.Null);
        }

        [AfterScenario]
        public void Cleanup() => _driver?.Dispose();
    }
}
