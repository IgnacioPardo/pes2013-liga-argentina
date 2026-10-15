# PES 2013 — Liga Argentina

Herramientas y documentación del mod para **PES 2013 PSP USA (ULUS10597)**, probado con el núcleo **PPSSPP de RetroArch**.

## Qué incluye el mod

- 24 clubes argentinos y 675 jugadores: veinte equipos en el lugar de Ligue 1, más Banfield, Olimpo, Instituto y Rosario Central.
- Nombres, escudos, formaciones y uniformes editables; correcciones de River, Argentina y Brasil.
- 25 cánticos argentinos: cinco para Boca, River, Racing, Independiente y San Lorenzo.
- Relatos de Mariano Closs: 3.326 eventos reasignados del banco donante a los eventos de PES 2013.
- Menús en español latinoamericano y configuración del relato independiente del idioma del texto.

El motor es PES 2013. Los planteles parten del **Clausura 2012** de Carlos Leonhart; no constituyen una actualización completa de los pases de 2013. Los uniformes editables no reproducen todos los patrocinadores de las camisetas oficiales.

## Empezar

Este repositorio contiene el código de conversión, las versiones de sus herramientas y las instrucciones de construcción. Los insumos del juego y de los mods donantes se aportan localmente.

1. Consultar los [insumos y la construcción](docs/BUILD.md).
2. Preparar las herramientas con `python3 tools/setup-dependencies.py`.
3. Convertir el archivo de opciones, construir los bancos de audio y generar una ISO aparte.
4. Seguir la [instalación en RetroArch](docs/INSTALL.md).

**Nombre del juego en el menú:** `PES 2013 - Liga Argentina`.

## Archivos necesarios

El código por sí solo no genera el juego: necesita estos insumos locales. Las rutas de la tabla son relativas a la raíz del repositorio, salvo la ISO de entrada y la carpeta del guardado original, que se pasan por argumento.

| Insumo | Archivo o carpeta esperada | Procedencia / requisitos |
| --- | --- | --- |
| Juego base | ISO indicada con `build-iso.py --source` | **PES 2013 PSP USA, ULUS10597**, versión En/Fr/Es/Pt. La imagen usada mide **1.675.264.000 bytes**. No sirve una ISO de PS2 o PC. |
| Guardado USA original | Carpeta `ULUS1059700008000/`, con `DATA.BIN`, `PARAM.SFO` e `ICON0.PNG` | Generado por el juego base; se pasa a `package-save.py --base-save`. Conservar la carpeta original. |
| Guardado base descifrado | `conversion/2013-decrypted.bin` | DATA.BIN del guardado USA, descifrado: **1.111.040 bytes**. |
| Clave del guardado USA | `conversion/2013.key` | Clave local de **16 bytes**, correspondiente a ese juego. La necesita el cifrador para generar el nuevo guardado. |
| Planteles y uniformes argentinos | `conversion/2012-decrypted.bin` | Archivo de opciones EUR **Clausura 2012 de Carlos Leonhart**, descifrado: **1.122.304 bytes**. [Publicación del autor](https://www.youtube.com/watch?v=cW4PuzhTcaQ). Para descifrarlo inicialmente hace falta su propia clave 2012. |
| Escudos | `conversion/boca.png` y `conversion/river.png` | PNG de los escudos con fondo transparente o claro, usados para generar los emblemas del guardado. |
| Ejecutable del juego base | `conversion/game-code/EBOOT.elf` | EBOOT.BIN extraído de la ISO USA y descifrado con pspdecrypt. |
| Tabla original de eventos | `conversion/game-code/over/0059.bin` | `realconditionS.ovl` extraído del `OVER.cpk` original; **106.496 bytes**. |
| Audio original de hinchadas | `audio-original/PSP_GAME/USRDIR/0SOUND.cpk` y `audio-original/files/0000.bin …` | Banco original de la ISO y sus **692 entradas** extraídas por ID. La entrada 0567 aporta la cabecera de audio compatible. |
| Plantilla de banco de comentarios | `commentary-original/PSP_GAME/USRDIR/MSOUND.cpk` | Extraído de la ISO USA original; se usa su estructura CPK. |
| Relatos de Closs | `commentary-closs/files/0000.bin …` | Entradas extraídas de `SSOUND.cpk` del donante PSP de **Lasso StaR**, basado en PES 2014. El audio ocupa los IDs **0–4917**. [Publicación del autor](https://lassostareditions.blogspot.com/2026/04/nuevo-efootball-2026-v3-para-ppsspppsp.html). |
| Tabla donante de eventos | `commentary-closs/over/0059.bin` | `realconditionS.ovl` del `OVER.cpk` del mismo donante de Closs; **106.496 bytes**. Debe corresponder al banco de audio anterior. |
| Cánticos argentinos | `chants-surling/Boca/`, `River/`, `Racing/`, `Independiente/` y `San-Lorenzo/` | **Cinco archivos `.adx` por club**, 25 en total, del paquete de Surling. [Publicación original](https://foro.pesretro.net/thread-5869.html). |

También hacen falta **FFmpeg**, **Python**, las dependencias de `requirements.txt`, y las cinco herramientas fijadas en `tools/dependencies.json`. Los comandos para obtenerlas, extraer los CPK, descifrar los guardados y construir el paquete están en [BUILD.md](docs/BUILD.md).

Los **resultados**, que se generan a partir de esos insumos, son `release/PES 2013 - Liga Argentina .iso` y la carpeta `release/PSP/SAVEDATA/ULUS1059700008000/`. Se necesitan ambos para instalar el mod con sus equipos y la selección de relatos.

## Código

| Archivo | Función |
| --- | --- |
| `conversion/convert.py` | Conversión de equipos, jugadores, escudos, formaciones y uniformes |
| `conversion/encode-chants.py` | Conversión de ADX a ATRAC3+ con encabezados compatibles con PSP |
| `conversion/repack-commentary.py` | Mapeo por eventos y reconstrucción del banco de Closs |
| `conversion/build-iso.py` | Integración en una copia de la ISO original |
| `conversion/package-save.py` | Cifrado del archivo de opciones en una carpeta nueva |
| `conversion/cpk_ids.py` | Lectura y extracción de archivos CPK indexados por ID |
| `conversion/national-kit-fix/apply.py` | Corrección puntual de Argentina y Brasil en un guardado existente |

Los scripts de comparación de audio permiten contrastar una grabación real del emulador con los clips de origen. No sustituyen las pruebas de juego.

## Estado verificado

Se llegó a partidos reales en RetroArch/PPSSPP de macOS. Se verificaron los cánticos y varios relatos durante el juego mediante comparación de audio, además de los uniformes titular y alternativo de Argentina y Brasil. El DualSense funcionó como jugador 1.

El paquete se transfirió a RetroArch de Apple TV. La ejecución en Apple TV de esta versión final no forma parte de la validación registrada. No se verificaron temporadas completas, todos los modos ni multijugador.

Más detalles: [arquitectura](docs/TECHNICAL.md), [validación](docs/VALIDATION.md) y [créditos](docs/CREDITS.md).

No se incluyen ISO/ROM, BIOS, archivos de opciones, claves, ejecutables del juego ni bancos de audio o texturas. Las herramientas externas se obtienen desde sus repositorios y conservan sus propias licencias.
