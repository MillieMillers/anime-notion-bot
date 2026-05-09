"""
╔══════════════════════════════════════════════════════════════════╗
║         NOTION ANIME TRACKER — Streamlit App                     ║
║  Busca anime via Jikan, previsualiza portadas y agrega a Notion  ║
╚══════════════════════════════════════════════════════════════════╝
Instalar: pip install streamlit requests
Correr  : streamlit run app.py

Credenciales en .streamlit/secrets.toml:
  NOTION_TOKEN = "secret_..."
  DATABASE_ID  = "..."
"""

import streamlit as st
import requests
import json
import time

# ══════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN — Credenciales via st.secrets
#  Crea el archivo .streamlit/secrets.toml con:
#    NOTION_TOKEN = "secret_TU_TOKEN"
#    DATABASE_ID  = "TU_DATABASE_ID"
# ══════════════════════════════════════════════════════════════════

NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
DATABASE_ID  = st.secrets["DATABASE_ID"]

JIKAN_BASE  = "https://api.jikan.moe/v4"
NOTION_BASE = "https://api.notion.com/v1"
NOTION_VER  = "2022-06-28"

# ══════════════════════════════════════════════════════════════════
#  MAPEO DE GÉNEROS (igual que el script original)
# ══════════════════════════════════════════════════════════════════

GENRE_MAP = {
    "Action": "Action", "Adventure": "Adventure", "Comedy": "Comedy",
    "Drama": "Drama", "Fantasy": "Fantasy", "Horror": "Horror",
    "Mystery": "Mystery", "Romance": "Romance", "Sci-Fi": "Sci-Fi",
    "Slice of Life": "Slice of Life", "Sports": "Sports",
    "Supernatural": "Supernatural", "Thriller": "Thriller",
    "Award Winning": "Award Winning", "Avant Garde": "Avant Garde",
    "Boys Love": "Boys Love", "Girls Love": "Girls Love",
    "Suspense": "Suspense", "Ecchi": "Ecchi", "Psychological": "Psychological",
    "School": "School", "Military": "Military", "Historical": "Historical",
    "Isekai": "Isekai", "Music": "Music", "Game": "Game", "Harem": "Harem",
    "Shounen": "Shounen", "Shoujo": "Shoujo", "Seinen": "Seinen", "Josei": "Josei",
    "Gourmet": "Slice of Life", "Magic": "Fantasy", "Martial Arts": "Action",
    "Samurai": "Historical", "Space": "Sci-Fi", "Super Power": "Action",
    "Vampire": "Supernatural", "Demons": "Supernatural", "Mecha": "Sci-Fi",
}

PROP = {
    "title":    "Title",
    "score":    "Score",
    "genres":   "Genres",
    "status":   "Status",
    "episodes": "Total Episodes",
    "mal_url":  "URL",
}

# ══════════════════════════════════════════════════════════════════
#  CSS PERSONALIZADO — Estética oscura tipo anime dashboard
# ══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500&display=swap');

/* Fondo general */
.stApp {
    background: #0e0e12;
}

/* Ocultar elementos default de Streamlit */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1100px; }

/* ── Header principal ── */
.app-header {
    text-align: center;
    padding: 2.5rem 0 1.5rem;
    margin-bottom: 0.5rem;
}

.app-header h1 {
    font-family: 'Syne', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -1px;
    margin: 0;
    line-height: 1;
}

.app-header h1 span {
    color: #6b8ef7;
}

.app-header p {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    color: #555566;
    margin-top: 0.5rem;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* ── Barra de búsqueda ── */
.search-container {
    max-width: 600px;
    margin: 0 auto 2rem;
}

/* Input de Streamlit */
.stTextInput input {
    background: #1a1a22 !important;
    border: 1.5px solid #2a2a38 !important;
    border-radius: 10px !important;
    color: #e8e8ea !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 0.75rem 1.1rem !important;
    transition: border-color 0.2s !important;
}

.stTextInput input:focus {
    border-color: #6b8ef7 !important;
    box-shadow: 0 0 0 3px rgba(107,142,247,0.12) !important;
}

.stTextInput input::placeholder { color: #44445a !important; }
.stTextInput label { color: #44445a !important; font-size: 0.75rem !important; }

/* ── Botón de búsqueda ── */
.stButton button {
    background: #6b8ef7 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.6rem 1.4rem !important;
    transition: background 0.15s, transform 0.1s !important;
    width: 100% !important;
}

.stButton button:hover {
    background: #5579f0 !important;
    transform: translateY(-1px) !important;
}

/* Botón de agregar — variante verde */
.add-btn button {
    background: #1a2a1a !important;
    color: #4ade80 !important;
    border: 1px solid #2a4a2a !important;
    font-size: 0.75rem !important;
    padding: 0.45rem 0.8rem !important;
}

.add-btn button:hover {
    background: #22c55e !important;
    color: #ffffff !important;
    border-color: #22c55e !important;
    transform: none !important;
}

/* ── Tarjeta de anime ── */
.anime-card {
    background: #16161e;
    border: 1px solid #222230;
    border-radius: 12px;
    overflow: hidden;
    transition: border-color 0.2s, transform 0.2s;
    height: 100%;
}

.anime-card:hover {
    border-color: #6b8ef7;
    transform: translateY(-3px);
}

.card-poster {
    width: 100%;
    aspect-ratio: 2/3;
    object-fit: cover;
    display: block;
}

.card-poster-placeholder {
    width: 100%;
    aspect-ratio: 2/3;
    background: linear-gradient(135deg, #1a1a28, #22223a);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #333350;
    font-size: 2rem;
}

.card-body {
    padding: 10px 11px 12px;
}

.card-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    color: #e8e8ea;
    line-height: 1.35;
    margin-bottom: 5px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    min-height: 2.2em;
}

.card-meta {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 6px;
}

.card-score {
    font-family: 'Syne', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    color: #fbbf24;
    background: rgba(251,191,36,0.1);
    padding: 1px 6px;
    border-radius: 4px;
}

.card-type {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.62rem;
    font-weight: 600;
    color: #6b8ef7;
    background: rgba(107,142,247,0.1);
    padding: 1px 6px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}

.card-year {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.62rem;
    color: #44445a;
}

/* ── Mensajes de estado ── */
.msg-success {
    background: #0f2a1a;
    border: 1px solid #166534;
    border-radius: 8px;
    padding: 10px 14px;
    color: #4ade80;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.8rem;
    margin-top: 6px;
}

.msg-error {
    background: #2a0f0f;
    border: 1px solid #991b1b;
    border-radius: 8px;
    padding: 10px 14px;
    color: #f87171;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.8rem;
    margin-top: 6px;
}

.msg-already {
    background: #1a1a0f;
    border: 1px solid #713f12;
    border-radius: 8px;
    padding: 10px 14px;
    color: #fbbf24;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.8rem;
    margin-top: 6px;
}

/* ── Sección de resultados ── */
.results-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    color: #44445a;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 1rem;
}

/* Spinner */
.stSpinner > div { border-top-color: #6b8ef7 !important; }

/* Selectbox */
.stSelectbox select {
    background: #1a1a22 !important;
    color: #e8e8ea !important;
    border-color: #2a2a38 !important;
}

/* Divisor */
hr { border-color: #1e1e2a !important; margin: 1.5rem 0 !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  FUNCIONES — Jikan API
# ══════════════════════════════════════════════════════════════════

@st.cache_data(ttl=300, show_spinner=False)
def search_anime(query: str) -> list[dict]:
    """Busca anime en Jikan. Resultado cacheado 5 minutos."""
    try:
        resp = requests.get(
            f"{JIKAN_BASE}/anime",
            params={"q": query, "limit": 8},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json().get("data", [])
    except Exception:
        return []


@st.cache_data(ttl=300, show_spinner=False)
def get_anime_detail(mal_id: int) -> dict | None:
    """Obtiene detalle completo de un anime. Resultado cacheado."""
    time.sleep(0.4)
    try:
        resp = requests.get(f"{JIKAN_BASE}/anime/{mal_id}/full", timeout=15)
        resp.raise_for_status()
        return resp.json().get("data", {})
    except Exception:
        return None


def clean_genres(raw_genres: list[dict]) -> list[str]:
    seen, result = set(), []
    for g in raw_genres:
        name   = g.get("name", "")
        mapped = GENRE_MAP.get(name, name)
        if mapped and mapped not in seen:
            result.append(mapped)
            seen.add(mapped)
    return result


def extract_anime_data(anime: dict) -> dict:
    all_genres = (
        anime.get("genres", []) +
        anime.get("demographics", []) +
        anime.get("themes", []) +
        anime.get("explicit_genres", [])
    )
    synopsis = anime.get("synopsis") or "Sin sinopsis disponible."
    synopsis = synopsis[:1997] + "..." if len(synopsis) > 2000 else synopsis

    images    = anime.get("images", {})
    jpg       = images.get("jpg", {})
    cover_url = jpg.get("large_image_url") or jpg.get("image_url") or ""

    return {
        "title":    anime.get("title_english") or anime.get("title", "Sin título"),
        "score":    anime.get("score"),
        "genres":   clean_genres(all_genres),
        "synopsis": synopsis,
        "cover":    cover_url,
        "episodes": anime.get("episodes"),
        "status":   anime.get("status", ""),
        "type":     anime.get("type", ""),
        "mal_url":  anime.get("url", ""),
        "mal_id":   anime.get("mal_id"),
    }


# ══════════════════════════════════════════════════════════════════
#  FUNCIONES — Notion API
# ══════════════════════════════════════════════════════════════════

def create_notion_page(data: dict) -> tuple[bool, str]:
    """
    Crea una página en Notion. Devuelve (éxito, mensaje).
    """
    status_map = {
        "Finished Airing":  "Not Started",
        "Currently Airing": "Up Next",
        "Not yet aired":    "Up Next",
    }

    properties = {
        PROP["title"]: {
            "title": [{"text": {"content": data["title"]}}]
        },
        PROP["genres"]: {
            "multi_select": [{"name": g} for g in data["genres"]]
        },
    }

    if data["score"] is not None:
        properties[PROP["score"]] = {"number": data["score"]}

    if data["episodes"] is not None:
        properties[PROP["episodes"]] = {"number": data["episodes"]}

    notion_status = status_map.get(data["status"], "Up Next")
    properties[PROP["status"]] = {"status": {"name": notion_status}}

    if data["mal_url"]:
        properties[PROP["mal_url"]] = {"url": data["mal_url"]}

    if data["cover"]:
        properties["Image"] = {
            "files": [{"name": data["title"], "type": "external",
                       "external": {"url": data["cover"]}}]
        }

    payload = {
        "parent":     {"database_id": DATABASE_ID},
        "properties": properties,
    }

    if data["cover"]:
        payload["cover"] = {"type": "external", "external": {"url": data["cover"]}}

    try:
        resp = requests.post(
            f"{NOTION_BASE}/pages",
            headers={
                "Authorization":  f"Bearer {NOTION_TOKEN}",
                "Content-Type":   "application/json",
                "Notion-Version": NOTION_VER,
            },
            data=json.dumps(payload),
            timeout=20,
        )
        resp.raise_for_status()
        page_url = resp.json().get("url", "")
        return True, page_url
    except requests.exceptions.HTTPError:
        msg = resp.json().get("message", "Error desconocido")
        return False, msg
    except Exception as e:
        return False, str(e)


# ══════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════

if "results"  not in st.session_state: st.session_state.results  = []
if "added"    not in st.session_state: st.session_state.added    = set()   # mal_ids ya agregados
if "messages" not in st.session_state: st.session_state.messages = {}      # {mal_id: (tipo, texto)}
if "query"    not in st.session_state: st.session_state.query    = ""


# ══════════════════════════════════════════════════════════════════
#  UI — Header
# ══════════════════════════════════════════════════════════════════

st.markdown("""
<div class="app-header">
    <h1>Anime <span>Tracker</span></h1>
    <p>Busca · Descubre · Agrega a Notion</p>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  UI — Barra de búsqueda
# ══════════════════════════════════════════════════════════════════

col_input, col_btn = st.columns([5, 1])

with col_input:
    query = st.text_input(
        label="search",
        placeholder="Busca un anime... (ej. Attack on Titan, Re:Zero)",
        label_visibility="collapsed",
        key="search_input",
    )

with col_btn:
    search_clicked = st.button("Buscar", use_container_width=True)


# ══════════════════════════════════════════════════════════════════
#  LÓGICA — Búsqueda
# ══════════════════════════════════════════════════════════════════

if search_clicked and query.strip():
    with st.spinner("Buscando en MyAnimeList..."):
        st.session_state.results  = search_anime(query.strip())
        st.session_state.messages = {}   # limpiar mensajes al nueva búsqueda
        st.session_state.query    = query.strip()

    if not st.session_state.results:
        st.markdown('<p class="results-label">Sin resultados para esa búsqueda.</p>',
                    unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  UI — Grid de resultados
# ══════════════════════════════════════════════════════════════════

if st.session_state.results:

    st.markdown(
        f'<p class="results-label">{len(st.session_state.results)} resultados '
        f'para "{st.session_state.query}"</p>',
        unsafe_allow_html=True
    )

    cols = st.columns(4, gap="small")

    for i, anime in enumerate(st.session_state.results):
        mal_id   = anime.get("mal_id")
        title_en = anime.get("title_english") or anime.get("title", "Sin título")
        title_jp = anime.get("title_japanese", "")
        score    = anime.get("score")
        year     = anime.get("year") or "?"
        atype    = anime.get("type", "")
        images   = anime.get("images", {})
        cover    = images.get("jpg", {}).get("large_image_url") or \
                   images.get("jpg", {}).get("image_url") or ""

        with cols[i % 4]:

            # Poster
            if cover:
                st.markdown(f"""
                <div class="anime-card">
                    <img class="card-poster" src="{cover}" alt="{title_en}" />
                    <div class="card-body">
                        <div class="card-title">{title_en}</div>
                        <div class="card-meta">
                            {"<span class='card-score'>★ " + str(score) + "</span>" if score else ""}
                            {"<span class='card-type'>" + atype + "</span>" if atype else ""}
                            <span class="card-year">{year}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="anime-card">
                    <div class="card-poster-placeholder">?</div>
                    <div class="card-body">
                        <div class="card-title">{title_en}</div>
                        <div class="card-meta">
                            {"<span class='card-score'>★ " + str(score) + "</span>" if score else ""}
                            {"<span class='card-type'>" + atype + "</span>" if atype else ""}
                            <span class="card-year">{year}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Botón Añadir
            already_added = mal_id in st.session_state.added

            if already_added:
                st.markdown('<div class="msg-already">✓ Ya en tu biblioteca</div>',
                            unsafe_allow_html=True)
            else:
                with st.container():
                    st.markdown('<div class="add-btn">', unsafe_allow_html=True)
                    if st.button("+ Añadir a Biblioteca", key=f"add_{mal_id}",
                                 use_container_width=True):

                        with st.spinner(f"Agregando {title_en}..."):
                            detail = get_anime_detail(mal_id)

                        if not detail:
                            st.session_state.messages[mal_id] = (
                                "error", "No se pudo obtener el detalle del anime."
                            )
                        else:
                            anime_data = extract_anime_data(detail)
                            success, result = create_notion_page(anime_data)

                            if success:
                                st.session_state.added.add(mal_id)
                                st.session_state.messages[mal_id] = (
                                    "success",
                                    f"Agregado a Notion correctamente."
                                )
                            else:
                                st.session_state.messages[mal_id] = (
                                    "error", f"Error: {result}"
                                )
                        st.rerun()

                    st.markdown('</div>', unsafe_allow_html=True)

            # Mostrar mensaje de feedback si existe
            if mal_id in st.session_state.messages:
                tipo, texto = st.session_state.messages[mal_id]
                css_class = "msg-success" if tipo == "success" else "msg-error"
                st.markdown(
                    f'<div class="{css_class}">{texto}</div>',
                    unsafe_allow_html=True
                )

            # Espacio entre filas
            if i % 4 == 3 and i < len(st.session_state.results) - 1:
                st.markdown("<br>", unsafe_allow_html=True)
