# 🛒 Yalla Shopping - Makeup POS System

A comprehensive Point of Sale (POS) system built with Streamlit and Google Sheets for makeup and beauty product businesses.

## ✨ Features

- **🧾 Point of Sale (POS)** - Complete sales interface with product selection
- **📦 Product Management** - Add, edit, and track inventory
- **👤 Customer Management** - Customer database with order history
- **📊 Dashboard** - Real-time sales analytics and low stock alerts
- **📈 Reports** - Sales reports and inventory tracking
- **📥 Stock Management** - Track stock movements and adjustments
- **🧾 Invoice Generation** - Professional HTML invoices with business branding
- **🔐 Password Protection** - Secure access to the system
- **🌐 Multi-language** - Arabic interface with RTL support

## 🚀 Quick Start

### Prerequisites
- Python 3.11.9
- Google Sheets API access
- Streamlit Cloud account (for deployment)

### Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Mohmedragab2398/makeup-pos-system.git
   cd makeup-pos-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Test the installation**
   ```bash
   python test_app.py
   python check_dependencies.py
   python health_check.py
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

### 🌐 Streamlit Cloud Deployment

1. **Fork this repository** to your GitHub account

2. **Create a Google Sheets spreadsheet** and note the Spreadsheet ID

3. **Set up Google Service Account**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable Google Sheets API and Google Drive API
   - Create a Service Account and download the JSON key
   - Share your spreadsheet with the service account email

4. **Deploy to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Deploy from your forked repository
   - Set main file path: `app.py`

5. **Configure Secrets** in Streamlit Cloud:
   ```toml
   # Spreadsheet ID from your Google Sheets URL
   SPREADSHEET_ID = "your_spreadsheet_id_here"
   
   # Google Service Account credentials
   [gcp_service_account]
   type = "service_account"
   project_id = "your-project-id"
   private_key_id = "your-private-key-id"
   private_key = "-----BEGIN PRIVATE KEY-----\nYOUR-PRIVATE-KEY\n-----END PRIVATE KEY-----\n"
   client_email = "your-service-account@your-project.iam.gserviceaccount.com"
   client_id = "your-client-id"
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
   ```

## 🔧 Configuration

### Default Login
- **Username**: No username required
- **Password**: `yalla2024`

### Business Settings
Configure your business information in the Settings page:
- Business name
- Phone number
- Address
- Logo (for invoices)

## 📊 Database Schema

The system uses Google Sheets with the following worksheets:

- **Products**: SKU, Name, RetailPrice, InStock, LowStockThreshold, Active, Notes
- **Customers**: CustomerID, Name, Phone, Address, Notes
- **Orders**: OrderID, DateTime, CustomerID, CustomerName, CustomerAddress, Channel, Subtotal, Discount, Delivery, Deposit, Total, Status, Notes
- **OrderItems**: OrderID, SKU, Name, Qty, UnitPrice, LineTotal
- **StockMovements**: Timestamp, SKU, Change, Reason, Reference, Note
- **Settings**: Key, Value

## 🛠️ Development

### Project Structure
```
makeup-pos-system/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── runtime.txt                     # Python version specification
├── check_dependencies.py           # Dependency verification script
├── health_check.py                 # Health check script
├── test_app.py                     # Comprehensive test suite
├── DEPLOYMENT_FINAL_SOLUTION.md    # Deployment troubleshooting guide
├── assets/                         # Static assets
│   └── logo_waadlash.jpg          # Default logo
├── data/                          # Sample data files
│   ├── customers_waadlash.csv
│   └── products_waadlash.csv
└── templates/                     # HTML templates
    └── invoice_template.html      # Invoice template
```

### Testing
Run the comprehensive test suite:
```bash
python test_app.py
```

### Troubleshooting
If you encounter import errors, refer to `DEPLOYMENT_FINAL_SOLUTION.md` for detailed troubleshooting steps.

## 🎯 Usage

1. **Login** with the default password `yalla2024`
2. **Add Products** in the Products section
3. **Add Customers** in the Customers section
4. **Make Sales** using the POS interface
5. **Track Inventory** in Stock Movements
6. **Generate Reports** for business insights
7. **Configure Settings** for your business

## 🔒 Security

- Password-protected access
- Secure Google Sheets integration
- Service account authentication
- No sensitive data stored locally

## 🌍 Localization

- Arabic interface with RTL support
- Cairo timezone (Africa/Cairo)
- Arabic number formatting
- Bilingual error messages

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 👨‍💻 Developer

**Mohamed Ragab**
- GitHub: [@Mohmedragab2398](https://github.com/Mohmedragab2398)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support and questions:
1. Check the `DEPLOYMENT_FINAL_SOLUTION.md` guide
2. Run the diagnostic scripts (`test_app.py`, `health_check.py`)
3. Open an issue on GitHub

---

**Built with ❤️ for the beauty industry**