# Better Vanilla

> *Minecraft, pero se ve mejor y no te perdés.*

Modpack vanilla+ para **Minecraft 26.2** con **Fabric**: cero mods de contenido, cero
cambios de estructuras o de worldgen. Shaders, un resource pack, un mapa y un par de
mejoras de interfaz (HUD de armadura, ordenar inventario) — la lógica de juego sigue
siendo la vanilla de Mojang.

Este repo **no contiene los archivos** — guarda la lista con versión, URL y hash de cada uno
([`assets.json`](assets.json)) y un script que los descarga. Así el repo pesa kilobytes en vez
de ~35 MB, los diffs muestran exactamente qué cambió, y nadie redistribuye mods ajenos.

| | |
|---|---|
| **Minecraft** | 26.2 |
| **Mod loader** | Fabric (Loader 0.19.3) |
| **Mods** | 11 (infraestructura + interfaz: rendimiento, mapa, HUD, inventario) |
| **Resource packs** | 1 |
| **Shaders** | 2 (uno por sistema operativo) |
| **RAM recomendada** | 4 GB mínimo, 6 GB cómodo |
| **Peso en disco** | ~35 MB |

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

Mods de infraestructura y de interfaz — ninguno cambia gameplay, worldgen ni agrega
contenido:

| Mod | Qué hace |
|---|---|
| [Fabric API](https://modrinth.com/mod/fabric-api) | Librería base que necesitan casi todos los mods de Fabric. No agrega contenido por sí sola. |
| [Fabric Language Kotlin](https://modrinth.com/mod/fabric-language-kotlin) | Runtime de Kotlin para Fabric: lo necesita Inventory Profiles Next. No agrega nada por sí solo. |
| [Inventory Profiles Next](https://modrinth.com/mod/inventory-profiles-next) | Ordena inventario y cofres con un botón que aparece en la interfaz o con un atajo de teclado. También apila ítems iguales, tira todo y bloquea slots. |
| [Iris](https://modrinth.com/mod/iris) | Motor de shaders para Fabric: es lo que permite usar shaderpacks como BSL o Bliss. |
| [libIPN](https://modrinth.com/mod/libipn) | Librería que necesita Inventory Profiles Next. No agrega nada por sí sola. |
| [Pickup Notifications](https://modrinth.com/mod/pickup-notifications) | Muestra un aviso emergente cada vez que recogés un ítem o ganás experiencia. En servidores multijugador tiene que estar también del lado del server. |
| [Sodium](https://modrinth.com/mod/sodium) | Reescribe el renderizado del juego para subir los FPS. No cambia nada del gameplay. |
| [uku's Armor HUD](https://modrinth.com/mod/ukus-armor-hud) | Muestra las piezas de armadura y la herramienta en la mano en un rincón de la pantalla, con su durabilidad y un aviso cuando alguna está por romperse. No hace falta abrir el inventario. |
| [ukulib](https://modrinth.com/mod/ukulib) | Librería de configuración que necesita uku's Armor HUD. No agrega nada por sí sola. |
| [Xaero's Minimap](https://modrinth.com/mod/xaeros-minimap) | Minimapa en la esquina de la pantalla con waypoints, mobs y jugadores. |
| [Xaero's World Map](https://modrinth.com/mod/xaeros-world-map) | Mapa a pantalla completa de todo lo que fuiste explorando. Se integra con el minimapa. |

---

## Resource pack

| Resource pack | Qué hace |
|---|---|
| [Faithful 32x](https://modrinth.com/resourcepack/faithful-32x) | Las texturas vanilla al doble de resolución, respetando el estilo y el arte original. |

---

## Apagar un mod sin sacarlo del pack

Agregale `.disabled` al final del nombre del archivo:

```bash
# macOS / Linux
mv mods/xaerominimap-fabric-26.2-26.4.2.jar{,.disabled}

# Windows (PowerShell)
Rename-Item mods\xaerominimap-fabric-26.2-26.4.2.jar `
            mods\xaerominimap-fabric-26.2-26.4.2.jar.disabled
```

`sync.py` lo respeta: no te lo vuelve a bajar ni lo borra con `--prune`, y lo propaga
igual (renombrado, sin duplicar) cuando corrés `--install`. Para prenderlo de vuelta,
sacale el sufijo.

---

## Shaders

Van los dos, elegís según en qué sistema estés jugando:

| Shader | Plataforma | Qué es |
|---|---|---|
| [Bliss Shaders](https://modrinth.com/shader/bliss-shader) v2.1.2 | **Windows / Linux** | Edit de Chocapic13. Más bonito y más caro que BSL: mejor agua, volumétricos y cielo. No corre en macOS (usa compute shaders). |
| [BSL Shaders](https://modrinth.com/shader/bsl-shaders) v10.1.3 | **macOS (y cualquiera)** | El mejor equilibrio entre cómo se ve y cuánto cuesta, con un menú de configuración enorme. Corre en cualquier plataforma, incluido macOS. |

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
