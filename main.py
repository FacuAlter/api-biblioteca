from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def inicio():
    return {"mensaje": "API de la biblioteca"}


@app.get("/libros")
def listar_libros():
    return []