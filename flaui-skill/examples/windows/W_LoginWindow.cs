using FlaUI.Core.AutomationElements;
using FlaUI.Core.Definitions;
using MiApp.UiTests.Support;

namespace MiApp.UiTests.Windows
{
    /// <summary>
    /// Window Object para la pantalla de login — espejo desktop del Page Object
    /// de playwright-skill. Toda la interacción con controles vive acá; los steps
    /// y los tests NUnit solo orquestan y assertan.
    ///
    /// AutomationId de cada campo confirmado con:
    ///   python analyzer/ui_inventory.py --src ./src/MiApp --format json
    /// NUNCA se inventan índices ni posiciones.
    /// </summary>
    public sealed class W_LoginWindow
    {
        private readonly Window _window;

        public W_LoginWindow(Window window) => _window = window;

        private TextBox TxtUsuario =>
            _window.FindFirstDescendant(cf => cf.ByAutomationId("txtUsuario")).AsTextBox();

        private TextBox TxtClave =>
            _window.FindFirstDescendant(cf => cf.ByAutomationId("txtClave")).AsTextBox();

        private Button BtnIngresar =>
            _window.FindFirstDescendant(cf => cf.ByAutomationId("btnIngresar")).AsButton();

        private CheckBox ChkRecordarme =>
            _window.FindFirstDescendant(cf => cf.ByAutomationId("chkRecordarme")).AsCheckBox();

        // lblError sale como "stable: false" en el inventario (WinForms sin
        // AccessibleName explícito) — se documenta la advertencia y se usa
        // ByControlType acotado como fallback en vez de inventar un AutomationId.
        private Label? MensajeErrorElement =>
            _window.FindFirstDescendant(cf =>
                cf.ByControlType(ControlType.Text).And(cf.ByAutomationId("lblError")))?.AsLabel();

        public void Login(string usuario, string clave)
        {
            UiWait.WaitUntilClickable(TxtUsuario).Text = usuario;
            TxtClave.Text = clave;
            UiWait.WaitUntilClickable(BtnIngresar).Invoke();
        }

        public void MarcarRecordarme(bool marcado) => ChkRecordarme.IsChecked = marcado;

        public string? MensajeError => MensajeErrorElement?.Text;

        public bool BotonIngresarHabilitado => BtnIngresar.IsEnabled;
    }
}
