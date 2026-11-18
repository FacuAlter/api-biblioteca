import json
from pathlib import Path
from threading import Lock
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field


app = FastAPI()



class LibroEntrada(BaseModel):
    titulo: str = Field(min_length=3,max_length=100)
    autor: str = Field(min_length=3,max_length=60)
    anio: int = Field(ge=1000, le=2100)
    disponible: bool = True



ARCHIVOS_LIBROS = Path(__file__).resolve().parent/ "datos"/ "libros.json"

def cargar_libros():
    if not ARCHIVOS_LIBROS.exists():
        return []
    with ARCHIVOS_LIBROS.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)

def guardar_libros(lista_libros):
    ARCHIVOS_LIBROS.parent.mkdir(exist_ok=True)

    temporal = ARCHIVOS_LIBROS.with_suffix(".tmp")
    with temporal.open("w", encoding="utf-8") as archivo:
        json.dump(lista_libros, archivo, ensure_ascii=False, indent=4)
    temporal.replace(ARCHIVOS_LIBROS)

libros = cargar_libros()
siguiente_id = max((libro["id"] for libro in libros), default=0) + 1
bloqueo = Lock()


#-------------------------------------TAREAS FACILES---------------------------------------------------------------

@app.get("/") # F1 GET/ devuelve 200 y exactamente {"mensaje"}
def inicio():
    return {"mensaje": "API de la biblioteca"}


# @app.get("/libros") #F2 Listar libros
# def listar_libros():
#     return libros

@app.post("/libros", status_code=201) #F3 Crear Libro
def crear_libro(libro: LibroEntrada):
    global siguiente_id
    with bloqueo:    
        nuevo_libro = {"id": siguiente_id, **libro.model_dump()}
        guardar_libros(libros + [nuevo_libro])
        libros.append(nuevo_libro)
        siguiente_id +=1
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


@app.get("/libros") # I3: GET con filtros opcionales
def listar_libros(
    autor: str | None = None,
    disponible: bool | None = None,
):
    #sorted crea una lista ordenada de mayor a menor
    resultados = sorted(libros, key=lambda libro: libro["id"]) 

    if autor is not None:
        autor_buscado = autor.casefold()
        resultados = [
            libro for libro in resultados
            if libro["autor"].casefold() == autor_buscado 
        ]
    if disponible is not None:
        resultados = [
            libro for libro in resultados
            if libro["disponible"] == disponible
        ]

    return resultados
