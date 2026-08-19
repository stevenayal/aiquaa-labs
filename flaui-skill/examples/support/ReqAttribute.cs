using NUnit.Framework;

namespace MiApp.UiTests.Support
{
    /// <summary>
    /// Vincula un test NUnit puro a un requerimiento funcional. Se traduce a
    /// &lt;property name="ReqId" value="RF-001"/&gt; en el TestResult.xml (NUnit3),
    /// que reporter/flaui_report.py lee para construir la matriz de trazabilidad.
    ///
    /// Uso:
    ///   [Test, Req("RF-001")]
    ///   public void Login_con_credenciales_validas() { ... }
    ///
    /// Para Reqnroll/Gherkin no se usa este atributo — se usa el tag @RF-001 en el
    /// .feature, que Reqnroll expone como Category y el reporter reconoce igual
    /// (regex ^RF-\d+$).
    /// </summary>
    public sealed class ReqAttribute : PropertyAttribute
    {
        public ReqAttribute(string reqId) : base("ReqId", reqId) { }
    }
}
