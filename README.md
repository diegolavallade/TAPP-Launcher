# TAPP Launcher

`TAPP Launcher` es un host de escritorio para Windows (WPF + WebView2) que abre paquetes `.tapp`.

## ¿Qué es exactamente?

- **Sí es**: un contenedor para mostrar una app web empaquetada dentro de un `.tapp` (un `.zip` con otra extensión).
- **No es**: un servidor backend ni un runtime de Python/Node.
- **No reemplaza** tu `server.py`: si tu frontend depende de APIs CRUD, ese backend debe correr aparte (local o remoto).

En otras palabras: TAPP Launcher te da una ventana de escritorio para la UI web, pero no ejecuta automáticamente la parte de servidor.

## Cómo carga un `.tapp`

1. Extrae el `.tapp` al cache temporal.
2. Lee `tapp.json` (si existe).
3. Resuelve `entry` (por defecto intenta `dist/index.html` y luego `index.html`).
4. Mapea archivos locales a un host virtual `https://appassets/...` usando WebView2.
5. Navega al `entry`.

## Estructura recomendada del paquete

```text
mi-app.tapp
├─ tapp.json
└─ dist/
   ├─ index.html
   ├─ assets/...
   └─ ...
```

Ejemplo de `tapp.json`:

```json
{
  "name": "Mi Intranet",
  "version": "1.0.0",
  "entry": "dist/index.html",
  "window": {
    "title": "Mi Intranet",
    "width": 1280,
    "height": 720,
    "resizable": true
  },
  "debug": {
    "openDevTools": false
  }
}
```

## Sobre tu caso (intranet + `server.py` + JSON + CRUD)

Si tu página “no se ve bien” al abrir `index.html` directo, normalmente es porque:

- el build espera rutas/base URL específicas,
- y/o depende de llamadas HTTP a un backend.

Con TAPP Launcher:

- la parte estática (`dist`) sí puede abrir bien dentro de la ventana,
- pero las APIs (`server.py`) **deben estar levantadas** para que CRUD/DB funcionen.

Si metiste un HTML autocontenido en `dist` y funcionó, eso confirma que el launcher sí está cargando bien contenido estático.

## Desarrollo

1. Abre `TAPP Launcher.csproj` en Visual Studio.
2. Restaura paquetes NuGet si lo pide.
3. Compila y ejecuta.
4. Arrastra un archivo `.tapp` a la ventana.

## Scripts incluidos

- `tapp_pack.py`: helper para empaquetar contenido TAPP.
- `tapp_pack_win.py`: variante/helper de empaquetado para Windows.
