# Parser AFIP

## Instrucciones de ejecución

Para ejecutar el script se debe tener Python 2.7 instalado.

Parámetros de ejecución:
- Directorio de datos de input (default: `data`)
- Directorio donde se guardarán los resultados del script (default: `resultados`)

Ejemplo de ejecución:
```bash
python compras-parser.py data resultados
```

## Conversor PDF

Dado que los PDFs escupidos por el sistema contable están mal comprimidos, no se puede extraer información directamente de ellos mediante un script.
Por lo tanto, se debe utilizar un conversor para pasar los archivos PDF a CSV, formato mucho más amigable para leer datos de tablas.

Usar **Tabula** (https://tabula.technology/), ya que el script parsea las columnas de manera particular de acuerdo a cómo suele devolver la información ese conversor.

Recordemos que debido a los problemas del PDF todos los conversores presentan algún inconveniente en la transformación de las tablas. No se garantiza el correcto funcionamiento del script en caso de usar cualquier otro conversor.

### Insutrcciones de Tabula
- Iniciar aplicación.
- Cargar en la página principal el PDF que se desea convertir e importarlo.
- Esperar que se procese el archivo y clickear `Extract Data`.
- Se presenta una pantalla para seleccionar las tablas a convertir dentro del archivo. Clickear y arrastrar para formar áreas que encuadren las tablas de cada página. La tabla se conforma por el encabezado (donde se nombran las columnas) y todos los registros; los pies de tabla con subtotales pueden ser ignorados.
- Una vez seleccionadas las tablas, clickear `Preview & Export Data`.
- En el menú lateral de la nueva pantalla, seleccionar como método de extracción `Stream`. Notar que algunos campos de la tabla estarán colapsados o vacíos. Ignorar los errores a groso modo, el script está programado para limpiarlos y saber trabajar con ellos.
- Exportar a CSV.


