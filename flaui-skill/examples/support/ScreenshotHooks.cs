using System;
using System.IO;
using FlaUI.Core.Capturing;
using NUnit.Framework;
using NUnit.Framework.Interfaces;
using Reqnroll;

namespace MiApp.UiTests.Support
{
    /// <summary>
    /// Captura de pantalla automática en cada fallo. El archivo se adjunta al
    /// TestContext (NUnit lo escribe como &lt;attachment&gt; en el TestResult.xml),
    /// y reporter/flaui_report.py lo embebe en el PDF junto al mensaje de error.
    /// Cubre los dos runners: hooks de Reqnroll (BDD) y TearDown de NUnit puro.
    /// </summary>
    public static class ScreenshotHooks
    {
        private static readonly string ScreenshotDir =
            Path.Combine(TestContext.CurrentContext.WorkDirectory, "screenshots");

        public static void CaptureOnFailure(string testName)
        {
            Directory.CreateDirectory(ScreenshotDir);
            var fileName = $"{Sanitize(testName)}_{DateTime.Now:yyyyMMdd_HHmmss}.png";
            var filePath = Path.Combine(ScreenshotDir, fileName);

            Capture.Screen().ToFile(filePath);
            TestContext.AddTestAttachment(filePath, $"Captura al fallar: {testName}");
        }

        private static string Sanitize(string name)
        {
            foreach (var c in Path.GetInvalidFileNameChars())
                name = name.Replace(c, '_');
            return name;
        }
    }

    /// <summary>Hooks Reqnroll — se ejecutan alrededor de cada escenario BDD.</summary>
    [Binding]
    public sealed class ReqnrollScreenshotHooks
    {
        private readonly ScenarioContext _scenarioContext;

        public ReqnrollScreenshotHooks(ScenarioContext scenarioContext)
        {
            _scenarioContext = scenarioContext;
        }

        [AfterScenario]
        public void AfterScenario()
        {
            if (_scenarioContext.TestError is not null)
            {
                ScreenshotHooks.CaptureOnFailure(_scenarioContext.ScenarioInfo.Title);
            }
        }
    }

    /// <summary>
    /// Base opcional para tests NUnit puros: heredar de esta clase o replicar el
    /// [TearDown] en la propia clase de test.
    /// </summary>
    public abstract class NUnitScreenshotBase
    {
        [TearDown]
        public void CaptureScreenshotOnFailure()
        {
            if (TestContext.CurrentContext.Result.Outcome.Status == TestStatus.Failed)
            {
                ScreenshotHooks.CaptureOnFailure(TestContext.CurrentContext.Test.Name);
            }
        }
    }
}
