# Instalación en RetroArch / PPSSPP

Usar el núcleo PPSSPP con la ISO y el guardado generados para ULUS10597.

1. Cerrar el juego y respaldar su guardado actual.
2. Copiar `PES 2013 - Liga Argentina .iso` al directorio de juegos.
3. Copiar la carpeta `ULUS1059700008000` completa dentro de `PPSSPP/PSP/SAVEDATA/` bajo el directorio de guardados de RetroArch.
4. Abrir la ISO desde cero. Un estado rápido anterior restaura datos anteriores al mod.
5. Buscar los veinte clubes principales en **Partido → Amistoso → Liga Argentina**. Los cuatro adicionales están en otros clubes.

En el Apple TV usado para la instalación, las rutas relativas al servidor web fueron:

```text
downloads/PSP/PES 2013 - Liga Argentina .iso
saves/PPSSPP/PSP/SAVEDATA/ULUS1059700008000/DATA.BIN
saves/PPSSPP/PSP/SAVEDATA/ULUS1059700008000/PARAM.SFO
saves/PPSSPP/PSP/SAVEDATA/ULUS1059700008000/ICON0.PNG
```

La ubicación puede cambiar según el directorio de guardados y la opción de ordenarlos por núcleo. No copiar otra carpeta `PSP` adicional dentro de `SAVEDATA`.

## Relatos

El archivo de opciones generado selecciona el banco **español de España**, que el mod reemplaza por Closs. Los menús permanecen en **español latinoamericano**. Elegir español latinoamericano como *idioma de comentarios* vuelve al banco original de Martinoli/García.

## Miniaturas

El nombre visible recomendado es **PES 2013 - Liga Argentina**. Para una lista llamada `Sony - PlayStation Portable.lpl`, las imágenes locales se guardan como:

```text
thumbnails/Sony - PlayStation Portable/Named_Boxarts/PES 2013 - Liga Argentina.png
thumbnails/Sony - PlayStation Portable/Named_Snaps/PES 2013 - Liga Argentina.png
```

La etiqueta `label` de la entrada debe coincidir con ese nombre. Consultar la [documentación de listas y miniaturas de RetroArch](https://docs.libretro.com/guides/roms-playlists-thumbnails/). Las carátulas instaladas localmente no forman parte de este repositorio.
