
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import random, string, io, json
import pytz
import base64

st.set_page_config(page_title="Simple POS • Makeup", page_icon="💄", layout="wide")
TZ = pytz.timezone("Africa/Cairo")

SCHEMAS = {
    "Products": ["SKU","Name","RetailPrice","WholesalePrice","InStock","LowStockThreshold","Active","Notes"],
    "Customers": ["CustomerID","Name","Phone","Address","Notes"],
    "Orders": ["OrderID","DateTime","CustomerID","CustomerName","Channel","PricingType","Subtotal","Discount","Delivery","Total","Status","Notes"],
    "OrderItems": ["OrderID","SKU","Name","Qty","UnitPrice","LineTotal"],
    "StockMovements": ["Timestamp","SKU","Change","Reason","Reference","Note"],
    "Settings": ["Key","Value"]
}

# ---------- Helpers ----------
def get_setting(settings_df, key, default=""):
    if (settings_df["Key"]==key).any():
        return settings_df.loc[settings_df["Key"]==key, "Value"].iloc[0]
    return default

@st.cache_resource(show_spinner=False)
def get_gspread_client(sa_info: dict):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = Credentials.from_service_account_info(sa_info, scopes=scopes)
    return gspread.authorize(credentials)

def ensure_worksheet(sh, name):
    try:
        ws = sh.worksheet(name)
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title=name, rows=1000, cols=30)
        header = SCHEMAS[name]
        ws.update(f"A1:{chr(64+len(header))}1", [header])
    return ws

def read_df(ws, expected_cols):
    records = ws.get_all_records()
    df = pd.DataFrame(records)
    for c in expected_cols:
        if c not in df.columns:
            df[c] = "" if c not in ["RetailPrice","WholesalePrice","InStock","LowStockThreshold","Subtotal","Discount","Delivery","Total","Qty","UnitPrice","LineTotal"] else 0
    return df[expected_cols]

def write_df(ws, df):
    ws.resize(rows=1)
    if df.empty:
        return
    values = [df.columns.tolist()] + df.astype(str).values.tolist()
    ws.update(f"A1:{gspread.utils.rowcol_to_a1(len(values), len(values[0]))}", values)

def gen_id(prefix):
    now = datetime.now(TZ).strftime("%Y%m%d%H%M%S")
    return f"{prefix}{now}{''.join(random.choices(string.digits, k=4))}"

def invoice_html(order_row, items_df, business_name="My Makeup Shop", business_phone="", business_addr="", logo_b64=""):
    order_meta = {k: order_row[k] for k in order_row.index}
    rows_html = ""
    for _, r in items_df.iterrows():
        rows_html += f"""
        <tr>
            <td>{r['SKU']}</td>
            <td>{r['Name']}</td>
            <td style='text-align:center'>{int(r['Qty'])}</td>
            <td style='text-align:right'>{float(r['UnitPrice']):.2f}</td>
            <td style='text-align:right'>{float(r['LineTotal']):.2f}</td>
        </tr>
        """

    html = f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>فاتورة #{order_meta['OrderID']}</title>
<style>
@media print {{
  @page {{ size: A4; margin: 14mm; }}
}}
body {{ font-family: Arial, Helvetica, Tahoma, sans-serif; margin: 16px; }}
.header {{ display:flex; justify-content:space-between; align-items:flex-start; gap:12px; }}
h1 {{ margin: 0; }}
.small {{ color:#555; font-size: 12px; }}
.table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
.table th, .table td {{ border: 1px solid #ddd; padding: 8px; }}
.table th {{ background: #f7f7f7; }}
.right {{ text-align:right; }}
.center {{ text-align:center; }}
.summary {{ margin-top: 16px; width: 100%; max-width: 360px; margin-left:auto; }}
.summary table {{ width:100%; border-collapse:collapse; }}
.summary td {{ padding:6px 0; }}
hr {{ border: none; border-top: 1px dashed #aaa; margin: 16px 0; }}
.footer {{ margin-top: 24px; font-size: 12px; color:#444; }}
.badge {{ display:inline-block; padding:2px 8px; background:#eee; border-radius: 6px; font-size:12px; }}
</style>
</head>
<body>
  <div class="header">
    <div>
      <h1>فاتورة</h1>
      <div class="small">رقم: <b>{order_meta['OrderID']}</b></div>
      <div class="small">التاريخ: <b>{order_meta['DateTime']}</b></div>
      <div class="small">النوع: <span class="badge">{order_meta['PricingType']}</span></div>
      <div class="small">القناة: {order_meta.get('Channel','')}</div>
    </div>
    <div class="right">
      <div><b>{business_name}</b></div>
      <div class="small">{business_phone}</div>
      <div class="small">{business_addr}</div>
      {f'<img src="data:image/png;base64,{logo_b64}" style="max-height:60px;margin-top:6px;" />' if logo_b64 else ''}
    </div>
  </div>

  <hr />

  <div>
    <div>العميل: <b>{order_meta['CustomerName']}</b></div>
    <div class="small">كود العميل: {order_meta.get('CustomerID','')}</div>
  </div>

  <table class="table">
    <thead>
      <tr>
        <th>الكود</th>
        <th>المنتج</th>
        <th class="center">الكمية</th>
        <th class="right">السعر</th>
        <th class="right">الإجمالي</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>

  <div class="summary">
    <table>
      <tr><td>الإجمالي:</td><td class="right"><b>{float(order_meta['Subtotal']):.2f}</b></td></tr>
      <tr><td>خصم:</td><td class="right">{float(order_meta['Discount']):.2f}</td></tr>
      <tr><td>توصيل:</td><td class="right">{float(order_meta['Delivery']):.2f}</td></tr>
      <tr><td><b>الإجمالي النهائي:</b></td><td class="right"><b>{float(order_meta['Total']):.2f}</b></td></tr>
      <tr><td>الحالة:</td><td class="right">{order_meta['Status']}</td></tr>
    </table>
  </div>

  <div class="footer">
    شكراً لتعاملكم معنا ✨
  </div>
</body>
</html>
"""
    return html

# ---------- App ----------
st.title("💄 POS & Inventory (Makeup) — Waad Lash by SASO")
st.caption("واجهة تعمل من اللابتوب والموبايل. قاعدة بيانات: Google Sheets.")

if "gcp_service_account" not in st.secrets:
    st.warning("ضع بيانات الـ Service Account داخل st.secrets['gcp_service_account'] وقيمة SPREADSHEET_ID داخل st.secrets['SPREADSHEET_ID']. راجع ملف README_AR.md.")
    st.stop()

sa_info = st.secrets["gcp_service_account"]
client = get_gspread_client(sa_info)

spreadsheet_id = st.secrets.get("SPREADSHEET_ID", "").strip()
if not spreadsheet_id:
    st.error("يجب إضافة SPREADSHEET_ID داخل secrets. راجع الخطوات في README_AR.md.")
    st.stop()

sh = client.open_by_key(spreadsheet_id)

def load_sheets(sh):
    sheets = {}
    for name in SCHEMAS:
        sheets[name] = ensure_worksheet(sh, name)
    return sheets

ws_map = load_sheets(sh)

settings_ws = ws_map["Settings"]
settings_df = read_df(settings_ws, SCHEMAS["Settings"])
biz_name = get_setting(settings_df, "BusinessName", "Waad Lash by SASO")
biz_phone = get_setting(settings_df, "BusinessPhone", "")
biz_addr  = get_setting(settings_df, "BusinessAddress", "")
logo_b64  = get_setting(settings_df, "BusinessLogoB64", "")

page = st.sidebar.radio("القائمة", [
    "📊 لوحة المعلومات",
    "🧾 بيع جديد (POS)",
    "📦 المنتجات",
    "👤 العملاء",
    "📥 حركة المخزون",
    "📈 التقارير",
    "⚙️ الإعدادات",
])

# -------- Dashboard --------
if page == "📊 لوحة المعلومات":
    products = read_df(ws_map["Products"], SCHEMAS["Products"])
    orders = read_df(ws_map["Orders"], SCHEMAS["Orders"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("إجمالي المنتجات", len(products))
    today_str = datetime.now(TZ).strftime("%Y-%m-%d")
    today_orders = orders[orders["DateTime"].astype(str).str.startswith(today_str)]
    col2.metric("طلبات اليوم", len(today_orders))
    sales_today = today_orders["Total"].astype(float).sum() if not today_orders.empty else 0
    col3.metric("مبيعات اليوم", f"{sales_today:.2f}")
    low_stock = products[(products["Active"]!="No") & (products["InStock"].astype(float) <= products["LowStockThreshold"].astype(float))]
    col4.metric("نواقص/قرب النفاذ", len(low_stock))

    if logo_b64:
        st.image(f"data:image/png;base64,{logo_b64}", caption=biz_name, use_column_width=False)

    st.subheader("تنبيهات المخزون المنخفض")
    if low_stock.empty:
        st.success("لا توجد عناصر منخفضة حالياً ✅")
    else:
        st.dataframe(low_stock)

    st.subheader("آخر 10 طلبات")
    st.dataframe(orders.sort_values("DateTime", ascending=False).head(10))

# -------- POS --------
elif page == "🧾 بيع جديد (POS)":
    products = read_df(ws_map["Products"], SCHEMAS["Products"])
    products = products[products["Active"]!="No"]
    customers = read_df(ws_map["Customers"], SCHEMAS["Customers"])

    st.markdown("### بيانات العميل")
    colA, colB = st.columns(2)
    with colA:
        mode = st.selectbox("اختر عميل", ["عميل موجود", "عميل جديد"])
    with colB:
        channel = st.selectbox("قناة الطلب", ["Facebook Page","Instagram","Phone","WhatsApp","Other"])

    cust_id, cust_name, cust_phone, cust_address, cust_notes = "", "", "", "", ""
    if mode == "عميل موجود" and not customers.empty:
        sel = st.selectbox("العميل", customers["Name"] + " — " + customers["Phone"])
        row = customers[customers["Name"] + " — " + customers["Phone"] == sel].iloc[0]
        cust_id = row["CustomerID"]; cust_name = row["Name"]; cust_phone=row["Phone"]; cust_address=row["Address"]
    else:
        cust_name = st.text_input("اسم العميل")
        cust_phone = st.text_input("رقم الموبايل")
        cust_address = st.text_input("العنوان")
        cust_notes = st.text_area("ملاحظات", "")

    st.markdown("---")
    st.markdown("### اختيار المنتجات")
    pricing_type = st.radio("نوع السعر", ["Retail","Wholesale"], horizontal=True)

    show_cols = ["SKU","Name","RetailPrice","WholesalePrice","InStock"]
    edit_df = products[show_cols].copy()
    edit_df["Qty"] = 0
    edit_df = st.data_editor(edit_df, num_rows="dynamic", use_container_width=True, key="pos_table")

    if pricing_type == "Retail":
        edit_df["UnitPrice"] = edit_df["RetailPrice"].astype(float)
    else:
        edit_df["UnitPrice"] = edit_df["WholesalePrice"].astype(float)
    edit_df["LineTotal"] = edit_df["Qty"].astype(float) * edit_df["UnitPrice"].astype(float)
    selected = edit_df[edit_df["Qty"].astype(float) > 0]

    subtotal = selected["LineTotal"].sum()
    col1, col2, col3 = st.columns(3)
    with col1:
        discount = st.number_input("خصم", min_value=0.0, value=0.0, step=1.0)
    with col2:
        delivery = st.number_input("توصيل", min_value=0.0, value=0.0, step=1.0)
    with col3:
        total = subtotal - discount + delivery
        st.metric("الإجمالي", f"{total:.2f}")

    st.markdown("---")
    status = st.selectbox("حالة الطلب", ["Paid","Pending","Shipped","Cancelled"], index=0)
    notes  = st.text_area("ملاحظات الطلب", "")

    if st.button("✅ تأكيد الطلب وخصم المخزون", use_container_width=True, type="primary", disabled=selected.empty or not cust_name):
        if mode == "عميل جديد" or customers.empty:
            cust_id = "CUST" + datetime.now(TZ).strftime("%Y%m%d%H%M%S")
            new_cust = pd.DataFrame([[cust_id,cust_name,cust_phone,cust_address,cust_notes]], columns=SCHEMAS["Customers"])
            ws = ws_map["Customers"]
            existing = read_df(ws, SCHEMAS["Customers"])
            updated = pd.concat([existing, new_cust], ignore_index=True)
            write_df(ws, updated)

        stock_ok = True
        prod_df = read_df(ws_map["Products"], SCHEMAS["Products"]).set_index("SKU")
        for _, r in selected.iterrows():
            sku = str(r["SKU"]); need = int(r["Qty"])
            available = int(float(prod_df.loc[sku, "InStock"])) if sku in prod_df.index else 0
            if need > available:
                stock_ok = False
                st.error(f"المخزون غير كافٍ للمنتج {sku} — المتاح {available} والطلب {need}")
        if stock_ok:
            order_id = gen_id("ORD")
            now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
            order_row = pd.Series({
                "OrderID": order_id, "DateTime": now, "CustomerID": cust_id, "CustomerName": cust_name,
                "Channel": channel, "PricingType": pricing_type, "Subtotal": float(subtotal),
                "Discount": float(discount), "Delivery": float(delivery), "Total": float(total),
                "Status": status, "Notes": notes
            })
            orders_ws = ws_map["Orders"]
            orders_df = read_df(orders_ws, SCHEMAS["Orders"])
            orders_df = pd.concat([orders_df, pd.DataFrame([order_row])], ignore_index=True)
            write_df(orders_ws, orders_df)

            items_ws = ws_map["OrderItems"]
            items_df = read_df(items_ws, SCHEMAS["OrderItems"])
            new_items = []
            for _, r in selected.iterrows():
                new_items.append([order_id, str(r["SKU"]), r["Name"], int(r["Qty"]), float(r["UnitPrice"]), float(r["LineTotal"])])
            add_items_df = pd.DataFrame(new_items, columns=SCHEMAS["OrderItems"])
            items_df = pd.concat([items_df, add_items_df], ignore_index=True)
            write_df(items_ws, items_df)

            stock_ws = ws_map["StockMovements"]
            stock_mov = read_df(stock_ws, SCHEMAS["StockMovements"])
            prod_df = read_df(ws_map["Products"], SCHEMAS["Products"]).set_index("SKU")

            for _, r in selected.iterrows():
                sku = str(r["SKU"]); qty = int(r["Qty"])
                if sku in prod_df.index:
                    current = int(float(prod_df.loc[sku,"InStock"]))
                    prod_df.loc[sku,"InStock"] = current - qty
                stock_mov = pd.concat([stock_mov, pd.DataFrame([[now, sku, -qty, "Sale", order_id, ""]], columns=SCHEMAS["StockMovements"])], ignore_index=True)

            write_df(ws_map["Products"], prod_df.reset_index())
            write_df(stock_ws, stock_mov)

            st.success(f"تم إنشاء الطلب {order_id} وتحديث المخزون ✅")
            invoice = invoice_html(order_row, add_items_df, business_name=biz_name, business_phone=biz_phone, business_addr=biz_addr, logo_b64=logo_b64)
            st.download_button("🧾 تحميل الفاتورة (HTML للطباعة)", data=invoice.encode("utf-8"), file_name=f"invoice_{order_id}.html", mime="text/html", use_container_width=True)

# -------- Products --------
elif page == "📦 المنتجات":
    ws = ws_map["Products"]
    df = read_df(ws, SCHEMAS["Products"])

    st.markdown("### إضافة/تعديل منتج")
    c1, c2, c3 = st.columns(3)
    with c1:
        sku = st.text_input("كود الصنف (SKU)")
        name = st.text_input("اسم المنتج")
        active = st.selectbox("نشط؟", ["Yes","No"], index=0)
    with c2:
        retail = st.number_input("سعر قطاعي", min_value=0.0, value=0.0, step=1.0)
        wholesale = st.number_input("سعر جملة", min_value=0.0, value=0.0, step=1.0)
    with c3:
        instock = st.number_input("المتاح بالمخزن", min_value=0, value=0, step=1)
        lowthr  = st.number_input("حد التنبيه (قرب النفاد)", min_value=0, value=5, step=1)
    notes = st.text_area("ملاحظات", "")

    colA, colB = st.columns(2)
    if colA.button("💾 حفظ/تحديث المنتج"):
        if sku and name:
            exists = df["SKU"].astype(str) == str(sku)
            if exists.any():
                idx = df.index[exists][0]
                df.loc[idx, ["Name","RetailPrice","WholesalePrice","InStock","LowStockThreshold","Active","Notes"]] = [name, retail, wholesale, instock, lowthr, active, notes]
            else:
                df = pd.concat([df, pd.DataFrame([[sku,name,retail,wholesale,instock,lowthr,active,notes]], columns=SCHEMAS["Products"])], ignore_index=True)
            write_df(ws, df)
            st.success("تم الحفظ ✅")
        else:
            st.error("الرجاء إدخال كود الصنف واسم المنتج")

    if colB.button("🧹 تفريغ الحقول"):
        st.experimental_rerun()

    st.markdown("---")
    st.subheader("قائمة المنتجات")
    st.dataframe(df, use_container_width=True)

# -------- Customers --------
elif page == "👤 العملاء":
    ws = ws_map["Customers"]
    df = read_df(ws, SCHEMAS["Customers"])

    st.markdown("### إضافة/تعديل عميل")
    c1, c2 = st.columns(2)
    with c1:
        cust_id = st.text_input("كود العميل (اتركه فارغ للإضافة التلقائية)")
        name = st.text_input("الاسم")
        phone = st.text_input("رقم الموبايل")
    with c2:
        address = st.text_input("العنوان")
        notes = st.text_area("ملاحظات", "")

    colA, colB = st.columns(2)
    if colA.button("💾 حفظ/تحديث العميل"):
        if not name:
            st.error("الاسم مطلوب")
        else:
            if not cust_id:
                cust_id = "CUST" + datetime.now(TZ).strftime("%Y%m%d%H%M%S")
            exists = df["CustomerID"].astype(str) == str(cust_id)
            if exists.any():
                idx = df.index[exists][0]
                df.loc[idx, ["Name","Phone","Address","Notes"]] = [name, phone, address, notes]
            else:
                df = pd.concat([df, pd.DataFrame([[cust_id,name,phone,address,notes]], columns=SCHEMAS["Customers"])], ignore_index=True)
            write_df(ws, df)
            st.success("تم الحفظ ✅")

    if colB.button("🧹 تفريغ الحقول"):
        st.experimental_rerun()

    st.markdown("---")
    st.subheader("قائمة العملاء")
    st.dataframe(df, use_container_width=True)

# -------- Stock Movements --------
elif page == "📥 حركة المخزون":
    ws_prod = ws_map["Products"]
    ws_mov  = ws_map["StockMovements"]

    products = read_df(ws_prod, SCHEMAS["Products"])
    movements = read_df(ws_mov, SCHEMAS["StockMovements"])

    st.markdown("### إضافة حركة مخزون")
    c1, c2, c3 = st.columns(3)
    with c1:
        sku = st.selectbox("اختر المنتج (SKU — Name)", products["SKU"] + " — " + products["Name"] if not products.empty else [])
    with c2:
        change = st.number_input("الكمية (+ إضافة / - خصم)", step=1, value=0)
    with c3:
        reason = st.selectbox("السبب", ["Purchase","Adjustment","ReturnIn","ReturnOut"])
    note = st.text_input("ملاحظة/مرجع")

    if st.button("➕ إضافة الحركة وتحديث المخزون", type="primary"):
        if sku and change != 0:
            sku_only = str(sku).split(" — ")[0]
            now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
            movements = pd.concat([movements, pd.DataFrame([[now, sku_only, int(change), reason, "", note]], columns=SCHEMAS["StockMovements"])], ignore_index=True)
            write_df(ws_mov, movements)
            products.set_index("SKU", inplace=True)
            if sku_only in products.index:
                current = int(float(products.loc[sku_only,"InStock"]))
                products.loc[sku_only,"InStock"] = current + int(change)
                products = products.reset_index()
                write_df(ws_prod, products)
                st.success("تم تحديث المخزون ✅")
        else:
            st.error("يرجى اختيار منتج وتحديد كمية صحيحة")

    st.markdown("---")
    st.subheader("سجل الحركات")
    st.dataframe(movements.sort_values("Timestamp", ascending=False), use_container_width=True)

# -------- Reports --------
elif page == "📈 التقارير":
    orders = read_df(ws_map["Orders"], SCHEMAS["Orders"])
    items  = read_df(ws_map["OrderItems"], SCHEMAS["OrderItems"])
    products = read_df(ws_map["Products"], SCHEMAS["Products"])

    st.markdown("### تقرير فترة")
    c1, c2 = st.columns(2)
    from datetime import date
    with c1:
        start = st.date_input("من", date.today())
    with c2:
        end   = st.date_input("إلى", date.today())

    if st.button("📤 استخراج التقرير (CSV)"):
        if not orders.empty:
            mask = orders["DateTime"].apply(lambda x: x[:10] >= str(start) and x[:10] <= str(end))
            sel_orders = orders[mask].copy()
            total_sales = sel_orders["Total"].astype(float).sum()

            sel_items = items[items["OrderID"].isin(sel_orders["OrderID"])]
            agg = sel_items.groupby(["SKU","Name"])["Qty"].sum().reset_index().rename(columns={"Qty":"SoldQty"})

            low_stock = products[(products["Active"]!="No") & (products["InStock"].astype(float) <= products["LowStockThreshold"].astype(float))]

            out = io.StringIO()
            out.write("=== Sales Summary ===\n")
            out.write(f"From,{start},To,{end}\n")
            out.write(f"Total Orders,{len(sel_orders)}\n")
            out.write(f"Total Sales,{total_sales:.2f}\n\n")
            out.write("=== Top Sold Items ===\n")
            agg.to_csv(out, index=False)
            out.write("\n=== Low Stock (at export time) ===\n")
            low_stock.to_csv(out, index=False)
            st.download_button("تنزيل التقرير CSV", out.getvalue(), file_name=f"report_{start}_to_{end}.csv", mime="text/csv")

    st.markdown("---")
    st.subheader("تقرير المخزون الحالي")
    st.dataframe(products[["SKU","Name","InStock","LowStockThreshold"]])

# -------- Settings --------
elif page == "⚙️ الإعدادات":
    st.markdown("### معلومات النشاط التجاري")
    c1, c2 = st.columns(2)
    with c1:
        new_biz_name = st.text_input("اسم النشاط", value=biz_name)
        new_biz_phone = st.text_input("هاتف", value=biz_phone)
    with c2:
        new_biz_addr = st.text_area("العنوان", value=biz_addr)

    logo_file = st.file_uploader("شعار المتجر (اختياري)", type=["png","jpg","jpeg"])
    logo_b64_new = logo_b64
    if logo_file is not None:
        logo_b64_new = base64.b64encode(logo_file.read()).decode("utf-8")
        st.image(logo_file, caption="معاينة الشعار", use_column_width=False)

    if st.button("💾 حفظ بيانات النشاط"):
        settings_ws = ws_map["Settings"]
        s = read_df(settings_ws, SCHEMAS["Settings"])
        def upsert(df, k, v):
            if (df["Key"]==k).any():
                df.loc[df["Key"]==k, "Value"] = v
            else:
                df = pd.concat([df, pd.DataFrame([[k,v]], columns=SCHEMAS["Settings"])], ignore_index=True)
            return df
        s = upsert(s, "BusinessName", new_biz_name)
        s = upsert(s, "BusinessPhone", new_biz_phone)
        s = upsert(s, "BusinessAddress", new_biz_addr)
        s = upsert(s, "BusinessLogoB64", logo_b64_new)
        write_df(settings_ws, s)
        st.success("تم الحفظ ✅")
