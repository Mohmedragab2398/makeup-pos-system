# 💄 Waad Lash by SASO — Professional Makeup POS System

A modern, fast, and efficient Point of Sale (POS) system built with Streamlit and Google Sheets backend. Perfect for makeup stores, beauty salons, and retail businesses.

## ✨ Features

- **🛒 Smart POS System**: Easy product selection with search by name/SKU
- **📊 Inventory Management**: Real-time stock tracking with low stock alerts
- **👥 Customer Management**: Customer database with order history
- **💰 Flexible Pricing**: Retail and wholesale pricing options
- **📋 Order Management**: Complete order processing with discounts and delivery
- **📄 Invoice Generation**: Professional HTML invoices for printing
- **📈 Reports & Analytics**: Sales reports and inventory movements
- **🚀 Performance Optimized**: Fast loading with intelligent caching

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Account
- Google Spreadsheet (ID already configured)

### Local Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/makeup-pos-system.git
   cd makeup-pos-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Google Sheets**
   - Create a Google Cloud Service Account
   - Download the JSON key file
   - Share your spreadsheet with the service account email as Editor
   - Copy the spreadsheet ID

4. **Set up secrets**
   ```bash
   mkdir .streamlit
   cp .streamlit/secrets.example.toml .streamlit/secrets.toml
   # Edit secrets.toml with your credentials
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

### Streamlit Cloud Deployment
1. Push your code to GitHub
2. Connect your repository to Streamlit Cloud
3. Add your secrets in the Streamlit Cloud dashboard
4. Deploy and share your app!

## 📁 Project Structure

```
makeup-pos-system/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .streamlit/           # Streamlit configuration
│   ├── secrets.toml      # Your API credentials (not in git)
│   └── secrets.example.toml  # Example secrets file
├── assets/               # Static assets (logos, images)
├── data/                 # Sample CSV data files
├── templates/            # HTML invoice templates
└── README.md            # This file
```

## 🔧 Configuration

### Google Sheets Setup
1. Create a new Google Spreadsheet
2. Create a Google Cloud Service Account
3. Enable Google Sheets API
4. Download the service account JSON key
5. Share the spreadsheet with the service account email

### Secrets Configuration
Create `.streamlit/secrets.toml`:
```toml
SPREADSHEET_ID = "your_spreadsheet_id_here"

[gcp_service_account]
type = "service_account"
project_id = "your_project_id"
private_key_id = "your_private_key_id"
private_key = """-----BEGIN PRIVATE KEY-----
your_private_key_content_here
-----END PRIVATE KEY-----"""
client_email = "your_service_account_email"
client_id = "your_client_id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your_cert_url"
universe_domain = "googleapis.com"
```

## 🎯 Usage

### POS Operations
1. **Product Selection**: Search products by name or SKU
2. **Quantity Entry**: Set quantities in the data editor
3. **Pricing**: Choose between retail and wholesale pricing
4. **Checkout**: Apply discounts, delivery fees, and complete the sale

### Inventory Management
- View current stock levels
- Track low stock items
- Monitor stock movements
- Update inventory counts

### Customer Management
- Add new customers
- View customer history
- Track customer orders
- Manage customer information

## 🚀 Performance Features

- **Smart Caching**: Reduces API calls to Google Sheets
- **Lazy Loading**: Worksheets are loaded only when needed
- **Efficient Data Handling**: Optimized pandas operations
- **Responsive UI**: Fast interactions and real-time updates

## 🔒 Security

- API credentials stored securely in Streamlit secrets
- No hardcoded sensitive information
- Secure Google Sheets API integration
- Environment variable support for local development

## 📱 Mobile Friendly

- Responsive design for mobile devices
- Touch-friendly interface
- Optimized for mobile POS operations
- Works on any device with a web browser

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:
1. Check the README_AR.md for Arabic instructions
2. Verify your Google Sheets configuration
3. Ensure all secrets are properly set
4. Check the Streamlit Cloud logs for deployment issues

## 🎉 Acknowledgments

- Built with Streamlit for the beautiful UI
- Powered by Google Sheets for data storage
- Optimized for performance and user experience
- Designed for professional makeup retail operations

---

**Ready for production use!** 🚀
