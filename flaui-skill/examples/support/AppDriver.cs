using System;
using System.Diagnostics;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.UIA3;

namespace MiApp.UiTests.Support
{
    /// <summary>
    /// Ciclo de vida de la aplicación bajo prueba. Lanza o adjunta el proceso,
    /// expone la ventana principal vía UIA3 y libera todo al terminar.
    /// La ruta del ejecutable y el modo (Launch/Attach) vienen de configuración —
    /// nunca hardcodeados en el test.
    /// </summary>
    public sealed class AppDriver : IDisposable
    {
        public Application App { get; }
        public UIA3Automation Automation { get; }
        public Window MainWindow { get; }

        private AppDriver(Application app, UIA3Automation automation, Window mainWindow)
        {
            App = app;
            Automation = automation;
            MainWindow = mainWindow;
        }

        public static AppDriver Launch(string exePath, string? arguments = null)
        {
            if (string.IsNullOrWhiteSpace(exePath))
                throw new InvalidOperationException(
                    "APP_EXE_PATH no configurado. Definir en appsettings.uitests.json o variable de entorno.");

            var app = arguments is null
                ? Application.Launch(exePath)
                : Application.Launch(new ProcessStartInfo(exePath, arguments));

            var automation = new UIA3Automation();

            // Retry: la ventana principal puede tardar en aparecer (splash screen, carga inicial).
            var mainWindow = FlaUI.Core.Tools.Retry.WhileNull(
                () => app.GetMainWindow(automation),
                timeout: TimeSpan.FromSeconds(15),
                interval: TimeSpan.FromMilliseconds(250)
            ).Result ?? throw new TimeoutException(
                $"La ventana principal de '{exePath}' no apareció en 15s.");

            return new AppDriver(app, automation, mainWindow);
        }

        /// <summary>Adjuntar a un proceso ya corriendo (útil en debug local o smoke previo a suite).</summary>
        public static AppDriver Attach(int processId)
        {
            var app = Application.Attach(processId);
            var automation = new UIA3Automation();
            var mainWindow = app.GetMainWindow(automation)
                ?? throw new InvalidOperationException($"No se encontró ventana principal para PID {processId}.");
            return new AppDriver(app, automation, mainWindow);
        }

        public void Dispose()
        {
            try
            {
                if (!App.HasExited)
                    App.Close();
            }
            finally
            {
                Automation.Dispose();
                App.Dispose();
            }
        }
    }
}
