API de la Biblioteca

## I1 · Pruebas de validación
Verifiqué que `POST /libros` devuelve `422` con un título de 2 o 101
caracteres, cuando falta el autor y cuando el año es `999`, `2101` o `"abc"`.