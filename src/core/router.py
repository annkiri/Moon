import os
import re
import time

from semantic_router import Route
from semantic_router.encoders import FastEmbedEncoder
from semantic_router.index.local import LocalIndex
from semantic_router.routers import SemanticRouter

print("⏳ [ROUTER] Inicializando Encoder...")
encoder = FastEmbedEncoder(name="sentence-transformers/all-MiniLM-L6-v2")

# --- 1. RUTAS DE ACCIÓN ---
finance_route = Route(
    name="finance",
    utterances=[
        "gaste 20 soles",
        "pague el alquiler",
        "compra de supermercado",
        "transferi dinero",
        "me cobraron netflix",
        "registra gasto",
        "pague el taxi",
        "almuerzo de 15 soles",
        "compre unas zapatillas",
        "acabo de pagar 45 soles",
        "anota que gaste 10 lucas",
        "fueron 120 cocos",
        "compre pasajes",
        "pase por la panaderia",
        "pague un jugo",
        "invitame un cigarro",
        "gaste en comida",
    ],
    score_threshold=0.45,
)

tasks_route = Route(
    name="tasks",
    utterances=[
        "recuerdame comprar leche",
        "tengo que entregar el reporte",
        "anota esta idea",
        "agendar reunion",
        "no olvidar comprar",
        "tengo que ir al banco",
        "hazme acordar mañana",
        "agenda una cita",
        # Desempates
        "recuerdame el cumpleaños",
        "hazme acordar del santo",
        "avisame de la reunion",
    ],
    score_threshold=0.45,
)

profile_route = Route(
    name="profile",
    utterances=[
        "me llamo andy",
        "soy programador",
        "mi correo es",
        "mi cumpleaños es",
        "guarda mi nombre",
        "soy de peru",
        "mi mama se llama",
    ],
    score_threshold=0.5,
)

# --- 2. RUTA DE CHAT (EL ESCUDO) ---
# Esta ruta atrapa la conversación normal para que NO vaya a los extractores
chat_route = Route(
    name="chat",
    utterances=[
        "hola",
        "como estas",
        "buenos dias",
        "explicame que son los algoritmos",  # <--- Tu caso
        "que es la vida",
        "dame mas detalle",  # <--- Tu caso ("mas detallado")
        "continua",
        "no entendi",
        "resumelo",
        "gracias",
        "ok",
        "vale",
        "interesante",
        "quien eres",
        "que puedes hacer",
    ],
    score_threshold=0.40,  # Umbral bajo para atrapar conversación
)

routes = [finance_route, tasks_route, profile_route, chat_route]

print("⚙️ [ROUTER] Construyendo índice local...")
index = LocalIndex()
router = SemanticRouter(encoder=encoder, routes=routes, index=index, auto_sync="local")

print(f"✅ [ROUTER] Sistema listo con {len(routes)} rutas activas.")


def clean_text(text: str) -> str:
    text = text.replace('"', "").replace("'", "")
    text = re.sub(
        r"^(hola|hi|hey|buenas)\s+(moon|mondri|mon)?\s*,?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    return text.strip()


def classify_intent(text: str) -> str | None:
    try:
        clean_input = clean_text(text)
        start = time.perf_counter()

        route_choice = router(clean_input)
        elapsed = (time.perf_counter() - start) * 1000

        name = route_choice.name

        # LOGICA DE CONTROL
        if name == "chat":
            print(
                f"🗣️ [ROUTER] Conversación detectada ({elapsed:.2f}ms) -> Directo a Mondri"
            )
            return None  # Devolvemos None para que NO ejecute tools

        if name:
            print(f"⚡ [ROUTER] Intención: '{name}' ({elapsed:.2f}ms)")
            return name
        else:
            print(f"🐢 [ROUTER] Intención: General/Chat ({elapsed:.2f}ms)")
            return None

    except Exception as e:
        print(f"⚠️ [ERROR] Fallo en Router: {e}")
        return None
