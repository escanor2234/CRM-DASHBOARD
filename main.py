# -*- coding: utf-8 -*-
"""
CRM Dashboard - Olist Brazilian E-Commerce
Jalankan:  streamlit run crm_dashboard.py
"""
import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------------
# KONFIGURASI
# ----------------------------------------------------------------------------
DEFAULT_PATH = r"D:\PELAJARAN\Semester 5\Bussiness Intelegence\tugas crm\data"

st.set_page_config(
    page_title="CRM Dashboard | Olist",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Palet: biru malam + teal sebagai warna utama, amber & koral untuk sorotan
INK, TEAL, AMBER, CORAL, SKY, PLUM, MOSS = (
    "#1F3A5F", "#1B998B", "#F4A259", "#E4572E", "#5BC0EB", "#7B2D8E", "#8AB17D",
)
PALETTE = [TEAL, INK, AMBER, CORAL, SKY, PLUM, MOSS, "#B8B8D1"]

SEG_COLORS = {
    "Champions": TEAL,
    "Loyal": MOSS,
    "Big Spenders": INK,
    "New Customers": SKY,
    "Potential Loyalist": "#9BC1BC",
    "Need Attention": AMBER,
    "Can't Lose Them": PLUM,
    "At Risk": CORAL,
    "Lost": "#A0A4AE",
}
SEG_ORDER = list(SEG_COLORS.keys())

PLAYBOOK = pd.DataFrame(
    [
        ("Champions", "Pertahankan & jadikan advokat", "Program VIP, akses awal produk baru, hadiah referral", "Email personal, push notification", "Jumlah referral, repeat rate"),
        ("Loyal", "Naikkan nilai per pesanan", "Bundling, upsell kategori pelengkap, poin loyalitas", "Email, in-app banner", "AOV, frekuensi order"),
        ("Big Spenders", "Ubah pembeli besar jadi pembeli rutin", "Voucher order kedua, free ongkir langganan", "Email, WhatsApp", "Konversi ke order ke-2"),
        ("New Customers", "Dorong order kedua dalam 30-60 hari", "Welcome series, rekomendasi produk terkait, voucher terbatas waktu", "Email otomatis, retargeting", "Second-purchase rate"),
        ("Potential Loyalist", "Bangun kebiasaan belanja", "Rekomendasi personal, cashback cicilan, gamifikasi poin", "Email, push", "Repeat rate 90 hari"),
        ("Need Attention", "Ingatkan sebelum hilang", "Penawaran terbatas waktu, pengingat keranjang, review produk", "Email, retargeting", "Reaktivasi 30 hari"),
        ("Can't Lose Them", "Rebut kembali pelanggan bernilai tinggi", "Telepon/WhatsApp personal, penawaran eksklusif, survei alasan pergi", "Personal outreach", "Win-back rate"),
        ("At Risk", "Win-back berbasis diskon", "Voucher besar sekali pakai, kampanye 'kami rindu Anda'", "Email, SMS, ads", "Win-back rate, ROI voucher"),
        ("Lost", "Reaktivasi murah atau lepaskan", "Kampanye musiman massal berbiaya rendah, lalu bersihkan dari daftar aktif", "Email massal, lookalike ads", "Biaya per reaktivasi"),
    ],
    columns=["Segmen", "Tujuan", "Taktik", "Kanal", "KPI"],
)

st.markdown(
    f"""
<style>
.block-container {{ padding-top: 1.6rem; }}
.page-head {{ border-left: 6px solid {TEAL}; padding: .2rem 0 .2rem 1rem; margin-bottom: 1.2rem; }}
.page-head h1 {{ margin: 0; font-size: 1.9rem; letter-spacing: -.01em; }}
.page-head p {{ margin: .25rem 0 0; opacity: .72; }}
.kpi {{ border: 1px solid rgba(128,128,128,.28); border-top: 4px solid var(--c, {TEAL});
        border-radius: 10px; padding: .85rem 1rem; background: rgba(128,128,128,.05); height: 100%; }}
.kpi .l {{ font-size: .85rem; opacity: .72; }}
.kpi .v {{ font-size: 1.7rem; font-weight: 700; line-height: 1.25; letter-spacing: -.01em; }}
.kpi .s {{ font-size: .8rem; opacity: .62; }}
.qa {{ border: 1px solid rgba(128,128,128,.28); border-radius: 10px; padding: .9rem 1.1rem;
       background: rgba(128,128,128,.05); height: 100%; margin-bottom: .6rem; }}
.qa .q {{ font-weight: 700; color: {TEAL}; margin-bottom: .3rem; }}
.qa .a {{ font-size: .93rem; line-height: 1.5; }}
</style>
""",
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------------
# HELPER UI
# ----------------------------------------------------------------------------
def money(x):
    a = abs(x)
    if a >= 1e6:
        return f"R$ {x / 1e6:.2f}M"
    if a >= 1e3:
        return f"R$ {x / 1e3:.1f}K"
    return f"R$ {x:,.0f}"


def head(title, subtitle):
    st.markdown(f'<div class="page-head"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def kpi(col, label, value, sub="", color=TEAL):
    col.markdown(
        f'<div class="kpi" style="--c:{color}"><div class="l">{label}</div>'
        f'<div class="v">{value}</div><div class="s">{sub}</div></div>',
        unsafe_allow_html=True,
    )


def qa(col, question, answer):
    col.markdown(f'<div class="qa"><div class="q">{question}</div><div class="a">{answer}</div></div>', unsafe_allow_html=True)


def style(fig, h=380):
    fig.update_layout(
        height=h,
        margin=dict(l=10, r=10, t=55, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8b92a5"),
        title_font=dict(size=15),
        legend=dict(orientation="h", y=-0.18),
        colorway=PALETTE,
    )
    fig.update_xaxes(gridcolor="rgba(128,128,128,.18)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(128,128,128,.18)", zeroline=False)
    return fig


def show(fig):
    try:
        st.plotly_chart(fig, width="stretch", theme=None)
    except TypeError:
        st.plotly_chart(fig, use_container_width=True, theme=None)


def table(df, **kw):
    try:
        st.dataframe(df, width="stretch", hide_index=True, **kw)
    except TypeError:
        st.dataframe(df, use_container_width=True, hide_index=True, **kw)


# ----------------------------------------------------------------------------
# DATA
# ----------------------------------------------------------------------------
@st.cache_data(show_spinner="Memuat dan menyiapkan data...")
def load_data(path):
    def rd(name, **kw):
        return pd.read_csv(os.path.join(path, name), encoding="utf-8-sig", **kw)

    zip_t = {"dtype": {"customer_zip_code_prefix": str}}
    cust = rd("olist_customers_dataset.csv", **zip_t)
    dcols = [
        "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
        "order_delivered_customer_date", "order_estimated_delivery_date",
    ]
    orders = rd("olist_orders_dataset.csv", parse_dates=dcols)
    items = rd("olist_order_items_dataset.csv")
    pay = rd("olist_order_payments_dataset.csv")
    rev = rd("olist_order_reviews_dataset.csv", usecols=["order_id", "review_score"])
    prod = rd("olist_products_dataset.csv", usecols=["product_id", "product_category_name"])
    sell = rd("olist_sellers_dataset.csv")
    geo = rd("olist_geolocation_dataset.csv", usecols=["geolocation_lat", "geolocation_lng", "geolocation_state"])
    trans = rd("product_category_name_translation.csv")

    # Agregasi ke level order
    pay = pay.sort_values(["order_id", "payment_sequential"])
    pay_o = pay.groupby("order_id").agg(
        payment_value=("payment_value", "sum"),
        installments=("payment_installments", "max"),
        payment_type=("payment_type", "first"),
    ).reset_index()
    it_o = items.groupby("order_id").agg(
        n_items=("order_item_id", "count"), items_value=("price", "sum"), freight=("freight_value", "sum"),
    ).reset_index()
    rev_o = rev.groupby("order_id", as_index=False).review_score.mean()

    fact = (
        orders.merge(cust, on="customer_id", how="left")
        .merge(pay_o, on="order_id", how="left")
        .merge(it_o, on="order_id", how="left")
        .merge(rev_o, on="order_id", how="left")
    )
    fact["revenue"] = fact.payment_value.fillna(fact.items_value + fact.freight).fillna(0)
    fact = fact.rename(columns={"order_purchase_timestamp": "purchase_ts"})
    fact = fact.dropna(subset=["purchase_ts"]).sort_values("purchase_ts").reset_index(drop=True)
    fact["month"] = fact.purchase_ts.dt.to_period("M").dt.to_timestamp()
    fact["dow"] = fact.purchase_ts.dt.day_name()
    fact["hour"] = fact.purchase_ts.dt.hour
    delivered = fact.order_delivered_customer_date
    fact["delivery_days"] = (delivered - fact.purchase_ts).dt.total_seconds() / 86400
    fact["is_late"] = np.where(delivered.notna(), (delivered > fact.order_estimated_delivery_date).astype(float), np.nan)

    # Level item + kategori Inggris + seller
    itf = (
        items.merge(prod, on="product_id", how="left")
        .merge(trans, on="product_category_name", how="left")
        .merge(sell[["seller_id", "seller_state"]], on="seller_id", how="left")
    )
    itf["category"] = itf.product_category_name_english.fillna(itf.product_category_name).fillna("unknown")
    itf = itf[["order_id", "order_item_id", "seller_id", "price", "freight_value", "category", "seller_state"]]

    geo_state = geo.groupby("geolocation_state").agg(lat=("geolocation_lat", "median"), lng=("geolocation_lng", "median")).reset_index()
    return fact, itf, geo_state


def segment(r, f, m):
    if r >= 4 and f >= 3:
        return "Champions"
    if r >= 3 and f >= 3:
        return "Loyal"
    if r <= 2 and f >= 3:
        return "Can't Lose Them"
    if r >= 4 and m >= 4:
        return "Big Spenders"
    if r >= 4:
        return "New Customers"
    if r == 3:
        return "Potential Loyalist" if m >= 3 else "Need Attention"
    if r == 2:
        return "At Risk"
    return "Lost"


def build_rfm(f, snapshot, thr):
    g = f.groupby("customer_unique_id").agg(
        last_purchase=("purchase_ts", "max"),
        first_purchase=("purchase_ts", "min"),
        frequency=("order_id", "nunique"),
        monetary=("revenue", "sum"),
        avg_review=("review_score", "mean"),
        late_orders=("is_late", "sum"),
        state=("customer_state", "last"),
        city=("customer_city", "last"),
    ).reset_index()
    g["recency"] = (snapshot - g.last_purchase).dt.days
    g["R"] = pd.qcut(g.recency.rank(method="first", ascending=False), 5, labels=False) + 1
    g["M"] = pd.qcut(g.monetary.rank(method="first"), 5, labels=False) + 1
    g["F"] = np.select([g.frequency >= 3, g.frequency == 2], [5, 3], default=1)
    g["rfm_score"] = g.R + g.F + g.M
    g["segment"] = [segment(r, fr, m) for r, fr, m in zip(g.R, g.F, g.M)]
    g["status"] = np.select([g.recency > thr, g.recency > thr * 0.6], ["Tidak aktif", "Berisiko"], default="Aktif")
    pen = ((5 - g.avg_review.fillna(4)) / 4).clip(0, 1)
    g["risk_score"] = (np.clip(g.recency / (thr * 1.5), 0, 1) * 60 + pen * 20 + (g.late_orders > 0) * 20).round(0)
    return g


# ----------------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🧭 Olist CRM")
    page = st.radio("Halaman", ["Overview", "Sales", "Customer Management"], label_visibility="collapsed")
    st.divider()
    path = st.text_input("Folder data", DEFAULT_PATH)

try:
    fact, itf, geo_state = load_data(path)
except (FileNotFoundError, OSError) as e:
    st.error(f"Data tidak ditemukan di folder: {path}\n\nPeriksa path dan nama file CSV. Detail: {e}")
    st.stop()

with st.sidebar:
    st.markdown("**Filter**")
    dmin, dmax = fact.purchase_ts.min().date(), fact.purchase_ts.max().date()
    rng = st.date_input("Periode order", (dmin, dmax), min_value=dmin, max_value=dmax)
    status_opts = sorted(fact.order_status.dropna().unique())
    status_sel = st.multiselect(
        "Status pesanan", status_opts, default=[s for s in status_opts if s not in ("canceled", "unavailable")],
    )
    state_sel = st.multiselect("Negara bagian (kosong = semua)", sorted(fact.customer_state.dropna().unique()))
    st.markdown("**Definisi pelanggan tidak aktif**")
    thr = st.slider("Tidak aktif jika tidak order lebih dari (hari)", 30, 365, 180, 15)
    st.caption("Nilai transaksi = total pembayaran per order (payment_value). Snapshot RFM = hari setelah order terakhir pada periode terpilih.")

if not isinstance(rng, (tuple, list)) or len(rng) != 2:
    st.info("Pilih tanggal awal dan akhir pada filter periode.")
    st.stop()

mask = (
    (fact.purchase_ts.dt.date >= rng[0])
    & (fact.purchase_ts.dt.date <= rng[1])
    & fact.order_status.isin(status_sel)
)
if state_sel:
    mask &= fact.customer_state.isin(state_sel)
f = fact[mask]
if f.customer_unique_id.nunique() < 20:
    st.warning("Data pada filter ini terlalu sedikit (kurang dari 20 pelanggan). Longgarkan filter.")
    st.stop()

snapshot = f.purchase_ts.max().normalize() + pd.Timedelta(days=1)
rfm = build_rfm(f, snapshot, thr)
itf_f = itf[itf.order_id.isin(f.order_id)]


# ----------------------------------------------------------------------------
# HALAMAN 1: OVERVIEW
# ----------------------------------------------------------------------------
def page_overview():
    head("Overview", "Ringkasan kinerja bisnis dan jawaban atas enam pertanyaan utama CRM.")

    total_rev = f.revenue.sum()
    n_orders = f.order_id.nunique()
    n_cust = len(rfm)
    repeat = (rfm.frequency > 1).mean() * 100
    late = np.nan_to_num(f.is_late.mean())
    c = st.columns(6)
    kpi(c[0], "Total revenue", money(total_rev), f"{rng[0]} s/d {rng[1]}", TEAL)
    kpi(c[1], "Total order", f"{n_orders:,}", f"{f.n_items.sum():,.0f} item terjual", INK)
    kpi(c[2], "Pelanggan unik", f"{n_cust:,}", "berdasarkan customer_unique_id", SKY)
    kpi(c[3], "Rata-rata nilai order", money(total_rev / n_orders), "AOV", AMBER)
    kpi(c[4], "Pelanggan repeat", f"{repeat:.1f}%", "membeli lebih dari sekali", CORAL)
    kpi(c[5], "Skor ulasan", f"{f.review_score.mean():.2f} / 5", f"{(1 - late) * 100:.1f}% tiba tepat waktu", PLUM)

    st.write("")
    m = f.groupby("month").agg(revenue=("revenue", "sum"), orders=("order_id", "nunique")).reset_index()
    fig = go.Figure()
    fig.add_bar(x=m.month, y=m.revenue, name="Revenue (R$)", marker_color=TEAL)
    fig.add_scatter(x=m.month, y=m.orders, name="Jumlah order", yaxis="y2", mode="lines+markers", line=dict(color=AMBER, width=3))
    fig.update_layout(title="Tren revenue dan jumlah order per bulan", yaxis2=dict(overlaying="y", side="right", showgrid=False))
    show(style(fig, 360))

    left, right = st.columns([1.15, 1])
    g = f.groupby("customer_state").agg(customers=("customer_unique_id", "nunique"), revenue=("revenue", "sum")).reset_index()
    gm = g.merge(geo_state, left_on="customer_state", right_on="geolocation_state", how="left").dropna(subset=["lat"])
    fig = px.scatter_geo(
        gm, lat="lat", lon="lng", size="customers", color="revenue", hover_name="customer_state",
        hover_data={"customers": ":,", "revenue": ":,.0f", "lat": False, "lng": False},
        color_continuous_scale=[[0, "#CFE8E4"], [0.5, TEAL], [1, INK]], size_max=55, title="Sebaran pelanggan di Brasil",
    )
    fig.update_geos(
        scope="south america", lataxis_range=[-35, 6], lonaxis_range=[-75, -33], showcountries=True,
        countrycolor="rgba(128,128,128,.5)", showland=True, landcolor="rgba(128,128,128,.10)",
        showframe=False, bgcolor="rgba(0,0,0,0)",
    )
    with left:
        show(style(fig, 430))
    top = g.nlargest(10, "revenue").sort_values("revenue")
    fig = px.bar(top, x="revenue", y="customer_state", orientation="h", title="10 negara bagian dengan revenue tertinggi", color_discrete_sequence=[INK])
    fig.update_layout(xaxis_title=None, yaxis_title=None)
    with right:
        show(style(fig, 430))

    st.subheader("Jawaban untuk enam pertanyaan bisnis")
    best = rfm[rfm.segment.isin(["Champions", "Loyal", "Big Spenders"])]
    top10 = rfm.monetary.nlargest(max(1, int(len(rfm) * 0.1))).sum() / rfm.monetary.sum() * 100
    st_share = (g.set_index("customer_state").customers / g.customers.sum() * 100).sort_values(ascending=False)
    top_city = rfm.city.value_counts().idxmax()
    n_inact = int((rfm.recency > thr).sum())
    one_time = (rfm.frequency == 1).mean() * 100
    a, b, c3 = st.columns(3)
    qa(a, "Siapa pelanggan terbaik?",
       f"{len(best):,} pelanggan ({len(best) / len(rfm) * 100:.1f}%) masuk segmen Champions, Loyal, atau Big Spenders dan menyumbang "
       f"{best.monetary.sum() / rfm.monetary.sum() * 100:.1f}% revenue. Top 10% pelanggan menyumbang {top10:.1f}% revenue.")
    qa(b, "Dari mana pelanggan berasal?",
       f"{st_share.index[0]} adalah basis terbesar ({st_share.iloc[0]:.1f}% pelanggan), diikuti {st_share.index[1]} ({st_share.iloc[1]:.1f}%). "
       f"Kota dengan pelanggan terbanyak: {top_city.title()}.")
    qa(c3, "Berapa nilai transaksi tiap pelanggan?",
       f"Rata-rata {money(rfm.monetary.mean())} per pelanggan (median {money(rfm.monetary.median())}). "
       f"Selisih rata-rata dan median menunjukkan sebagian kecil pelanggan bernilai sangat besar.")
    a, b, c3 = st.columns(3)
    qa(a, "Pelanggan mana yang berpotensi tidak aktif?",
       f"{n_inact:,} pelanggan ({n_inact / len(rfm) * 100:.1f}%) tidak order lebih dari {thr} hari. "
       f"Daftar prioritas ada di Customer Management, tab Risiko tidak aktif.")
    qa(b, "Bagaimana meningkatkan loyalitas?",
       f"{one_time:.1f}% pelanggan hanya membeli sekali. Fokus utama: dorong order kedua lewat welcome series, voucher terbatas waktu, "
       f"dan perbaikan pengiriman serta ulasan (lihat tab Loyalitas dan strategi).")
    qa(c3, "Strategi pemasaran apa yang diterapkan?",
       "Pisahkan perlakuan per segmen RFM: hargai Champions dan Loyal, rebut kembali Can't Lose Them dan At Risk, "
       "serta ubah New Customers dan Big Spenders menjadi pembeli rutin. Rincian taktik ada di Customer Management.")


# ----------------------------------------------------------------------------
# HALAMAN 2: SALES
# ----------------------------------------------------------------------------
def page_sales():
    head("Sales", "Kinerja penjualan: tren, produk, pembayaran, logistik, dan seller.")
    gross = itf_f.price.sum()
    fr = itf_f.freight_value.sum()
    c = st.columns(5)
    kpi(c[0], "Revenue (pembayaran)", money(f.revenue.sum()), "", TEAL)
    kpi(c[1], "Item terjual", f"{len(itf_f):,}", "", INK)
    kpi(c[2], "Rata-rata harga item", money(itf_f.price.mean()), "", AMBER)
    kpi(c[3], "Total ongkir", money(fr), f"{fr / (gross + fr) * 100:.1f}% dari nilai belanja", CORAL)
    kpi(c[4], "Rata-rata cicilan", f"{f.installments.mean():.1f}x", "per order", PLUM)
    st.write("")

    t1, t2, t3, t4 = st.tabs(["Tren dan produk", "Pembayaran", "Logistik dan kepuasan", "Seller"])

    with t1:
        m = f.groupby("month").revenue.sum().reset_index()
        m["mom"] = m.revenue.pct_change() * 100
        mm = m.dropna()
        fig = px.bar(mm, x="month", y="mom", title="Pertumbuhan revenue bulanan (MoM, %)", color=mm.mom > 0,
                     color_discrete_map={True: TEAL, False: CORAL})
        fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title="%")
        show(style(fig, 320))

        cat = itf_f.groupby("category").agg(revenue=("price", "sum"), items=("order_item_id", "count")).reset_index()
        n = st.slider("Jumlah kategori ditampilkan", 5, 30, 15)
        l, r = st.columns(2)
        fig = px.treemap(cat.nlargest(n, "revenue"), path=["category"], values="revenue", color="revenue",
                         color_continuous_scale=[[0, "#CFE8E4"], [1, INK]], title=f"Peta revenue {n} kategori teratas")
        fig.update_layout(coloraxis_showscale=False)
        with l:
            show(style(fig, 420))
        top = cat.nlargest(10, "revenue").sort_values("revenue")
        fig = px.bar(top, x="revenue", y="category", orientation="h", title="10 kategori dengan revenue tertinggi", color_discrete_sequence=[TEAL])
        fig.update_layout(xaxis_title=None, yaxis_title=None)
        with r:
            show(style(fig, 420))

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        hm = f.groupby(["dow", "hour"]).size().unstack(fill_value=0).reindex(index=days, columns=range(24), fill_value=0)
        fig = px.imshow(hm, aspect="auto", color_continuous_scale=[[0, "#E8F4F2"], [1, INK]],
                        labels=dict(x="Jam", y="Hari", color="Order"), title="Kapan pelanggan paling sering berbelanja")
        show(style(fig, 330))

    with t2:
        l, r = st.columns(2)
        pt = f.groupby("payment_type").agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"), aov=("revenue", "mean")).reset_index()
        fig = px.pie(pt, names="payment_type", values="revenue", hole=0.55, title="Porsi revenue per metode pembayaran", color_discrete_sequence=PALETTE)
        with l:
            show(style(fig, 380))
        inst = f.installments.clip(upper=12).dropna().astype(int).value_counts().sort_index().reset_index()
        inst.columns = ["cicilan", "orders"]
        fig = px.bar(inst, x="cicilan", y="orders", title="Distribusi jumlah cicilan (12 = 12 atau lebih)", color_discrete_sequence=[AMBER])
        with r:
            show(style(fig, 380))
        fig = px.bar(pt.sort_values("aov"), x="aov", y="payment_type", orientation="h", title="Rata-rata nilai order per metode pembayaran", color_discrete_sequence=[PLUM])
        fig.update_layout(xaxis_title="R$", yaxis_title=None)
        show(style(fig, 300))

    with t3:
        l, r = st.columns(2)
        dd = f.dropna(subset=["delivery_days"])
        fig = px.histogram(dd[dd.delivery_days <= 60], x="delivery_days", nbins=60, title="Lama pengiriman (hari)", color_discrete_sequence=[SKY])
        fig.update_layout(xaxis_title="Hari", yaxis_title="Order")
        with l:
            show(style(fig, 360))
        ls = f.dropna(subset=["is_late"]).groupby("customer_state").is_late.mean().mul(100).sort_values(ascending=False).head(12).reset_index()
        fig = px.bar(ls, x="customer_state", y="is_late", title="Negara bagian dengan keterlambatan tertinggi (%)", color_discrete_sequence=[CORAL])
        fig.update_layout(xaxis_title=None, yaxis_title="% terlambat")
        with r:
            show(style(fig, 360))
        l, r = st.columns(2)
        rv = f.review_score.dropna().round().astype(int).value_counts().sort_index().reset_index()
        rv.columns = ["skor", "jumlah"]
        fig = px.bar(rv, x="skor", y="jumlah", title="Distribusi skor ulasan", color_discrete_sequence=[TEAL])
        with l:
            show(style(fig, 330))
        lt = f.dropna(subset=["review_score", "is_late"]).groupby("is_late").review_score.mean().reset_index()
        lt["pengiriman"] = lt.is_late.map({0.0: "Tepat waktu", 1.0: "Terlambat"})
        fig = px.bar(lt, x="pengiriman", y="review_score", title="Rata-rata skor ulasan: tepat waktu vs terlambat", color="pengiriman",
                     color_discrete_map={"Tepat waktu": TEAL, "Terlambat": CORAL}, text_auto=".2f")
        fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title="Skor", yaxis_range=[0, 5])
        with r:
            show(style(fig, 330))

    with t4:
        l, r = st.columns(2)
        sl = itf_f.groupby("seller_id").agg(revenue=("price", "sum"), items=("order_item_id", "count")).nlargest(10, "revenue").reset_index()
        sl["seller"] = sl.seller_id.str[:8]
        fig = px.bar(sl.sort_values("revenue"), x="revenue", y="seller", orientation="h", title="10 seller dengan revenue tertinggi", color_discrete_sequence=[INK])
        fig.update_layout(xaxis_title=None, yaxis_title=None)
        with l:
            show(style(fig, 400))
        ss = itf_f.groupby("seller_state").price.sum().nlargest(10).reset_index()
        fig = px.bar(ss, x="seller_state", y="price", title="Asal seller berdasarkan revenue", color_discrete_sequence=[AMBER])
        fig.update_layout(xaxis_title=None, yaxis_title=None)
        with r:
            show(style(fig, 400))


# ----------------------------------------------------------------------------
# HALAMAN 3: CUSTOMER MANAGEMENT
# ----------------------------------------------------------------------------
def page_customer():
    head("Customer Management", "Segmentasi RFM, asal dan nilai pelanggan, risiko tidak aktif, serta strategi loyalitas.")
    t1, t2, t3, t4, t5 = st.tabs(["Pelanggan terbaik (RFM)", "Asal pelanggan", "Nilai transaksi", "Risiko tidak aktif", "Loyalitas dan strategi"])

    # ---- Tab 1
    with t1:
        seg = rfm.groupby("segment").agg(pelanggan=("customer_unique_id", "count"), revenue=("monetary", "sum"),
                                         rata_recency=("recency", "mean"), rata_order=("frequency", "mean"),
                                         rata_nilai=("monetary", "mean")).reindex(SEG_ORDER).dropna().reset_index()
        seg["pct_pelanggan"] = seg.pelanggan / seg.pelanggan.sum() * 100
        seg["pct_revenue"] = seg.revenue / seg.revenue.sum() * 100
        best = rfm[rfm.segment.isin(["Champions", "Loyal", "Big Spenders"])]
        c = st.columns(4)
        kpi(c[0], "Pelanggan terbaik", f"{len(best):,}", "Champions + Loyal + Big Spenders", TEAL)
        kpi(c[1], "Kontribusi revenue", f"{best.monetary.sum() / rfm.monetary.sum() * 100:.1f}%", "dari segmen terbaik", INK)
        kpi(c[2], "Rata-rata nilai", money(best.monetary.mean()), "per pelanggan terbaik", AMBER)
        kpi(c[3], "Pelanggan repeat", f"{(rfm.frequency > 1).sum():,}", f"{(rfm.frequency > 1).mean() * 100:.1f}% dari seluruh pelanggan", CORAL)
        st.write("")
        l, r = st.columns(2)
        fig = px.bar(seg, x="segment", y="pelanggan", color="segment", color_discrete_map=SEG_COLORS, title="Jumlah pelanggan per segmen", text_auto=",")
        fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None)
        with l:
            show(style(fig, 380))
        fig = px.pie(seg, names="segment", values="revenue", hole=0.55, color="segment", color_discrete_map=SEG_COLORS, title="Kontribusi revenue per segmen")
        with r:
            show(style(fig, 380))

        samp = rfm.sample(min(6000, len(rfm)), random_state=1)
        fig = px.scatter(samp, x="recency", y="monetary", color="segment", color_discrete_map=SEG_COLORS, log_y=True, opacity=0.6,
                         hover_data=["customer_unique_id", "frequency", "state"], title="Peta pelanggan: recency vs nilai transaksi (sampel)",
                         category_orders={"segment": SEG_ORDER})
        fig.update_layout(xaxis_title="Hari sejak order terakhir", yaxis_title="Nilai transaksi (R$, skala log)")
        show(style(fig, 420))

        st.markdown("**Ringkasan segmen**")
        table(seg.rename(columns={"segment": "Segmen", "pelanggan": "Pelanggan", "revenue": "Revenue", "rata_recency": "Rata-rata recency (hari)",
                                  "rata_order": "Rata-rata order", "rata_nilai": "Rata-rata nilai", "pct_pelanggan": "% pelanggan", "pct_revenue": "% revenue"}),
              column_config={"Revenue": st.column_config.NumberColumn(format="R$ %.0f"), "Rata-rata nilai": st.column_config.NumberColumn(format="R$ %.0f"),
                             "Rata-rata recency (hari)": st.column_config.NumberColumn(format="%.0f"), "Rata-rata order": st.column_config.NumberColumn(format="%.2f"),
                             "% pelanggan": st.column_config.NumberColumn(format="%.1f%%"), "% revenue": st.column_config.NumberColumn(format="%.1f%%")})
        st.caption("Aturan skor: Recency dan Monetary memakai kuintil (5 = terbaik). Frequency: 1 order = 1, 2 order = 3, 3+ order = 5, karena mayoritas pelanggan hanya membeli sekali.")

        st.markdown("**Daftar pelanggan per segmen**")
        pick = st.selectbox("Segmen", [s for s in SEG_ORDER if s in set(rfm.segment)])
        lst = rfm[rfm.segment == pick].sort_values(["rfm_score", "monetary"], ascending=False)
        cols = ["customer_unique_id", "city", "state", "recency", "frequency", "monetary", "R", "F", "M", "rfm_score", "avg_review"]
        table(lst[cols].head(200), column_config={"monetary": st.column_config.NumberColumn("monetary", format="R$ %.2f"), "avg_review": st.column_config.NumberColumn(format="%.1f")})
        st.download_button(f"Unduh daftar {pick} (CSV)", lst[cols].to_csv(index=False).encode("utf-8"), f"pelanggan_{pick.replace(' ', '_').lower()}.csv", "text/csv")

    # ---- Tab 2
    with t2:
        by_state = rfm.groupby("state").agg(pelanggan=("customer_unique_id", "count"), revenue=("monetary", "sum"), rata_nilai=("monetary", "mean")).reset_index()
        l, r = st.columns(2)
        s1 = by_state.nlargest(12, "pelanggan").sort_values("pelanggan")
        fig = px.bar(s1, x="pelanggan", y="state", orientation="h", title="Pelanggan per negara bagian", color_discrete_sequence=[TEAL])
        fig.update_layout(xaxis_title=None, yaxis_title=None)
        with l:
            show(style(fig, 400))
        s2 = by_state[by_state.pelanggan >= 50].nlargest(12, "rata_nilai").sort_values("rata_nilai")
        fig = px.bar(s2, x="rata_nilai", y="state", orientation="h", title="Rata-rata nilai per pelanggan (min. 50 pelanggan)", color_discrete_sequence=[AMBER])
        fig.update_layout(xaxis_title="R$", yaxis_title=None)
        with r:
            show(style(fig, 400))
        cities = rfm.groupby(["city", "state"]).agg(pelanggan=("customer_unique_id", "count"), revenue=("monetary", "sum")).reset_index().nlargest(15, "pelanggan")
        cities["city"] = cities.city.str.title() + " (" + cities.state + ")"
        fig = px.bar(cities.sort_values("pelanggan"), x="pelanggan", y="city", orientation="h", color="revenue",
                     color_continuous_scale=[[0, "#CFE8E4"], [1, INK]], title="15 kota dengan pelanggan terbanyak (warna = revenue)")
        fig.update_layout(xaxis_title=None, yaxis_title=None)
        show(style(fig, 460))
        top3 = by_state.nlargest(3, "pelanggan")
        st.info(f"Tiga negara bagian teratas ({', '.join(top3.state)}) berisi {top3.pelanggan.sum() / len(rfm) * 100:.1f}% pelanggan. "
                "Konsentrasi ini membuat kampanye regional berbiaya rendah efektif di wilayah tersebut.")

    # ---- Tab 3
    with t3:
        c = st.columns(4)
        kpi(c[0], "Rata-rata per pelanggan", money(rfm.monetary.mean()), "", TEAL)
        kpi(c[1], "Median per pelanggan", money(rfm.monetary.median()), "", INK)
        kpi(c[2], "Nilai tertinggi", money(rfm.monetary.max()), "", AMBER)
        kpi(c[3], "Rata-rata order per pelanggan", f"{rfm.frequency.mean():.2f}", "", CORAL)
        st.write("")
        l, r = st.columns(2)
        cap = rfm.monetary.quantile(0.99)
        fig = px.histogram(rfm[rfm.monetary <= cap], x="monetary", nbins=60, title="Distribusi nilai transaksi per pelanggan (sampai persentil 99)", color_discrete_sequence=[TEAL])
        fig.update_layout(xaxis_title="R$", yaxis_title="Pelanggan")
        with l:
            show(style(fig, 380))
        fq = rfm.frequency.clip(upper=5).value_counts().sort_index().reset_index()
        fq.columns = ["order", "pelanggan"]
        fq["order"] = fq.order.astype(str).replace({"5": "5+"})
        fig = px.bar(fq, x="order", y="pelanggan", title="Jumlah order per pelanggan", color_discrete_sequence=[INK], text_auto=",")
        fig.update_layout(xaxis_title="Order", yaxis_title=None)
        with r:
            show(style(fig, 380))

        srt = rfm.monetary.sort_values(ascending=False).reset_index(drop=True)
        cum = srt.cumsum() / srt.sum() * 100
        pctc = (np.arange(1, len(srt) + 1) / len(srt)) * 100
        idx = np.linspace(0, len(srt) - 1, 400).astype(int)
        top20 = cum.iloc[int(len(srt) * 0.2) - 1] if len(srt) >= 5 else float("nan")
        fig = go.Figure()
        fig.add_scatter(x=pctc[idx], y=cum.iloc[idx], mode="lines", name="Kumulatif revenue", line=dict(color=TEAL, width=3), fill="tozeroy")
        fig.add_scatter(x=[0, 100], y=[0, 100], mode="lines", name="Pembagian merata", line=dict(color="#A0A4AE", dash="dash"))
        fig.update_layout(title=f"Kurva Pareto: 20% pelanggan teratas menyumbang {top20:.1f}% revenue", xaxis_title="% pelanggan (terbesar ke terkecil)", yaxis_title="% revenue kumulatif")
        show(style(fig, 380))

        st.markdown("**Cari pelanggan**")
        q = st.text_input("Masukkan customer_unique_id (boleh sebagian)")
        if q:
            hit = rfm[rfm.customer_unique_id.str.contains(q.strip(), case=False, na=False)].head(10)
            if hit.empty:
                st.warning("Pelanggan tidak ditemukan pada filter yang aktif.")
            else:
                table(hit[["customer_unique_id", "city", "state", "segment", "status", "recency", "frequency", "monetary", "avg_review"]])
                orders = f[f.customer_unique_id.isin(hit.customer_unique_id)][["customer_unique_id", "order_id", "purchase_ts", "order_status", "revenue", "payment_type", "review_score"]]
                table(orders.sort_values("purchase_ts", ascending=False))

    # ---- Tab 4
    with t4:
        n_in = int((rfm.status == "Tidak aktif").sum())
        n_rk = int((rfm.status == "Berisiko").sum())
        hv = rfm[(rfm.status != "Aktif") & (rfm.monetary >= rfm.monetary.quantile(0.75))]
        c = st.columns(4)
        kpi(c[0], "Tidak aktif", f"{n_in:,}", f"lebih dari {thr} hari tanpa order", CORAL)
        kpi(c[1], "Berisiko", f"{n_rk:,}", f"{int(thr * 0.6)} sampai {thr} hari tanpa order", AMBER)
        kpi(c[2], "Aktif", f"{int((rfm.status == 'Aktif').sum()):,}", "", TEAL)
        kpi(c[3], "Nilai tinggi yang berisiko", f"{len(hv):,}", "kuartil teratas nilai transaksi", PLUM)
        st.write("")
        l, r = st.columns(2)
        fig = px.histogram(rfm, x="recency", nbins=60, title="Distribusi hari sejak order terakhir", color_discrete_sequence=[SKY])
        fig.add_vline(x=thr, line_dash="dash", line_color=CORAL, annotation_text=f"batas {thr} hari")
        fig.update_layout(xaxis_title="Hari", yaxis_title="Pelanggan")
        with l:
            show(style(fig, 360))
        stc = rfm.status.value_counts().reindex(["Aktif", "Berisiko", "Tidak aktif"]).reset_index()
        stc.columns = ["status", "pelanggan"]
        fig = px.pie(stc, names="status", values="pelanggan", hole=0.55, color="status", color_discrete_map={"Aktif": TEAL, "Berisiko": AMBER, "Tidak aktif": CORAL}, title="Status keaktifan pelanggan")
        with r:
            show(style(fig, 360))

        st.markdown("**Prioritas win-back: pelanggan bernilai tinggi yang berisiko atau tidak aktif**")
        st.caption("Skor risiko (0-100) menggabungkan lama tidak order (60%), skor ulasan rendah (20%), dan pernah mengalami keterlambatan (20%).")
        pri = hv.sort_values(["risk_score", "monetary"], ascending=False)
        cols = ["customer_unique_id", "city", "state", "segment", "status", "recency", "frequency", "monetary", "avg_review", "risk_score"]
        table(pri[cols].head(200), column_config={
            "risk_score": st.column_config.ProgressColumn("risk_score", min_value=0, max_value=100, format="%d"),
            "monetary": st.column_config.NumberColumn(format="R$ %.2f"), "avg_review": st.column_config.NumberColumn(format="%.1f")})
        st.download_button("Unduh daftar win-back (CSV)", pri[cols].to_csv(index=False).encode("utf-8"), "daftar_winback.csv", "text/csv")

    # ---- Tab 5
    with t5:
        st.markdown("**Apa yang mendorong pelanggan membeli lagi?**")
        first = f.drop_duplicates("customer_unique_id", keep="first").merge(rfm[["customer_unique_id", "frequency"]], on="customer_unique_id")
        first["repeat"] = first.frequency > 1
        l, m_, r = st.columns(3)
        a = first.dropna(subset=["review_score"]).assign(skor=lambda d: d.review_score.round().astype(int)).groupby("skor").repeat.mean().mul(100).reset_index()
        fig = px.bar(a, x="skor", y="repeat", title="Repeat rate menurut skor ulasan order pertama", color_discrete_sequence=[TEAL], text_auto=".1f")
        fig.update_layout(xaxis_title="Skor ulasan", yaxis_title="% repeat")
        with l:
            show(style(fig, 330))
        b = first.dropna(subset=["is_late"]).assign(p=lambda d: d.is_late.map({0.0: "Tepat waktu", 1.0: "Terlambat"})).groupby("p").repeat.mean().mul(100).reset_index()
        fig = px.bar(b, x="p", y="repeat", title="Repeat rate menurut ketepatan pengiriman", color="p", color_discrete_map={"Tepat waktu": TEAL, "Terlambat": CORAL}, text_auto=".1f")
        fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title="% repeat")
        with m_:
            show(style(fig, 330))
        cnt = first.payment_type.value_counts()
        c_ = first[first.payment_type.isin(cnt[cnt >= 100].index)].groupby("payment_type").repeat.mean().mul(100).reset_index()
        fig = px.bar(c_, x="payment_type", y="repeat", title="Repeat rate menurut metode bayar order pertama", color_discrete_sequence=[AMBER], text_auto=".1f")
        fig.update_layout(xaxis_title=None, yaxis_title="% repeat")
        with r:
            show(style(fig, 330))
        st.caption("Catatan: pelanggan dengan order pertama yang baru punya waktu lebih singkat untuk membeli lagi, sehingga repeat rate bisa sedikit lebih rendah untuk mereka.")

        st.markdown("**Retensi kohort (% pelanggan yang kembali membeli setelah n bulan)**")
        cc = f[["customer_unique_id", "month"]].drop_duplicates()
        cc = cc.join(cc.groupby("customer_unique_id").month.min().rename("cohort"), on="customer_unique_id")
        cc["idx"] = (cc.month.dt.year - cc.cohort.dt.year) * 12 + (cc.month.dt.month - cc.cohort.dt.month)
        co = cc.groupby(["cohort", "idx"]).customer_unique_id.nunique().unstack()
        size = co[0]
        keep = size[size >= 100].index
        if len(keep) == 0:
            st.info("Ukuran kohort terlalu kecil pada filter ini.")
        else:
            ret = co.loc[keep].div(size[keep], axis=0).mul(100)
            ret = ret[[c for c in ret.columns if 1 <= c <= 12]]
            ret.index = ret.index.strftime("%Y-%m")
            fig = px.imshow(ret, aspect="auto", text_auto=".1f", color_continuous_scale=[[0, "#E8F4F2"], [1, INK]],
                            labels=dict(x="Bulan setelah order pertama", y="Kohort", color="% kembali"))
            show(style(fig, 460))

        st.markdown("**Strategi per segmen**")
        play = PLAYBOOK.merge(rfm.groupby("segment").agg(Pelanggan=("customer_unique_id", "count")).reset_index().rename(columns={"segment": "Segmen"}), on="Segmen", how="left")
        play["Pelanggan"] = play.Pelanggan.fillna(0).astype(int)
        table(play[["Segmen", "Pelanggan", "Tujuan", "Taktik", "Kanal", "KPI"]])

        st.markdown("**Rekomendasi program loyalitas**")
        st.markdown(
            "- **Program poin dan tier** (Silver, Gold, Platinum) berdasarkan skor RFM, supaya pembeli sekali punya alasan kembali.\n"
            "- **Welcome series 60 hari** untuk New Customers dengan rekomendasi produk dari kategori yang baru dibeli.\n"
            "- **Perbaiki pengalaman pengiriman** di wilayah dengan keterlambatan tinggi, karena pengiriman terlambat menurunkan ulasan dan peluang repeat.\n"
            "- **Minta ulasan dan tindak lanjuti ulasan rendah** dengan kompensasi cepat sebelum pelanggan berhenti.\n"
            "- **Penawaran cicilan atau free ongkir** untuk segmen bernilai tinggi yang mulai tidak aktif."
        )


{"Overview": page_overview, "Sales": page_sales, "Customer Management": page_customer}[page]()