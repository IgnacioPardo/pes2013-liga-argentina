# Construcción

## Alcance

Las instrucciones documentan el flujo usado para el paquete probado. La preparación de los insumos es manual; no hay un descargador de juegos ni una instalación automática en dispositivos. Ejecutar los comandos desde la raíz del repositorio.

Entorno comprobado: macOS Apple Silicon, Python 3.9, FFmpeg, CMake, un compilador C/C++ y libsndfile. Las versiones de Python están en `requirements.txt`; los commits externos, en `tools/dependencies.json`.

## Herramientas

```sh
python3 -m venv tools/venv
tools/venv/bin/python -m pip install -r requirements.txt
python3 tools/setup-dependencies.py
cmake -S tools/atracdenc -B tools/atracdenc/build -DCMAKE_BUILD_TYPE=Release
cmake --build tools/atracdenc/build --target atracdenc -j 4
make -C tools/pspdecrypt
```

El parche CMake incluido limita atracdenc a arm64 en macOS, como en el entorno probado. Para compilar el cifrador de guardados con su backend PPSSPP:

```sh
cc -O2 tools/psp-savedata-endecrypter/endecrypter_ppsspp.cpp \
  tools/psp-savedata-endecrypter/libkirk/*.c -lstdc++ \
  -o tools/psp-savedata-endecrypter/endecrypter
```

FFmpeg debe estar disponible en `PATH`. Python necesita Tkinter para importar las definiciones del editor, aunque la conversión no abre su interfaz gráfica. Las licencias de cada herramienta se detallan en [CREDITS.md](CREDITS.md).

## Insumos locales

Obtener los insumos de tus copias del juego y de los trabajos acreditados. Conservar los originales. El siguiente árbol es relativo al repositorio:

```text
conversion/
  2012-decrypted.bin              # opción EUR Clausura 2012, 1.122.304 bytes
  2013-decrypted.bin              # opción base ULUS10597, 1.111.040 bytes
  2013.key                        # clave de guardado de 16 bytes, obtenida localmente
  boca.png                       # escudo RGBA con fondo transparente o claro
  river.png                      # escudo RGBA con fondo transparente o claro
  game-code/
    EBOOT.elf                    # EBOOT descifrado de la ISO original USA
    over/0059.bin                # realconditionS.ovl original, 106.496 bytes

audio-original/
  PSP_GAME/USRDIR/0SOUND.cpk
  files/0000.bin ...             # extracción de los 692 ID de 0SOUND

commentary-original/PSP_GAME/USRDIR/MSOUND.cpk

commentary-closs/
  over/0059.bin                  # realconditionS.ovl del donante PES 2014
  files/0000.bin ...             # SSOUND del donante; audio en ID 0–4917

chants-surling/
  Boca/                          # cinco .adx por carpeta
  River/
  Racing/
  Independiente/
  San-Lorenzo/
```

Los nombres de las carpetas son significativos. El orden de los cinco archivos ADX de cada club es alfabético. Extraer `EBOOT.BIN`, `OVER.cpk`, `0SOUND.cpk` y `MSOUND.cpk` de la ISO propia con una herramienta de archivos ISO. Para extraer bancos CPK por ID:

```sh
tools/venv/bin/python conversion/cpk_ids.py ruta/0SOUND.cpk audio-original/files
tools/venv/bin/python conversion/cpk_ids.py ruta/OVER-original.cpk conversion/game-code/over
tools/venv/bin/python conversion/cpk_ids.py ruta/OVER-donante.cpk commentary-closs/over
tools/venv/bin/python conversion/cpk_ids.py ruta/SSOUND-donante.cpk commentary-closs/files
```

Descifrar `EBOOT.BIN` con `tools/pspdecrypt/pspdecrypt` según su ayuda y guardar el resultado como `conversion/game-code/EBOOT.elf`. No es necesario ejecutar el código del juego donante.

Para un guardado cuyo DATA.BIN y clave ya se tienen:

```sh
tools/psp-savedata-endecrypter/endecrypter ruta/DATA.BIN ruta/clave.key \
  > conversion/2013-decrypted.bin
```

Repetir para el guardado 2012 usando su propia clave y el nombre `2012-decrypted.bin`. La clave 2012 no se usa para volver a cifrar el resultado 2013.

## Construir

```sh
tools/venv/bin/python conversion/convert.py
tools/venv/bin/python conversion/encode-chants.py
tools/venv/bin/python conversion/repack-commentary.py
tools/venv/bin/python conversion/build-iso.py \
  --source '/ruta/Pro Evolution Soccer 2013 (USA) (En,Fr,Es,Pt).iso' \
  --output 'release/PES 2013 - Liga Argentina .iso'
tools/venv/bin/python conversion/package-save.py \
  --base-save '/ruta/guardado-original/ULUS1059700008000' \
  --output 'release/PSP/SAVEDATA/ULUS1059700008000'
```

`--base-save` debe ser el guardado USA original que corresponde a la base usada. El cifrador modifica PARAM.SFO; el script trabaja sobre una copia y exige una carpeta de salida nueva. El script de ISO exige que origen y destino sean distintos.

Los bancos intermedios se generan en `conversion/`. Los scripts incluyen comprobaciones de tamaños, IDs y tablas de eventos para detectar insumos incompatibles. No desactivar esas comprobaciones para intentar aceptar otra región o versión del juego.

Los archivos generados no se agregan a Git. La ISO y el guardado final se transfieren juntos siguiendo [INSTALL.md](INSTALL.md).
