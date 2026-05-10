"""
NOTION ANIME TRACKER — Streamlit App v3
Correr: streamlit run app.py

Credenciales en .streamlit/secrets.toml:
  NOTION_TOKEN = "secret_..."
  DATABASE_ID  = "..."
"""

import streamlit as st
import requests
import json
import time

# ══════════════════════════════════════════════════════════════════
#  CONFIGURACION
# ══════════════════════════════════════════════════════════════════

NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
DATABASE_ID  = st.secrets["DATABASE_ID"]

JIKAN_BASE  = "https://api.jikan.moe/v4"
NOTION_BASE = "https://api.notion.com/v1"
NOTION_VER  = "2022-06-28"

GENRE_MAP = {
    "Action":"Action","Adventure":"Adventure","Comedy":"Comedy","Drama":"Drama",
    "Fantasy":"Fantasy","Horror":"Horror","Mystery":"Mystery","Romance":"Romance",
    "Sci-Fi":"Sci-Fi","Slice of Life":"Slice of Life","Sports":"Sports",
    "Supernatural":"Supernatural","Thriller":"Thriller","Suspense":"Suspense",
    "Psychological":"Psychological","School":"School","Military":"Military",
    "Historical":"Historical","Isekai":"Isekai","Music":"Music","Game":"Game",
    "Harem":"Harem","Ecchi":"Ecchi","Shounen":"Shounen","Shoujo":"Shoujo",
    "Seinen":"Seinen","Josei":"Josei","Award Winning":"Award Winning",
    "Avant Garde":"Avant Garde","Boys Love":"Boys Love","Girls Love":"Girls Love",
    "Gourmet":"Slice of Life","Magic":"Fantasy","Martial Arts":"Action",
    "Samurai":"Historical","Space":"Sci-Fi","Super Power":"Action",
    "Vampire":"Supernatural","Demons":"Supernatural","Mecha":"Sci-Fi",
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
#  PAGE CONFIG — debe ir antes de cualquier otro comando st.*
# ══════════════════════════════════════════════════════════════════

st.set_page_config(page_title="Anime Tracker", layout="wide")

# ══════════════════════════════════════════════════════════════════
#  CSS — modo dia/noche automatico
#  NOTA: los SVGs NO van dentro de st.markdown de tarjetas.
#  Solo se usan caracteres Unicode o texto plano en el HTML de cards.
# ══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500;600&display=swap');

/* Variables de color — modo DIA */
:root {
  --accent:       #3E8BFF;
  --accent-dim:   #2b6fd4;
  --accent-soft:  rgba(62,139,255,0.10);
  --bg:           #f4f5f9;
  --surface:      #ffffff;
  --border:       #e0e4f0;
  --txt-1:        #111827;
  --txt-2:        #4b5563;
  --txt-3:        #9ca3af;
  --tag-bg:       rgba(62,139,255,0.09);
  --tag-txt:      #2563c7;
  --ok-bg:        #f0fdf4;
  --ok-bd:        #bbf7d0;
  --ok-txt:       #15803d;
  --err-bg:       #fef2f2;
  --err-bd:       #fecaca;
  --err-txt:      #b91c1c;
  --done-bg:      #eff6ff;
  --done-bd:      #bfdbfe;
  --done-txt:     #1d4ed8;
}

/* Variables de color — modo NOCHE */
@media (prefers-color-scheme: dark) {
  :root {
    --accent:       #5ba3ff;
    --accent-dim:   #4a8ff0;
    --accent-soft:  rgba(91,163,255,0.10);
    --bg:           #111113;
    --surface:      #1c1c1f;
    --border:       #2e2e34;
    --txt-1:        #e8e8ea;
    --txt-2:        #9ca3af;
    --txt-3:        #6b7280;
    --tag-bg:       rgba(91,163,255,0.10);
    --tag-txt:      #7fb3ff;
    --ok-bg:        #052e16;
    --ok-bd:        #166534;
    --ok-txt:       #4ade80;
    --err-bg:       #2a0a0a;
    --err-bd:       #7f1d1d;
    --err-txt:      #f87171;
    --done-bg:      #0c1a3a;
    --done-bd:      #1e3a8a;
    --done-txt:     #93c5fd;
  }
}

/* App */
.stApp { background: var(--bg) !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.8rem 2rem 3rem !important; max-width: 1100px !important; }

/* Header */
.app-header {
  padding: 0.5rem 0 1.5rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1.6rem;
}
.app-title {
  font-family: 'Syne', sans-serif;
  font-size: 1.55rem;
  font-weight: 800;
  color: var(--txt-1);
  letter-spacing: -0.4px;
  margin: 0;
  line-height: 1;
}
.app-title span { color: var(--accent); }
.app-sub {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.68rem;
  color: var(--txt-3);
  text-transform: uppercase;
  letter-spacing: 0.9px;
  margin-top: 5px;
}

/* Input de busqueda */
.stTextInput > div > div > input {
  background: var(--surface) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--txt-1) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.88rem !important;
  transition: border-color 0.18s !important;
  box-shadow: none !important;
}
.stTextInput > div > div > input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(62,139,255,0.12) !important;
}
.stTextInput > div > div > input::placeholder { color: var(--txt-3) !important; }
.stTextInput label { display: none !important; }

/* Boton principal */
.stButton > button {
  background: var(--accent) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 10px !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 600 !important;
  font-size: 0.85rem !important;
  width: 100% !important;
  transition: background 0.15s, transform 0.1s !important;
}
.stButton > button:hover {
  background: var(--accent-dim) !important;
  transform: translateY(-1px) !important;
}

/* Imagen del poster — quitar el margen/padding de Streamlit */
.stImage { margin: 0 !important; }
.stImage img {
  border-radius: 9px 9px 0 0 !important;
  display: block !important;
  width: 100% !important;
  object-fit: cover !important;
}

/* Tarjeta contenedora */
.card-wrap {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 11px;
  overflow: hidden;
  transition: border-color 0.18s, box-shadow 0.18s;
  margin-bottom: 2px;
}
.card-wrap:hover {
  border-color: var(--accent);
  box-shadow: 0 5px 20px rgba(62,139,255,0.14);
}

/* Cuerpo de la tarjeta */
.card-body {
  padding: 8px 10px 10px;
}
.card-title {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.74rem;
  font-weight: 600;
  color: var(--txt-1);
  line-height: 1.35;
  margin-bottom: 5px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 2.1em;
}
.card-meta {
  display: flex;
  align-items: center;
  gap: 5px;
  flex-wrap: wrap;
}
.b-score {
  font-family: 'Syne', sans-serif;
  font-size: 0.66rem;
  font-weight: 700;
  color: #d97706;
  background: rgba(217,119,6,0.10);
  padding: 1px 6px;
  border-radius: 4px;
}
.b-type {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.6rem;
  font-weight: 600;
  color: var(--accent);
  background: var(--accent-soft);
  padding: 1px 6px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}
.b-year {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.6rem;
  color: var(--txt-3);
}

/* Mensajes debajo del boton */
.msg {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.71rem;
  font-weight: 500;
  padding: 6px 9px;
  border-radius: 7px;
  margin-top: 4px;
  text-align: center;
}
.msg-ok   { background:var(--ok-bg);   border:1px solid var(--ok-bd);   color:var(--ok-txt);   }
.msg-err  { background:var(--err-bg);  border:1px solid var(--err-bd);  color:var(--err-txt);  }
.msg-done { background:var(--done-bg); border:1px solid var(--done-bd); color:var(--done-txt); font-weight:600; }

/* Etiqueta de resultados */
.results-label {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--txt-3);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 1rem;
}
.results-label strong { color: var(--accent); }

/* Spinner */
.stSpinner > div { border-top-color: var(--accent) !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  FUNCIONES — JIKAN
# ══════════════════════════════════════════════════════════════════

@st.cache_data(ttl=300, show_spinner=False)
def search_anime(query: str) -> list[dict]:
    try:
        r = requests.get(f"{JIKAN_BASE}/anime", params={"q": query, "limit": 8}, timeout=15)
        r.raise_for_status()
        return r.json().get("data", [])
    except Exception:
        return []


@st.cache_data(ttl=300, show_spinner=False)
def get_anime_detail(mal_id: int) -> dict | None:
    time.sleep(0.4)
    try:
        r = requests.get(f"{JIKAN_BASE}/anime/{mal_id}/full", timeout=15)
        r.raise_for_status()
        return r.json().get("data", {})
    except Exception:
        return None


def clean_genres(raw: list[dict]) -> list[str]:
    seen, out = set(), []
    for g in raw:
        m = GENRE_MAP.get(g.get("name", ""), g.get("name", ""))
        if m and m not in seen:
            out.append(m)
            seen.add(m)
    return out


def extract_data(anime: dict) -> dict:
    genres = clean_genres(
        anime.get("genres", []) + anime.get("demographics", []) +
        anime.get("themes", []) + anime.get("explicit_genres", [])
    )
    syn  = anime.get("synopsis") or "Sin sinopsis."
    syn  = syn[:1997] + "..." if len(syn) > 2000 else syn
    jpg  = (anime.get("images") or {}).get("jpg", {})
    return {
        "title":    anime.get("title_english") or anime.get("title", "Sin titulo"),
        "score":    anime.get("score"),
        "genres":   genres,
        "synopsis": syn,
        "cover":    jpg.get("large_image_url") or jpg.get("image_url") or "",
        "episodes": anime.get("episodes"),
        "status":   anime.get("status", ""),
        "mal_url":  anime.get("url", ""),
        "mal_id":   anime.get("mal_id"),
    }


# ══════════════════════════════════════════════════════════════════
#  FUNCIONES — NOTION
# ══════════════════════════════════════════════════════════════════

def create_notion_page(data: dict) -> tuple[bool, str]:
    status_map = {
        "Finished Airing": "Not Started",
        "Currently Airing": "Up Next",
        "Not yet aired": "Up Next",
    }
    props = {
        PROP["title"]:  {"title":        [{"text": {"content": data["title"]}}]},
        PROP["genres"]: {"multi_select": [{"name": g} for g in data["genres"]]},
        PROP["status"]: {"status":       {"name": status_map.get(data["status"], "Up Next")}},
    }
    if data["score"] is not None:
        props[PROP["score"]] = {"number": data["score"]}
    if data["episodes"] is not None:
        props[PROP["episodes"]] = {"number": data["episodes"]}
    if data["mal_url"]:
        props[PROP["mal_url"]] = {"url": data["mal_url"]}

    payload = {"parent": {"database_id": DATABASE_ID}, "properties": props}
    if data["cover"]:
        payload["cover"] = {"type": "external", "external": {"url": data["cover"]}}

    try:
        r = requests.post(
            f"{NOTION_BASE}/pages",
            headers={"Authorization": f"Bearer {NOTION_TOKEN}",
                     "Content-Type": "application/json",
                     "Notion-Version": NOTION_VER},
            data=json.dumps(payload), timeout=20,
        )
        r.raise_for_status()
        return True, r.json().get("url", "")
    except requests.exceptions.HTTPError:
        return False, r.json().get("message", "Error desconocido")
    except Exception as e:
        return False, str(e)


# ══════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════

for k, v in [("results", []), ("added", set()), ("msgs", {}), ("query", "")]:
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════
#  UI — HEADER
# ══════════════════════════════════════════════════════════════════

st.markdown("""
<div class="app-header">
  <div class="app-title">Anime <span>Tracker</span></div>
  <div class="app-sub">Busca &middot; Descubre &middot; Agrega a Notion</div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  UI — BUSQUEDA
# ══════════════════════════════════════════════════════════════════

c1, c2 = st.columns([5, 1])
with c1:
    query = st.text_input("q", placeholder="Busca un anime... (ej. Bleach, Vinland Saga)",
                          label_visibility="collapsed", key="search_input")
with c2:
    clicked = st.button("Buscar", use_container_width=True, key="btn_search")

if clicked and query.strip():
    with st.spinner("Buscando..."):
        st.session_state.results = search_anime(query.strip())
        st.session_state.msgs    = {}
        st.session_state.query   = query.strip()
    if not st.session_state.results:
        st.warning(f'Sin resultados para "{query}"')


# ══════════════════════════════════════════════════════════════════
#  UI — RESULTADOS
#  Clave del error anterior: se usaba HTML complejo con SVGs dentro
#  de st.markdown(), lo que Streamlit escapaba como texto plano.
#  SOLUCION: usar st.image() para los posters (componente nativo)
#  y HTML simple (sin SVG) para los badges de texto.
# ══════════════════════════════════════════════════════════════════

if st.session_state.results:
    n = len(st.session_state.results)
    st.markdown(
        f'<div class="results-label">Resultados para '
        f'<strong>"{st.session_state.query}"</strong> — {n} titulos</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(4, gap="small")

    for idx, anime in enumerate(st.session_state.results):
        mal_id   = anime.get("mal_id") or idx
        title_en = anime.get("title_english") or anime.get("title") or "Sin titulo"
        score    = anime.get("score")
        year     = anime.get("year") or "?"
        atype    = anime.get("type") or ""
        jpg      = (anime.get("images") or {}).get("jpg", {})
        cover    = jpg.get("large_image_url") or jpg.get("image_url") or ""

        # Clave unica: indice + mal_id — resuelve StreamlitDuplicateElementKey
        ukey = f"{idx}_{mal_id}"

        with cols[idx % 4]:

            # ── Inicio del wrapper de tarjeta ──
            st.markdown('<div class="card-wrap">', unsafe_allow_html=True)

            # POSTER — st.image() es nativo y no tiene problemas de escapado
            if cover:
                st.image(cover, use_container_width=True)
            else:
                st.markdown(
                    '<div style="aspect-ratio:2/3;background:var(--accent-soft);'
                    'border-radius:9px 9px 0 0;"></div>',
                    unsafe_allow_html=True,
                )

            # CUERPO — HTML simple, sin SVGs embebidos
            score_html = f'<span class="b-score">&#9733; {score}</span>' if score else ""
            type_html  = f'<span class="b-type">{atype}</span>'          if atype else ""
            year_html  = f'<span class="b-year">{year}</span>'

            st.markdown(f"""
            <div class="card-body">
              <div class="card-title">{title_en}</div>
              <div class="card-meta">
                {score_html}
                {type_html}
                {year_html}
              </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Cierre del wrapper ──
            st.markdown('</div>', unsafe_allow_html=True)

            # BOTON — siempre fuera del HTML, componente nativo de Streamlit
            already = mal_id in st.session_state.added

            if already:
                st.markdown(
                    '<div class="msg msg-done">Agregado a Notion</div>',
                    unsafe_allow_html=True,
                )
            else:
                # Key unica por boton — evita el error de keys duplicadas
                if st.button("Añadir a Biblioteca", key=f"add_{ukey}",
                             use_container_width=True):
                    with st.spinner("Obteniendo datos..."):
                        detail = get_anime_detail(mal_id)

                    if not detail:
                        st.session_state.msgs[ukey] = ("err", "No se pudo obtener el detalle.")
                    else:
                        anime_data = extract_data(detail)
                        ok, result = create_notion_page(anime_data)
                        if ok:
                            st.session_state.added.add(mal_id)
                            st.session_state.msgs[ukey] = ("ok", "Agregado correctamente.")
                        else:
                            st.session_state.msgs[ukey] = ("err", f"Error: {result}")
                    st.rerun()

            # Mensaje de feedback
            if ukey in st.session_state.msgs:
                tipo, txt = st.session_state.msgs[ukey]
                css = "msg-ok" if tipo == "ok" else "msg-err"
                icon = "&#10003;" if tipo == "ok" else "&#9888;"
                st.markdown(
                    f'<div class="msg {css}">{icon} {txt}</div>',
                    unsafe_allow_html=True,
                )
