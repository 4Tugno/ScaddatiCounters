import streamlit as st
import re
import zipfile
import pandas as pd

# Titolo e intestazione
st.title("Estrattore di 💩 e Statistiche Chat")
st.write("Carica il file `.zip` esportato da WhatsApp. Il sistema applicherà il tuo algoritmo per calcolare i punteggi!")

st.write("") # <--- Riga vuota per distanziare
st.divider()

# --- SEZIONE IMPOSTAZIONI ---
st.header("⚙️ Impostazioni")
st.write("") # <--- Riga vuota per distanziare

st.write("**1. Partecipanti alla chat**")

# Creiamo 2 colonne per disporre i 6 input in modo ordinato e spazioso
col1, col2 = st.columns(2)

with col1:
    nome1 = st.text_input("Partecipante 1", value="Sofiapia")
    nome2 = st.text_input("Partecipante 2", value="Danilo Fortugno")
    nome3 = st.text_input("Partecipante 3", value="Demetrio Schedine")

with col2:
    nome4 = st.text_input("Partecipante 4", value="Cristian Assumma")
    nome5 = st.text_input("Partecipante 5", value="Arianna")
    nome6 = st.text_input("Partecipante 6", value="Andre💜")

# Raccogliamo i nomi in una lista pulita (ignorando eventuali campi lasciati vuoti)
lista_nomi_grezza = [nome1, nome2, nome3, nome4, nome5, nome6]
lista_nomi = [nome.strip() for nome in lista_nomi_grezza if nome.strip()]

st.write("") # <--- Riga vuota per distanziare
st.write("") # <--- Un'altra riga vuota

st.write("**2. Regole di Conteggio**")
# Variabile booleana contaTutto_Var
contaTutto_Var = st.checkbox("Modalità 'Conta Tutto' (ignora il mese e conta solo il totale)", value=False)

# Variabile mese_da_contare
mese_da_contare = 1
if not contaTutto_Var:
    mese_da_contare = st.number_input("Inserisci il numero del mese da analizzare (1-12):", min_value=1, max_value=12, value=1)

st.write("") # <--- Riga vuota per distanziare
st.divider()

# --- SEZIONE CARICAMENTO E ANALISI ---
st.write("**3. Avvia l'Analisi**")
file_zip_caricato = st.file_uploader("Carica il file ZIP della chat", type=["zip"])

if file_zip_caricato is not None:
    if len(lista_nomi) == 0:
         st.error("⚠️ Inserisci almeno un nome nella sezione Impostazioni prima di continuare!")
    else:
        # Creiamo i dizionari dinamicamente in base ai nomi inseriti
        contatore = {nome: [0, 0.0] for nome in lista_nomi}
        contaTutto = {nome: 0 for nome in lista_nomi}

        # Apriamo lo zip in memoria
        with zipfile.ZipFile(file_zip_caricato) as z:
            nome_file_txt = None
            for nome in z.namelist():
                if nome.endswith('.txt'):
                    nome_file_txt = nome
                    break
            
            if nome_file_txt:
                st.success(f"📂 Chat trovata: **{nome_file_txt}**")
                
                # Leggiamo il contenuto e lo dividiamo in righe
                with z.open(nome_file_txt) as f:
                    contenuto = f.read().decode("utf-8")
                    lines = contenuto.splitlines()
                
                # --- LOGICA DI ESTRAZIONE ---
                for line in lines:
                    if "💩" in line:
                        for key in contaTutto.keys():
                            if contaTutto_Var:
                                if key in line:
                                    contaTutto[key] += 1
                            else:
                                data_full = line.split(",")
                                if len(data_full) > 0 and "/" in data_full[0]:
                                    data_mese = data_full[0].split("/")

                                    if len(data_mese) > 1:
                                        try:
                                            mese = int(data_mese[1])
                                        except ValueError:
                                            continue # Salta se il mese non è un numero valido

                                        if mese == mese_da_contare:
                                            if key in line: 
                                                if "💩" in line: 
                                                    try:
                                                        consistenza_line = line.split("💩")[1] 
                                                        consistenza = re.findall(r'\d+(?:[.,]\d+)?', consistenza_line) 
                                                        
                                                        if consistenza: 
                                                            consistenza_number = consistenza[0].replace(",", ".") 
                                                            contatore[key][0] += 1
                                                            contatore[key][1] += float(consistenza_number)
                                                    except Exception:
                                                        pass 
                
                # --- SEZIONE RISULTATI ---
                st.write("") # <--- Spazio prima dei risultati
                st.header("📊 Risultati")
                
                if contaTutto_Var:
                    st.info("Risultati della modalità **Conta Tutto**")
                    df_totale = pd.DataFrame(list(contaTutto.items()), columns=["Nome", "Totale Volte"])
                    st.dataframe(df_totale, use_container_width=True)
                else:
                    st.info(f"Risultati per il **Mese {mese_da_contare}**")
                    dati_tabella = []
                    for nome, valori in contatore.items():
                        dati_tabella.append({
                            "Nome": nome,
                            "Conteggio Volte": valori[0],
                            "Consistenza Totale (Somma)": round(valori[1], 2)
                        })
                    df_mese = pd.DataFrame(dati_tabella)
                    st.dataframe(df_mese, use_container_width=True)

            else:
                st.error("Nessun file di testo (.txt) trovato all'interno dello zip!")
