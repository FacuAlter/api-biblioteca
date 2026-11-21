import json
from pathlib import Path
from threading import Lock
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field, field_validator


app = FastAPI()



class LibroEntrada(BaseModel):
    titulo: str = Field(min_length=3,max_length=100)
    autor: str = Field(min_length=3,max_length=60)
    anio: int = Field(ge=1000, le=2100)
    disponible: bool = True

class LibroGuardado(LibroEntrada):
    #Un libro guardado tambien debe tener su ID
    id: int = Field(gt=0)

class LibroParcial(BaseModel):
    # Cada campo puede omitirse en la petición.
    titulo: str | None = Field(default=None, min_length=3, max_length=100)
    autor: str | None = Field(default=None, min_length=3, max_length=60)
    anio: int | None = Field(default=None, ge=1000, le=2100)
    disponible: bool | None = None
    # Rechaza null si el cliente lo envía explícitamente.
    @field_validator("titulo", "autor", "anio", "disponible")
    @classmethod
    def rechazar_null(cls, valor):
        if valor is None:
            raise ValueError("El campo no puede ser null")
        return valor


ARCHIVOS_LIBROS = Path(__file__).resolve().parent/ "datos"/ "libros.json"

def cargar_libros():
    try:
        #Abre el archivo en modo lectura
        with ARCHIVOS_LIBROS.open("r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        #El archivo debe contener un lista jSOn
        if not isinstance(datos, list):
            return[]
        #Valida cada libro y lo convierte nuevamente en diccionario
        return[
            LibroGuardado.model_validate(libro).model_dump()
            for libro in datos
        ]
    except (FileNotFoundError, ValueError):
        #Arranca vacia si falta el archivo, esta vacio o sus datos son invalidos
        return []

def guardar_libros(lista_libros):
    #Crea la carpeta datos si doavia no existe
    ARCHIVOS_LIBROS.parent.mkdir(parents=True, exist_ok=True)
    
    #Prepara un archivo temporal en la misma carpeta
    temporal = ARCHIVOS_LIBROS.with_suffix(".tmp")
    
    #Escribe la lista completa con caracteres y sangria legible
    with temporal.open("w", encoding="utf-8") as archivo:
        json.dump(lista_libros, archivo, ensure_ascii=False, indent=4)

    #Reemplaza el archivo difinitivo cuando termina la escritura
    temporal.replace(ARCHIVOS_LIBROS)

# I8: recupera los datos al iniciar la API.
libros = cargar_libros()

# I7 e I8: Al iniciar, calcula el próximo ID usando el mayor ID guardado.
# Si la lista está vacía, default=0 hace que el primer ID sea 1.
siguiente_id = max((libro["id"] for libro in libros), default=0) + 1
bloqueo = Lock()


#-------------------------------------TAREAS FACILES---------------------------------------------------------------

@app.get("/") # F1 GET/ devuelve 200 y exactamente {"mensaje"}
def inicio():
    return {"mensaje": "API de la biblioteca"}


# @app.get("/libros") #F2 Listar libros
# def listar_libros():
#     return libros

# @app.post("/libros", status_code=201) #F3 Crear Libro
# def crear_libro(libro: LibroEntrada):
#     global siguiente_id
#     with bloqueo:    
#         nuevo_libro = {"id": siguiente_id, **libro.model_dump()}
#         guardar_libros(libros + [nuevo_libro])
#         libros.append(nuevo_libro)
#         siguiente_id +=1
#     return nuevo_libro


@app.post("/libros", status_code=201) #F3 Crear Libro. #I6 Rechaza libros duplicados
def crear_libro(libro: LibroEntrada):
    global siguiente_id                 # I7: permite modificar el contador global que conserva el próximo ID.
    with bloqueo:
        # I6: prepara los textos para comparar ignorando mayúsculas.
        titulo_buscado = libro.titulo.casefold()
        autor_buscado =libro.autor.casefold()
        
        #I6: Aqui revisa si existe la misma combinacion de titulo y autor
        for existente in libros:
            mismo_titulo = existente["titulo"].casefold() == titulo_buscado
            mismo_autor = existente ["autor"].casefold() == autor_buscado

            if mismo_titulo and mismo_autor:
                raise HTTPException(
                    status_code = 409,
                    detail = "Ya este este libron ese titulo y autor"
                )
        # Asigna el proximo ID y agrega los datos validos
        
        # I7: asigna el ID usando el contador, que se conserva al borrar libros.
        nuevo_libro = {"id": siguiente_id,**libro.model_dump()}

        #Guarda en el archivo antes de actualizar la memoria
        guardar_libros(libros + [nuevo_libro])
        libros.append(nuevo_libro)

        #I7: aumenta el contador después de una creación exitosa.
        #Si se borra este libro, la próxima creación usa el número siguiente.
        #Avanza el contador unicamente cuando se creo el libro
        siguiente_id += 1

    return nuevo_libro

@app.get("/libros/{id}")            #F4 & F5 Consulta de libro por ID  
def obtener_libro(id: int):
    for libro in libros:
        if libro["id"] == id:
            return libro
    raise HTTPException(status_code=404, detail ="Libro no encontrado")

@app.delete("/libros/{id}", status_code=204)    #F6 Eliminar Libros
def eliminar_libro(id: int):
    with bloqueo:
        for indice, libro in enumerate(libros):
            if libro["id"] == id:
                libros_actualizados = libros.copy()
                del libros_actualizados[indice]
                guardar_libros(libros_actualizados)
                libros[:] = libros_actualizados
                return Response(status_code = 204)
    raise HTTPException(status_code=404, detail="Libro no encontrado")

#----------------------------------------FIN DE TAREAS FACILES-----------------------------------------------------------------------

#-----------------------------------------TAREAS INTERMEDIAS-------------------------------------------------------------------

@app.put("/libros/{id}")                                    #I2 Actualizar libro
def actualizar_libro(id: int, libro: LibroEntrada):
    with bloqueo:
        for indice, libro_guardado in enumerate(libros): #enumerate devuelve la posicion en la lista y libro guardado
            if libro_guardado["id"] == id:                  #Busco por ID uds ls posicion para remplazar el libro en una copia
                libro_actualizado = {"id": id, **libro.model_dump()}
                
                libros_actualizados = libros.copy()
                libros_actualizados[indice] = libro_actualizado

                guardar_libros(libros_actualizados)
                libros[:] = libros_actualizados

                return libro_actualizado

    raise HTTPException(status_code=404, detail="Libro no encontrado")


@app.get("/libros") # I3: GET con filtros opcionales /I4: Paginación
def listar_libros(
    autor: str | None = None,           # Filtro opcional por autor.
    disponible: bool | None = None,     # Filtro opcional por disponibilidad.
    desde: int = 0,                     # Cantidad de libros que se saltean.
    limite: int = 0,                     # Cantidad máxima de libros a devolver.
):
    # Crea una lista nueva ordenada por ID de menor a mayor.
    resultados = sorted(libros, key=lambda libro: libro["id"]) 

    # Aplica el filtro por autor si se envió el parámetro.
    if autor is not None:
        autor_buscado = autor.casefold()
        resultados = [
            libro for libro in resultados
            if libro["autor"].casefold() == autor_buscado 
        ]
    
    # Aplica el filtro por disponibilidad si se envió el parámetro.
    if disponible is not None:
        resultados = [
            libro for libro in resultados
            if libro["disponible"] == disponible
        ]

    # Calcula la posición final del segmento que vamos a devolver.
    fin = desde + limite

    # Selecciona desde la posición inicial hasta antes de la posición final.
    return resultados[desde:fin]


@app.patch("/libros/{id}")  # I5: actualización parcial.
def actualizar_libro_parcial(id: int, libro: LibroParcial):
    # Procesa una modificación por vez.
    with bloqueo:
        for indice, libro_guardado in enumerate(libros):
            if libro_guardado["id"] == id:
                # Obtiene únicamente los campos enviados en el JSON.
                cambios = libro.model_dump(exclude_unset=True)

                # Copia el libro actual y aplica los cambios recibidos.
                libro_actualizado = libro_guardado.copy()
                libro_actualizado.update(cambios)

                # Prepara la lista con el libro actualizado.
                libros_actualizados = libros.copy()
                libros_actualizados[indice] = libro_actualizado

                # Guarda antes de actualizar la lista en memoria.
                guardar_libros(libros_actualizados)
                libros[:] = libros_actualizados

                # Devuelve el libro completo, conservando su ID.
                return libro_actualizado

    raise HTTPException(status_code=404, detail="Libro no encontrado")




