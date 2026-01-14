using System.IO;
using System.IO.Compression;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace TAPP_Launcher
{
    public static class TappLoader
    {
        public static string ExtractToCache(string tappPath)
        {
            if (!File.Exists(tappPath))
                throw new FileNotFoundException("No existe el archivo .tapp", tappPath);

            var fi = new FileInfo(tappPath);
            var key = $"{fi.FullName}|{fi.Length}|{fi.LastWriteTimeUtc.Ticks}";
            var hash = Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(key)));

            var outDir = Path.Combine(Path.GetTempPath(), "tapp-cache", hash);

            if (!Directory.Exists(outDir))
            {
                Directory.CreateDirectory(outDir);
                ZipFile.ExtractToDirectory(tappPath, outDir, overwriteFiles: true);
            }

            return outDir;
        }

        public static TappManifest LoadManifest(string rootDir)
        {
            var mfPath = Path.Combine(rootDir, "tapp.json");
            if (!File.Exists(mfPath))
                return new TappManifest(); // default

            var json = File.ReadAllText(mfPath, Encoding.UTF8);
            return JsonSerializer.Deserialize<TappManifest>(json,
                new JsonSerializerOptions { PropertyNameCaseInsensitive = true }
            ) ?? new TappManifest();
        }

        public static string ResolveEntry(string rootDir, TappManifest mf)
        {
            var entry = mf.entry;
            if (string.IsNullOrWhiteSpace(entry))
            {
                // default práctico para Vite
                var distIndex = Path.Combine(rootDir, "dist", "index.html");
                entry = File.Exists(distIndex) ? "dist/index.html" : "index.html";
            }

            // Validación mínima
            var full = Path.GetFullPath(Path.Combine(rootDir, entry));
            if (!full.StartsWith(Path.GetFullPath(rootDir), StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("entry apunta fuera del paquete.");

            if (!File.Exists(full))
                throw new FileNotFoundException($"No existe entry '{entry}' dentro del tapp.", full);

            return entry.Replace("\\", "/");
        }
    }
}
