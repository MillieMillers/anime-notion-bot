"""
NOTION ANIME TRACKER — Streamlit App v2
Busca anime via Jikan, previsualiza portadas y agrega a Notion.

Instalar : pip install streamlit requests
Correr   : streamlit run app.py

Credenciales en .streamlit/secrets.toml:
  NOTION_TOKEN = "secret_..."
  DATABASE_ID  = "..."
"""

import streamlit as st
import requests
import json
import time

# ══════════════════════════════════════════════════════════════════
#  CONFIGURACION — credenciales via st.secrets
# ══════════════════════════════════════════════════════════════════

NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
DATABASE_ID  = st.secrets["DATABASE_ID"]

JIKAN_BASE  = "https://api.jikan.moe/v4"
NOTION_BASE = "https://api.notion.com/v1"
NOTION_VER  = "2022-06-28"

# ══════════════════════════════════════════════════════════════════
#  MAPEO DE GENEROS
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
#  ICONOS SVG — sin emojis, color via CSS var
# ══════════════════════════════════════════════════════════════════

SVG = {
    "search": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" stroke-width="2" stroke-linecap="round">
        <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
    </svg>""",

    "add": """<svg width="13" height="13" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
        <path d="M12 5v14M5 12h14"/>
    </svg>""",

    "check": """<svg width="13" height="13" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
        <path d="M20 6L9 17l-5-5"/>
    </svg>""",

    "alert": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
        <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3
                 L13.71 3.86a2 2 0 00-3.42 0z"/>
        <path d="M12 9v4M12 17h.01"/>
    </svg>""",

    "empty": """<svg width="36" height="36" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" stroke-width="1.4" stroke-linecap="round">
        <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35M8 11h6"/>
    </svg>""",

    "film": """<svg width="11" height="11" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
        <rect x="2" y="2" width="20" height="20" rx="2"/>
        <path d="M7 2v20M17 2v20M2 12h20M2 7h5M17 7h5M2 17h5M17 17h5"/>
    </svg>""",

    "star": """<svg width="9" height="9" viewBox="0 0 12 12">
        <path d="M6 1l1.3 2.7H10L7.8 5.5l.9 2.8L6 6.7 3.3 8.3l.9-2.8L2 3.7h2.7z"
              fill="#f59e0b"/>
    </svg>""",

    "notion": """<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
        <path d="M4.459 4.208c.746.606 1.026.56 2.428.466l13.215-.793c.28 0 .047-.28-.046-.326
                 L17.86 1.968c-.42-.326-.981-.7-2.055-.607L3.01 2.295c-.466.046-.56.28-.374.466
                 zm.793 3.08v13.904c0 .747.373 1.027 1.214.98l14.523-.84c.841-.046.935-.56.935-1.167
                 V6.354c0-.606-.233-.933-.748-.887l-15.177.887c-.56.047-.747.327-.747.933zm14.337.745
                 c.093.42 0 .84-.42.888l-.7.14v10.264c-.608.327-1.168.514-1.635.514-.748 0-.935-.234
                 -1.495-.933l-4.577-7.186v6.952L12.21 19s0 .84-1.168.84l-3.222.186c-.093-.186 0-.653
                 .327-.746l.84-.233V9.854L7.822 9.76c-.094-.42.14-1.026.793-1.073l3.456-.233 4.764
                 7.279v-6.44l-1.215-.14c-.093-.514.28-.887.747-.933z"/>
    </svg>""",
}

# ══════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Anime Tracker",
    page_icon="https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f4fa.png",
    layout="wide",
)

# ══════════════════════════════════════════════════════════════════
#  CSS — modo dia/noche automatico + azul rey #3E8BFF
# ══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500;600&display=swap');

/* ── Variables de color ── */
:root {
  --accent:      #3E8BFF;
  --accent-dim:  #2b6fd4;
  --accent-soft: rgba(62,139,255,0.10);
  --bg:          #f4f5f9;
  --surface:     #ffffff;
  --surface-2:   #f0f2f8;
  --border:      #e0e4f0;
  --txt-1:       #111827;
  --txt-2:       #4b5563;
  --txt-3:       #9ca3af;
  --card-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 2px 10px rgba(62,139,255,0.07);
  --card-hover:  0 6px 24px rgba(62,139,255,0.16);
  --success-bg:  #f0fdf4;
  --success-bd:  #bbf7d0;
  --success-txt: #15803d;
  --error-bg:    #fef2f2;
  --error-bd:    #fecaca;
  --error-txt:   #b91c1c;
  --done-bg:     #eff6ff;
  --done-bd:     #bfdbfe;
  --done-txt:    #1d4ed8;
}

@media (prefers-color-scheme: dark) {
  :root {
    --accent:      #5ba3ff;
    --accent-dim:  #4a8ff0;
    --accent-soft: rgba(91,163,255,0.10);
    --bg:          #111113;
    --surface:     #1c1c1f;
    --surface-2:   #242428;
    --border:      #2e2e34;
    --txt-1:       #e8e8ea;
    --txt-2:       #9ca3af;
    --txt-3:       #6b7280;
    --card-shadow: 0 1px 4px rgba(0,0,0,0.4), 0 2px 10px rgba(0,0,0,0.3);
    --card-hover:  0 6px 24px rgba(0,0,0,0.5);
    --success-bg:  #052e16;
    --success-bd:  #166534;
    --success-txt: #4ade80;
    --error-bg:    #2a0a0a;
    --error-bd:    #7f1d1d;
    --error-txt:   #f87171;
    --done-bg:     #0c1a3a;
    --done-bd:     #1e3a8a;
    --done-txt:    #93c5fd;
  }
}

/* ── Reset de Streamlit ── */
.stApp { background: var(--bg) !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 3rem !important; max-width: 1140px !important; }

/* ── Header de la app ── */
.app-header {
  padding: 1rem 0 2rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.app-header-title {
  font-family: 'Syne', sans-serif;
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--txt-1);
  letter-spacing: -0.5px;
  line-height: 1;
}

.app-header-title span { color: var(--accent); }

.app-header-sub {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.72rem;
  color: var(--txt-3);
  letter-spacing: 0.8px;
  text-transform: uppercase;
  margin-top: 4px;
}

/* ── Barra de busqueda ── */
.stTextInput > div > div > input {
  background: var(--surface) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--txt-1) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.9rem !important;
  padding: 0.7rem 1rem !important;
  transition: border-color 0.18s !important;
  box-shadow: none !important;
}

.stTextInput > div > div > input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(62,139,255,0.12) !important;
}

.stTextInput > div > div > input::placeholder { color: var(--txt-3) !important; }
.stTextInput label { display: none !important; }

/* ── Boton principal (Buscar) ── */
.stButton > button {
  background: var(--accent) !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: 10px !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 600 !important;
  font-size: 0.85rem !important;
  padding: 0.62rem 1.4rem !important;
  width: 100% !important;
  transition: background 0.15s, transform 0.1s !important;
  letter-spacing: 0.2px;
}

.stButton > button:hover {
  background: var(--accent-dim) !important;
  transform: translateY(-1px) !important;
}

/* ── Tarjeta ── */
.anime-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 13px;
  overflow: hidden;
  box-shadow: var(--card-shadow);
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
  position: relative;
}

.anime-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--card-hover);
  border-color: var(--accent);
}

.anime-card::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 2px;
  background: var(--accent);
  border-radius: 0 0 13px 13px;
  transform: scaleX(0);
  transition: transform 0.18s ease;
}
.anime-card:hover::after { transform: scaleX(1); }

/* Poster */
.card-img-wrap {
  width: 100%;
  aspect-ratio: 2/3;
  overflow: hidden;
  background: var(--accent-soft);
  position: relative;
}

.card-img-wrap img {
  width: 100%; height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.25s ease;
}
.anime-card:hover .card-img-wrap img { transform: scale(1.04); }

/* Score badge */
.score-badge {
  position: absolute;
  top: 6px; right: 6px;
  background: rgba(10,12,20,0.72);
  color: #fff;
  font-family: 'Syne', sans-serif;
  font-size: 0.62rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 5px;
  display: flex;
  align-items: center;
  gap: 3px;
  backdrop-filter: blur(4px);
}

/* Cuerpo de tarjeta */
.card-body {
  padding: 9px 10px 11px;
}

.card-title {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--txt-1);
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 5px;
  min-height: 2.1em;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 5px;
  flex-wrap: wrap;
  margin-bottom: 6px;
}

.badge-score {
  font-family: 'Syne', sans-serif;
  font-size: 0.68rem;
  font-weight: 700;
  color: #f59e0b;
  background: rgba(245,158,11,0.1);
  padding: 1px 6px;
  border-radius: 4px;
}

.badge-type {
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

.badge-year {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.6rem;
  color: var(--txt-3);
}

/* ── Mensajes de feedback ── */
.msg {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.72rem;
  font-weight: 500;
  padding: 7px 10px;
  border-radius: 7px;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 5px;
  line-height: 1.3;
}

.msg-success {
  background: var(--success-bg);
  border: 1px solid var(--success-bd);
  color: var(--success-txt);
}

.msg-error {
  background: var(--error-bg);
  border: 1px solid var(--error-bd);
  color: var(--error-txt);
}

.msg-done {
  background: var(--done-bg);
  border: 1px solid var(--done-bd);
  color: var(--done-txt);
  justify-content: center;
  font-weight: 600;
}

/* ── Seccion de resultados ── */
.results-header {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--txt-3);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.results-header span {
  color: var(--accent);
  font-weight: 700;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* ── Separador ── */
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

/* ── Boton de añadir (override del boton principal) ── */
div[data-testid="stButton"].add-action > button {
  background: var(--surface) !important;
  color: var(--accent) !important;
  border: 1px solid var(--accent) !important;
  font-size: 0.72rem !important;
  padding: 0.4rem 0.8rem !important;
  border-radius: 7px !important;
  font-weight: 600 !important;
}

div[data-testid="stButton"].add-action > button:hover {
  background: var(--accent) !important;
  color: #ffffff !important;
  transform: none !important;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  FUNCIONES — JIKAN API
# ══════════════════════════════════════════════════════════════════

@st.cache_data(ttl=300, show_spinner=False)
def search_anime(query: str) -> list[dict]:
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
    time.sleep(0.4)
    try:
        resp = requests.get(f"{JIKAN_BASE}/anime/{mal_id}/full", timeout=15)
        resp.raise_for_status()
        return resp.json().get("data", {})
    except Exception:
        return None


def clean_genres(raw: list[dict]) -> list[str]:
    seen, result = set(), []
    for g in raw:
        name   = g.get("name", "")
        mapped = GENRE_MAP.get(name, name)
        if mapped and mapped not in seen:
            result.append(mapped)
            seen.add(mapped)
    return result


def extract_anime_data(anime: dict) -> dict:
    all_genres = (
        anime.get("genres", []) + anime.get("demographics", []) +
        anime.get("themes", []) + anime.get("explicit_genres", [])
    )
    synopsis = anime.get("synopsis") or "Sin sinopsis disponible."
    synopsis = synopsis[:1997] + "..." if len(synopsis) > 2000 else synopsis
    images   = anime.get("images", {})
    jpg      = images.get("jpg", {})
    cover    = jpg.get("large_image_url") or jpg.get("image_url") or ""

    return {
        "title":    anime.get("title_english") or anime.get("title", "Sin titulo"),
        "score":    anime.get("score"),
        "genres":   clean_genres(all_genres),
        "synopsis": synopsis,
        "cover":    cover,
        "episodes": anime.get("episodes"),
        "status":   anime.get("status", ""),
        "type":     anime.get("type", ""),
        "mal_url":  anime.get("url", ""),
        "mal_id":   anime.get("mal_id"),
    }


# ══════════════════════════════════════════════════════════════════
#  FUNCIONES — NOTION API
# ══════════════════════════════════════════════════════════════════

def create_notion_page(data: dict) -> tuple[bool, str]:
    status_map = {
        "Finished Airing":  "Not Started",
        "Currently Airing": "Up Next",
        "Not yet aired":    "Up Next",
    }

    properties = {
        PROP["title"]:  {"title":        [{"text": {"content": data["title"]}}]},
        PROP["genres"]: {"multi_select": [{"name": g} for g in data["genres"]]},
    }

    if data["score"] is not None:
        properties[PROP["score"]] = {"number": data["score"]}
    if data["episodes"] is not None:
        properties[PROP["episodes"]] = {"number": data["episodes"]}

    properties[PROP["status"]] = {
        "status": {"name": status_map.get(data["status"], "Up Next")}
    }

    if data["mal_url"]:
        properties[PROP["mal_url"]] = {"url": data["mal_url"]}

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
        return True, resp.json().get("url", "")
    except requests.exceptions.HTTPError:
        return False, resp.json().get("message", "Error desconocido")
    except Exception as e:
        return False, str(e)


# ══════════════════════════════════════════════════════════════════
#  SESSION STATE — inicializar
# ══════════════════════════════════════════════════════════════════

for key, default in [
    ("results",  []),
    ("added",    set()),     # set de mal_ids ya agregados
    ("messages", {}),        # {unique_key: (tipo, texto)}
    ("query",    ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ══════════════════════════════════════════════════════════════════
#  UI — HEADER
# ══════════════════════════════════════════════════════════════════

st.markdown(f"""
<div class="app-header">
  <div>
    <div class="app-header-title">Anime <span>Tracker</span></div>
    <div class="app-header-sub">Busca · Descubre · Agrega a Notion</div>
  </div>
  <div style="color:var(--accent);opacity:0.6">{SVG["notion"]}</div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  UI — BARRA DE BUSQUEDA
# ══════════════════════════════════════════════════════════════════

col_q, col_btn = st.columns([5, 1])

with col_q:
    query = st.text_input(
        label="anime_search",
        placeholder="Busca un anime... (ej. Attack on Titan, Jujutsu Kaisen)",
        label_visibility="collapsed",
        key="search_input",
    )

with col_btn:
    search_clicked = st.button("Buscar", use_container_width=True, key="btn_search")


# ══════════════════════════════════════════════════════════════════
#  LOGICA — BUSQUEDA
# ══════════════════════════════════════════════════════════════════

if search_clicked and query.strip():
    with st.spinner("Buscando en MyAnimeList..."):
        st.session_state.results  = search_anime(query.strip())
        st.session_state.messages = {}
        st.session_state.query    = query.strip()

    if not st.session_state.results:
        st.markdown(f"""
        <div style="display:flex;flex-direction:column;align-items:center;
                    gap:10px;padding:40px 20px;color:var(--txt-3);text-align:center">
          <div style="color:var(--txt-3)">{SVG["empty"]}</div>
          <p style="font-family:'DM Sans',sans-serif;font-size:0.85rem;
                    font-weight:600;color:var(--txt-2);margin:0">Sin resultados</p>
          <p style="font-family:'DM Sans',sans-serif;font-size:0.75rem;margin:0">
            No se encontro ningun anime para <em>"{query}"</em>
          </p>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  UI — GRID DE RESULTADOS
# ══════════════════════════════════════════════════════════════════

if st.session_state.results:

    count = len(st.session_state.results)
    st.markdown(f"""
    <div class="results-header">
      Resultados para
      <span>"{st.session_state.query}"</span>
      &mdash; {count} anime{"s" if count != 1 else ""}
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(4, gap="small")

    for idx, anime in enumerate(st.session_state.results):

        mal_id   = anime.get("mal_id") or 0
        title_en = anime.get("title_english") or anime.get("title", "Sin titulo")
        score    = anime.get("score")
        year     = anime.get("year") or "?"
        atype    = anime.get("type", "")
        cover    = (anime.get("images") or {}).get("jpg", {}).get("large_image_url") or \
                   (anime.get("images") or {}).get("jpg", {}).get("image_url") or ""

        # ── CLAVE UNICA: combina indice + mal_id para evitar duplicados ──
        # Esto resuelve StreamlitDuplicateElementKey aunque el mismo anime
        # aparezca varias veces en los resultados.
        unique_key = f"{idx}_{mal_id}"

        col = cols[idx % 4]

        with col:

            # Tarjeta HTML
            score_html = f"""
              <div class="score-badge">
                {SVG["star"]}&nbsp;{score}
              </div>""" if score else ""

            img_html = (
                f'<img src="{cover}" alt="{title_en}" loading="lazy">'
                if cover else
                f'<div style="width:100%;height:100%;display:flex;align-items:center;'
                f'justify-content:center;color:var(--accent);opacity:0.25;font-size:2rem">?</div>'
            )

            score_badge_html = f"""
              <span class="badge-score">{SVG["star"]} {score}</span>
            """ if score else ""

            type_badge = f'<span class="badge-type">{atype}</span>' if atype else ""
            year_badge = f'<span class="badge-year">{year}</span>'

            st.markdown(f"""
            <div class="anime-card">
              <div class="card-img-wrap">
                {img_html}
                {score_html}
              </div>
              <div class="card-body">
                <div class="card-title">{title_en}</div>
                <div class="card-meta">
                  {score_badge_html}
                  {type_badge}
                  {year_badge}
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Estado del boton ──
            already = mal_id in st.session_state.added

            if already:
                st.markdown(f"""
                <div class="msg msg-done">
                  {SVG["check"]} En tu biblioteca
                </div>""", unsafe_allow_html=True)

            else:
                # CLAVE UNICA para el boton — evita StreamlitDuplicateElementKey
                if st.button(
                    "Añadir a Biblioteca",
                    key=f"btn_add_{unique_key}",
                    use_container_width=True,
                ):
                    with st.spinner(f"Agregando..."):
                        detail = get_anime_detail(mal_id)

                    if not detail:
                        st.session_state.messages[unique_key] = (
                            "error", "No se pudo obtener el detalle."
                        )
                    else:
                        anime_data = extract_anime_data(detail)
                        ok, result = create_notion_page(anime_data)

                        if ok:
                            st.session_state.added.add(mal_id)
                            st.session_state.messages[unique_key] = (
                                "success", "Agregado correctamente a Notion."
                            )
                        else:
                            st.session_state.messages[unique_key] = (
                                "error", f"Error: {result}"
                            )
                    st.rerun()

            # Mensaje de feedback debajo del boton
            if unique_key in st.session_state.messages:
                tipo, texto = st.session_state.messages[unique_key]
                icon = SVG["check"] if tipo == "success" else SVG["alert"]
                css  = "msg-success" if tipo == "success" else "msg-error"
                st.markdown(
                    f'<div class="msg {css}">{icon}{texto}</div>',
                    unsafe_allow_html=True,
                )

            # Separacion vertical entre filas
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
