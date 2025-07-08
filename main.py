from fastapi import FastAPI
from fastapi import Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import random
import string

from fastapi.responses import RedirectResponse
from fastapi import HTTPException 

from sqlmodel import SQLModel, Field, create_engine, Session, select





app = FastAPI(
    title = "Acortador de enlaces",
    description = "Un servicio sencillo para acortar enlaces con redirección automática.",
    version="1.0.0"
)
from pydantic import BaseModel
class LinkRequest(BaseModel):
    url: str
    

templates = Jinja2Templates(directory="templates")


app.mount("/static", StaticFiles(directory="static"), name="static")


def generar_codigo(longitud=6):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choices(caracteres, k=longitud))


class Enlace(SQLModel, table=True):
    codigo: str = Field(primary_key=True)
    url: str




sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def crear_tablas():
    SQLModel.metadata.create_all(engine)

crear_tablas()








@app.post("/acortar")
def acortar_desde_form(request: Request, url: str = Form(...)):
    codigo = generar_codigo()
    enlace = Enlace(codigo=codigo, url=url)

    with Session(engine) as session:
        session.add(enlace)
        session.commit()

    short_url = f"http://localhost:8000/{codigo}"
    return templates.TemplateResponse("formulario.html", {
        "request": request,
        "short_url": short_url,
        "formulario_visible": True
    })




@app.get("/{codigo}")
def redirigir(codigo: str):
    with Session(engine) as session:
        statement = select(Enlace).where(Enlace.codigo == codigo)
        resultado = session.exec(statement).first()

        if resultado:
            return RedirectResponse(resultado.url)
        else:
            raise HTTPException(status_code=404, detail="Enlace no encontrado")
    



@app.get("/")
def formulario(request: Request):
    return templates.TemplateResponse("formulario.html", {"request": request})




if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
