using System;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Conditions;
using FlaUI.Core.Tools;

namespace MiApp.UiTests.Support
{
    /// <summary>
    /// Esperas explícitas sobre UIAutomation. PROHIBIDO usar Thread.Sleep en los tests —
    /// UIA es asincrónico (animaciones, binding WPF, carga de datos) y un sleep fijo
    /// produce tests lentos cuando sobra tiempo y flaky cuando falta.
    /// </summary>
    public static class UiWait
    {
        public static readonly TimeSpan DefaultTimeout = TimeSpan.FromSeconds(10);
        private static readonly TimeSpan PollInterval = TimeSpan.FromMilliseconds(200);

        /// <summary>Espera hasta que el elemento exista en el árbol UIA.</summary>
        public static AutomationElement WaitForElement(
            Func<AutomationElement?> find, TimeSpan? timeout = null, string? description = null)
        {
            var result = Retry.WhileNull(find, timeout ?? DefaultTimeout, PollInterval);
            return result.Result ?? throw new TimeoutException(
                $"Elemento no encontrado{(description is null ? "" : $" ({description})")} " +
                $"tras {(timeout ?? DefaultTimeout).TotalSeconds}s.");
        }

        /// <summary>
        /// Espera hasta que el elemento esté visible Y habilitado (clickeable).
        /// Genérico sobre el tipo concreto (TextBox, Button, ...) para no perder sus
        /// miembros específicos (.Text, .Invoke()) al devolverlo.
        /// </summary>
        public static T WaitUntilClickable<T>(T element, TimeSpan? timeout = null)
            where T : AutomationElement
        {
            var ok = Retry.WhileFalse(
                () => !element.IsOffscreen && element.IsEnabled,
                timeout ?? DefaultTimeout, PollInterval);

            if (!ok.Success)
                throw new TimeoutException(
                    $"Elemento '{element.AutomationId}' no quedó clickeable tras " +
                    $"{(timeout ?? DefaultTimeout).TotalSeconds}s (offscreen o deshabilitado).");

            return element;
        }

        /// <summary>Espera hasta que un elemento (ej. spinner) desaparezca del árbol.</summary>
        public static void WaitUntilGone(
            Func<AutomationElement?> find, TimeSpan? timeout = null)
        {
            var ok = Retry.WhileTrue(
                () => find() is not null,
                timeout ?? DefaultTimeout, PollInterval);

            if (!ok.Success)
                throw new TimeoutException(
                    $"Elemento no desapareció tras {(timeout ?? DefaultTimeout).TotalSeconds}s.");
        }

        /// <summary>Espera hasta que un diálogo modal con el título dado aparezca.</summary>
        public static Window WaitForModal(FlaUI.Core.AutomationElements.Window mainWindow, string title,
            TimeSpan? timeout = null)
        {
            var result = Retry.WhileNull(
                () => mainWindow.ModalWindows.Length > 0
                    ? Array.Find(mainWindow.ModalWindows, w => w.Title.Contains(title, StringComparison.OrdinalIgnoreCase))
                    : null,
                timeout ?? DefaultTimeout, PollInterval);

            return result.Result ?? throw new TimeoutException(
                $"Diálogo modal '{title}' no apareció tras {(timeout ?? DefaultTimeout).TotalSeconds}s.");
        }
    }
}
