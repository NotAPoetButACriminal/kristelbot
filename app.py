import streamlit as st
from docxtpl import DocxTemplate
import io
import uuid
from datetime import datetime

# --- INITIALIZE SESSION STATE ---
if "varijante" not in st.session_state:
    st.session_state.varijante = []

if "literatura" not in st.session_state:
    st.session_state.literatura = [
        {
            "id": str(uuid.uuid4()),
            "tekst": "Richards et al. Standards and guidelines for the interpretation of sequence variants: a joint consensus recommendation of the American College of Medical Genetics and Genomics and the Association for Molecular Pathology. Genetics in Medicine 2015."
        },
        {
            "id": str(uuid.uuid4()),
            "tekst": "https://varsome.com"
        }
    ]

# Config
analysis_config = {
    "WRFZO": {
        "naziv": "Sekvenciranje celog egzoma",
        "sifra": "039",
        "geni": "svih",
        "panel": "Exome 2.0 (Illumina)",
        "ograda": "",
        "instrument": "NextSeq 2000 (Illumina)"
        
    },
    "pWES": {
        "naziv": "Sekvenciranje celog egzoma",
        "sifra": "040",
        "geni": "svih",
        "panel": "Exome 2.0 (Illumina)",
        "ograda": "",
        "instrument": "NextSeq 2000 (Illumina)"
        
    },
    "RFZO": {
        "naziv": "Sekvenciranje kliničkog egzoma",
        "sifra": "037",
        "geni": "4813 klinički relevantnih",
        "panel": "TruSight One (Illumina)",
        "ograda": "Geni koji se ne nalaze na TSO panelu nisu analizirani. ",
        "instrument": "NextSeq 550 (Illumina)"
        
    },
    "SOVO": {
        "naziv": "Sekvenciranje kliničkog egzoma",
        "sifra": "037-SOVO",
        "geni": "4813 klinički relevantnih",
        "panel": "TruSight One (Illumina)",
        "ograda": "Geni koji se ne nalaze na TSO panelu nisu analizirani. ",
        "instrument": "NextSeq 550 (Illumina)"
    },
    "NGS": {
        "naziv": "Sekvenciranje kliničkog egzoma",
        "sifra": "018",
        "geni": "4813 klinički relevantnih",
        "panel": "TruSight One (Illumina)",
        "ograda": "Geni koji se ne nalaze na TSO panelu nisu analizirani. ",
        "instrument": "NextSeq 550 (Illumina)"
    }
}

ACMG_criteria = {
    "PM5_Moderate": "Varijanta se nalazi u kodonu u kojem je prethodno prijavljena patogena missense varijanta (PM5_Moderate).",
    "PM2_Supporting": "Varijanta je nađena sa niskom učestalošću u GnomAD Exomes i GnomAD Genomes populacionim bazama podataka (PM2_Supporting).",
    "PP2_Supporting": "Varijanta se nalazi u genu u kojem su missense variajnte čest uzrok bolesti (PP2_Supporting),",
    "BP4_Supporting": "međutim, kompjuterski prediktivni skorovi idu u prilog njenoj benignosti (BP4_Supporting)."
}

st.set_page_config(page_title="IMGGI Report Generator", layout="centered")
st.title("RFZO Genetički Izveštaj")

# Block 1
with st.container(border=True):
    st.subheader("📋 Opšti Podaci")

    datum = st.date_input("Datum izveštaja", format="DD.MM.YYYY", min_value=datetime(1900, 1, 1))
    ustanova = ustanova_opcija = st.selectbox("Ustanova", ["Institut za zdravstvenu zaštitu majke i deteta Srbije „Dr Vukan Čupić“",
                                                        "Univerzitetska dečja klinika",
                                                        "drugo"])
    if ustanova_opcija == "drugo":
        ustanova = st.text_input("Druga ustanova")
    else:
        ustanova = ustanova_opcija
    lekari = st.text_input("Lekari (koji upućuju)")

# Block 2
with st.container(border=True):
    st.subheader("🧪 Podaci o uzorku")

    col1, col2 = st.columns(2)

    with col1:
        analiza_vrsta = st.selectbox("Vrsta analize", options=list(analysis_config.keys()))
        uzorak_opcija = st.selectbox("Tip uzorka", ["periferna krv", "izolovana DNK", "koštana srž", "amnionska tečnost", "horionske čupice","drugo"])
        if uzorak_opcija == "drugo":
            pacijent_uzorak = st.text_input("Unesite tip uzorka")
        else:
            pacijent_uzorak = uzorak_opcija
        ima_eksterni = st.checkbox("Eksterni broj uzorka")
        if ima_eksterni:
            pacijent_eksterni = st.text_input("")
            if not pacijent_eksterni:
                pacijent_eksterni = "-"
        else:
            pacijent_eksterni = "-"

    with col2:
        pacijent_broj = st.text_input("Broj pacijenta (za izveštaj i uzorak)")
        pacijent_prijem = st.date_input("Datum prijema uzorka", value=None, format="DD.MM.YYYY", min_value=datetime(1900, 1, 1))

    analiza_naziv = analysis_config[analiza_vrsta]["naziv"]
    analiza_sifra = analysis_config[analiza_vrsta]["sifra"]
    analiza_geni = analysis_config[analiza_vrsta]["geni"]
    analiza_panel = analysis_config[analiza_vrsta]["panel"]
    CES_ograda = analysis_config[analiza_vrsta]["ograda"]
    analiza_instrument = analysis_config[analiza_vrsta]["instrument"]
    analiza_kod = analiza_vrsta

# Block 3
with st.container(border=True):
    st.subheader("🪪 Podaci o pacijentu")
    col3, col4 = st.columns(2)

    with col3:
        pacijent_ime = st.text_input("Ime i prezime pacijenta")
        pacijent_pol = st.selectbox("Pol", ["ženski", "muški"])
        
    with col4:
        pacijent_ime_genitiv = st.text_input("Ime i prezime u Genitivu - npr. 'Jelene Jović'")
        pacijent_datum = st.date_input("Datum rođenja", value=None, format="DD.MM.YYYY", min_value=datetime(1900, 1, 1))

    pacijent_dijagnoza = st.text_input("Dijagnoza")

    HPO = st.text_input("Analizirani HPO termini (npr. Flexion contracture HP:0001371, Multiple joint contractures HP:0002828,)")


# Block 4
with st.container(border=True):
    st.subheader("🧬 Rezultat")
    rezultat_rezultat = st.selectbox("Rezultat", ["NEGATIVAN", "POZITIVAN", "NEODREĐEN"])
    segregaciona = st.checkbox("Neophodna segregaciona analiza")

    for i, varijanta in enumerate(st.session_state.varijante):
        vid = varijanta.setdefault("id", str(uuid.uuid4()))

        with st.expander(f"Varijanta {i+1}:", expanded=True):
            v_col1, v_col2, v_col3 = st.columns(3)
            
            with v_col1:
                varijanta["gen"] = st.text_input("Gen", key=f"gen_{vid}")
                varijanta["klasa"] = st.selectbox("Klasa",
                                                  ["patogena varijanta (klasa 1)",
                                                   "verovatno patogena varijanta (klasa 2)",
                                                   "varijanta neodređenog značaja (klasa 3)",
                                                   "verovatno benigna varijanta (klasa 4)",
                                                   "benigna varijanta (klasa 5)"],
                                                  key=f"class_{vid}")
                varijanta["hromozom"] = st.text_input("Hromozom", key=f"chr_{vid}")
                varijanta["gnomadE"] = st.text_input("GnomAD Exomes (%)", value="0.00", key=f"gnE_{vid}")

            with v_col2:
                varijanta["transkript"] = st.text_input("Transkript", key=f"trans_{vid}")
                varijanta["zigotnost"] = st.selectbox("Zigotnost",
                                                      ["heterozigot",
                                                       "homozigot",
                                                       "hemizigot"],
                                                       key=f"zig_{vid}")
                varijanta["egzon"] = st.text_input("Egzon (npr. 4/6)", key=f"ex_{vid}")
                varijanta["gnomadG"] = st.text_input("GnomAD Genomes (%)", value="0.00", key=f"gnG_{vid}")

            with v_col3:
                varijanta["HGVS"] = st.text_input("HGVS (npr. c.123A>G)", key=f"hgvs_{vid}")
                varijanta["tip"] = st.text_input("Tip (npr. Missense)", key=f"tip_{vid}")
                varijanta["skor"] = st.text_input("MetaRNN skor", key=f"score_{vid}")
            
            varijanta["bolest"] = st.text_input("Patogene varijante u genu asocirane su sa: npr. 'urođenom arahnodaktilijom (engl. Arachnodactyly, congenital)'", key=f"dis_{vid}")
            varijanta["model"] = st.selectbox("Model nasleđivanja",
                                              ["autozomno dominantno",
                                               "autozomno recesivno",
                                               "autozomno dominantno ili autozomno recesivno"], key=f"mod_{vid}")
            
            st.divider()
            criteria = st.multiselect(
                "Izaberite ACMG kriterijume:", 
                list(ACMG_criteria.keys()),
                key=f"ms_{vid}"
            )

            sentences = []
            for criterium in criteria:
                varijanta[f"sentence_{criterium}"] = st.text_area(f"{criterium}",
                                                                  value=varijanta.get(f"sentence_{criterium}", ACMG_criteria[criterium]),
                                                                  key=f"{criterium}_{vid}"
                )
                sentences.append(varijanta[f"sentence_{criterium}"])
            
            varijanta["acmg_oznake"] = ", ".join(criteria)
            varijanta["acmg_recenice"] = " ".join(sentences)
            st.divider()


            
            if st.button(f"🗑️ Ukloni varijantu {i+1}", key=f"remove_{vid}"):
                st.session_state.varijante.pop(i)
                st.rerun()

    if st.button("➕ Dodaj novu varijantu"):
        st.session_state.varijante.append({"id": str(uuid.uuid4())})
        st.rerun()

# Block 5
with st.container(border=True):
    st.subheader("📚 Literatura")

    for i, ref in enumerate(st.session_state.literatura):
        lid = ref.setdefault("id", str(uuid.uuid4()))

        l_col1, l_col2 = st.columns([9, 1]) 
        
        with l_col1:
            ref["tekst"] = st.text_area(f"Referenca {i+1}", value=ref.get("tekst", ""), key=f"lit_{lid}")
            
        with l_col2:
            st.write("") # Spacing to align with the text box
            st.write("")
            if st.button("🗑️", key=f"del_lit_{lid}", use_container_width=True):
                st.session_state.literatura.pop(i)
                st.rerun()

    if st.button("➕ Dodaj referencu"):
        st.session_state.literatura.append({"id": str(uuid.uuid4())})
        st.rerun()

# Block 6
with st.container(border=True):
    st.subheader("✍️ Analizator")
    analizator = st.selectbox("analizator", ["Kris", "Vlada", "Niko"], label_visibility="collapsed")

# Report Generation

if st.button("📄 Generiši Izveštaj", type="primary"):
    missing_fields = []
    if not ustanova: missing_fields.append("Ustanova")
    if not lekari: missing_fields.append("Lekari (koji upućuju)")
    if not pacijent_broj: missing_fields.append("Broj pacijenta")
    if not pacijent_ime: missing_fields.append("Ime i prezime pacijenta")
    if not pacijent_ime_genitiv: missing_fields.append("Ime i prezime (Genitiv)")
    if not pacijent_datum: missing_fields.append("Datum rođenja")
    if not pacijent_dijagnoza: missing_fields.append("Sumnja na dijagnozu")
    if ima_eksterni and not pacijent_eksterni: 
        missing_fields.append("Eksterni broj uzorka (označili ste da ga unosite)")
    if uzorak_opcija == "Drugo" and not pacijent_uzorak:
        missing_fields.append("Unesite tip uzorka (označili ste opciju 'Drugo')")
    if not HPO: missing_fields.append("HPO termini")
    if rezultat_rezultat in ["POZITIVAN", "NEODREĐEN"] and len(st.session_state.varijante) == 0:
        missing_fields.append("Barem jedna varijanta (jer je rezultat POZITIVAN ili NEODREĐEN)")
    # Check every field inside every added variant
    for i, var in enumerate(st.session_state.varijante):
        if not var.get("gen", ""): missing_fields.append(f"Gen (Varijanta {i+1})")
        if not var.get("hromozom", ""): missing_fields.append(f"Hromozom (Varijanta {i+1})")
        if not var.get("HGVS", ""): missing_fields.append(f"HGVS (Varijanta {i+1})")
        if not var.get("transkript", ""): missing_fields.append(f"Transkript (Varijanta {i+1})")
        if not var.get("egzon", ""): missing_fields.append(f"Egzon (Varijanta {i+1})")
        if not var.get("tip", ""): missing_fields.append(f"Tip varijante (Varijanta {i+1})")
        if not var.get("model", ""): missing_fields.append(f"Model nasleđivanja (Varijanta {i+1})")
        if not var.get("bolest", ""): missing_fields.append(f"Asocirana bolest (Varijanta {i+1})")
        if not var.get("skor", ""): missing_fields.append(f"In silico skor (Varijanta {i+1})")
        if not str(var.get("gnomadE", "")): missing_fields.append(f"GnomAD Exomes (Varijanta {i+1})")
        if not str(var.get("gnomadG", "")): missing_fields.append(f"GnomAD Genomes (Varijanta {i+1})")

    if len(missing_fields) > 0:
        error_msg = "**Ne možete generisati izveštaj. Molimo popunite sledeća polja:**\n"
        for field in missing_fields:
            error_msg += f"- {field}\n"
        st.error(error_msg)

    else:
        try:
            doc = DocxTemplate("izveštaj_template.docx")
            context = {
                "datum": datum.strftime("%d.%m.%Y."),
                "ustanova": ustanova,
                "lekari": lekari,
                "analiza_naziv": analiza_naziv,
                "analiza_sifra": analiza_sifra,
                "pacijent_broj": pacijent_broj,
                "analiza_kod": analiza_kod,
                "pacijent_eksterni": pacijent_eksterni,
                "pacijent_prijem": pacijent_prijem.strftime("%d.%m.%Y."),
                "pacijent_uzorak": pacijent_uzorak,
                "pacijent_ime": pacijent_ime,
                "pacijent_datum": pacijent_datum.strftime("%d.%m.%Y."),
                "pacijent_pol": pacijent_pol,
                "pacijent_dijagnoza": pacijent_dijagnoza,
                "analiza_geni": analiza_geni,
                "analiza_panel": analiza_panel,
                "HPO": HPO,
                "CES_ograda": CES_ograda,
                "rezultat_rezultat": rezultat_rezultat,
                "segregaciona": segregaciona,
                "pacijent_ime_genitiv": pacijent_ime_genitiv,
                "varijante": st.session_state.varijante,
                "analizator": analizator,
                "literatura": st.session_state.literatura,
                "analiza_instrument": analiza_instrument
            }

            doc.render(context)
            
            bio = io.BytesIO()
            doc.save(bio)
            
            st.success("Izveštaj je uspešno generisan!")
            st.download_button(
                label="⬇️ Preuzmi .docx",
                data=bio.getvalue(),
                file_name=f"Izveštaj {analiza_kod} I-01-{analiza_sifra}-{pacijent_broj}_{pacijent_ime}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except Exception as e:
            st.error(f"Došlo je do greške: {e}")
