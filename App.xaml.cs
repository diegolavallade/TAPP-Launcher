using System.Configuration;
using System.Data;
using System.Windows;

namespace TAPP_Launcher
{
    /// <summary>
    /// Interaction logic for App.xaml
    /// </summary>

    public partial class App : Application
    {
        protected override async void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);

            var forceDevTools = e.Args.Any(a => a.Equals("--devtools", StringComparison.OrdinalIgnoreCase));
            var tappPath = e.Args.FirstOrDefault(a => a.EndsWith(".tapp", StringComparison.OrdinalIgnoreCase));

            var win = new MainWindow();
            win.Show();

            if (!string.IsNullOrWhiteSpace(tappPath))
                await win.OpenTappAsync(tappPath, forceDevTools);
        }
    }

}
