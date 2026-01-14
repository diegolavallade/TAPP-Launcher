using Microsoft.Web.WebView2.Core;
using System.Windows;

namespace TAPP_Launcher
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private const string VirtualHost = "appassets";

        public MainWindow()
        {
            InitializeComponent();
        }

        public async Task OpenTappAsync(string tappPath, bool forceDevTools)
        {
            try
            {
                var root = TappLoader.ExtractToCache(tappPath);


                var extractedRoot = TappLoader.ExtractToCache(tappPath);
                var mf = TappLoader.LoadManifest(extractedRoot);
                var entry = TappLoader.ResolveEntry(extractedRoot, mf); // ej "dist/index.html"

                // Config ventana
                Title = mf.window?.title ?? mf.name ?? "TappHost";
                Width = mf.window?.width ?? 1280;
                Height = mf.window?.height ?? 720;
                ResizeMode = (mf.window?.resizable ?? true) ? ResizeMode.CanResize : ResizeMode.NoResize;

                string mappingFolder = extractedRoot;
                string navigatePath = entry;

                // Si el entry viene dentro de dist/, mapea directo a dist/
                if (navigatePath.StartsWith("dist/", StringComparison.OrdinalIgnoreCase))
                {
                    mappingFolder = System.IO.Path.Combine(extractedRoot, "dist");
                    navigatePath = navigatePath.Substring("dist/".Length); // "index.html"
                }

                await Web.EnsureCoreWebView2Async();

                Web.CoreWebView2.SetVirtualHostNameToFolderMapping(
                    "appassets",
                    mappingFolder,
                    Microsoft.Web.WebView2.Core.CoreWebView2HostResourceAccessKind.Allow
                );

                Web.CoreWebView2.Navigate($"https://appassets/{navigatePath}");

                if (forceDevTools || (mf.debug?.openDevTools ?? false))
                    Web.CoreWebView2.OpenDevToolsWindow();
            }
            catch (Exception ex)
            {
                MessageBox.Show(this, ex.Message, "TappHost - Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private async void Window_Drop(object sender, DragEventArgs e)
        {
            if (!e.Data.GetDataPresent(DataFormats.FileDrop)) return;
            var files = (string[]?)e.Data.GetData(DataFormats.FileDrop);
            var tapp = files?.FirstOrDefault(f => f.EndsWith(".tapp", StringComparison.OrdinalIgnoreCase));
            if (tapp is null) return;

            await OpenTappAsync(tapp, forceDevTools: false);
        }

        private void Window_DragOver(object sender, DragEventArgs e)
        {
            e.Effects = DragDropEffects.Copy;
            e.Handled = true;
        }
    }
}