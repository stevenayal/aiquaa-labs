using MiApp.UiTests.Support;
using MiApp.UiTests.Windows;
using NUnit.Framework;

namespace MiApp.UiTests.Tests
{
    /// <summary>
    /// Tests NUnit puros — para casos técnicos/regresión y validaciones data-driven
    /// que no aportan valor de negocio como escenario Gherkin (ver F_EXAMPLE_LOGIN.feature
    /// para el flujo BDD equivalente).
    /// </summary>
    [TestFixture]
    public sealed class LoginTests : NUnitScreenshotBase
    {
        private AppDriver _driver = null!;
        private W_LoginWindow _login = null!;

        private static string ExePath =>
            System.Environment.GetEnvironmentVariable("APP_EXE_PATH")
            ?? throw new System.InvalidOperationException("APP_EXE_PATH no configurada.");

        [SetUp]
        public void SetUp()
        {
            _driver = AppDriver.Launch(ExePath);
            _login = new W_LoginWindow(_driver.MainWindow);
        }

        [TearDown]
        public new void CaptureScreenshotOnFailure()
        {
            base.CaptureScreenshotOnFailure();
            _driver.Dispose();
        }

        [Test, Req("RF-001")]
        public void Login_con_credenciales_validas()
        {
            _login.Login("demo.qa", "Passw0rd!");
            Assert.That(_login.MensajeError, Is.Null.Or.Empty);
        }

        [Test, Req("RF-002")]
        [TestCase("", "Passw0rd!", TestName = "Login_boton_deshabilitado_con_usuario_vacio")]
        [TestCase("demo.qa", "", TestName = "Login_boton_deshabilitado_con_clave_vacia")]
        public void Login_boton_deshabilitado_con_campos_vacios(string usuario, string clave)
        {
            _login.Login(usuario, clave);
            Assert.That(_login.BotonIngresarHabilitado, Is.False);
        }

        [Test]
        // Smoke sin [Req] a propósito — no mapea a un RF puntual, valida arranque general.
        // Aparece en el PDF bajo "SIN REQUERIMIENTO", no rompe la matriz de trazabilidad.
        public void Smoke_la_app_levanta_y_muestra_la_ventana_de_login()
        {
            Assert.That(_driver.MainWindow, Is.Not.Null);
        }
    }
}
