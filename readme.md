# 🛍️ Shopify Store Insights Fetcher

A comprehensive Python application that extracts detailed insights from Shopify stores without using the official Shopify API. Built with FastAPI, this tool scrapes and analyzes Shopify websites to provide structured data about products, policies, contact information, and more.


## 📋 Table of Contents
- [Features](#-features)
- [Architecture](#-architecture)
- [Installation & Setup](#-installation--setup)
- [Database Setup](#-database-setup)
- [Running the Application](#-running-the-application)
- [API Documentation](#-api-documentation)
- [Input/Output Examples](#-inputoutput-examples)
- [Database Commands](#-database-commands)
- [Method & Approach](#-method--approach)
- [File Structure](#-file-structure)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)

## ✨ Features

### Mandatory Requirements ✅
1. **Complete Product Catalog** - Fetches all products with details, pricing, and variants
2. **Hero Products** - Identifies featured products displayed on the homepage
3. **Privacy Policy** - Extracts and stores privacy policy content
4. **Return/Refund Policies** - Locates and extracts refund policy information
5. **FAQs** - Finds and structures frequently asked questions
6. **Social Media Handles** - Discovers Instagram, Facebook, Twitter, TikTok links
7. **Contact Details** - Extracts emails, phone numbers, and addresses
8. **Brand Context** - Gets "About Us" and brand story information
9. **Important Links** - Finds order tracking, contact, blog, and other key links

### Bonus Features 🎉
1. **MySQL Database Persistence** - Stores all extracted data with relationships
2. **RESTful API** - Clean, documented API endpoints with FastAPI
3. **Interactive Web Interface** - Simple HTML frontend for testing
4. **Comprehensive Error Handling** - Robust error handling with appropriate HTTP status codes
5. **Environment Configuration** - Secure credential management
6. **Scalable Architecture** - Built with production-ready patterns

## 🏗️ Architecture

```
shopify-insights-fetcher/
├── main.py                 # Main FastAPI application with all endpoints
├── requirements.txt        # Python dependencies
├── .env.template          # Environment variables template
├── .env                   # Your actual environment variables (not in git)
├── setup.sh               # Automated setup script for Linux/Mac
├── test_frontend.html     # Interactive web interface for testing
├── README.md              # This comprehensive documentation
└── .gitignore            # Git ignore rules
```

### Tech Stack
- **Backend Framework**: FastAPI (Python 3.8+)
- **Database**: MySQL with SQLAlchemy ORM
- **HTTP Client**: httpx for async requests
- **HTML Parsing**: BeautifulSoup4
- **Data Validation**: Pydantic models
- **Environment Management**: python-dotenv

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MySQL Server 8.0+
- Git (for cloning)

### Step 1: Clone Repository
```bash
git clone https://github.com/eshwar2111/shopify-insights-fetcher.git
cd shopify-insights-fetcher
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Environment Configuration
```bash
# Copy template and edit with your credentials
cp .env.template .env

# Edit .env file with your MySQL credentials
# Use any text editor (notepad, vim, etc.)
notepad .env  # Windows
```

**Example .env file:**
```bash
# Database Configuration
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=shopify_insights

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
```

## 🗄️ Database Setup

### Install MySQL (if not installed)

**Windows:**
1. Download MySQL Installer from [official website](https://dev.mysql.com/downloads/installer/)
2. Run installer and choose "Developer Default"
3. Set root password during installation
4. Start MySQL service

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install mysql-server mysql-client
sudo systemctl start mysql
sudo mysql_secure_installation
```

**macOS:**
```bash
brew install mysql
brew services start mysql
```

### Create Database and User
```bash
# Connect to MySQL
mysql -u root -p

# Run these SQL commands:
```

```sql
-- Create database
CREATE DATABASE IF NOT EXISTS shopify_insights;

-- Create dedicated user (optional, can use root)
CREATE USER IF NOT EXISTS 'shopify_user'@'localhost' IDENTIFIED BY 'secure_password_123';

-- Grant privileges
GRANT ALL PRIVILEGES ON shopify_insights.* TO 'shopify_user'@'localhost';
FLUSH PRIVILEGES;

-- Verify database creation
SHOW DATABASES;
USE shopify_insights;

-- Exit
EXIT;
```

## 🚀 Running the Application

### Start the Application
```bash
# Make sure virtual environment is activated
python main.py

# Alternative method
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Verify Installation
1. **API Status**: Visit `http://localhost:8000`
   - Should show: `{"message": "Shopify Store Insights Fetcher API", "version": "1.0.0"}`

2. **API Documentation**: Visit `http://localhost:8000/docs`
   - Interactive Swagger UI documentation

3. **Database Connection**: Check the console for database connection logs

## 📖 API Documentation

### Base URL
```
http://localhost:8000
```

### Main Endpoints

#### 1. Extract Store Insights
**POST** `/fetch-insights`

Extract comprehensive insights from a Shopify store.

**Request Body:**
```json
{
  "website_url": "https://memy.co.in"
}
```

#### 2. Get Stored Insights  
**GET** `/insights/{website_url:path}`

Retrieve previously analyzed insights.

#### 3. List All Brands
**GET** `/brands`

Get list of all analyzed brands.

#### 4. Database Statistics
**GET** `/database/stats`

View database statistics and summaries.

## 📊 Input/Output Examples

### Input Example
```json
{
  "website_url": "https://memy.co.in"
}
```

### Output Example
```json
{
  "website_url": "https://memy.co.in",
  "brand_name": "Memy",
  "product_catalog": [
    {
      "id": "7234567890123",
      "title": "Classic Cotton T-Shirt",
      "description": "Comfortable cotton t-shirt perfect for everyday wear...",
      "price": "999.00",
      "images": [
        "https://cdn.shopify.com/s/files/1/0234/5678/products/tshirt1.jpg",
        "https://cdn.shopify.com/s/files/1/0234/5678/products/tshirt2.jpg"
      ],
      "variants": [
        {
          "id": 41234567890123,
          "title": "S / Black",
          "price": "999.00",
          "available": true
        }
      ]
    }
  ],
  "hero_products": [
    {
      "id": "7234567890123",
      "title": "Featured Cotton T-Shirt",
      "price": "999.00"
    }
  ],
  "privacy_policy": "Privacy Policy content extracted from /privacy-policy page...",
  "return_refund_policy": "Return policy content extracted from /refund-policy page...",
  "faqs": [
    {
      "question": "Do you offer Cash on Delivery (COD)?",
      "answer": "Yes, we offer COD for orders above ₹500 in select cities."
    },
    {
      "question": "What is your return policy?",
      "answer": "We offer 30-day returns on all unworn items with original tags."
    }
  ],
  "social_handles": {
    "instagram": "https://instagram.com/memy_official",
    "facebook": "https://facebook.com/memyofficial",
    "twitter": null,
    "tiktok": null,
    "youtube": null,
    "linkedin": null
  },
  "contact_details": {
    "emails": [
      "info@memy.co.in",
      "support@memy.co.in"
    ],
    "phone_numbers": [
      "+91-9876543210",
      "1800-123-4567"
    ],
    "addresses": []
  },
  "brand_context": "Memy is a contemporary fashion brand that focuses on creating comfortable, stylish clothing for the modern consumer. Founded with a mission to blend comfort with style...",
  "important_links": {
    "order_tracking": "https://memy.co.in/pages/track-order",
    "contact_us": "https://memy.co.in/pages/contact",
    "blogs": "https://memy.co.in/blogs/news",
    "shipping_info": "https://memy.co.in/pages/shipping-policy",
    "size_guide": "https://memy.co.in/pages/size-guide"
  },
  "competitors": []
}
```

## 🗄️ Database Commands

### Connect to Database
```bash
mysql -u root -p
USE shopify_insights;
```

### View Database Structure
```sql
-- Show all tables
SHOW TABLES;

-- Describe table structures
DESCRIBE brand_insights;
DESCRIBE products;
DESCRIBE competitors;

-- Show table relationships
SELECT 
    TABLE_NAME,
    COLUMN_NAME,
    CONSTRAINT_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE REFERENCED_TABLE_SCHEMA = 'shopify_insights';
```

### Query Brand Data
```sql
-- List all analyzed brands
SELECT id, brand_name, website_url, created_at, updated_at 
FROM brand_insights 
ORDER BY created_at DESC;

-- Count total brands
SELECT COUNT(*) as total_brands FROM brand_insights;

-- View brand with social handles
SELECT 
    brand_name,
    website_url,
    JSON_EXTRACT(social_handles, '$.instagram') as instagram,
    JSON_EXTRACT(social_handles, '$.facebook') as facebook,
    JSON_EXTRACT(contact_details, '$.emails') as emails
FROM brand_insights;

-- Brands with most products
SELECT 
    b.brand_name,
    b.website_url,
    COUNT(p.id) as product_count
FROM brand_insights b
LEFT JOIN products p ON b.id = p.brand_id
GROUP BY b.id
ORDER BY product_count DESC;
```

### Query Product Data
```sql
-- View all products with brand info
SELECT 
    b.brand_name,
    p.title,
    p.price,
    p.product_id
FROM products p
JOIN brand_insights b ON p.brand_id = b.id
ORDER BY b.brand_name, p.title;

-- Count products per brand
SELECT 
    b.brand_name,
    COUNT(p.id) as product_count,
    AVG(CAST(p.price as DECIMAL(10,2))) as avg_price
FROM brand_insights b
LEFT JOIN products p ON b.id = p.brand_id
GROUP BY b.id;

-- Find products with specific price range
SELECT 
    b.brand_name,
    p.title,
    p.price
FROM products p
JOIN brand_insights b ON p.brand_id = b.id
WHERE CAST(p.price as DECIMAL(10,2)) BETWEEN 500 AND 2000
ORDER BY CAST(p.price as DECIMAL(10,2)) DESC;

-- Most expensive products
SELECT 
    b.brand_name,
    p.title,
    p.price
FROM products p
JOIN brand_insights b ON p.brand_id = b.id
ORDER BY CAST(p.price as DECIMAL(10,2)) DESC
LIMIT 10;
```

### Advanced Analytics Queries
```sql
-- Brands with FAQs count
SELECT 
    brand_name,
    JSON_LENGTH(faqs) as faq_count,
    created_at
FROM brand_insights
WHERE faqs IS NOT NULL
ORDER BY JSON_LENGTH(faqs) DESC;

-- Brands with social media presence
SELECT 
    brand_name,
    website_url,
    CASE 
        WHEN JSON_EXTRACT(social_handles, '$.instagram') IS NOT NULL THEN 'Yes' 
        ELSE 'No' 
    END as has_instagram,
    CASE 
        WHEN JSON_EXTRACT(social_handles, '$.facebook') IS NOT NULL THEN 'Yes' 
        ELSE 'No' 
    END as has_facebook
FROM brand_insights;

-- Data extraction statistics
SELECT 
    COUNT(*) as total_brands,
    COUNT(CASE WHEN privacy_policy IS NOT NULL THEN 1 END) as brands_with_privacy_policy,
    COUNT(CASE WHEN return_refund_policy IS NOT NULL THEN 1 END) as brands_with_return_policy,
    COUNT(CASE WHEN brand_context IS NOT NULL THEN 1 END) as brands_with_context,
    AVG(JSON_LENGTH(faqs)) as avg_faqs_per_brand
FROM brand_insights;
```

### Database Maintenance
```sql
-- Clear all data (use with caution)
DELETE FROM products;
DELETE FROM competitors;
DELETE FROM brand_insights;

-- Reset auto-increment
ALTER TABLE brand_insights AUTO_INCREMENT = 1;
ALTER TABLE products AUTO_INCREMENT = 1;
ALTER TABLE competitors AUTO_INCREMENT = 1;

-- Backup specific brand data
SELECT * FROM brand_insights WHERE brand_name = 'Memy';
SELECT * FROM products WHERE brand_id = (SELECT id FROM brand_insights WHERE brand_name = 'Memy');
```

## 🔬 Method & Approach

### Data Extraction Strategy

#### 1. Product Catalog Extraction
```python
# Uses Shopify's public JSON endpoint
GET /products.json?limit=250&page={page}
```
- Handles pagination automatically
- Extracts: ID, title, description, price, images, variants
- Processes large catalogs efficiently

#### 2. Hero Products Identification
- Analyzes homepage HTML structure
- Identifies product links in hero sections
- Matches homepage products with catalog data
- Returns top 6 featured products

#### 3. Policy Content Extraction
- Searches multiple common URL patterns:
  - `/pages/privacy-policy`, `/privacy-policy`, `/privacy`
  - `/pages/refund-policy`, `/return-policy`, `/refunds`
- Extracts clean text content using BeautifulSoup
- Handles various page layouts and structures

#### 4. FAQ Detection & Extraction
```python
# Multiple detection methods:
# 1. Structured FAQ sections (.faq-item, .accordion-item)
# 2. Pattern matching (Q: ... A: ... format)
# 3. Heading-based detection (H3/H4 questions)
```

#### 5. Social Media Discovery
- Scans all page links for social media domains
- Supports: Instagram, Facebook, Twitter, TikTok, YouTube, LinkedIn
- Filters out non-profile links

#### 6. Contact Information Extraction
```python
# Email extraction using regex
email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# Phone number extraction
phone_pattern = r'[\+]?[1-9]?[\s\-\(\)]?\d{3}[\s\-\(\)]?\d{3}[\s\-]?\d{4}'
```

### Technical Implementation

#### Database Design
- **Normalized schema** with proper relationships
- **JSON columns** for complex data (social handles, FAQs)
- **Indexes** on frequently queried columns
- **Foreign key constraints** for data integrity

#### Error Handling Strategy
- **HTTP status codes**: 401 for website not found, 500 for internal errors
- **Graceful degradation**: Continues extraction even if some sections fail
- **Comprehensive logging**: Tracks all operations and errors
- **Retry logic**: Handles temporary network failures

#### Performance Optimizations
- **Async HTTP requests** using httpx
- **Connection pooling** for database operations
- **Efficient HTML parsing** with BeautifulSoup
- **Pagination handling** for large product catalogs

## 📁 File Structure

```
shopify-insights-fetcher/
├── main.py                    # Main FastAPI application (800+ lines)
│   ├── Database Models        # SQLAlchemy models for brands, products, competitors
│   ├── Pydantic Models       # Data validation and serialization
│   ├── ShopifyInsightsFetcher # Core extraction logic
│   ├── API Endpoints         # FastAPI routes
│   └── Database Operations   # Database interaction layer
├── requirements.txt          # Python dependencies
├── .env.template            # Environment variables template
├── .env                     # Your actual environment variables (gitignored)
├── setup.sh                 # Automated setup script (Linux/Mac)
├── test_frontend.html       # Interactive web interface
├── README.md               # This documentation
└── .gitignore             # Git ignore rules
```

## 🧪 Testing

### Method 1: Interactive Web Interface
1. Open `test_frontend.html` in your browser
2. Enter a Shopify store URL
3. Click "Fetch Store Insights"
4. View comprehensive results

### Method 2: API Documentation
1. Visit `http://localhost:8000/docs`
2. Try the POST `/fetch-insights` endpoint
3. Use sample URLs: `https://memy.co.in`, `https://hairoriginals.com`

### Method 3: Command Line Testing
```bash
# Test with curl
curl -X POST "http://localhost:8000/fetch-insights" \
     -H "Content-Type: application/json" \
     -d '{"website_url": "https://memy.co.in"}'

# Test with Python
python -c "
import requests
response = requests.post('http://localhost:8000/fetch-insights', 
                        json={'website_url': 'https://memy.co.in'})
print(f'Status: {response.status_code}')
print(f'Brand: {response.json().get(\"brand_name\")}')
print(f'Products: {len(response.json().get(\"product_catalog\", []))}')
"
```

### Tested Shopify Stores
- ✅ **memy.co.in** - Indian fashion brand
- ✅ **hairoriginals.com** - Hair care products
- ✅ **colourpop.com** - Cosmetics brand
- ✅ **gymshark.com** - Fitness apparel
- ✅ **allbirds.com** - Sustainable footwear

## 🐛 Troubleshooting

### Common Issues & Solutions

#### 1. MySQL Connection Error
```
Error: Can't connect to MySQL server
```
**Solutions:**
```bash
# Check MySQL service status
net start | findstr MySQL          # Windows
sudo systemctl status mysql       # Linux
brew services list | grep mysql   # macOS

# Start MySQL service
net start MySQL80                 # Windows
sudo systemctl start mysql        # Linux
brew services start mysql         # macOS

# Test connection
mysql -u root -p
```

#### 2. Authentication Error
```
Error: Access denied for user 'root'@'localhost'
```
**Solutions:**
```sql
-- Reset MySQL root password
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'new_password';
FLUSH PRIVILEGES;
```

#### 3. Website Not Found (401)
```
HTTPException: Website not found or inaccessible
```
**Causes:**
- Invalid URL format
- Website blocking requests
- Network connectivity issues

**Solutions:**
- Ensure URL includes `https://`
- Try different Shopify stores
- Check internet connection

#### 4. Database Permission Issues
```sql
-- Grant all privileges
GRANT ALL PRIVILEGES ON shopify_insights.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

#### 5. Port Already in Use
```bash
# Find and kill process using port 8000
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

#### 6. Module Import Errors
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check virtual environment
which python
pip list
```

### Performance Issues

#### Slow Extraction
- Large product catalogs take 30-60 seconds
- Network speed affects performance
- Some websites have rate limiting

#### Memory Usage
- Scales with product catalog size
- Close browser tabs if memory constrained
- Consider pagination for very large catalogs

### Debugging Tips

#### Enable Debug Mode
```bash
# In .env file
DEBUG=True
LOG_LEVEL=DEBUG
```

#### Check Logs
```python
# The application logs all operations
# Check console output for detailed information
```

#### Database Debugging
```sql
-- Check if data is being stored
SELECT COUNT(*) FROM brand_insights;
SELECT COUNT(*) FROM products;

-- View recent entries
SELECT * FROM brand_insights ORDER BY created_at DESC LIMIT 5;
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-extraction-method`
3. Make your changes
4. Add tests if applicable
5. Commit: `git commit -am 'Add new extraction method for reviews'`
6. Push: `git push origin feature/new-extraction-method`
7. Create a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add type hints to new functions
- Include docstrings for new methods
- Test with multiple Shopify stores
- Update README for new features

## 📄 License

This project is for educational and research purposes. Please respect website terms of service and implement appropriate rate limiting when scraping websites.

## 🔗 References & Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM Documentation](https://docs.sqlalchemy.org/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [Shopify Store Examples](https://webinopoly.com/blogs/news/top-100-most-successful-shopify-stores)

## 📊 Project Statistics

- **Lines of Code**: 800+ (main.py)
- **Database Tables**: 3 (normalized schema)
- **API Endpoints**: 5+ RESTful endpoints
- **Data Points Extracted**: 9+ mandatory + bonus features
- **Supported Stores**: Any Shopify store
- **Technologies Used**: 7+ (FastAPI, MySQL, SQLAlchemy, etc.)

---

**Made with ❤️ for the GenAI Developer Intern Assignment**

**Repository**: https://github.com/eshwar2111/shopify-insights-fetcher  
**Author**: Eshwar  
**Contact**: [eshwar211104@gmail.com]

🌟 **Star this repository if you found it helpful!**
