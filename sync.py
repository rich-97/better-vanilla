#!/usr/bin/env python3
"""Descarga/actualiza mods, resource pack y shaders del pack, verificando SHA1. Solo stdlib.

  python3 sync.py            descarga lo que falte o esté corrupto
  python3 sync.py --prune    además borra lo que ya no está en assets.json
  python3 sync.py --verify   solo re-verifica hashes, no descarga nada
  python3 sync.py --install [ruta]     además, copia todo a .minecraft (auto-detecta si falta ruta)
  python3 sync.py --uninstall [ruta]   borra de .minecraft solo lo que puso este pack
  python3 sync.py --test     autotest de instalar/desinstalar/sobrantes

ponytail: calcado de terra-incognita/sync.py, sin el chequeo --deps (era específico de
Forge/mods.toml, acá son 5 mods Fabric con versión ya fijada a mano, no hace falta).
"""
import hashlib, json, os, pathlib, platform, shutil, sys, tempfile, urllib.request

ROOT = pathlib.Path(__file__).parent
DEST = {"mod": "mods", "resourcepack": "resourcepacks", "shaderpack": "shaderpacks"}
UA = {"User-Agent": "better-vanilla-sync/1.0"}


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sobrantes(carpetas, conocidos):
    """Archivos en `carpetas` que assets.json no reclama."""
    return [p for d in carpetas for p in d.iterdir()
            if p.is_file() and p.name != ".DS_Store"
            and p.name not in conocidos
            and p.name.removesuffix(".disabled") not in conocidos]


def minecraft_dir(sistema=None):
    """Carpeta .minecraft estándar según el SO. CurseForge App/Prism/MultiMC/
    Modrinth App usan carpetas por instancia: para esos, pasar la ruta a mano
    con --install <ruta>."""
    sistema = sistema or platform.system()
    home = pathlib.Path.home()
    if sistema == "Darwin":
        return home / "Library" / "Application Support" / "minecraft"
    if sistema == "Windows":
        return pathlib.Path(os.environ.get("APPDATA", str(home))) / ".minecraft"
    return home / ".minecraft"          # Linux y cualquier otro *nix


def instalar(destino, origen_root=ROOT):
    """Copia mods/resourcepacks/shaderpacks ya sincronizados a una carpeta
    .minecraft real. No borra nada del destino que no sea de este pack: lo que
    el usuario haya agregado a mano en su carpeta real queda intacto. Si un
    archivo pasó a .disabled (o volvió) en el repo, lo renombra del lado del
    destino en vez de duplicarlo."""
    if destino.resolve() == origen_root.resolve():
        print("  el destino es este mismo repo, no tiene sentido")
        return 1
    if not destino.is_dir():
        print(f"  no existe {destino} -- pasá la ruta correcta con --install <ruta> "
              f"(CurseForge App/Prism/MultiMC/Modrinth App usan carpetas por instancia)")
        return 1
    copiados = renombrados = al_dia = 0
    for carpeta in DEST.values():
        origen = origen_root / carpeta
        if not origen.is_dir():
            continue
        objetivo = destino / carpeta
        objetivo.mkdir(exist_ok=True)
        for src in sorted(origen.iterdir()):
            if not src.is_file() or src.name == ".DS_Store":
                continue
            base = src.name.removesuffix(".disabled")
            apagado = src.name != base
            dst = objetivo / src.name
            opuesto = objetivo / (base if apagado else base + ".disabled")
            if opuesto.exists() and not dst.exists():
                print(f"  renombrando (.disabled)  {opuesto.name} -> {dst.name}")
                opuesto.rename(dst)
                renombrados += 1
            if dst.exists() and sha1(dst) == sha1(src):
                al_dia += 1
                continue
            print(f"  copiando  {carpeta}/{src.name}")
            shutil.copy2(src, dst)
            copiados += 1
    print(f"\n{copiados} copiados / {renombrados} renombrados (.disabled) / "
          f"{al_dia} ya al día -> {destino}")
    return 0


def desinstalar(destino, rows=None):
    """Borra de una carpeta .minecraft real solo lo que este pack reclama en
    assets.json (activos o .disabled). No toca nada más: ni otros mods que el
    usuario haya puesto a mano, ni mundos, ni configs."""
    if not destino.is_dir():
        print(f"  no existe {destino}")
        return 1
    if rows is None:
        rows = json.loads((ROOT / "assets.json").read_text(encoding="utf-8"))
    conocidos = {r["filename"] for r in rows}
    borrados = 0
    for carpeta in DEST.values():
        objetivo = destino / carpeta
        if not objetivo.is_dir():
            continue
        for nombre in conocidos:
            for candidato in (objetivo / nombre, objetivo / (nombre + ".disabled")):
                if candidato.exists():
                    print(f"  borrando  {carpeta}/{candidato.name}")
                    candidato.unlink()
                    borrados += 1
    print(f"\n{borrados} archivos borrados de {destino}")
    return 0


def autotest():
    home = pathlib.Path.home()
    assert minecraft_dir("Darwin") == home / "Library" / "Application Support" / "minecraft"
    assert minecraft_dir("Linux") == home / ".minecraft"
    assert minecraft_dir("Windows").name == ".minecraft"
    print("  minecraft_dir(): 3 casos OK")

    with tempfile.TemporaryDirectory() as t:
        t = pathlib.Path(t)
        origen, destino = t / "repo", t / "minecraft"
        (origen / "mods").mkdir(parents=True)
        destino.mkdir()
        jar = origen / "mods" / "Foo.jar"
        jar.write_bytes(b"contenido")

        assert instalar(t / "no-existe", origen_root=origen) == 1
        assert instalar(destino, origen_root=origen) == 0
        assert (destino / "mods" / "Foo.jar").read_bytes() == b"contenido"

        jar.rename(origen / "mods" / "Foo.jar.disabled")
        instalar(destino, origen_root=origen)
        assert (destino / "mods" / "Foo.jar.disabled").exists()
        assert not (destino / "mods" / "Foo.jar").exists()

        (origen / "mods" / "Foo.jar.disabled").rename(origen / "mods" / "Foo.jar")
        instalar(destino, origen_root=origen)
        assert (destino / "mods" / "Foo.jar").exists()
        assert not (destino / "mods" / "Foo.jar.disabled").exists()
    print("  instalar(): copiar + toggle .disabled sin duplicar OK")

    with tempfile.TemporaryDirectory() as t:
        carpeta = pathlib.Path(t)
        for n in ("Bajado.jar", "Huerfano.jar"):
            (carpeta / n).write_bytes(b"x")
        resultado = {p.name for p in sobrantes([carpeta], {"Bajado.jar"})}
        assert resultado == {"Huerfano.jar"}, resultado
    print("  sobrantes(): detecta archivos no reclamados OK")

    with tempfile.TemporaryDirectory() as t:
        destino = pathlib.Path(t)
        (destino / "mods").mkdir()
        (destino / "mods" / "DelPack.jar").write_bytes(b"x")
        (destino / "mods" / "DeOtroMod.jar").write_bytes(b"x")     # no es de este pack
        rows_falsas = [{"filename": "DelPack.jar"}]
        assert desinstalar(destino, rows=rows_falsas) == 0
        assert not (destino / "mods" / "DelPack.jar").exists()
        assert (destino / "mods" / "DeOtroMod.jar").exists()
    print("  desinstalar(): borra lo del pack, no toca lo demás OK")
    return 0


def main(argv):
    if "--test" in argv:
        return autotest()
    if "--uninstall" in argv:
        i = argv.index("--uninstall")
        ruta = argv[i + 1] if i + 1 < len(argv) and not argv[i + 1].startswith("--") else None
        destino = pathlib.Path(ruta).expanduser() if ruta else minecraft_dir()
        return desinstalar(destino)
    prune, verify = "--prune" in argv, "--verify" in argv
    rows = json.loads((ROOT / "assets.json").read_text(encoding="utf-8"))
    wanted = {r["filename"]: r for r in rows}
    conocidos = set(wanted)
    for d in DEST.values():
        (ROOT / d).mkdir(exist_ok=True)

    ok = bad = new = off = 0
    for name, r in sorted(wanted.items()):
        dest = ROOT / DEST[r["type"]] / name
        if dest.with_name(name + ".disabled").exists():
            off += 1
            continue
        if dest.exists() and sha1(dest) == r["sha1_remote"]:
            ok += 1
            continue
        if verify:
            print(f"  FALTA/CORRUPTO  {name}")
            bad += 1
            continue
        print(f"  bajando  {name}")
        req = urllib.request.Request(r["url"], headers=UA)
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = resp.read()
        got = hashlib.sha1(data).hexdigest()
        if got != r["sha1_remote"]:
            print(f"  !! hash no coincide en {name} ({got}) - no se guarda")
            bad += 1
            continue
        dest.write_bytes(data)
        new += 1

    strays = sobrantes([ROOT / d for d in DEST.values()], conocidos)
    for p in strays:
        if prune:
            print(f"  borrando sobrante  {p.name}")
            p.unlink()
        else:
            print(f"  sobrante (usa --prune para borrar)  {p.name}")

    print(f"\n{ok} ya estaban / {new} descargados / {bad} con problemas / "
          f"{len(strays)} sobrantes" + (f" / {off} apagados (.disabled)" if off else ""))

    codigo = 1 if bad else 0
    if "--install" in argv:
        i = argv.index("--install")
        ruta = argv[i + 1] if i + 1 < len(argv) and not argv[i + 1].startswith("--") else None
        destino = pathlib.Path(ruta).expanduser() if ruta else minecraft_dir()
        print()
        codigo = instalar(destino) or codigo
    return codigo


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
