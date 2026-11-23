## API de la Biblioteca

## Desarrollor
  Facundo Nicolás Flores 

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
  "id": 1,
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


### I6 — Conflicto por libro duplicado

`POST /libros` devuelve `409 Conflict` si ya existe un libro con
el mismo título y autor, sin distinguir mayúsculas y minúsculas.
El intento duplicado no agrega un libro ni avanza el contador de IDs.
La respuesta contiene `{"detail": "Ya existe un libro con ese título y autor"}`.

### I7 — IDs que no se reutilizan

Cada libro recibe un ID mediante un contador que aumenta al crear un libro.
Borrar un libro no disminuye el contador.
Durante una misma ejecución, los IDs eliminados no se reutilizan.

Por ejemplo, si se crean los libros 1, 2 y 3, se borra el 3
y se crea otro, el nuevo libro recibe el ID 4.
Al iniciar la API, el contador se calcula como el mayor ID guardado más uno,
o 1 si la lista está vacía.

### I8 — Persistencia en archivo

Los libros se guardan en `datos/libros.json`.
La ruta se calcula tomando como referencia la ubicación de `main.py`.
La carpeta `datos` se crea automáticamente al guardar si todavía no existe.
Las operaciones POST, PUT, PATCH y DELETE guardan los cambios.
Al iniciar, la API recupera los libros y calcula el próximo ID
como el mayor ID guardado más uno, o 1 si la lista está vacía.
Si el archivo falta, está vacío o contiene datos inválidos,
la API inicia con una lista vacía.

### I9 — Búsqueda por texto

`GET /libros/buscar?texto=...` busca coincidencias parciales
en el título o autor, sin distinguir mayúsculas y minúsculas.
El parámetro `texto` es obligatorio.
Devuelve `200 OK` con una lista ordenada por ID.
Si no hay coincidencias, devuelve `[]`.
Si falta `texto`, devuelve `422`.
La búsqueda también funciona con los libros recuperados después de reiniciar.

Ejemplo: `GET /libros/buscar?texto=borges`