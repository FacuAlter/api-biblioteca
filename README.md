API de la Biblioteca
## Instalación y ejecución

API REST hecha con FastAPI para gestionar los libros de una biblioteca.

Desde PowerShell, ubicado en la carpeta raíz del proyecto (`api-biblioteca`), creá y activá el entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instalá las dependencias del proyecto:

```powershell
pip install -r requirements.txt
```

Levantá el servidor:

```powershell
python -m uvicorn main:app --reload
```

Con el servidor corriendo, abrí [Swagger](http://127.0.0.1:8000/docs) para probar los endpoints.
------------------------------------------------------------------------------------------------------------------------------

## I1 · Pruebas de validación
Verifiqué que `POST /libros` devuelve `422` con un título de 2 o 101
caracteres, cuando falta el autor y cuando el año es `999`, `2101` o `"abc"`.

### I2 — Actualizar un libro

`PUT /libros/{id}` reemplaza los datos de un libro existente y conserva su `id`.
Los campos `titulo`, `autor` y `anio` son obligatorios. `disponible` es opcional
y queda en `true` si se omite. La actualización se guarda en `datos/libros.json`.

**Ejemplo: `PUT /libros/1`**

```json
{
  "titulo": "El Aleph",
  "autor": "Jorge Luis Borges",
  "anio": 1949
}
```

**Respuesta `200 OK`**

```json
{
  "id": 5,
  "titulo": "El Aleph",
  "autor": "Jorge Luis Borges",
  "anio": 1949,
  "disponible": true
}
```

| Código | Cuándo se devuelve |
|---|---|
| `200 OK` | El libro se actualizó y se devuelve con su mismo `id`. |
| `404 Not Found` | No existe un libro con el `id` indicado. |
| `422 Unprocessable Entity` | El `id` no es un entero o los datos enviados no cumplen las validaciones. |


### I3 — Filtrar libros

`GET /libros` acepta dos parámetros opcionales. `autor` compara el nombre
completo sin distinguir mayúsculas y minúsculas. `disponible` acepta `true`
o `false`. Si se envían ambos, se aplican los dos filtros.

Ejemplo: `GET /libros?autor=jorge%20luis%20borges&disponible=false`

La respuesta es `200 OK` con una lista ordenada por ID. Si no hay
coincidencias, la lista es `[]`.

### I4 — Paginación

`GET /libros` acepta los parámetros opcionales `desde` y `limite`.
`desde` indica cuántos libros saltear y vale `0` por defecto.
`limite` indica cuántos libros devolver como máximo y vale `100` por defecto.
La paginación se aplica después de los filtros, sobre la lista ordenada por ID.

Ejemplo: `GET /libros?desde=2&limite=2`
Saltea los primeros dos libros y devuelve como máximo los dos siguientes.

### I5 — Actualización parcial

`PATCH /libros/{id}` actualiza únicamente los campos enviados.
Los campos omitidos conservan su valor y el ID se mantiene.
Un cuerpo vacío `{}` devuelve el libro completo sin cambios.
Las modificaciones se guardan en `datos/libros.json`.

Ejemplo de cuerpo para cambiar la disponibilidad:
`{"disponible": false}`

Devuelve `200 OK` con el libro completo, `404` si el libro no existe
y `422` si un campo enviado es inválido.