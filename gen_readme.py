#!/usr/bin/env python3
"""Genera el README.md del modpack desde assets.json + descripciones en español."""
import json, pathlib, urllib.parse

ROOT = pathlib.Path(__file__).parent
rows = json.loads((ROOT / "assets.json").read_text(encoding="utf-8"))

DEST = {"mod": "mods", "resourcepack": "resourcepacks", "shaderpack": "shaderpacks"}

# Descripciones en español. Clave = slug de Modrinth.
D = {
 "fabric-api": "Librería base que necesitan casi todos los mods de Fabric. No agrega contenido por sí sola.",
 "sodium": "Reescribe el renderizado del juego para subir los FPS. No cambia nada del gameplay.",
 "iris": "Motor de shaders para Fabric: es lo que permite usar shaderpacks como BSL o Bliss.",
 "xaeros-minimap": "Minimapa en la esquina de la pantalla con waypoints, mobs y jugadores.",
 "xaeros-world-map": "Mapa a pantalla completa de todo lo que fuiste explorando. Se integra con el minimapa.",
}

RP = {
 "faithful-32x": "Las texturas vanilla al doble de resolución, respetando el estilo y el arte original.",
}

SH = {
 "bsl-shaders": "El mejor equilibrio entre cómo se ve y cuánto cuesta, con un menú de configuración enorme. Corre en cualquier plataforma, incluido macOS.",
 "bliss-shader": "Edit de Chocapic13. Más bonito y más caro que BSL: mejor agua, volumétricos y cielo. No corre en macOS (usa compute shaders).",
}

mods = [r for r in rows if r["type"] == "mod"]
packs = [r for r in rows if r["type"] == "resourcepack"]
shaders = [r for r in rows if r["type"] == "shaderpack"]

for etiqueta, claves, desc in [("mods", {r["slug"] for r in mods}, D),
                                ("resource packs", {r["slug"] for r in packs}, RP),
                                ("shaders", {r["slug"] for r in shaders}, SH)]:
    assert not claves - set(desc), f"{etiqueta} sin descripción: {sorted(claves - set(desc))}"
    assert not set(desc) - claves, f"descripción sobrante en {etiqueta}: {sorted(set(desc) - claves)}"


def link(r, kind):
    return f'[{r["title"]}](https://modrinth.com/{kind}/{r["slug"]})'


def tabla_nucleo():
    out = ["| Mod | Qué hace |", "|---|---|"]
    for r in sorted(mods, key=lambda r: r["title"].lower()):
        out.append(f'| {link(r, "mod")} | {D[r["slug"]]} |')
    return "\n".join(out)


def tabla_rp():
    out = ["| Resource pack | Qué hace |", "|---|---|"]
    for r in sorted(packs, key=lambda r: r["title"].lower()):
        out.append(f'| {link(r, "resourcepack")} | {RP[r["slug"]]} |')
    return "\n".join(out)


def tabla_sh():
    out = ["| Shader | Plataforma | Qué es |", "|---|---|---|"]
    for r in sorted(shaders, key=lambda r: r["title"].lower()):
        out.append(f'| {link(r, "shader")} v{r["version_number"]} | **{r["plataforma"]}** | {SH[r["slug"]]} |')
    return "\n".join(out)


def peso_local():
    """Suma el tamaño real en disco de lo ya descargado. 0 si todavía no se corrió sync.py."""
    total = 0
    for r in rows:
        p = ROOT / DEST[r["type"]] / r["filename"]
        if p.exists():
            total += p.stat().st_size
    return total


peso = peso_local()
peso_txt = f"~{round(peso / 1e6)} MB" if peso else "se calcula al correr sync.py"

README = f"""# Better Vanilla

> *Minecraft, pero se ve mejor y no te perdés.*

Modpack vanilla+ para **Minecraft 26.2** con **Fabric**: cero mods de contenido, cero
cambios de estructuras o de worldgen. Solo shaders, un resource pack y un mapa —
la experiencia de juego es exactamente la vanilla de Mojang.

Este repo **no contiene los archivos** — guarda la lista con versión, URL y hash de cada uno
([`assets.json`](assets.json)) y un script que los descarga. Así el repo pesa kilobytes en vez
de {peso_txt}, los diffs muestran exactamente qué cambió, y nadie redistribuye mods ajenos.

| | |
|---|---|
| **Minecraft** | 26.2 |
| **Mod loader** | Fabric (Loader 0.19.3) |
| **Mods** | {len(mods)} (todos de infraestructura: loader, rendimiento, mapa) |
| **Resource packs** | {len(packs)} |
| **Shaders** | {len(shaders)} (uno por sistema operativo) |
| **RAM recomendada** | 4 GB mínimo, 6 GB cómodo |
| **Peso en disco** | {peso_txt} |

---

## Instalación

### 0. Instalar el perfil de Fabric

Una sola vez: instalá **Fabric Loader** para Minecraft **26.2** con el
[instalador oficial](https://fabricmc.net/use/installer/). Esto crea un perfil nuevo en el
launcher, separado de tus otros perfiles — no toca nada existente.

### 1. Descargar todo

```bash
git clone <URL-DE-ESTE-REPO>
cd better-vanilla
python3 sync.py          # en Windows: py sync.py
```

Todo librería estándar de Python 3, sin dependencias que instalar. Funciona igual en
macOS, Linux y Windows. Descarga todo en `./mods`, `./resourcepacks` y `./shaderpacks`,
verificando el SHA1 de cada archivo. Si ya los tenías, solo baja lo que cambió.

### 2. Copiar a tu instancia

**Launcher oficial de Mojang**

```bash
python3 sync.py --install                          # detecta .minecraft solo
```

**CurseForge App / Prism / MultiMC / Modrinth App**

```bash
python3 sync.py --install "/ruta/a/tu/instancia"
```

Copia `mods/`, `resourcepacks/` y `shaderpacks/` a la carpeta indicada. No borra nada
que no sea de este pack.

### 3. Activar resource pack y shader

Dentro del juego:
- Opciones → Resource Packs → mover **Faithful 32x** a la derecha.
- Opciones → Video Settings → Shader Packs → elegir **BSL** (mac) o **Bliss** (Windows/Linux).

---

## Núcleo

Mods de infraestructura — ninguno cambia gameplay ni agrega contenido:

{tabla_nucleo()}

---

## Resource pack

{tabla_rp()}

---

## Apagar un mod sin sacarlo del pack

Agregale `.disabled` al final del nombre del archivo:

```bash
# macOS / Linux
mv mods/xaerominimap-fabric-26.2-26.4.2.jar{{,.disabled}}

# Windows (PowerShell)
Rename-Item mods\\xaerominimap-fabric-26.2-26.4.2.jar `
            mods\\xaerominimap-fabric-26.2-26.4.2.jar.disabled
```

`sync.py` lo respeta: no te lo vuelve a bajar ni lo borra con `--prune`, y lo propaga
igual (renombrado, sin duplicar) cuando corrés `--install`. Para prenderlo de vuelta,
sacale el sufijo.

---

## Shaders

Van los dos, elegís según en qué sistema estés jugando:

{tabla_sh()}

Corren gracias a **Iris** (ya en la lista de mods), que además necesita **Sodium** para
funcionar. Sodium por sí solo sube los FPS aunque nunca actives un shader.

> ### ⚠️ Por qué hay uno para cada sistema
>
> Los shaders modernos usan **compute shaders**, que necesitan **OpenGL 4.3**. macOS
> tope en **4.1** y Apple ya no lo actualiza (dejó OpenGL por Metal), así que en Mac no
> arrancan — no importa qué GPU tengas. Es una limitación estructural de macOS, no de
> una versión puntual de un shader en particular.
>
> - **Bliss** usa compute shaders → Windows y Linux, donde se ve mejor.
> - **BSL** evita depender de ellos → anda en todos lados, incluido macOS.

---

## Actualizar

```bash
git pull
python3 sync.py --prune
```

`--prune` borra de `mods/`, `resourcepacks/` y `shaderpacks/` lo que ya no está en la
lista. Para verificar que no se corrompió nada sin descargar: `python3 sync.py --verify`.

Para actualizar un asset, editá su entrada en `assets.json` (`version_number`, `url`,
`sha1_remote`, `filename`) y commiteá. Después corré `python3 gen_readme.py` para que
este archivo siga al día.

---

## Desinstalar

```bash
python3 sync.py --uninstall
python3 sync.py --uninstall "/ruta/a/tu/instancia"    # CurseForge App/Prism/MultiMC/Modrinth App
```

Borra de `.minecraft` (auto-detectado igual que `--install`) únicamente los archivos
que `assets.json` reclama como propios — nada más. No borra el perfil de Fabric del
launcher ni tus mundos.

---

## Notas

- Si además tenés instalado otro modpack (por ejemplo `terra-incognita`) en el mismo
  launcher: el launcher de Mojang comparte las carpetas `mods/`, `resourcepacks/` y
  `shaderpacks/` entre todos los perfiles. Para alternar entre packs, desinstalá uno
  (`sync.py --uninstall` en su propio repo) antes de instalar el otro.
- En el resource pack mirá el `pack_format`: tiene que coincidir con Minecraft 26.2.
  Uno más nuevo o más viejo suele cargar igual, pero el juego avisa y puede faltar
  alguna textura.

## Licencia

Cada mod, shader y resource pack pertenece a su autor y conserva su propia licencia.
Este repo solo contiene la lista y los scripts.
"""

(ROOT / "README.md").write_text(README, encoding="utf-8")
print(f"README.md escrito: {len(mods)} mods + {len(packs)} resource pack + {len(shaders)} shaders, {peso_txt}")
