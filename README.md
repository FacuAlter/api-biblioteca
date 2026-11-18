API de la Biblioteca

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