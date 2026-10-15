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
