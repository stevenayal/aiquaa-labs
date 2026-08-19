namespace MiApp.UI
{
    partial class LoginForm
    {
        private System.ComponentModel.IContainer components = null;

        private System.Windows.Forms.TextBox txtUsuario;
        private System.Windows.Forms.TextBox txtClave;
        private System.Windows.Forms.Button btnIngresar;
        private System.Windows.Forms.Label lblError;
        private System.Windows.Forms.CheckBox chkRecordarme;
        private System.Windows.Forms.Panel panelLogin;

        private void InitializeComponent()
        {
            this.txtUsuario = new System.Windows.Forms.TextBox();
            this.txtClave = new System.Windows.Forms.TextBox();
            this.btnIngresar = new System.Windows.Forms.Button();
            this.lblError = new System.Windows.Forms.Label();
            this.chkRecordarme = new System.Windows.Forms.CheckBox();
            this.panelLogin = new System.Windows.Forms.Panel();

            // txtUsuario
            this.txtUsuario.Name = "txtUsuario";
            this.txtUsuario.Location = new System.Drawing.Point(80, 40);

            // txtClave
            this.txtClave.Name = "txtClave";
            this.txtClave.Location = new System.Drawing.Point(80, 80);

            // btnIngresar
            this.btnIngresar.Name = "btnIngresar";
            this.btnIngresar.Text = "Ingresar";
            this.btnIngresar.AccessibleName = "btnIngresar";
            this.btnIngresar.Location = new System.Drawing.Point(80, 120);

            // lblError — sin Name ni AccessibleName explícitos: control inestable a propósito
            this.lblError.Text = "";
            this.lblError.Location = new System.Drawing.Point(80, 150);

            // chkRecordarme
            this.chkRecordarme.Name = "chkRecordarme";
            this.chkRecordarme.Text = "Recordarme";

            // panelLogin
            this.panelLogin.Name = "panelLogin";
        }
    }
}
