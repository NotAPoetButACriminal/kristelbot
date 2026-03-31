import streamlit as st
from docxtpl import DocxTemplate
import io
import uuid
import json
import os
from datetime import datetime
from ACMG_criteria import ACMG_criteria
from HPO import HPO
from analysis_config import analysis_config

st.set_page_config(page_title="IMGGI Report Generator", layout="centered")

### Login ###

if not st.session_state.get("loggedin", False):
    st.title("RFZO Izveštaj Generator")
    with st.form("login"):
        username = st.text_input("Email:",
                                 autocomplete = "username")
        password = st.text_input("Password:",
                                 type="password",
                                 autocomplete ="current-password")
        login = st.form_submit_button("Log in", use_container_width=True)
        if login:
            if username in st.secrets["email"] and st.secrets["email"][username]["password"] == password:
                st.session_state["loggedin"] = True
                st.session_state["username"] = username
                st.session_state["puno_ime"] = st.secrets["email"][username]["puno_ime"]
                st.rerun()
            else:
                st.error("Wrong username or password")
    st.stop()

### Initialize ###

if "varijante" not in st.session_state:
    st.session_state.varijante = []

if "cnvovi" not in st.session_state:
    st.session_state.cnvovi = []

if "literatura" not in st.session_state:
    st.session_state.literatura = [
        {
            "id": str(uuid.uuid4()),
            "tekst": "Richards et al. Standards and guidelines for the interpretation of sequence variants: a joint consensus recommendation of the American College of Medical Genetics and Genomics and the Association for Molecular Pathology. Genetics in Medicine 2015."
        },
        {
            "id": str(uuid.uuid4()),
            "tekst": "Online Mendelian Inheritance in Man, OMIM®, world wide web url: http://omim.org/,” McKusick-Nathans Institute of Genetic Medicine, Johns Hopkins University (Baltimore, MD)"
        },
        {
            "id": str(uuid.uuid4()),
            "tekst": "https://www.orpha.net"
        },
        {
            "id": str(uuid.uuid4()),
            "tekst": "https://varsome.com"
        },
        {
            "id": str(uuid.uuid4()),
            "tekst": "https://hpo.jax.org"
        }
    ]

obrazlozenja_json = "/data/obrazlozenja.json"
if "obrazlozenja" not in st.session_state:
    if not os.path.exists(obrazlozenja_json):
        with open(obrazlozenja_json, "w", encoding="utf-8") as f:
            json.dump({}, f)
    with open(obrazlozenja_json, "r", encoding="utf-8") as f:
        st.session_state.obrazlozenja = json.load(f)

# Block 1
st.title("RFZO Genetički Izveštaj")

with st.container(border=True):
    st.subheader("📋 Opšti Podaci")

    datum = st.date_input("Datum izveštaja:",
                          format="DD.MM.YYYY",
                          min_value=datetime(1900, 1, 1))
    
    ustanova = st.selectbox("Ustanova:",
                            ["Univerzitetska dečja klinika",
                             "Institut za zdravstvenu zaštitu majke i deteta Srbije „Dr Vukan Čupić“",
                             "UKCS - Klinika za ginekologiju i akušerstvo",
                             "UKCS - Klinika za neurologiju",
                             "UKCS - Klinika za nefrologiju",
                             "UKCS - Klinika za kardiologiju",
                             "UKCS - Klinika za očne bolesti",
                             "UKCS - Klinika za alergologiju i imunologiju"
                             "Institut za zdravstvenu zaštitu dece i omladine Vojvodine",
                             "Univerzitetski klinički centar Niš - Klinika za pedijatriju",
                             "Klinika za neurologiju i psihijatriju za decu i omladinu, Beograd",],
                            accept_new_options = True)
    
    lekari = st.text_input("Lekari:",
                           "dr Goran Čuturilo, dr Jelena Ruml Stojanović, dr Brankica Bosankić, dr Marija Mijović",
                           placeholder = "dr Slavica Ostojić, dr Jovana Beđik, dr Jelena Kojović")

# Block 2
with st.container(border=True):
    st.subheader("🧪 Podaci o uzorku")

    col1, col2 = st.columns(2)

    with col1:
        analiza_vrsta = st.selectbox("Vrsta analize:",
                                     options = list(analysis_config.keys()))
        
        uzorak_opcija = st.selectbox("Tip uzorka",
                                     ["periferna krv", "izolovana DNK", "koštana srž", "amnionska tečnost", "horionske čupice","drugo"])
        if uzorak_opcija == "drugo":
            pacijent_uzorak = st.text_input("Unesite tip uzorka")
        else:
            pacijent_uzorak = uzorak_opcija
        
        ima_eksterni = st.toggle("Eksterni broj uzorka")
        if ima_eksterni:
            pacijent_eksterni = st.text_input("Eksterni:",
                                              label_visibility="collapsed")
            if not pacijent_eksterni:
                pacijent_eksterni = "-"
        else:
            pacijent_eksterni = "-"

    with col2:
        pacijent_broj = st.text_input("Broj:", placeholder = "1127")
        
        pacijent_prijem = st.date_input("Datum prijema uzorka",
                                        value=None, format="DD.MM.YYYY",
                                        min_value=datetime(1900, 1, 1),
                                        help = "Datum može da se kuca!")

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
        pacijent_ime = st.text_input("Ime i prezime pacijenta:",
                                     placeholder = "Petar Jović")
        
        pacijent_pol = st.selectbox("Pol", ["ženski", "muški"])
        
    with col4:
        pacijent_ime_genitiv = st.text_input("Ime i prezime u Genitivu:",
                                             placeholder = "Petra Jovića",
                                             help = "Neophodno za rečenicu 'Kod pacijenta XY...'")
        
        col_datum, col_nepoznato = st.columns([5, 3])
        with col_nepoznato:
            st.space(size="small")
            datum_nepoznat = st.toggle("Prenatalna")
            
        with col_datum:
            if datum_nepoznat:
                st.text_input("Datum rođenja:", "/")
                pacijent_datum = "/"
            else:
                pacijent_datum = st.date_input("Datum rođenja:",
                                       value=None, format="DD.MM.YYYY",
                                       min_value=datetime(1900, 1, 1))
            if pacijent_datum in ["/", None, ""]:
                formatiran_datum = "/"
            else:
                formatiran_datum = pacijent_datum.strftime("%d.%m.%Y.")

    pacijent_dijagnoza = st.text_input("Dijagnoza",
                                       placeholder = "dilatativna kardiomiopatija I42.0")

    col5, col6 = st.columns([5, 1])
    with col6:
        st.space(size="small")
        rucni_unos_hpo = st.toggle("Ručni HPO",
                                   help = "Override kada želite da kopirate HPO termine od nekud")
    with col5:
        if not rucni_unos_hpo:
            HPO_termini = st.multiselect("Odaberite HPO termine:", HPO,
                                         placeholder="Type to search")
            HPO = ", ".join(HPO_termini)
        else:
            HPO = st.text_area("Analizirani HPO termini:",
                               placeholder = "Flexion contracture HP:0001371, Multiple joint contractures HP:0002828")


# Block 4
with st.container(border=True):
    st.subheader("🧬 Rezultat")
    rezultat_rezultat = st.selectbox("Rezultat", ["NEGATIVAN", "POZITIVAN", "NEODREĐEN"])

    ### SNV ###
    for i, varijanta in enumerate(st.session_state.varijante):
        vid = varijanta.setdefault("vid", str(uuid.uuid4()))

        with st.expander(f"Varijanta {i+1}:", expanded=True):
            v_col1, v_col2, v_col3 = st.columns(3)
            
            with v_col1:
                varijanta["gen"] = st.text_input("Gen:",
                                                 placeholder = "DMD, HBB, COL3A1",
                                                 key=f"gen_{vid}")
                varijanta["klasa"] = st.selectbox("Klasa:",
                                                  ["patogena varijanta (klasa 1)",
                                                   "verovatno patogena varijanta (klasa 2)",
                                                   "varijanta neodređenog značaja (klasa 3)",
                                                   "verovatno benigna varijanta (klasa 4)",
                                                   "benigna varijanta (klasa 5)"],
                                                  key=f"class_{vid}")
                varijanta["hromozom"] = st.text_input("Hromozom",
                                                      placeholder = "12",
                                                      key=f"chr_{vid}")
                varijanta["gnomadE"] = st.text_input("GnomAD Exomes (%)",
                                                     value="0.00",
                                                     key=f"gnE_{vid}")

            with v_col2:
                varijanta["transkript"] = st.text_input("Transkript:",
                                                        placeholder = "NM_123123.1",
                                                        key=f"trans_{vid}")
                varijanta["zigotnost"] = st.selectbox("Zigotnost",
                                                      ["heterozigot",
                                                       "homozigot",
                                                       "hemizigot"],
                                                       key=f"zig_{vid}")
                varijanta["egzon"] = st.text_input("Egzon / intron:",
                                                   "Egzon: ",
                                                   placeholder = "Egzon: 4/6 ili Intron: 3/18",
                                                   key=f"ex_{vid}")
                varijanta["gnomadG"] = st.text_input("GnomAD Genomes (%)",
                                                     value="0.00",
                                                     key=f"gnG_{vid}")

            with v_col3:
                varijanta["HGVS"] = st.text_input("HGVS:",
                                                  placeholder = "c.123A>G",
                                                  key=f"hgvs_{vid}")
                varijanta["tip"] = st.text_input("Tip:",
                                                 placeholder = "Missense",
                                                 key=f"tip_{vid}")
                varijanta["skor"] = st.text_input("Preditkivni skor",
                                                  "MetaRNN: ",
                                                  placeholder = "MetaRNN: 0.85 ili CADD: 27 itd.",
                                                  key=f"score_{vid}")
            
            criteria = st.multiselect(
                "Izaberite ACMG kriterijume:", 
                list(ACMG_criteria.keys()),
                placeholder="Type to search",
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
            varijanta["acmg_tekst"] = " ".join(sentences)
            
            varijanta["bolest"] = st.selectbox("Patogene varijante u genu asocirane su sa:",
                                                options = list(st.session_state.obrazlozenja.keys()),
                                                accept_new_options = True,
                                                help = "Izaberite ili iskucajte novu i kliknite Add: (ili Enter)",
                                                key = f"dis_{vid}")
            varijanta["model"] = st.selectbox("Model nasleđivanja",
                                              ["autozomno dominantno",
                                               "autozomno recesivno",
                                               "autozomno dominantno ili autozomno recesivno",
                                               "X-vezano recesivno",
                                               "X-vezano dominantno"],
                                              key=f"mod_{vid}")
            varijanta["obrazlozenje"] = st.text_area("Obrazloženje:",
                                                     placeholder = "Napišite novo obrazloženje ili ostavite prazno. Nova obrazloženja biće sačuvana kada sledeći put odaberete istu bolest.",
                                                     height = "content",
                                                     help = "Svaka bolest koja je uneta prvi put biće zapamćena zajedno sa obrazloženjem tako da sledeći put možete da je odaberete",
                                                     key=f"obr_{vid}_{varijanta["bolest"]}",
                                                     value=st.session_state.obrazlozenja.get(varijanta["bolest"], ""))
            
            if st.button(f"🗑️ Ukloni varijantu {i+1}", key=f"remove_{vid}"):
                st.session_state.varijante.pop(i)
                st.rerun()
    
    if st.button("➕ Dodaj novu varijantu"):
        st.session_state.varijante.append({"vid": str(uuid.uuid4())})
        st.rerun()
    
    ### CNV ###
    for i, cnv in enumerate(st.session_state.cnvovi):
        cid = cnv.setdefault("cid", str(uuid.uuid4()))

        with st.expander(f"CNV {i+1}:", expanded=True):
            c_col1, c_col2, c_col3 = st.columns(3)
            with c_col1:
                cnv["tip"] = st.selectbox("Tip:",
                                          ["delecija","duplikacija"],
                                          key=f"tip_{cid}")
                if cnv["tip"] == "delecija":
                    cnv["tip_mnozina"] = "delecije"
                else:
                    cnv["tip_mnozina"] = "duplikacije"
            with c_col2:
                cnv["klasa"] = st.selectbox("Klasa",
                                            ["patogena",
                                             "verovatno patogena",
                                             "neodređenog značaja",
                                             "verovatno benigna",
                                             "benigna"],
                                            key=f"class_{cid}")
            with c_col3:
                cnv["region"] = st.text_input("Region:",
                                              placeholder = "22q13.33",
                                              key=f"region_{cid}")
            c_col4, c_col5 = st.columns([2,1])
            with c_col4:
                cnv["opis"] = st.text_input("Koordinate:",
                                            placeholder = "GRCh38 Chr22: 50684335 - 50780969",
                                            key = f"opis_{cid}")
            with c_col5:
                cnv["duzina"] = st.text_input("Dužina:",
                                            placeholder = "96.6 kb",
                                            key = f"duzina_{cid}")
            cnv["geni"] = st.text_input("CNV Obuhvata:",
                                              placeholder = "11 gena; DMD gen; 31 gen uključujući i HBB; od 11. do 23. egzona DMD gena itd.",
                                              key=f"geni_{cid}")
            
            cnv["bolest"] = st.selectbox("Patogene varijante u genu asocirane su sa:",
                                                options = list(st.session_state.obrazlozenja.keys()),
                                                accept_new_options = True,
                                                help = "Izaberite ili iskucajte novu i kliknite Add: (ili Enter)",
                                                key = f"dis_{cid}")
            cnv["model"] = st.selectbox("Model nasleđivanja",
                                              ["autozomno dominantno",
                                               "autozomno recesivno",
                                               "autozomno dominantno ili autozomno recesivno",
                                               "X-vezano recesivno",
                                               "X-vezano dominantno"],
                                              key=f"mod_{cid}")
            cnv["obrazlozenje"] = st.text_area("Obrazloženje:",
                                                     placeholder = "Napišite novo obrazloženje ili ostavite prazno. Nova obrazloženja biće sačuvana kada sledeći put odaberete istu bolest.",
                                                     height = "content",
                                                     help = "Svaka bolest koja je uneta prvi put biće zapamćena zajedno sa obrazloženjem tako da sledeći put možete da je odaberete",
                                                     key=f"obr_{cid}_{cnv["bolest"]}",
                                                     value=st.session_state.obrazlozenja.get(cnv["bolest"], ""))

            if st.button(f"🗑️ Ukloni CNV {i+1}", key=f"remove_{cid}"):
                st.session_state.cnvovi.pop(i)
                st.rerun()

    if st.button("➕ Dodaj novu CNV"):
        st.session_state.cnvovi.append({"cid": str(uuid.uuid4())})
        st.rerun()

    segregaciona = st.toggle("Neophodna segregaciona analiza")
    treba_napomena = st.toggle("Napomena:",
                               help = "Preporučivanje segregacione analize ne ide u napomenu već ima poseban toggle")
    napomena = ""
    if treba_napomena:
            napomena = st.text_area("napomena",
                                    label_visibility="collapsed",
                                    height = "content",
                                    value = "Kod pacijenta je detektovana jedna patogena genetička varijanta NM_000527.5:c.343C>T (p.Arg115Cys) u genu LDLR, koja nije direktno vezana za uočeni fenotip. Patogene genetičke varijante u ovom genu asocirane su sa razvojem familijarne hiperholesterolemije (eng. Hypercholesterolemia, familial, 1) [broj citata].")

# Block 5
with st.container(border=True):
    st.subheader("📚 Literatura")

    for i, ref in enumerate(st.session_state.literatura):
        lid = ref.setdefault("lid", str(uuid.uuid4()))

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
        st.session_state.literatura.append({"lid": str(uuid.uuid4())})
        st.rerun()

# Block 6
with st.container(border=True):
    st.subheader("✍️ Analizator")
    analizator = st.text_input("analizator",
                               value = st.session_state["puno_ime"],
                               label_visibility="collapsed",
                               disabled = True)
    if st.button("Log out", use_container_width=True):
        st.session_state.clear()
        st.rerun()

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
    if rezultat_rezultat in ["POZITIVAN", "NEODREĐEN"] and len(st.session_state.varijante) == 0 and len(st.session_state.cnvovi) == 0:
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
            doc = DocxTemplate("izvestaj_template.docx")
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
                "pacijent_datum": formatiran_datum,
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
                "cnvovi": st.session_state.cnvovi,
                "treba_napomena": treba_napomena,
                "napomena" : napomena,
                "analizator": st.session_state["puno_ime"],
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

            for i, varijanta in enumerate(st.session_state.varijante):
                if varijanta["bolest"] and varijanta["obrazlozenje"] and st.session_state.obrazlozenja.get(varijanta["bolest"]) != varijanta["obrazlozenje"]:
                    st.session_state.obrazlozenja[varijanta["bolest"]] = varijanta["obrazlozenje"]
                    with open(obrazlozenja_json, "w", encoding="utf-8") as f:
                        json.dump(st.session_state.obrazlozenja, f, ensure_ascii=False, indent=4)

            for i, cnv in enumerate(st.session_state.cnvovi):
                if cnv["bolest"] and cnv["obrazlozenje"] and st.session_state.obrazlozenja.get(cnv["bolest"]) != cnv["obrazlozenje"]:
                    st.session_state.obrazlozenja[cnv["bolest"]] = cnv["obrazlozenje"]
                    with open(obrazlozenja_json, "w", encoding="utf-8") as f:
                        json.dump(st.session_state.obrazlozenja, f, ensure_ascii=False, indent=4)

        except Exception as e:
            st.error(f"Došlo je do greške: {e}")

st.write("Sve želje, bagove ili primedbe na default vrednosti prijaviti na djordje.pavlovic@imgge.bg.ac.rs")
