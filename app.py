import os
import sqlite3

import pandas as pd
import streamlit as st
import altair as alt

# Local imports
from db_init import ensure_db, DB_PATH


st.set_page_config(page_title="TP1 BI - Dashboard", page_icon="📊", layout="wide")
st.title("TP1 – Tableau de bord (SQLite + Streamlit)")


# Ensure database exists with demo data
ensure_db(DB_PATH)


@st.cache_data(show_spinner=False)
def load_data(db_path: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
	conn = sqlite3.connect(db_path)
	try:
		clients = pd.read_sql_query("SELECT * FROM clients", conn)
		produits = pd.read_sql_query("SELECT * FROM produits", conn)
		ventes = pd.read_sql_query("SELECT * FROM ventes", conn, parse_dates=["date"])  # type: ignore[arg-type]

		# Join tables to simplify aggregations
		df = (
			ventes
			.merge(clients, left_on="client_id", right_on="id", suffixes=("_vente", "_client"))
			.merge(produits, left_on="produit_id", right_on="id", suffixes=("", "_produit"))
		)
		df["CA"] = df["quantite"] * df["prix_unitaire"]
		return clients, produits, ventes, df
	finally:
		conn.close()


clients, produits, ventes, df = load_data(DB_PATH)


# KPIs
col1, col2, col3, col4 = st.columns(4)
with col1:
	ca_total = float(df["CA"].sum())
	st.metric("Chiffre d'affaires total", f"{ca_total:,.2f} €")
with col2:
	qte_total = int(df["quantite"].sum())
	st.metric("Quantité totale vendue", f"{qte_total}")
with col3:
	panier_moyen = ca_total / max(len(df), 1)
	st.metric("Panier moyen (par vente)", f"{panier_moyen:,.2f} €")
with col4:
	nb_clients = df["client_id"].nunique()
	st.metric("Clients actifs", f"{nb_clients}")


st.divider()

left, right = st.columns(2)

with left:
	st.subheader("CA par région")
	ca_region = df.groupby("region", as_index=False)["CA"].sum().sort_values("CA", ascending=False)
	chart_region = (
		alt.Chart(ca_region)
		.mark_bar(color="#4c78a8")
		.encode(x=alt.X("CA:Q", title="CA (€)"), y=alt.Y("region:N", sort='-x', title="Région"), tooltip=["region", alt.Tooltip("CA", format=",.2f")])
		.properties(height=350)
	)
	st.altair_chart(chart_region, use_container_width=True)

with right:
	st.subheader("Top produits (CA)")
	top_prod = (
		df.groupby(["produit_id", "nom_produit"], as_index=False)["CA"].sum()
		.sort_values("CA", ascending=False)
	)
	chart_top = (
		alt.Chart(top_prod)
		.mark_bar(color="#f58518")
		.encode(x=alt.X("CA:Q", title="CA (€)"), y=alt.Y("nom_produit:N", sort='-x', title="Produit"), tooltip=["nom_produit", alt.Tooltip("CA", format=",.2f")])
		.properties(height=350)
	)
	st.altair_chart(chart_top, use_container_width=True)


st.subheader("Évolution mensuelle du CA")
monthly = (
	df.assign(mois=df["date"].dt.to_period("M").dt.to_timestamp())
	.groupby("mois", as_index=False)["CA"].sum()
	.sort_values("mois")
)

chart_month = (
	alt.Chart(monthly)
	.mark_line(point=True, color="#54a24b")
	.encode(x=alt.X("mois:T", title="Mois"), y=alt.Y("CA:Q", title="CA (€)"), tooltip=[alt.Tooltip("mois:T", title="Mois"), alt.Tooltip("CA:Q", format=",.2f")])
	.properties(height=320)
)
st.altair_chart(chart_month, use_container_width=True)


with st.expander("Voir les données sources"):
	st.write("clients", clients)
	st.write("produits", produits)
	st.write("ventes", ventes)

st.caption("Astuce: utilisez la commande 'streamlit run app.py' pour lancer l'application.")

