import streamlit as st
import re
import zipfile
import pandas as pd

# Titolo e intestazione
st.title("Estrattore di 💩 e Statistiche Chat")
st.write("Carica il file `.zip` esportato da WhatsApp. Il sistema applicherà il tuo algoritmo per calcolare i punteggi!")

# --- SEZIONE IMPOSTAZIONI (I tuoi parametri) ---
st.header("⚙️ Impostazioni Algoritmo")

# Crea la variabile booleana contaTutto_Var tramite una spunta (checkbox)
contaTutto_Var = st.checkbox("Modalità 'Conta Tutto' (ignora il mese e conta solo il totale delle volte)", value=False)

# Crea la variabile mese_da_contare tramite un selettore (visibile solo se contaTutto_Var è False)
mese_da_contare = 1
if not contaTutto_Var:
    mese_da_contare = st.number_input("Inserisci il numero del mese da analizzare (1-12):", min_value=1, max_value=12, value=1)

st.divider()

# --- SEZIONE CARICAMENTO E ANALISI ---
file_zip_caricato = st.file_uploader("Carica il file ZIP della chat", type=["zip"])

if file_zip_caricato is not None:
    # Inizializza i tuoi dizionari (si resettano ad ogni nuovo caricamento)
    contatore = {
        "Sofiapia": [0, 0.0],
        "Danilo Fortugno": [0, 0.0],
        "Demetrio Schedine": [0, 0.0],
        "Cristian Assumma": [0, 0.0],
        "Arianna": [0, 0.0],
        "Andre💜": [0, 0.0]
    }

    contaTutto = {
        "Sofiapia": 0,
        "Danilo Fortugno": 0,
        "Demetrio Schedine": 0,
        "Cristian Assumma": 0,
        "Arianna": 0,
        "Andre💜": 0
    }

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
                lines = contenuto.splitlines() # Equivale al tuo f.readlines()
            
            # --- LA TUA LOGICA ORIGINALE ---
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

                                # Mese Preso
                                if len(data_mese) > 1:
                                    mese = int(data_mese[1])

                                    if mese == mese_da_contare:
                                        if key in line: # Controllo nome
                                            if "💩" in line: # Controllo presenza
                                                # Ho aggiunto un try/except per evitare blocchi se una riga finisce improvvisamente con l'emoji
                                                try:
                                                    consistenza_line = line.split("💩")[1] 
                                                    consistenza = re.findall(r'\d+(?:[.,]\d+)?', consistenza_line) 
                                                    
                                                    if consistenza: # Se ha trovato un numero
                                                        consistenza_number = consistenza[0].replace(",", ".") 
                                                        
                                                        # Aggiornamento contatore
                                                        contatore[key][0] += 1
                                                        contatore[key][1] += float(consistenza_number)
                                                except Exception:
                                                    pass # Salta le righe non valide e continua silensiosamente
            
            # --- SEZIONE RISULTATI (Grafica) ---
            st.header("📊 Risultati")
            
            if contaTutto_Var:
                st.info("Risultati della modalità **Conta Tutto**")
                # Mostriamo il dizionario contaTutto in una tabella ordinata
                df_totale = pd.DataFrame(list(contaTutto.items()), columns=["Nome", "Totale Volte"])
                st.dataframe(df_totale, use_container_width=True)
            else:
                st.info(f"Risultati per il **Mese {mese_da_contare}**")
                # Prepariamo i dati del dizionario 'contatore' per essere mostrati in tabella
                dati_tabella = []
                for nome, valori in contatore.items():
                    dati_tabella.append({
                        "Nome": nome,
                        "Conteggio Volte": valori[0],
                        "Consistenza Totale (Somma)": round(valori[1], 2) # Arrotondato a 2 decimali
                    })
                df_mese = pd.DataFrame(dati_tabella)
                st.dataframe(df_mese, use_container_width=True)

        else:
            st.error("Nessun file di testo (.txt) trovato all'interno dello zip!")
