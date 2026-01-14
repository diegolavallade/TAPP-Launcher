#!/usr/bin/env python3
"""
tapp_pack.py — empaquetador mínimo para .tapp (TypeScript App)

Qué hace:
- (Opcional) corre instalación + build (Vite/React/TS típico)
- Genera tapp.json si no existe (o lo respeta si ya existe)
- Empaqueta dist/ + tapp.json en un ZIP con extensión .tapp

Requisitos:
- Python 3.9+
- (Opcional) Node.js + npm/pnpm/yarn si usas --build

Uso rápido:
  python tapp_pack.py C:\ruta\proyecto --build
  python tapp_pack.py . --out GraphWars.tapp --build
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


def die(msg: str, code: int = 1) -> None:
    print(f"[tapp_pack] ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def run(cmd: list[str], cwd: Path) -> None:
    print("[tapp_pack] $", " ".join(cmd))
    exe = cmd[0]
    if os.name == "nt" and shutil.which(exe) is None and shutil.which(exe + ".cmd") is not None:
        cmd = [exe + ".cmd", *cmd[1:]]
    p = subprocess.run(cmd, cwd=str(cwd), shell=False)

    if p.returncode != 0:
        die(f"Comando falló con código {p.returncode}: {' '.join(cmd)}")


def detect_package_manager(project: Path) -> str:
    # Preferir lockfiles
    if (project / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (project / "yarn.lock").exists():
        return "yarn"
    return "npm"


def ensure_build(project: Path, clean: bool) -> None:
    pm = detect_package_manager(project)

    if clean:
        dist = project / "dist"
        if dist.exists():
            print("[tapp_pack] limpiando dist/ ...")
            shutil.rmtree(dist, ignore_errors=True)

    if pm == "pnpm":
        if shutil.which("pnpm") is None:
            die("No encuentro 'pnpm' en PATH. Instálalo o usa npm/yarn.")
        # instalación
        if (project / "pnpm-lock.yaml").exists():
            run(["pnpm", "install", "--frozen-lockfile"], project)
        else:
            run(["pnpm", "install"], project)
        # build
        run(["pnpm", "run", "build"], project)

    elif pm == "yarn":
        if shutil.which("yarn") is None:
            die("No encuentro 'yarn' en PATH. Instálalo o usa npm/pnpm.")
        # Yarn v1/v3 varía; esto funciona en v1 y en muchos setups modernos.
        run(["yarn", "install"], project)
        run(["yarn", "build"], project)

    else:  # npm
        if shutil.which("npm") is None:
            die("No encuentro 'npm' en PATH. Instala Node.js.")
        if (project / "package-lock.json").exists():
            run(["npm", "ci"], project)
        else:
            run(["npm", "install"], project)
        run(["npm", "run", "build"], project)


def read_package_json(project: Path) -> dict:
    pj = project / "package.json"
    if not pj.exists():
        die("No veo package.json en el directorio del proyecto.")
    try:
        return json.loads(pj.read_text(encoding="utf-8"))
    except Exception as e:
        die(f"No pude leer/parsear package.json: {e}")


def load_or_generate_manifest(project: Path, args, pkg: dict) -> tuple[dict, Path]:
    """
    Si existe tapp.json en el proyecto, lo usa.
    Si no existe, genera uno (sin escribirlo al proyecto) y lo mete al .tapp.
    """
    existing = project / "tapp.json"
    if existing.exists() and not args.force_manifest:
        try:
            mf = json.loads(existing.read_text(encoding="utf-8"))
            return mf, existing
        except Exception as e:
            die(f"tapp.json existe pero no se puede parsear: {e}")

    name = args.name or str(pkg.get("name") or "TappApp")
    version = args.version or str(pkg.get("version") or "0.0.0")
    title = args.title or name

    mf = {
        "name": name,
        "version": version,
        "entry": args.entry or "dist/index.html",
        "window": {
            "title": title,
            "width": args.width,
            "height": args.height,
            "resizable": not args.fixed,
        },
        "debug": {
            "openDevTools": bool(args.devtools),
        },
    }

    # manifest temporal (no ensuciamos repo)
    temp_dir = project / ".tapp_tmp"
    temp_dir.mkdir(exist_ok=True)
    temp_manifest = temp_dir / "tapp.json"
    temp_manifest.write_text(json.dumps(mf, ensure_ascii=False, indent=2), encoding="utf-8")
    return mf, temp_manifest


def add_folder_to_zip(z: ZipFile, folder: Path, base: Path) -> None:
    folder = folder.resolve()
    if not folder.exists():
        die(f"No existe la carpeta: {folder}")
    for p in folder.rglob("*"):
        if p.is_file():
            arcname = p.relative_to(base).as_posix()
            z.write(p, arcname)


def add_path_to_zip(z: ZipFile, p: Path, base: Path) -> None:
    p = p.resolve()
    if p.is_dir():
        add_folder_to_zip(z, p, base)
    elif p.is_file():
        z.write(p, p.relative_to(base).as_posix())
    else:
        die(f"No existe: {p}")


def main() -> int:
    ap = argparse.ArgumentParser(prog="tapp_pack", add_help=True)
    ap.add_argument("project", help="Ruta al proyecto (carpeta con package.json)")
    ap.add_argument("--out", help="Salida .tapp (default: <name>.tapp junto al proyecto)")
    ap.add_argument("--build", action="store_true", help="Corre install + build antes de empaquetar")
    ap.add_argument("--clean", action="store_true", help="Borra dist/ antes del build")
    ap.add_argument("--include", action="append", default=[], help="Ruta extra a incluir (puede repetirse)")

    # manifest controls
    ap.add_argument("--force-manifest", action="store_true", help="Ignora tapp.json existente y genera uno nuevo")
    ap.add_argument("--entry", default=None, help="Entry (default: dist/index.html)")
    ap.add_argument("--name", default=None, help="Nombre (default: package.json name)")
    ap.add_argument("--version", default=None, help="Versión (default: package.json version)")
    ap.add_argument("--title", default=None, help="Título de ventana")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--fixed", action="store_true", help="Ventana no redimensionable")
    ap.add_argument("--devtools", action="store_true", help="Marca openDevTools=true en el manifest generado")

    args = ap.parse_args()

    project = Path(args.project).expanduser().resolve()
    if not project.exists():
        die("La ruta del proyecto no existe.")
    if not project.is_dir():
        die("project debe ser una carpeta.")

    pkg = read_package_json(project)

    if args.build:
        ensure_build(project, clean=args.clean)

    dist = project / "dist"
    if not dist.exists():
        die("No encuentro dist/. ¿Olvidaste correr el build? (usa --build)")

    manifest, manifest_path = load_or_generate_manifest(project, args, pkg)

    out_path = Path(args.out).expanduser().resolve() if args.out else None
    if out_path is None:
        base_name = str(manifest.get("name") or pkg.get("name") or "app")
        # nombre seguro
        safe = "".join(c for c in base_name if c.isalnum() or c in ("-", "_", ".")).strip("._-") or "app"
        out_path = (project / f"{safe}.tapp").resolve()
    else:
        if out_path.suffix.lower() != ".tapp":
            out_path = out_path.with_suffix(".tapp")

    out_path.parent.mkdir(parents=True, exist_ok=True)

    # crear zip
    print(f"[tapp_pack] creando {out_path} ...")
    with ZipFile(out_path, "w", compression=ZIP_DEFLATED) as z:
        # manifest al root del zip
        z.write(manifest_path, "tapp.json")

        # dist/ completo
        add_folder_to_zip(z, dist, project)

        # extras
        for inc in args.include:
            add_path_to_zip(z, (project / inc) if not Path(inc).is_absolute() else Path(inc), project)

    # cleanup temporal si lo generamos
    tmp_dir = project / ".tapp_tmp"
    if tmp_dir.exists():
        try:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass

    print("[tapp_pack] OK:", out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
