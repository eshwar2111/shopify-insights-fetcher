#!/bin/bash

# Shopify Insights Fetcher - Complete Setup Script

echo "🚀 Setting up Shopify Insights Fetcher..."

# Check if Python 3.8+ is installed
python_version=$(python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1,2)
if [[ -z "$python_version" ]] || [[ $(echo "$python_version < 3.8" | bc -l) -eq 1 ]]; then
    echo "❌ Python 3.8+ is required. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📋 Installing Python packages..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file..."
    cp .env.template .env
    echo "📝 Please edit .env file with your MySQL credentials"
    echo "   - Update DATABASE_URL with your MySQL password"
fi

# Check if MySQL is installed
if ! command -v mysql &> /dev/null; then
    echo "⚠️ MySQL is not installed. Please install MySQL first:"
    echo "   Ubuntu/Debian: sudo apt install mysql-server"
    echo "   macOS: brew install mysql"
    echo "   Windows: Download from https://dev.mysql.com/downloads/"
    exit 1
fi

echo "✅ MySQL detected"

# Test MySQL connection
echo "🔍 Testing MySQL connection..."
if ! mysql -u root -p -e "SELECT 1;" &> /dev/null; then
    echo "⚠️ Could not connect to MySQL. Please ensure:"
    echo "   1. MySQL service is running"
    echo "   2. Root password is correct"
    echo "   3. Run: sudo systemctl start mysql (Linux)"
    echo "   4. Run: brew services start mysql (macOS)"
fi

# Create database and user
echo "🗃️ Setting up database..."
read -p "Enter MySQL root password: " -s mysql_root_password
echo

mysql -u root -p$mysql_root_password << EOF
CREATE DATABASE IF NOT EXISTS shopify_insights;
CREATE USER IF NOT EXISTS 'shopify_user'@'localhost' IDENTIFIED BY 'shopify_password_123';
GRANT ALL PRIVILEGES ON shopify_insights.* TO 'shopify_user'@'localhost';
FLUSH PRIVILEGES;
EOF

if [ $? -eq 0 ]; then
    echo "✅ Database setup completed"
    
    # Update .env with the database credentials
    sed -i 's/your_password_here/shopify_password_123/g' .env
    
else
    echo "❌ Database setup failed. Please check your MySQL root password."
    exit 1
fi

echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Review .env file and update if needed"
echo "3. Start the application: python main.py"
echo "4. Visit http://localhost:8000/docs for API documentation"
echo ""
echo "Test the API with:"
echo 'curl -X POST "http://localhost:8000/fetch-insights" -H "Content-Type: application/json" -d '"'"'{"website_url": "https://memy.co.in"}'"'"