using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace TAPP_Launcher
{
    public sealed class TappManifest
    {
        public string? name { get; set; }
        public string? version { get; set; }
        public string? entry { get; set; } // ej: "dist/index.html"
        public WindowCfg? window { get; set; }
        public DebugCfg? debug { get; set; }

        public sealed class WindowCfg
        {
            public string? title { get; set; }
            public int width { get; set; } = 1280;
            public int height { get; set; } = 720;
            public bool resizable { get; set; } = true;
        }

        public sealed class DebugCfg
        {
            public bool openDevTools { get; set; } = false;
        }
    }

}
