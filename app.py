import os
import re
import time
from datetime import date, datetime
from io import BytesIO

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

st.set_page_config(page_title="KINSHAS'Art — WENZE", page_icon="📷", layout="wide")

SHEET_ID = st.secrets.get("SHEET_ID", "1xfePFn23hxdth7sGEjC7p1wx4dntKQG0sDsrft1AMH8")
PHOTO_FOLDER_ID = st.secrets.get("PHOTO_FOLDER_ID", "1hc4849GOXleDwAVh3Hf0kAsX76B-EZ1I")
ID_FOLDER_ID = st.secrets.get("ID_FOLDER_ID", "1X5iL0qCcusj9VQNiF0_UuiCkXsIbsqyk")
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "")
JURY_PASSWORD = st.secrets.get("JURY_PASSWORD", "")

COMMUNES = ["Gombe","Kintambo","Ngaliema","Lingwala","Barumbu","Kinshasa","Mont-Ngafula","Kalamu","Kasa-Vubu","Bumbu","Makala","Ngiri-Ngiri","Selembao","Bandalungwa","Lemba","Matete","Ngaba","Kisenso","Limete","Masina","Ndjili","Kimbanseke","Nsele","Maluku"]

st.markdown("""
<style>
:root { --wine:#7a1826; --gold:#d4a94f; --ink:#1f1c1d; --cream:#faf7f1; }
.stApp { background: linear-gradient(180deg,#fff 0%,#faf7f1 100%); color:var(--ink); }
.block-container { max-width:1180px; padding-top:1.3rem; }
.hero { padding:3.1rem 2.5rem; border-radius:26px; background:linear-gradient(120deg,#5f101c,#8c2333); color:white; box-shadow:0 18px 50px rgba(76,12,24,.16); margin-bottom:1.3rem; }
.hero .eyebrow { letter-spacing:.18em; font-size:.78rem; font-weight:700; color:#f2d999; }
.hero h1 { font-size:3.4rem; margin:.25rem 0 .2rem; line-height:1; }
.hero p { max-width:760px; font-size:1.08rem; opacity:.94; }
.pill { display:inline-block; margin-top:.7rem; padding:.45rem .8rem; border:1px solid rgba(255,255,255,.35); border-radius:999px; }
.card { background:#fff; border:1px solid #eee7dd; border-radius:20px; padding:1.3rem; box-shadow:0 8px 28px rgba(42,32,25,.05); height:100%; }
.card h3 { color:var(--wine); margin-top:0; }
.small { color:#6e6661; font-size:.92rem; }
div.stButton > button, div.stFormSubmitButton > button { background:#7a1826; color:white; border:0; border-radius:12px; font-weight:700; padding:.65rem 1rem; }
div.stButton > button:hover, div.stFormSubmitButton > button:hover { background:#64121e; color:white; }
[data-testid="stMetric"] { background:#fff; border:1px solid #eee7dd; padding:1rem; border-radius:16px; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def google_clients():
    info = dict(st.secrets["gcp_service_account"])
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(info, scopes=scopes)
    gc = gspread.authorize(creds)
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)
    return gc, drive

def ws(name):
    gc, _ = google_clients()
    return gc.open_by_key(SHEET_ID).worksheet(name)

def upload_to_drive(uploaded_file, folder_id, filename):
    _, drive = google_clients()
    data = BytesIO(uploaded_file.getvalue())
    media = MediaIoBaseUpload(data, mimetype=uploaded_file.type or "application/octet-stream", resumable=False)
    f = drive.files().create(body={"name": filename, "parents": [folder_id]}, media_body=media, fields="id,webViewLink").execute()
    return f.get("webViewLink", f"https://drive.google.com/open?id={f['id']}")

def age_on(dob, ref=None):
    ref = ref or date.today()
    return ref.year - dob.year - ((ref.month, ref.day) < (dob.month, dob.day))

def next_candidate_id(admin):
    # ID is written as a literal value, never a formula. Re-check immediately before append.
    ids = admin.col_values(1)[1:]
    nums = []
    for value in ids:
        m = re.fullmatch(r"MSN-(\d+)", str(value).strip())
        if m: nums.append(int(m.group(1)))
    return f"MSN-{(max(nums, default=0)+1):04d}"

def authenticate(kind):
    key = "ADMIN_PASSWORD" if kind == "Admin" else "JURY_PASSWORD"
    expected = ADMIN_PASSWORD if kind == "Admin" else JURY_PASSWORD
    if not expected:
        st.warning(f"Configure {key} dans les secrets Streamlit avant d'ouvrir cet espace.")
        return False
    entered = st.text_input(f"Mot de passe {kind}", type="password", key=f"pwd_{kind}")
    return entered == expected

st.markdown("""<section class="hero"><div class="eyebrow">KINSHAS'ART À TRAVERS NOS YEUX</div><h1>WENZE</h1><p>Le marché vu par celles et ceux qui font Kinshasa. Une photographie, un regard, une histoire.</p><span class="pill">Concours photo • Kinshasa • 18–25 ans</span></section>""", unsafe_allow_html=True)

page = st.sidebar.radio("Navigation", ["Accueil", "Participer", "Règlement", "Jury", "Administration"])

if page == "Accueil":
    c1,c2,c3 = st.columns(3)
    with c1: st.markdown('<div class="card"><h3>01 — Observer</h3><p>Choisis une scène réelle dans un marché municipal de Kinshasa.</p></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="card"><h3>02 — Photographier</h3><p>Propose une seule image originale qui raconte WENZE à travers ton regard.</p></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="card"><h3>03 — Participer</h3><p>Complète ton dossier et reçois ton identifiant candidat permanent.</p></div>', unsafe_allow_html=True)
    st.subheader("La présélection")
    st.write("Les photographies conformes sont évaluées sur 100 points : interprétation du thème, créativité, composition et maîtrise technique. Les 50 meilleures passent à l’étape suivante.")

elif page == "Participer":
    st.header("Déposer ma candidature")
    st.caption("Les données d’identité restent réservées à l’administration et ne sont pas affichées au jury.")
    with st.form("candidature", clear_on_submit=False):
        a,b = st.columns(2)
        nom = a.text_input("Nom *")
        prenom = b.text_input("Prénom *")
        a,b = st.columns(2)
        tel = a.text_input("Téléphone WhatsApp *", placeholder="+243 …")
        email = b.text_input("E-mail")
        a,b = st.columns(2)
        dob = a.date_input("Date de naissance *", min_value=date(1990,1,1), max_value=date.today(), value=date(2005,1,1))
        commune = b.selectbox("Commune *", ["— Sélectionner —"] + COMMUNES)
        st.markdown("#### Fichiers")
        piece = st.file_uploader("Pièce d’identité *", type=["jpg","jpeg","png","pdf"])
        photo = st.file_uploader("Photo du concours * — JPG/JPEG uniquement", type=["jpg","jpeg"])
        appareil = st.checkbox("Je confirme que la photo a été réalisée avec un appareil photo professionnel ou semi-professionnel.")
        original = st.checkbox("Je certifie être l’auteur de cette photo; elle n’est ni générée par IA, ni récupérée sur Internet, ni réalisée par autrui.")
        marche = st.checkbox("Je confirme que la photo a été réalisée dans un marché municipal de Kinshasa et respecte le thème WENZE.")
        retouche = st.checkbox("Je confirme que les éventuelles retouches ne dénaturent pas la scène.")
        engagements = st.checkbox("Je certifie avoir entre 18 et 25 ans, résider à Kinshasa, accepter le règlement et autoriser l’utilisation de ma photo pour la communication et l’exposition avec mention de mon nom.")
        submit = st.form_submit_button("Envoyer ma candidature", use_container_width=True)

    if submit:
        errors=[]
        if not nom.strip() or not prenom.strip() or not tel.strip(): errors.append("Nom, prénom et WhatsApp sont obligatoires.")
        if commune == "— Sélectionner —": errors.append("Sélectionne ta commune.")
        if not (18 <= age_on(dob) <= 25): errors.append("L’âge doit être compris entre 18 et 25 ans.")
        if not piece or not photo: errors.append("La pièce d’identité et la photo sont obligatoires.")
        if not all([appareil, original, marche, retouche, engagements]): errors.append("Toutes les confirmations du règlement doivent être cochées.")
        if errors:
            for e in errors: st.error(e)
        else:
            try:
                admin = ws("Administration")
                candidate_id = next_candidate_id(admin)
                safe = re.sub(r"[^A-Za-z0-9_-]+", "_", f"{candidate_id}_{nom}_{prenom}")
                photo_url = upload_to_drive(photo, PHOTO_FOLDER_ID, f"{safe}_PHOTO.{photo.name.split('.')[-1].lower()}")
                piece_url = upload_to_drive(piece, ID_FOLDER_ID, f"{safe}_IDENTITE.{piece.name.split('.')[-1].lower()}")
                row = [candidate_id, datetime.now().strftime("%d/%m/%Y %H:%M:%S"), nom.strip(), prenom.strip(), tel.strip(), email.strip(), dob.strftime("%d/%m/%Y"), commune, piece_url, "Acceptés via Streamlit", photo_url, "À vérifier", "", "À vérifier", "À évaluer", "En attente", "Candidature Streamlit"]
                admin.append_row(row, value_input_option="USER_ENTERED")
                st.success("Candidature enregistrée avec succès.")
                st.markdown(f"### Ton identifiant candidat : `{candidate_id}`")
                st.info("Conserve cet identifiant. Il est définitif et servira pour le suivi de ta candidature.")
            except Exception as e:
                st.error("L’enregistrement n’a pas pu être finalisé. Réessaie ou contacte l’organisation.")
                st.caption(f"Détail technique : {e}")

elif page == "Règlement":
    st.header("Règlement photo — WENZE")
    st.markdown("""
- Une seule photographie par candidat.
- Appareil photo professionnel ou semi-professionnel obligatoire.
- Format JPG ou JPEG.
- Photo originale réalisée par le candidat : aucune image générée par IA, récupérée sur Internet ou réalisée par autrui.
- Les retouches sont autorisées uniquement si elles ne dénaturent pas la scène.
- La photographie doit être réalisée dans un marché municipal de Kinshasa et respecter le thème **WENZE**.

### Grille de présélection — 100 points
| Critère | Points |
|---|---:|
| Regard et interprétation du thème | 25 |
| Créativité & originalité | 25 |
| Composition & cadrage | 25 |
| Maîtrise technique | 25 |

Les **50 meilleures photographies** passent à la deuxième étape.
""")

elif page == "Jury":
    st.header("Espace Jury")
    st.caption("Espace anonymisé : le jury travaille uniquement avec l’ID candidat et la photographie.")
    if authenticate("Jury"):
        admin = ws("Administration")
        rows = admin.get_all_records()
        eligible = [r for r in rows if str(r.get("Admissibilité","")).strip()=="Admissible"]
        if not eligible:
            st.info("Aucune photographie admissible n’est encore disponible.")
        else:
            ids=[r["ID candidat"] for r in eligible]
            cid=st.selectbox("ID candidat", ids)
            cand=next(r for r in eligible if r["ID candidat"]==cid)
            st.markdown(f"**Photo :** {cand.get('Photo du concours','')}")
            jure=st.text_input("Nom / code du juré")
            cols=st.columns(4)
            scores=[cols[0].number_input("Thème /25",0,25,0),cols[1].number_input("Créativité /25",0,25,0),cols[2].number_input("Composition /25",0,25,0),cols[3].number_input("Technique /25",0,25,0)]
            st.metric("Total", f"{sum(scores)}/100")
            comment=st.text_area("Commentaire")
            if st.button("Enregistrer l’évaluation"):
                if not jure.strip(): st.error("Indique le juré.")
                else:
                    ws("Évaluation jury").append_row([cid,cand.get("Photo du concours",""),jure.strip(),*scores,sum(scores),comment], value_input_option="USER_ENTERED")
                    st.success("Évaluation enregistrée.")

elif page == "Administration":
    st.header("Administration")
    if authenticate("Admin"):
        admin=ws("Administration")
        rows=admin.get_all_records()
        total=len([r for r in rows if r.get("ID candidat")])
        admissibles=sum(str(r.get("Admissibilité","")).strip()=="Admissible" for r in rows)
        a,b,c=st.columns(3)
        a.metric("Candidatures", total); b.metric("Admissibles", admissibles); c.metric("À vérifier", max(total-admissibles,0))
        st.dataframe(rows, use_container_width=True, hide_index=True)
        st.warning("Les pièces d’identité sont des données confidentielles. Ne partage pas cet espace avec le jury.")
