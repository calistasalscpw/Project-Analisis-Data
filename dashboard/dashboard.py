import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

#Mendefinisikan Functions

def create_reviews_df(df):
  reviews_df = df.groupby(by="review_score").review_id.nunique().sort_values(ascending=False)
  return reviews_df

def create_byyear_df(df):
  byyear_df = df.groupby(by=all_df["shipping_limit_date"].dt.year).price.sum().reset_index()
  byyear_df.rename(columns={
      "price": "revenue",
      "shipping_limit_date": "year"
  }, inplace=True)

  return byyear_df

def create_bymonth_df(df):
  bymonth_df = df.groupby(by=all_df["shipping_limit_date"].dt.month).price.sum().reset_index()
  bymonth_df.rename(columns={
      "price": "revenue",
      "shipping_limit_date": "month"
  }, inplace=True)

  return bymonth_df

def create_monthly_orders_df(df):
  monthly_orders_df = df.resample(rule='M', on='shipping_limit_date').agg({
    "order_id" : "nunique",
    "price" : "sum"
  })
  monthly_orders_df = monthly_orders_df.reset_index()
  monthly_orders_df.rename(columns={
      "order_id": "order_count",
      "price": "revenue"
  }, inplace=True)

  return monthly_orders_df

#Membaca file CSV

all_df = pd.read_csv("all_data.csv", low_memory=False)

#Kolom dengan tipe datetime akan digunakan sebagai filter

datetime_columns = ["shipping_limit_date", "review_creation_date"]
all_df.sort_values(by="shipping_limit_date", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
  all_df[column] = pd.to_datetime(all_df[column])

#Membuat komponen filter pada sidebar

min_date = all_df["shipping_limit_date"].min()
max_date = all_df["shipping_limit_date"].max()

with st.sidebar:
  #Menambahkan logo
  st.image("https://www.pngkey.com/png/full/392-3922066_moon-white-crescent-moon-transparent.png")

  #Mengambil start_date dan end_date dari data input
  start_date, end_date = st.date_input(
      label="Rentang Waktu", min_value=min_date,
      max_value=max_date,
      value=[min_date, max_date]
  )

#Set untuk mengambil tanggal di antara start_date and end_date
main_df = all_df[(all_df["shipping_limit_date"] >= str(start_date)) &
                (all_df["shipping_limit_date"] <= str(end_date))]

monthly_orders_df = create_monthly_orders_df(main_df)
reviews_df = create_reviews_df(main_df)
byyear_df = create_byyear_df(main_df)
bymonth_df = create_bymonth_df(main_df)

#Membuat header/judul website
st.header("E-Commerce Collection Dashboard :moon:")

#Menampilkan dulu informasi total order per bulan dan pemasukan dalam bentuk metric
st.subheader("Orders in Total")

col1, col2 = st.columns(2)

with col1:
  total_orders = monthly_orders_df.order_count.sum()
  st.metric("Total orders", value=total_orders)

with col2:
  total_revenue = format_currency(monthly_orders_df.revenue.sum(), "BRL", locale='es_CO')
  st.metric("Total Revenue", value=total_revenue)

#warna untuk grafik
colors=["#F27BBD", "#C65BCF", "#874CCC", "#6C22A6", "#10439F"]

fig, ax = plt.subplots(figsize=(10, 5))

sns.barplot(
    x = "shipping_limit_date",
    y = "order_count",
    data=monthly_orders_df,
    palette=colors,
    ax=ax
)

st.pyplot(fig)

#Visualisasi jawaban pertanyaan pertama
st.subheader("Customers' Satisfaction Distribution")

labels = reviews_df.index
sizes = reviews_df.values

fig, ax = plt.subplots()
ax.pie(sizes, labels=labels, autopct='%1.1f%%',
       colors=colors)

ax.axis('equal')
plt.title(label="Persebaran Rating Kepuasan Pelanggan")

st.pyplot(fig)

#Visualisasi jawaban pertanyaan kedua
st.subheader("Yearly Income Level")

fig, ax = plt.subplots(figsize=(10, 5))

sns.barplot(
    y="revenue",
    x="year",
    data=byyear_df.sort_values(by="year", ascending=False),
    palette=colors
)

plt.title("Number of Revenue by Year")
plt.ylabel("Revenue")
plt.xlabel("Year")
st.pyplot(fig)

st.subheader("Monthly Income Level")

fig, ax = plt.subplots(figsize=(10, 5))

sns.barplot(
    y="revenue",
    x="month",
    data=bymonth_df.sort_values(by="month", ascending=False),
    palette=colors
)

plt.title("Number of Revenue by Month")
plt.ylabel("Revenue")
plt.xlabel("Month")
st.pyplot(fig)
