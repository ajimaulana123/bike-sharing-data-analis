import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from matplotlib.ticker import FuncFormatter

# Mengatur gaya seaborn
sns.set(style='dark')

# Definisi Fungsi
def get_total_count_by_hour(hour_df):
    """Menghitung total penyewaan sepeda berdasarkan jam."""
    return hour_df.groupby("hours").agg({"count_cr": "sum"})

def filter_days_by_date(day_df, start_date, end_date):
    """Menyaring DataFrame hari berdasarkan tanggal mulai dan tanggal akhir."""
    return day_df.query(f'dteday >= "{start_date}" and dteday <= "{end_date}"')

def total_registered_by_day(day_df):
    """Mendapatkan total penyewaan terdaftar per hari."""
    reg_df = day_df.groupby("dteday").agg({"registered": "sum"}).reset_index()
    reg_df.rename(columns={"registered": "register_sum"}, inplace=True)
    return reg_df

def total_casual_by_day(day_df):
    """Mendapatkan total penyewaan kasual per hari."""
    cas_df = day_df.groupby("dteday").agg({"casual": "sum"}).reset_index()
    cas_df.rename(columns={"casual": "casual_sum"}, inplace=True)
    return cas_df

def total_orders_by_hour(hour_df):
    """Mendapatkan total pesanan berdasarkan jam."""
    return hour_df.groupby("hours").count_cr.sum().sort_values(ascending=False).reset_index()

def total_orders_by_season(day_df):
    """Mendapatkan total penyewaan sepeda berdasarkan musim."""
    return day_df.groupby("season").count_cr.sum().reset_index()

# Memuat data
days_df = pd.read_csv('dashboard/day_clean.csv')
hours_df = pd.read_csv('dashboard/hour_clean.csv')

# Mengonversi kolom tanggal menjadi datetime
for df in [days_df, hours_df]:
    df['dteday'] = pd.to_datetime(df['dteday'])

# Pemilihan Tanggal di Sidebar
min_date = days_df["dteday"].min()
max_date = days_df["dteday"].max()

with st.sidebar:
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Menyaring DataFrame berdasarkan tanggal yang dipilih
main_df_days = filter_days_by_date(days_df, start_date, end_date)
main_df_hour = filter_days_by_date(hours_df, start_date, end_date)

# Agregasi Data
hour_count_df = get_total_count_by_hour(main_df_hour)
day_df_count_2011 = filter_days_by_date(main_df_days, "2011-01-01", "2012-12-31")
reg_df = total_registered_by_day(main_df_days)
cas_df = total_casual_by_day(main_df_days)
sum_order_items_df = total_orders_by_hour(main_df_hour)
season_df = total_orders_by_season(main_df_hour)

# Visualisasi Dashboard
st.header('Bike Sharing')
st.subheader('Daily Sharing')

col1, col2, col3 = st.columns(3)

with col1:
    total_orders = day_df_count_2011.count_cr.sum()
    formatted_orders = f"{total_orders:,}".replace(",", ".")
    st.metric("Total Sharing Bike", value=formatted_orders)

st.subheader("Penyewaan Sepeda Berdasarkan Jam")

# Plot untuk penyewaan sepeda berdasarkan jam
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

# Penyewaan terbanyak
sns.barplot(x="hours", y="count_cr", data=sum_order_items_df.head(5), 
            hue="hours", palette=["#D3D3D3", "#D3D3D3", "#FF7F7F", "#D3D3D3", "#D3D3D3"], 
            ax=ax[0], legend=False)

ax[0].set_xlabel("Jam (PM)", fontsize=30)
ax[0].set_title("Jam dengan Banyak Penyewa Sepeda", fontsize=30)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

# Penyewaan terdikit
sns.barplot(x="hours", y="count_cr", data=sum_order_items_df.sort_values(by="hours").head(5), 
            hue="hours", palette=["#D3D3D3"]*4 + ["#90CAF9"], 
            ax=ax[1], legend=False)

ax[1].set_xlabel("Jam (AM)", fontsize=30)
ax[1].set_title("Jam dengan Sedikit Penyewa Sepeda", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

# Plot untuk penyewaan sepeda berdasarkan musim
st.subheader("Penyewaan Sepeda Berdasarkan Musim")

fig, ax = plt.subplots(figsize=(20, 10))

top_seasons = (
    days_df.groupby("season", observed=True)["count_cr"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
    .head(10)
)

sns.barplot(
    x="season",
    y="count_cr",
    data=top_seasons,
    ax=ax,
    palette=["#FF7F7F", "#D3D3D3", "#D3D3D3", "#D3D3D3"],
    dodge=False,
    legend=False
)

# Format sumbu y
def format_func(value, tick_number):
    if value >= 1_000_000:
        return f'{value / 1_000_000:.1f} juta'
    elif value >= 1_000:
        return f'{value / 1_000:.0f} ribu'
    else:
        return int(value)

ax.yaxis.set_major_formatter(FuncFormatter(format_func))
ax.set_title("Grafik Penyewaan Sepeda Antar Musim", fontsize=50)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=35)
ax.tick_params(axis='y', labelsize=30)

st.pyplot(fig)
