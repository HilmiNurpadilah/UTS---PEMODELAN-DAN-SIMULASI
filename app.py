from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)


def jalankan_simulasi(initial_stock: int, threshold: int, restock_amount: int):
    """Simulasi sederhana dinamika stok berbasis data penjualan harian.

    Aturan:
    - Stok berkurang sesuai penjualan harian (sales).
    - Jika stok setelah penjualan <= threshold, maka dilakukan restock sejumlah restock_amount.
    - Jika stok tidak cukup untuk memenuhi permintaan, tercatat sebagai penjualan tidak terlayani.
    """

    df = pd.read_csv("model/hasil_simulasi_es_teh.csv")  # data dasar penjualan

    stock = initial_stock
    stock_list = []
    sales_realized_list = []
    sales_lost_list = []
    restock_list = []

    for sales in df["sales"]:
        # Penjualan yang bisa dipenuhi dan yang tidak terlayani
        if stock >= sales:
            sales_realized = sales
            sales_lost = 0
        else:
            sales_realized = stock
            sales_lost = sales - stock

        stock -= sales_realized

        # Keputusan restock berdasarkan threshold
        restock = 0
        if stock <= threshold:
            restock = restock_amount
            stock += restock

        stock_list.append(stock)
        sales_realized_list.append(sales_realized)
        sales_lost_list.append(sales_lost)
        restock_list.append(restock)

    # Tambahkan kolom hasil simulasi ke DataFrame
    df["sales_realized"] = sales_realized_list
    df["sales_lost"] = sales_lost_list
    df["restock"] = restock_list
    df["stock_after_simulation"] = stock_list

    # Ringkasan nilai
    summary = {
        "total_penjualan_permintaan": int(df["sales"].sum()),
        "total_penjualan_terpenuhi": int(df["sales_realized"].sum()),
        "total_penjualan_tidak_terlayani": int(df["sales_lost"].sum()),
        "jumlah_hari_restock": int((df["restock"] > 0).sum()),
        "total_unit_restock": int(df["restock"].sum()),
        "stok_rata_rata": float(df["stock_after_simulation"].mean()),
    }

    return df, summary


@app.route("/", methods=["GET", "POST"])
def index():
    # Nilai awal default agar halaman tetap menampilkan sesuatu saat pertama dibuka
    initial_stock = 100
    threshold = 20
    restock_amount = 50

    if request.method == "POST":
        try:
            initial_stock = int(request.form.get("initial_stock", initial_stock))
            threshold = int(request.form.get("threshold", threshold))
            restock_amount = int(request.form.get("restock_amount", restock_amount))
        except ValueError:
            # Jika input tidak valid, biarkan gunakan nilai default
            pass

    df, summary = jalankan_simulasi(initial_stock, threshold, restock_amount)

    data = df.to_dict(orient="records")
    chart_labels = df["date"].tolist() if "date" in df.columns else list(range(1, len(df) + 1))
    chart_stock = df["stock_after_simulation"].tolist()
    chart_sales = df["sales_realized"].tolist()

    return render_template(
        "index.html",
        data=data,
        summary=summary,
        initial_stock=initial_stock,
        threshold=threshold,
        restock_amount=restock_amount,
        chart_labels=chart_labels,
        chart_stock=chart_stock,
        chart_sales=chart_sales,
    )


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

