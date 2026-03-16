import streamlit as st
import yfinance as yf
import math

# Configurazione della pagina
st.set_page_config(page_title="Calcolatore Worldline", page_icon="📊", layout="centered")

st.title("📊 Calcolatore Worldline")
st.write("I prezzi vengono prelevati in automatico se disponibili, altrimenti inseriscili manualmente.")

# Costanti fisse
PREZZO_SOTTOSCRIZIONE = 0.202
RAPPORTO = 6.0

# --- FUNZIONE PER RECUPERARE I PREZZI LIVE ---
@st.cache_data(ttl=60) 
def get_live_prices():
    try:
        # Recupera l'azione Worldline (Ticker: WLN.PA)
        ticker_azione = yf.Ticker("WLN.PA")
        p_azione = ticker_azione.info.get('currentPrice', ticker_azione.info.get('previousClose', 0.0000))
        
        # Recupera il diritto (Sostituisci con il ticker reale su Yahoo Finance se esiste)
        ticker_diritto = yf.Ticker("WLN-RT.PA") 
        p_diritto = ticker_diritto.info.get('currentPrice', ticker_diritto.info.get('previousClose', 0.0000))
        
        return p_azione, p_diritto
    except Exception:
        return 0.0000, 0.0000

# Chiamiamo la funzione
live_azione, live_diritto = get_live_prices()

# Impostiamo i valori di default
default_azione = live_azione if live_azione > 0 else 0.0000
default_diritto = live_diritto if live_diritto > 0 else 0.0000

# Creiamo due colonne per gli input dei prezzi
col1, col2 = st.columns(2)
with col1:
    prezzo_azione = st.number_input("1️⃣ Prezzo attuale AZIONE (€)", min_value=0.0000, value=default_azione, format="%.4f", step=0.0010)
    if live_azione > 0:
        st.caption("✅ *Prezzo azione aggiornato in automatico*")
with col2:
    prezzo_diritto = st.number_input("2️⃣ Prezzo attuale DIRITTO (€)", min_value=0.0000, value=default_diritto, format="%.4f", step=0.0010)
    if live_diritto > 0:
        st.caption("✅ *Prezzo diritto aggiornato in automatico*")
    elif default_azione > 0:
        st.caption("⚠️ *Prezzo diritto non trovato. Inseriscilo a mano.*")

st.divider()

# Input per la simulazione
st.subheader("🎯 Vuoi simulare un acquisto? (Opzionale)")
num_azioni_desiderate = st.number_input("Inserisci il numero di azioni che vuoi ottenere:", min_value=0, value=0, step=1)

# Bottone per avviare il calcolo
if st.button("Calcola Convenienza", type="primary", use_container_width=True):
    
    if prezzo_azione == 0 or prezzo_diritto == 0:
        st.error("Inserisci un prezzo valido e maggiore di zero per procedere al calcolo.")
    else:
        # --- 1. CALCOLO CONVENIENZA BASE ---
        costo_via_diritti = (prezzo_diritto / RAPPORTO) + PREZZO_SOTTOSCRIZIONE
        differenza = prezzo_azione - costo_via_diritti
        
        st.subheader("💡 Verdetto")
        if differenza > 0.001:
            percentuale = (differenza / prezzo_azione) * 100
            st.success(f"🟢 **CONVIENE COMPRARE I DIRITTI!** Risparmio teorico: € {differenza:.4f} per azione ({percentuale:.2f}%).")
            prezzo_migliore = costo_via_diritti
        elif differenza < -0.001:
            percentuale = (abs(differenza) / costo_via_diritti) * 100
            st.info(f"🔵 **CONVIENE COMPRARE L'AZIONE!** Risparmio teorico: € {abs(differenza):.4f} per azione ({percentuale:.2f}%).")
            prezzo_migliore = prezzo_azione
        else:
            st.warning("⚖️ **EQUILIBRIO.** I prezzi sono praticamente allineati.")
            prezzo_migliore = prezzo_azione
            
        col3, col4 = st.columns(2)
        col3.metric("Costo acquisto diretto", f"€ {prezzo_azione:.4f}")
        col4.metric("Costo via diritti", f"€ {costo_via_diritti:.4f}")

        # --- 2. CALCOLO INVERSO DEL TERP (NOVITÀ) ---
        st.divider()
        st.subheader("🕰️ Macchina del Tempo (Valore Pre-Aumento)")
        
        # Formula Inversa: P_pre = (P_effettivo * (1 + RAPPORTO)) - (RAPPORTO * PREZZO_SOTTOSCRIZIONE)
        prezzo_equivalente_pre_aumento = (prezzo_migliore * (1 + RAPPORTO)) - (RAPPORTO * PREZZO_SOTTOSCRIZIONE)
        
        st.info(f"Acquistando oggi al prezzo migliore disponibile (**€ {prezzo_migliore:.4f}**), è come se stessi comprando l'azione Worldline a **€ {prezzo_equivalente_pre_aumento:.4f}** PRIMA che iniziasse l'aumento di capitale.")

        # --- 3. SIMULATORE DI ACCUMULO ---
        if num_azioni_desiderate > 0:
            st.divider()
            st.subheader("🛒 Dettaglio Operazione")
            
            diritti_necessari = math.ceil(num_azioni_desiderate / RAPPORTO)
            azioni_effettive = diritti_necessari * RAPPORTO
            
            costo_acquisto_diritti = diritti_necessari * prezzo_diritto
            costo_sottoscrizione = azioni_effettive * PREZZO_SOTTOSCRIZIONE
            costo_totale_operazione = costo_acquisto_diritti + costo_sottoscrizione
            costo_a_mercato = azioni_effettive * prezzo_azione
            risparmio_totale = costo_a_mercato - costo_totale_operazione

            if azioni_effettive > num_azioni_desiderate:
                st.caption(f"⚠️ *Poiché 1 diritto = {int(RAPPORTO)} azioni, i calcoli sono basati su {int(azioni_effettive)} azioni (il multiplo più vicino).*")
                
            st.write(f"- Compra **{diritti_necessari} diritti** sul mercato (Spesa: € {costo_acquisto_diritti:.2f})")
            st.write(f"- Paga la **sottoscrizione alla banca** (Spesa: € {costo_sottoscrizione:.2f})")
            st.write(f"**💰 Costo totale dell'operazione tramite diritti:** **€ {costo_totale_operazione:.2f}**")
            
            if risparmio_totale > 0:
                st.success(f"🎁 Risparmio totale rispetto all'acquisto in borsa: **€ {risparmio_totale:.2f}**")
            elif risparmio_totale < 0:
                st.error(f"💸 Perdita totale rispetto all'acquisto in borsa: **€ {abs(risparmio_totale):.2f}** (Ti conviene comprare le azioni direttamente)")