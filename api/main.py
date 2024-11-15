from typing import Union
from fastapi import FastAPI, status, Depends, HTTPException
from typing import Annotated
from auth import get_current_user, router as auth_router
from predict import router as predict_router
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Créez un instrumentateur et configurez-le
instrumentator = Instrumentator()

# Instrumenter l'application et exposer les métriques
instrumentator.instrument(app).expose(app)

# Inclusion du routeur d'authentification
app.include_router(auth_router)
app.include_router(predict_router)

# Route pour obtenir les informations de l'utilisateur actuel
@app.get("/", status_code=status.HTTP_200_OK)
async def user(user: Annotated[dict, Depends(get_current_user)]):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return {"User": user}

