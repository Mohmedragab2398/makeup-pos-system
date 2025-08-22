# YALLA SHOPPING POS SYSTEM - PRODUCTION READY v1.0.0
import streamlit as st
import pandas as pd

# Handle imports with error checking (no runtime install to avoid Cloud failures)
try:
    import gspread
    from google.oauth2.service_account import Credentials
    # Only show success message in development, not in production
    if st.secrets.get("DEVELOPMENT_MODE", False):
        st.success("✅ All critical dependencies loaded successfully!")
except ImportError as e:
    st.error(f"❌ Import Error: {e}")
    st.error("🔧 SOLUTION: Clear Streamlit Cloud cache and redeploy!")
    st.error("Dependencies missing. Ensure requirements.txt includes complete Google Auth ecosystem.")
    
    with st.expander("🛠️ Troubleshooting Steps", expanded=True):
        st.markdown("""
        **Step 1: Clear Streamlit Cloud Cache**
        1. Go to your app → Click 'Manage app'
        2. Settings → Advanced → Clear cache
        3. Click 'Reboot app'
        
        **Step 2: Verify Dependencies**
        - Check that requirements.txt includes all Google Auth packages
        - Ensure Python version is 3.11.9 in runtime.txt
        
        **Step 3: Force Redeploy**
        - Make a small change to any file
        - Commit and push to GitHub
        """)
    
    st.code("pip install -r requirements.txt", language="bash")
    st.stop()

try:
    import pytz
    import base64
    import random, string, io, json, os
    from collections.abc import Mapping
    from datetime import datetime
    # Set timezone
    TZ = pytz.timezone("Africa/Cairo")
except Exception as e:
    st.error(f"❌ **Unexpected Error:** {e}")
    st.stop()

st.set_page_config(page_title="Yalla Shopping", page_icon="🛒", layout="wide")

# Password Protection
def check_password():
    """Returns `True` if the user had the correct password."""
    
    # Initialize session state keys
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if "show_password_change" not in st.session_state:
        st.session_state["show_password_change"] = False
    
    # Get current password from settings or use default
    current_password = "yalla2024"  # Default password
    
    if not st.session_state["password_correct"]:
        st.markdown("### 🔐 تسجيل الدخول")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            password_input = st.text_input("كلمة المرور", type="password", key="password")
        with col2:
            if st.button("دخول", type="primary"):
                if password_input == current_password:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("كلمة مرور خاطئة")
        
        # Password change option
        if st.button("تغيير كلمة المرور"):
            st.session_state["show_password_change"] = True
            
        if st.session_state["show_password_change"]:
            st.markdown("---")
            st.markdown("### 🔑 تغيير كلمة المرور")
            st.info("**ملاحظة:** لتغيير كلمة المرور، يجب تعديل الكود مباشرة في ملف `app.py`")
            st.code("current_password = \"كلمة_المرور_الجديدة\"")
            if st.button("إغلاق"):
                st.session_state["show_password_change"] = False
                
        return False
    else:
        return True

if not check_password():
    st.stop()

def load_logo():
    """Load and return logo as base64 string"""
    logo_paths = [
        "assets/logo_yalla_shopping.png",  # New logo
        "assets/logo_waadlash.jpg",        # Fallback logo
    ]
    
    for logo_path in logo_paths:
        try:
            with open(logo_path, "rb") as file:
                logo_bytes = file.read()
                return base64.b64encode(logo_bytes).decode()
        except FileNotFoundError:
            continue
    return None

def display_app_header():
    """Display app header with logo and title"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        logo_b64 = load_logo()
        if logo_b64:
            # Determine image type based on first few bytes or file extension
            if logo_b64.startswith('/9j/') or logo_b64.startswith('iVBOR'):
                mime_type = "image/png" if logo_b64.startswith('iVBOR') else "image/jpeg"
                st.image(f"data:{mime_type};base64,{logo_b64}", width=200)
            else:
                st.image(f"data:image/png;base64,{logo_b64}", width=200)
        else:
            st.title("🛒 Yalla Shopping")
        
        st.caption("Py Saso Mostafa")
        st.caption("Designed by Mohamed Ragab")

# Display logo and title
display_app_header()

st.markdown("---")

SCHEMAS = {
    "Products": ["SKU","Name","RetailPrice","InStock","LowStockThreshold","Active","Notes"],
    "Customers": ["CustomerID","Name","Phone","Address","Notes"],
    "Orders": ["OrderID","DateTime","CustomerID","CustomerName","CustomerAddress","Channel","Subtotal","Discount","Delivery","Deposit","Total","Status","Notes"],
    "OrderItems": ["OrderID","SKU","Name","Qty","UnitPrice","LineTotal"],
    "StockMovements": ["Timestamp","SKU","Change","Reason","Reference","Note"],
    "Settings": ["Key","Value"]
}

# ---------- Helpers ----------
def get_setting(settings_df, key, default: str = "") -> str:
    if (settings_df["Key"]==key).any():
        return settings_df.loc[settings_df["Key"]==key, "Value"].iloc[0]
    return default

def _coerce_to_plain_dict(value):
    """Return a plain dict from Streamlit AttrDict/dict or JSON string."""
    if isinstance(value, (dict, Mapping)):
        # Convert any nested AttrDicts by serializing
        try:
            return json.loads(json.dumps(value))
        except Exception:
            try:
                return dict(value)
            except Exception:
                pass
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            pass
    return None

def load_service_account_credentials():
    """Load Google service account credentials from Streamlit secrets.

    Supports either:
    - [gcp_service_account] (recommended)
    - GOOGLE_SERVICE_ACCOUNT (JSON string or inline TOML table)
    """
    try:
        if "gcp_service_account" in st.secrets:
            coerced = _coerce_to_plain_dict(st.secrets["gcp_service_account"]) 
            if coerced:
                # Fix private key formatting if needed
                if "private_key" in coerced:
                    private_key = coerced["private_key"]
                    # Clean up the private key - remove any extra whitespace and fix newlines
                    private_key = private_key.strip()
                    # Replace literal \n with actual newlines
                    if "\\n" in private_key:
                        private_key = private_key.replace("\\n", "\n")
                    
                    # Ensure proper formatting
                    lines = private_key.split('\n')
                    # Remove empty lines and strip whitespace
                    lines = [line.strip() for line in lines if line.strip()]
                    
                    # Reconstruct with proper formatting
                    if lines:
                        # Ensure proper BEGIN/END format
                        if not lines[0].startswith("-----BEGIN PRIVATE KEY-----"):
                            st.error("❌ Private key must start with '-----BEGIN PRIVATE KEY-----'")
                            st.stop()
                        if not lines[-1].endswith("-----END PRIVATE KEY-----"):
                            st.error("❌ Private key must end with '-----END PRIVATE KEY-----'")
                            st.stop()
                        
                        # Reconstruct the private key with proper newlines
                        coerced["private_key"] = '\n'.join(lines)
                
                return coerced
        
        if "GOOGLE_SERVICE_ACCOUNT" in st.secrets:
            coerced = _coerce_to_plain_dict(st.secrets["GOOGLE_SERVICE_ACCOUNT"]) 
            if coerced:
                # Fix private key formatting if needed
                if "private_key" in coerced:
                    private_key = coerced["private_key"]
                    private_key = private_key.strip()
                    if "\\n" in private_key:
                        private_key = private_key.replace("\\n", "\n")
                    
                    # Clean up formatting
                    lines = private_key.split('\n')
                    lines = [line.strip() for line in lines if line.strip()]
                    if lines:
                        coerced["private_key"] = '\n'.join(lines)
                
                return coerced
        
        st.error("❌ بيانات Service Account غير موجودة في secrets.")
        st.info("📋 أضف [gcp_service_account] أو GOOGLE_SERVICE_ACCOUNT في إعدادات Streamlit Cloud.")
        st.stop()
        
    except Exception as e:
        st.error(f"❌ خطأ في تحميل بيانات Service Account: {str(e)}")
        st.error("🔧 تأكد من صحة تنسيق البيانات في secrets")
        st.stop()
    
    return {}  # This line will never be reached due to st.stop()

def load_spreadsheet_id():
    """Read Spreadsheet ID from secrets or environment variables."""
    sid = str(st.secrets.get("SPREADSHEET_ID", "")).strip()
    if not sid:
        sid = os.environ.get("SPREADSHEET_ID", "").strip()
    return sid

@st.cache_resource(show_spinner=False)
def get_gspread_client(_sa_info: dict):
    """Create gspread client with proper error handling"""
    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        credentials = Credentials.from_service_account_info(_sa_info, scopes=scopes)
        return gspread.authorize(credentials)
        
    except Exception as e:
        st.error(f"❌ خطأ في إنشاء اتصال Google Sheets: {str(e)}")
        
        # Check for quota exceeded error
        if "quota" in str(e).lower() or "rate_limit" in str(e).lower():
            st.error("🚫 تم تجاوز حد استخدام Google Sheets API")
            st.info("⏳ انتظر دقيقة واحدة ثم حاول مرة أخرى")
            with st.expander("💡 نصائح لتجنب تجاوز الحد", expanded=True):
                st.markdown("""
                **لتجنب تجاوز حد الاستخدام:**
                1. تجنب تحديث الصفحة بشكل متكرر
                2. انتظر بين العمليات
                3. استخدم النظام بشكل طبيعي دون إعادة تحميل مستمرة
                
                **الحد الحالي:** 60 طلب في الدقيقة
                """)
        else:
            with st.expander("🛠️ إرشادات إصلاح المشكلة", expanded=True):
                st.markdown("""
                **تحقق من:**
                1. صحة بيانات Service Account في secrets
                2. أن Service Account له صلاحية الوصول للجدول
                3. أن SPREADSHEET_ID صحيح
                """)
        st.stop()

def ensure_worksheet(sh, name):
    try:
        ws = sh.worksheet(name)
        # Verify the worksheet has proper headers
        try:
            all_values = ws.get_all_values()
            expected_headers = SCHEMAS[name]
            
            if not all_values:
                # Empty worksheet, add headers
                ws.update(values=[expected_headers], range_name=f"A1:{chr(64+len(expected_headers))}1")
            else:
                first_row = all_values[0]
                # Check for duplicate headers or wrong headers
                has_duplicates = len(first_row) != len(set(first_row)) and any(first_row)
                headers_wrong = (len(first_row) < len(expected_headers) or 
                               not all(first_row[i] == expected_headers[i] for i in range(min(len(first_row), len(expected_headers)))))
                
                if has_duplicates or headers_wrong:
                    # Keep existing data but fix headers
                    if len(all_values) > 1:
                        data_rows = all_values[1:]
                        ws.clear()
                        ws.update(values=[expected_headers], range_name=f"A1:{chr(64+len(expected_headers))}1")
                        if data_rows:
                            # Ensure data fits schema
                            formatted_data = []
                            for row in data_rows:
                                # Skip empty rows
                                if any(cell.strip() for cell in row if cell):
                                    formatted_row = row[:len(expected_headers)] + [''] * max(0, len(expected_headers) - len(row))
                                    formatted_data.append(formatted_row)
                            if formatted_data:
                                end_col = chr(64 + len(expected_headers))
                                end_row = len(formatted_data) + 1
                                ws.update(values=formatted_data, range_name=f"A2:{end_col}{end_row}")
                    else:
                        ws.clear()
                        ws.update(values=[expected_headers], range_name=f"A1:{chr(64+len(expected_headers))}1")
                        
        except Exception as e:
            st.warning(f"تحذير: مشكلة في تحديث رؤوس الأعمدة لورقة {name}: {str(e)}")
            
    except gspread.exceptions.WorksheetNotFound:
        try:
            ws = sh.add_worksheet(title=name, rows=1000, cols=30)
            header = SCHEMAS[name]
            ws.update(values=[header], range_name=f"A1:{chr(64+len(header))}1")
        except Exception as e:
            st.error(f"خطأ في إنشاء ورقة {name}: {str(e)}")
            st.stop()
    return ws

@st.cache_data(ttl=120, show_spinner=False)
def _read_df_cached(ws_title: str, expected_cols_tuple: tuple):
    ws = ws_map[ws_title]
    expected_cols = list(expected_cols_tuple)
    
    try:
        # First check if worksheet has any data
        all_values = ws.get_all_values()
        if not all_values or len(all_values) < 1:
            # Empty worksheet, create with headers
            header = SCHEMAS[ws_title]
            ws.clear()
            ws.update(values=[header], range_name=f"A1:{chr(64+len(header))}1")
            # Return empty dataframe with expected columns
            df = pd.DataFrame(columns=header)
        else:
            # Get the expected headers from schema
            expected_headers = SCHEMAS[ws_title]
            first_row = all_values[0]
            
            # Check if headers match expected schema
            headers_match = (len(first_row) >= len(expected_headers) and 
                             all(first_row[i] == expected_headers[i] for i in range(len(expected_headers))))
            
            if not headers_match:
                # Fix headers by clearing and setting correct ones
                st.warning(f"إصلاح رؤوس الأعمدة لورقة {ws_title}")
                # Keep existing data but fix headers
                if len(all_values) > 1:
                    data_rows = all_values[1:]  # Keep data rows
                    ws.clear()
                    ws.update(values=[expected_headers], range_name=f"A1:{chr(64+len(expected_headers))}1")
                    if data_rows:
                        # Add data back, ensuring it fits the schema
                        formatted_data = []
                        for row in data_rows:
                            # Pad or trim row to match expected columns
                            formatted_row = row[:len(expected_headers)] + [''] * max(0, len(expected_headers) - len(row))
                            formatted_data.append(formatted_row)
                        if formatted_data:
                            end_col = chr(64 + len(expected_headers))
                            end_row = len(formatted_data) + 1
                            ws.update(values=formatted_data, range_name=f"A2:{end_col}{end_row}")
                else:
                    ws.clear()
                    ws.update(values=[expected_headers], range_name=f"A1:{chr(64+len(expected_headers))}1")
            
            # Now get records with expected headers to handle duplicates
            try:
                records = ws.get_all_records(expected_headers=expected_headers)
                df = pd.DataFrame(records)
            except Exception:
                # If still failing, try with empty_value parameter
                try:
                    records = ws.get_all_records(expected_headers=expected_headers, empty_value='')
                    df = pd.DataFrame(records)
                except Exception:
                    # Last resort: manually parse the data
                    all_values = ws.get_all_values()
                    if len(all_values) > 1:
                        data_rows = all_values[1:]
                        df = pd.DataFrame(data_rows, columns=expected_headers[:len(all_values[0]) if all_values else len(expected_headers)])
                    else:
                        df = pd.DataFrame(columns=expected_headers)
            
    except Exception as e:
        st.error(f"خطأ في قراءة ورقة {ws_title}: {str(e)}")
        # Create empty dataframe with expected schema
        df = pd.DataFrame(columns=expected_cols)
    
    # Ensure all expected columns exist
    for c in expected_cols:
        if c not in df.columns:
            df[c] = "" if c not in ["RetailPrice","InStock","LowStockThreshold","Subtotal","Discount","Delivery","Deposit","Total","Qty","UnitPrice","LineTotal"] else 0
    
    # Return only the expected columns in the right order
    result_df = df[expected_cols]
    # Ensure we return a DataFrame, not a Series
    if isinstance(result_df, pd.Series):
        result_df = result_df.to_frame().T
    return result_df

def _coerce_numeric(df: pd.DataFrame, cols):
    df_copy = df.copy()
    for c in cols:
        if c in df_copy.columns:
            df_copy[c] = pd.to_numeric(df_copy[c], errors="coerce").fillna(0)
    return df_copy

def _coerce_str(df: pd.DataFrame, cols):
    df_copy = df.copy()
    for c in cols:
        if c in df_copy.columns:
            df_copy[c] = df_copy[c].astype(str)
    return df_copy

def read_df(ws, expected_cols, schema_name=None):
    # Use worksheet title as the cache key to reduce API reads
    df = _read_df_cached(ws.title, tuple(expected_cols)).copy()
    # Normalize types for reliable arithmetic and concatenation
    if schema_name == "Products":
        df = _coerce_str(df, ["SKU","Name","Active","Notes"]) 
        df = _coerce_numeric(df, ["RetailPrice","InStock","LowStockThreshold"])
        df = df.astype({"InStock":"int64","LowStockThreshold":"int64"})
    elif schema_name == "Customers":
        df = _coerce_str(df, ["CustomerID","Name","Phone","Address","Notes"]) 
    elif schema_name == "Orders":
        df = _coerce_str(df, ["OrderID","DateTime","CustomerID","CustomerName","CustomerAddress","Channel","Status","Notes"]) 
        df = _coerce_numeric(df, ["Subtotal","Discount","Delivery","Deposit","Total"]) 
    elif schema_name == "OrderItems":
        df = _coerce_str(df, ["OrderID","SKU","Name"]) 
        df = _coerce_numeric(df, ["Qty","UnitPrice","LineTotal"])
        df = df.astype({"Qty":"int64"})
    elif schema_name == "StockMovements":
        df = _coerce_str(df, ["Timestamp","SKU","Reason","Reference","Note"]) 
        df = _coerce_numeric(df, ["Change"])
        df = df.astype({"Change":"int64"})
    return df

def write_df(ws, df):
    try:
        # Clear the worksheet first
        ws.clear()
        if df.empty:
            # Even if empty, write headers
            ws_name = ws.title
            if ws_name in SCHEMAS:
                headers = SCHEMAS[ws_name]
                ws.update(values=[headers], range_name=f"A1:{chr(64+len(headers))}1")
            return
        
        # Ensure dataframe has the right columns in the right order
        ws_name = ws.title
        if ws_name in SCHEMAS:
            expected_cols = SCHEMAS[ws_name]
            # Add missing columns
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = "" if col not in ["RetailPrice","InStock","LowStockThreshold","Subtotal","Discount","Delivery","Deposit","Total","Qty","UnitPrice","LineTotal"] else 0
            # Reorder columns to match schema
            df = df[expected_cols]
        
        # Convert to string and handle NaN values
        df_str = df.fillna('').astype(str)
        values = [df_str.columns.tolist()] + df_str.values.tolist()
        
        # Update the worksheet
        end_col = chr(64 + len(values[0]))
        end_row = len(values)
        ws.update(values=values, range_name=f"A1:{end_col}{end_row}")
        
    except Exception as e:
        st.error(f"خطأ في كتابة البيانات: {str(e)}")
        raise e

def validate_worksheet_data(ws_name):
    """Validate and fix worksheet structure if needed"""
    try:
        ws = ws_map[ws_name]
        expected_headers = SCHEMAS[ws_name]
        
        # Get current data
        all_values = ws.get_all_values()
        if not all_values:
            # Empty worksheet, add headers
            ws.update(values=[expected_headers], range_name=f"A1:{chr(64+len(expected_headers))}1")
            return True
            
        first_row = all_values[0]
        
        # Check for issues
        has_duplicates = len(first_row) != len(set(first_row)) and any(first_row)
        headers_wrong = (len(first_row) < len(expected_headers) or 
                        not all(first_row[i] == expected_headers[i] for i in range(min(len(first_row), len(expected_headers)))))
        
        if has_duplicates or headers_wrong:
            st.warning(f"إصلاح بنية البيانات لورقة {ws_name}")
            # Fix the worksheet
            ensure_worksheet(ws_map.sh, ws_name)
            return True
            
        return True
    except Exception as e:
        st.error(f"خطأ في التحقق من ورقة {ws_name}: {str(e)}")
        return False

def gen_id(prefix):
    now = datetime.now(TZ).strftime("%Y%m%d%H%M%S")
    return f"{prefix}{now}{''.join(random.choices(string.digits, k=4))}"

def invoice_html(order_row, items_df, business_name="Yalla Shopping", business_phone="", business_addr="", logo_b64=""):
    # Use the new logo if no logo is provided
    if not logo_b64:
        logo_b64 = load_logo()
    order_meta = {k: order_row[k] for k in order_row.index}
    
    # Get customer address from the order data
    customer_address = order_meta.get('CustomerAddress', '')
    
    # Calculate final amount after deposit
    subtotal = float(order_meta.get('Subtotal', 0))
    discount = float(order_meta.get('Discount', 0))
    delivery = float(order_meta.get('Delivery', 0))
    deposit = float(order_meta.get('Deposit', 0))
    
    # Calculate amounts
    after_discount = subtotal - discount
    final_total = after_discount + delivery
    remaining_balance = final_total - deposit
    
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
.logo-container {{ text-align: center; margin-bottom: 10px; }}
.logo {{ max-height: 100px; max-width: 200px; border-radius: 8px; }}
.logo-placeholder {{ 
    font-size: 18px; 
    font-weight: bold; 
    color: #008080; 
    padding: 15px; 
    border: 2px solid #008080; 
    border-radius: 12px; 
    text-align: center;
    background: linear-gradient(135deg, #f0f8ff, #e6f3ff);
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}}
h1 {{ margin: 0; }}
.small {{ color:#555; font-size: 12px; }}
.table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
.table th, .table td {{ border: 1px solid #ddd; padding: 8px; }}
.table th {{ background: #f7f7f7; }}
.right {{ text-align:right; }}
.center {{ text-align:center; }}
.summary {{ margin-top: 16px; width: 100%; max-width: 400px; margin-left:auto; }}
.summary table {{ width:100%; border-collapse:collapse; }}
.summary td {{ padding:6px 0; }}
.summary .highlight {{ background: #f0f8ff; font-weight: bold; }}
hr {{ border: none; border-top: 1px dashed #aaa; margin: 16px 0; }}
.footer {{ margin-top: 24px; font-size: 12px; color:#444; }}
.badge {{ display:inline-block; padding:2px 8px; background:#eee; border-radius: 6px; font-size:12px; }}
.customer-info {{ background: #f9f9f9; padding: 12px; border-radius: 8px; margin: 16px 0; }}
</style>
</head>
<body>
  <div class="header">
    <div>
      <h1>فاتورة</h1>
      <div class="small">رقم: <b>{order_meta['OrderID']}</b></div>
      <div class="small">التاريخ: <b>{order_meta['DateTime']}</b></div>
      <div class="small">القناة: {order_meta.get('Channel','')}</div>
    </div>
    <div class="right">
      <div class="logo-container">
        {f'<img src="data:image/png;base64,{logo_b64}" class="logo" alt="Yalla Shopping Logo" />' if logo_b64 else '<div class="logo-placeholder">🛒 Yalla Shopping<br><small>Py Saso Mostafa</small></div>'}
      </div>
      <div><b>{business_name}</b></div>
      <div class="small">{business_phone}</div>
      <div class="small">{business_addr}</div>
    </div>
  </div>

  <hr />

  <div class="customer-info">
    <div><strong>العميل:</strong> <b>{order_meta['CustomerName']}</b></div>
    <div class="small"><strong>كود العميل:</strong> {order_meta.get('CustomerID','')}</div>
    {f'<div class="small"><strong>العنوان:</strong> {customer_address}</div>' if customer_address else ''}
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
      <tr><td>إجمالي المنتجات:</td><td class="right">{subtotal:.2f}</td></tr>
      <tr><td>خصم:</td><td class="right">-{discount:.2f}</td></tr>
      <tr><td>بعد الخصم:</td><td class="right highlight">{after_discount:.2f}</td></tr>
      <tr><td>توصيل:</td><td class="right">+{delivery:.2f}</td></tr>
      <tr><td><strong>الإجمالي النهائي:</strong></td><td class="right highlight"><strong>{final_total:.2f}</strong></td></tr>
      <tr><td>عربون مدفوع:</td><td class="right">-{deposit:.2f}</td></tr>
      <tr class="highlight"><td><strong>المتبقي:</strong></td><td class="right"><strong>{remaining_balance:.2f}</strong></td></tr>
      <tr><td>الحالة:</td><td class="right">{order_meta['Status']}</td></tr>
    </table>
  </div>

  <div class="footer">
    <p><strong>ملاحظات:</strong> {order_meta.get('Notes', 'لا توجد ملاحظات')}</p>
    <p>شكراً لتعاملكم معنا ✨</p>
    <p class="small">تم إنشاء هذه الفاتورة بواسطة نظام Yalla Shopping</p>
  </div>
</body>
</html>
"""
    return html

# ---------- App ----------
st.title("🛒 Yalla Shopping")
st.caption("واجهة تعمل من اللابتوب والموبايل. قاعدة بيانات: Google Sheets.")

# Load credentials (supporting multiple secret formats)
sa_info = load_service_account_credentials()
if sa_info is None:
    st.error("فشل في تحميل بيانات Service Account")
    st.stop()

client = get_gspread_client(sa_info)

# Load Spreadsheet ID from secrets or environment
spreadsheet_id = load_spreadsheet_id()
if not spreadsheet_id:
    st.error("يجب إضافة SPREADSHEET_ID داخل secrets أو كمتغير بيئة. راجع الخطوات في README_AR.md.")
    st.stop()

try:
    sh = client.open_by_key(spreadsheet_id)
except Exception as e:
    st.error(f"خطأ في فتح جدول البيانات: {str(e)}")
    st.error("تأكد من صحة SPREADSHEET_ID وأن Service Account له صلاحية الوصول للجدول.")
    st.stop()

class LazyWs:
    def __init__(self, sh):
        self.sh = sh
        self._cache = {}
    def __getitem__(self, name: str):
        if name in self._cache:
            return self._cache[name]
        ws = ensure_worksheet(self.sh, name)
        self._cache[name] = ws
        return ws

ws_map = LazyWs(sh)

try:
    settings_ws = ws_map["Settings"]
    settings_df = read_df(settings_ws, SCHEMAS["Settings"])
    biz_name = get_setting(settings_df, "BusinessName", "Yalla Shopping")
    biz_phone = get_setting(settings_df, "BusinessPhone", "")
    biz_addr  = get_setting(settings_df, "BusinessAddress", "")
    logo_b64  = get_setting(settings_df, "BusinessLogoB64", "")
except Exception as e:
    st.error(f"خطأ في تحميل الإعدادات: {str(e)}")
    # Use default values if settings can't be loaded
    biz_name = "Yalla Shopping"
    biz_phone = ""
    biz_addr = ""
    logo_b64 = ""

# Add system status and logout in sidebar
with st.sidebar:
    # Logout button
    if st.button("🚪 تسجيل الخروج", type="secondary"):
        st.session_state["password_correct"] = False
        st.rerun()
    
    st.markdown("---")
    
    if st.button("🔧 فحص النظام"):
        st.write("**حالة النظام:**")
        try:
            # Check all required worksheets
            required_sheets = ["Products", "Customers", "Orders", "OrderItems", "StockMovements", "Settings"]
            for sheet_name in required_sheets:
                try:
                    ws = ws_map[sheet_name]
                    st.success(f"✅ {sheet_name}")
                except Exception as e:
                    st.error(f"❌ {sheet_name}: {str(e)}")
        except Exception as e:
            st.error(f"خطأ في فحص النظام: {str(e)}")

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
    try:
        # Validate worksheets before reading
        if not validate_worksheet_data("Products"):
            st.stop()
        if not validate_worksheet_data("Orders"):
            st.stop()
            
        products = read_df(ws_map["Products"], SCHEMAS["Products"], "Products")
        orders = read_df(ws_map["Orders"], SCHEMAS["Orders"], "Orders")
    except Exception as e:
        st.error(f"خطأ في تحميل البيانات: {str(e)}")
        st.error("تأكد من وجود أوراق Products و Orders في جدول البيانات مع الرؤوس الصحيحة.")
        if st.button("إعادة تهيئة أوراق البيانات"):
            try:
                ensure_worksheet(sh, "Products")
                ensure_worksheet(sh, "Orders")
                st.success("تم إعادة تهيئة أوراق البيانات. يرجى إعادة تحميل الصفحة.")
            except Exception as e2:
                st.error(f"فشل في إعادة التهيئة: {str(e2)}")
        st.stop()

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
    if not orders.empty and "DateTime" in orders.columns:
        try:
            # Ensure DateTime is string for sorting
            orders_sorted = orders.copy()
            orders_sorted["DateTime"] = orders_sorted["DateTime"].astype(str)
            # Check if DataFrame is not empty and has the column
            if not orders_sorted.empty and "DateTime" in orders_sorted.columns:
                st.dataframe(orders_sorted.sort_values(by="DateTime", ascending=False).head(10))
            else:
                st.dataframe(orders.head(10))
        except Exception as e:
            st.warning(f"خطأ في ترتيب الطلبات: {str(e)}")
            st.dataframe(orders.head(10))
    else:
        st.dataframe(orders.head(10))

# -------- POS --------
elif page == "🧾 بيع جديد (POS)":
    try:
        # Validate worksheets before reading
        validate_worksheet_data("Products")
        validate_worksheet_data("Customers")
        
        products = read_df(ws_map["Products"], SCHEMAS["Products"], "Products")
        products = products[products["Active"]!="No"]
        customers = read_df(ws_map["Customers"], SCHEMAS["Customers"], "Customers")
    except Exception as e:
        st.error(f"خطأ في تحميل بيانات المنتجات والعملاء: {str(e)}")
        st.error("تأكد من وجود أوراق Products و Customers في جدول البيانات.")
        if st.button("إعادة تهيئة أوراق البيانات"):
            try:
                ensure_worksheet(sh, "Products")
                ensure_worksheet(sh, "Customers")
                st.success("تم إعادة تهيئة أوراق البيانات. يرجى إعادة تحميل الصفحة.")
            except Exception as e2:
                st.error(f"فشل في إعادة التهيئة: {str(e2)}")
        st.stop()

    st.markdown("### بيانات العميل")
    colA, colB = st.columns(2)
    with colA:
        mode = st.selectbox("اختر عميل", ["عميل موجود", "عميل جديد"])
    with colB:
        channel = st.selectbox("قناة الطلب", ["Facebook Page","Instagram","Phone","WhatsApp","Other"])

    cust_id, cust_name, cust_phone, cust_address, cust_notes = "", "", "", "", ""
    if mode == "عميل موجود" and not customers.empty:
        customer_labels = (customers["Name"].astype(str) + " — " + customers["Phone"].astype(str))
        sel = st.selectbox("العميل", customer_labels.tolist())
        row = customers[customer_labels == sel].iloc[0]
        cust_id = row["CustomerID"]; cust_name = row["Name"]; cust_phone=row["Phone"]; cust_address=row["Address"]
    else:
        cust_name = st.text_input("اسم العميل")
        cust_phone = st.text_input("رقم الموبايل")
        cust_address = st.text_input("العنوان")
        cust_notes = st.text_area("ملاحظات", "")

    st.markdown("---")
    st.markdown("### اختيار المنتجات")

    # Search and filter helpers for easier selection
    with st.container():
        c1, c2 = st.columns([3,1])
        with c1:
            query = st.text_input("🔎 ابحث بالاسم أو الكود (SKU)", value="")
        with c2:
            only_instock = st.checkbox("عرض المتاح فقط", value=False)

    filtered = products.copy()
    if query.strip():
        q = query.strip()
        mask = (
            filtered["Name"].astype(str).str.contains(q, case=False, na=False) |
            filtered["SKU"].astype(str).str.contains(q, case=False, na=False)
        )
        filtered = filtered[mask]
    if only_instock:
        filtered = filtered[filtered["InStock"].astype(float) > 0]

    show_cols = ["SKU","Name","RetailPrice","InStock"]
    edit_df = filtered[show_cols].copy()
    edit_df["Qty"] = 0
    edit_df = st.data_editor(edit_df, num_rows="dynamic", use_container_width=True, key="pos_table")

    # Quick add (typeahead select + qty) to speed up POS
    with st.expander("➕ إضافة سريعة للسلة", expanded=False):
        labels = (products["SKU"].astype(str) + " — " + products["Name"].astype(str)).tolist()
        quick_label = st.selectbox("اختر منتج", labels, index=None, placeholder="اكتب الاسم أو الكود…")
        quick_qty = st.number_input("الكمية", min_value=1, value=1, step=1)
        col_add1, col_add2 = st.columns(2)
        with col_add1:
            if st.button("إضافة", key="quick_add_btn") and quick_label:
                sku_q = str(quick_label).split(" — ")[0]
                if "quick_cart" not in st.session_state:
                    st.session_state["quick_cart"] = {}
                st.session_state["quick_cart"][sku_q] = st.session_state["quick_cart"].get(sku_q, 0) + int(quick_qty)
                st.success("تمت الإضافة للسلة المؤقتة ✅")
        with col_add2:
            if st.button("تفريغ السلة المؤقتة"):
                st.session_state["quick_cart"] = {}

        edit_df["UnitPrice"] = edit_df["RetailPrice"].astype(float)
    edit_df["LineTotal"] = edit_df["Qty"].astype(float) * edit_df["UnitPrice"].astype(float)
    selected_editor = edit_df[edit_df["Qty"].astype(float) > 0]

    # Build quick cart dataframe if present and merge with editor selection
    quick_df = pd.DataFrame(columns=["SKU","Name","Qty","UnitPrice","LineTotal"])
    if "quick_cart" in st.session_state and st.session_state["quick_cart"]:
        rows = []
        base = products.set_index("SKU")
        for sku_q, qty_q in st.session_state["quick_cart"].items():
            if sku_q in base.index:
                prod = base.loc[sku_q]
                price = float(prod["RetailPrice"])
                rows.append([str(sku_q), str(prod["Name"]), int(qty_q), price, price*int(qty_q)])
        if rows:
            quick_df = pd.DataFrame(rows, columns=["SKU","Name","Qty","UnitPrice","LineTotal"])

    if not selected_editor.empty or not quick_df.empty:
        tmp = pd.concat([selected_editor[["SKU","Name","Qty","UnitPrice","LineTotal"]], quick_df], ignore_index=True)
        # Group same SKU
        selected = tmp.groupby(["SKU","Name","UnitPrice"], as_index=False)["Qty"].sum()
        selected["LineTotal"] = selected["Qty"].astype(float) * selected["UnitPrice"].astype(float)
    else:
        selected = pd.DataFrame(columns=["SKU","Name","Qty","UnitPrice","LineTotal"])

    subtotal = selected["LineTotal"].sum()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        discount = st.number_input("خصم", min_value=0.0, value=0.0, step=1.0)
    with col2:
        delivery = st.number_input("توصيل", min_value=0.0, value=0.0, step=1.0)
    with col3:
        deposit = st.number_input("عربون", min_value=0.0, value=0.0, step=1.0)
    with col4:
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
            existing = read_df(ws, SCHEMAS["Customers"], "Customers")
            updated = pd.concat([existing, new_cust], ignore_index=True)
            write_df(ws, updated)

        stock_ok = True
        prod_df = read_df(ws_map["Products"], SCHEMAS["Products"], "Products").set_index("SKU")
        for _, r in selected.iterrows():
            sku = str(r["SKU"]); need = int(float(str(r["Qty"])))
            available = int(float(str(prod_df.loc[sku, "InStock"]))) if sku in prod_df.index else 0
            if need > available:
                stock_ok = False
                st.error(f"المخزون غير كافٍ للمنتج {sku} — المتاح {available} والطلب {need}")
        if stock_ok:
            # Validate required worksheets
            validate_worksheet_data("Orders")
            validate_worksheet_data("OrderItems")
            validate_worksheet_data("StockMovements")
            
            order_id = gen_id("ORD")
            now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
            order_row = pd.Series({
                "OrderID": order_id, "DateTime": now, "CustomerID": cust_id, "CustomerName": cust_name,
                "CustomerAddress": cust_address, "Channel": channel, "Subtotal": float(subtotal),
                "Discount": float(discount), "Delivery": float(delivery), "Deposit": float(deposit), "Total": float(total),
                "Status": status, "Notes": notes
            })
            orders_ws = ws_map["Orders"]
            orders_df = read_df(orders_ws, SCHEMAS["Orders"], "Orders")
            orders_df = pd.concat([orders_df, pd.DataFrame([order_row])], ignore_index=True)
            write_df(orders_ws, orders_df)

            items_ws = ws_map["OrderItems"]
            items_df = read_df(items_ws, SCHEMAS["OrderItems"], "OrderItems")
            new_items = []
            for _, r in selected.iterrows():
                new_items.append([order_id, str(r["SKU"]), str(r["Name"]), int(float(str(r["Qty"]))), float(str(r["UnitPrice"])), float(str(r["LineTotal"]))])
            add_items_df = pd.DataFrame(new_items, columns=SCHEMAS["OrderItems"])
            items_df = pd.concat([items_df, add_items_df], ignore_index=True)
            write_df(items_ws, items_df)

            stock_ws = ws_map["StockMovements"]
            stock_mov = read_df(stock_ws, SCHEMAS["StockMovements"], "StockMovements")
            prod_df = read_df(ws_map["Products"], SCHEMAS["Products"], "Products").set_index("SKU")

            for _, r in selected.iterrows():
                sku = str(r["SKU"]); qty = int(float(str(r["Qty"])))
                if sku in prod_df.index:
                    current = int(float(str(prod_df.loc[sku,"InStock"])))
                    prod_df.loc[sku,"InStock"] = current - qty
                stock_mov = pd.concat([stock_mov, pd.DataFrame([[now, sku, -qty, "Sale", order_id, ""]], columns=SCHEMAS["StockMovements"])], ignore_index=True)

            write_df(ws_map["Products"], prod_df.reset_index())
            write_df(stock_ws, stock_mov)

            st.success(f"تم إنشاء الطلب {order_id} وتحديث المخزون ✅")
            # Use the file system logo if available, otherwise use uploaded logo
            invoice_logo = load_logo() or logo_b64
            invoice = invoice_html(order_row, add_items_df, business_name=biz_name, business_phone=biz_phone, business_addr=biz_addr, logo_b64=invoice_logo)
            st.download_button("🧾 تحميل الفاتورة (HTML للطباعة)", data=invoice.encode("utf-8"), file_name=f"invoice_{order_id}.html", mime="text/html", use_container_width=True)

# -------- Products --------
elif page == "📦 المنتجات":
    validate_worksheet_data("Products")
    ws = ws_map["Products"]
    df = read_df(ws, SCHEMAS["Products"], "Products")

    st.markdown("### إضافة/تعديل منتج")
    c1, c2, c3 = st.columns(3)
    with c1:
        sku = st.text_input("كود الصنف (SKU)")
        name = st.text_input("اسم المنتج")
        active = st.selectbox("نشط؟", ["Yes","No"], index=0)
    with c2:
        retail = st.number_input("سعر المنتج", min_value=0.0, value=0.0, step=1.0)
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
                df.loc[idx, ["Name","RetailPrice","InStock","LowStockThreshold","Active","Notes"]] = [name, retail, instock, lowthr, active, notes]
            else:
                df = pd.concat([df, pd.DataFrame([[sku,name,retail,instock,lowthr,active,notes]], columns=SCHEMAS["Products"])], ignore_index=True)
            write_df(ws, df)
            st.success("تم الحفظ ✅")
        else:
            st.error("الرجاء إدخال كود الصنف واسم المنتج")

    if colB.button("🧹 تفريغ الحقول"):
        st.rerun()

    st.markdown("---")
    st.subheader("قائمة المنتجات")
    st.dataframe(df, use_container_width=True)

# -------- Customers --------
elif page == "👤 العملاء":
    validate_worksheet_data("Customers")
    ws = ws_map["Customers"]
    df = read_df(ws, SCHEMAS["Customers"], "Customers")

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
        st.rerun()

    st.markdown("---")
    
    # Customer Search and Order History
    st.subheader("🔍 البحث عن العميل وطلباته")
    
    # Search by name or phone
    search_query = st.text_input("ابحث بالاسم أو رقم الموبايل", placeholder="اكتب اسم العميل أو رقم الموبايل...")
    
    if search_query:
        # Search in customers
        name_mask = df["Name"].astype(str).str.contains(search_query, case=False, na=False)
        phone_mask = df["Phone"].astype(str).str.contains(search_query, case=False, na=False)
        search_results = df[name_mask | phone_mask]
        
        if not search_results.empty:
            st.success(f"تم العثور على {len(search_results)} عميل")
            
            # Show customer details
            for _, customer in search_results.iterrows():
                with st.expander(f"👤 {customer['Name']} - {customer['Phone']}", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**كود العميل:** {customer['CustomerID']}")
                        st.write(f"**العنوان:** {customer['Address']}")
                        st.write(f"**الملاحظات:** {customer['Notes']}")
                    
                    with col2:
                        # Get customer orders
                        try:
                            validate_worksheet_data("Orders")
                            validate_worksheet_data("OrderItems")
                            orders = read_df(ws_map["Orders"], SCHEMAS["Orders"], "Orders")
                            customer_orders = orders[orders["CustomerID"] == customer["CustomerID"]]
                        except Exception as e:
                            st.error(f"خطأ في تحميل طلبات العميل: {str(e)}")
                            customer_orders = pd.DataFrame()
                        
                        if not customer_orders.empty:
                            st.write(f"**إجمالي الطلبات:** {len(customer_orders)}")
                            st.write(f"**إجمالي المبيعات:** {customer_orders['Total'].astype(float).sum():.2f}")
                            
                            # Show order details
                            st.write("**تفاصيل الطلبات:**")
                            for _, order in customer_orders.iterrows():
                                order_items = read_df(ws_map["OrderItems"], SCHEMAS["OrderItems"], "OrderItems")
                                order_products = order_items[order_items["OrderID"] == order["OrderID"]]
                                
                                st.write(f"📋 **طلب {order['OrderID']}** - {order['DateTime']}")
                                st.write(f"   الحالة: {order['Status']} | القناة: {order['Channel']}")
                                st.write(f"   الإجمالي: {order['Total']} | الخصم: {order['Discount']} | التوصيل: {order['Delivery']} | العربون: {order['Deposit']}")
                                
                                if not order_products.empty:
                                    st.write("   المنتجات:")
                                    for _, item in order_products.iterrows():
                                        st.write(f"     • {item['Name']} (SKU: {item['SKU']}) - الكمية: {item['Qty']} - السعر: {item['UnitPrice']}")
                                st.write("---")
                        else:
                            st.info("لا توجد طلبات لهذا العميل")
        else:
            st.warning("لم يتم العثور على عميل بهذه البيانات")

    st.markdown("---")
    st.subheader("قائمة العملاء")
    st.dataframe(df, use_container_width=True)

# -------- Stock Movements --------
elif page == "📥 حركة المخزون":
    validate_worksheet_data("Products")
    validate_worksheet_data("StockMovements")
    
    ws_prod = ws_map["Products"]
    ws_mov  = ws_map["StockMovements"]

    products = read_df(ws_prod, SCHEMAS["Products"], "Products")
    movements = read_df(ws_mov, SCHEMAS["StockMovements"], "StockMovements")

    st.markdown("### إضافة حركة مخزون")
    c1, c2, c3 = st.columns(3)
    with c1:
        product_labels = (products["SKU"].astype(str) + " — " + products["Name"].astype(str)) if not products.empty else pd.Series([], dtype=str)
        selected_label = st.selectbox("اختر المنتج (SKU — Name)", product_labels.tolist())
        sku = str(selected_label).split(" — ")[0] if selected_label else ""
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
            products_copy = products.copy()
            products_copy.set_index("SKU", inplace=True)
            if sku_only in products_copy.index:
                current = int(float(str(products_copy.loc[sku_only,"InStock"])))
                products_copy.loc[sku_only,"InStock"] = current + int(change)
                products_copy = products_copy.reset_index()
                write_df(ws_prod, products_copy)
                st.success("تم تحديث المخزون ✅")
        else:
            st.error("يرجى اختيار منتج وتحديد كمية صحيحة")

    st.markdown("---")
    st.subheader("سجل الحركات")
    if not movements.empty and "Timestamp" in movements.columns:
        try:
            # Ensure Timestamp is string for sorting
            movements_sorted = movements.copy()
            movements_sorted["Timestamp"] = movements_sorted["Timestamp"].astype(str)
            # Check if DataFrame is not empty and has the column
            if not movements_sorted.empty and "Timestamp" in movements_sorted.columns:
                st.dataframe(movements_sorted.sort_values(by="Timestamp", ascending=False), use_container_width=True)
            else:
                st.dataframe(movements, use_container_width=True)
        except Exception as e:
            st.warning(f"خطأ في ترتيب الحركات: {str(e)}")
            st.dataframe(movements, use_container_width=True)
    else:
        st.dataframe(movements, use_container_width=True)

# -------- Reports --------
elif page == "📈 التقارير":
    validate_worksheet_data("Orders")
    validate_worksheet_data("OrderItems")
    validate_worksheet_data("Products")
    
    orders = read_df(ws_map["Orders"], SCHEMAS["Orders"], "Orders")
    items  = read_df(ws_map["OrderItems"], SCHEMAS["OrderItems"], "OrderItems")
    products = read_df(ws_map["Products"], SCHEMAS["Products"], "Products")

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
    
    # Password change section
    with st.expander("🔑 تغيير كلمة المرور", expanded=False):
        st.info("**ملاحظة:** لتغيير كلمة المرور، يجب تعديل الكود مباشرة في ملف `app.py`")
        st.code("current_password = \"كلمة_المرور_الجديدة\"")
    
    st.markdown("---")
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
        st.success("✅ تم تحميل الشعار بنجاح! سيظهر في الفواتير.")
    
    # Show current logo - check both uploaded and file system logos
    current_logo_b64 = load_logo()
    if current_logo_b64 or logo_b64:
        st.markdown("**الشعار الحالي:**")
        display_logo = logo_b64 if logo_b64 else current_logo_b64
        st.image(f"data:image/png;base64,{display_logo}", caption="الشعار المستخدم حالياً", width=150)
        
        if current_logo_b64 and not logo_b64:
            st.success("✅ يتم استخدام الشعار من ملف assets/logo_yalla_shopping.png")
    else:
        st.info("ℹ️ لا يوجد شعار محدد حالياً. سيظهر النص الافتراضي '🛒 Yalla Shopping' في الفواتير.")
        st.markdown("**لإضافة الشعار الجديد:**")
        st.code("احفظ الشعار كملف assets/logo_yalla_shopping.png في مجلد المشروع")

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