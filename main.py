import json
from pathlib import Path
from threading import Lock
from fastapi import FastAPI
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



@app.get("/") # F1 GET/ devuelve 200 y exactamente {"mensaje"}
def inicio():
    return {"mensaje": "API de la biblioteca"}


@app.get("/libros")
def listar_libros():
    return libros

@app.post("/libros", status_code=201)
def crear_libro(libro: LibroEntrada):
    global siguiente_id
    with bloqueo:    
        nuevo_libro = {"id": siguiente_id, **libro.model_dump()}
        guardar_libros(libros + [nuevo_libro])
        libros.append(nuevo_libro)
        siguiente_id +=1
    return nuevo_libro