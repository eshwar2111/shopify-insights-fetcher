"""
Shopify Store Insights Fetcher Application
A comprehensive solution to extract insights from Shopify stores
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, ValidationError
from typing import List, Optional, Dict, Any
import httpx
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import urljoin, urlparse
import asyncio
from datetime import datetime
import logging
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.exc import SQLAlchemyError
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please create a .env file with DATABASE_URL=mysql+pymysql://user:password@host:port/database"
    )
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class BrandInsights(Base):
    __tablename__ = "brand_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    website_url = Column(String(255), unique=True, index=True)
    brand_name = Column(String(255))
    products = relationship("Product", back_populates="brand")
    hero_products = Column(JSON)
    privacy_policy = Column(Text)
    return_refund_policy = Column(Text)
    faqs = Column(JSON)
    social_handles = Column(JSON)
    contact_details = Column(JSON)
    brand_context = Column(Text)
    important_links = Column(JSON)
    competitors = relationship("Competitor", back_populates="brand")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brand_insights.id"))
    product_id = Column(String(255))
    title = Column(String(500))
    description = Column(Text)
    price = Column(String(50))
    images = Column(JSON)
    variants = Column(JSON)
    brand = relationship("BrandInsights", back_populates="products")

class Competitor(Base):
    __tablename__ = "competitors"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brand_insights.id"))
    competitor_url = Column(String(255))
    competitor_data = Column(JSON)
    brand = relationship("BrandInsights", back_populates="competitors")

# Pydantic Models
class ProductModel(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[str] = None
    images: Optional[List[str]] = []
    variants: Optional[List[Dict[str, Any]]] = []

class ContactDetails(BaseModel):
    emails: List[str] = []
    phone_numbers: List[str] = []
    addresses: List[str] = []

class SocialHandles(BaseModel):
    instagram: Optional[str] = None
    facebook: Optional[str] = None
    twitter: Optional[str] = None
    tiktok: Optional[str] = None
    youtube: Optional[str] = None
    linkedin: Optional[str] = None

class FAQ(BaseModel):
    question: str
    answer: str

class ImportantLinks(BaseModel):
    order_tracking: Optional[str] = None
    contact_us: Optional[str] = None
    blogs: Optional[str] = None
    shipping_info: Optional[str] = None
    size_guide: Optional[str] = None

class BrandInsightsModel(BaseModel):
    website_url: str
    brand_name: Optional[str] = None
    product_catalog: List[ProductModel] = []
    hero_products: List[ProductModel] = []
    privacy_policy: Optional[str] = None
    return_refund_policy: Optional[str] = None
    faqs: List[FAQ] = []
    social_handles: SocialHandles = SocialHandles()
    contact_details: ContactDetails = ContactDetails()
    brand_context: Optional[str] = None
    important_links: ImportantLinks = ImportantLinks()
    competitors: List[Dict[str, Any]] = []

class StoreInsightsRequest(BaseModel):
    website_url: HttpUrl

class ShopifyInsightsFetcher:
    def __init__(self):
        self.session = httpx.AsyncClient(timeout=30.0)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.aclose()

    async def fetch_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse a webpage"""
        try:
            response = await self.session.get(url, headers=self.headers, follow_redirects=True)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except httpx.HTTPError as e:
            logger.error(f"Error fetching {url}: {e}")
            raise HTTPException(status_code=401, detail=f"Website not found or inaccessible: {url}")

    async def fetch_json(self, url: str) -> Dict[str, Any]:
        """Fetch JSON data from URL"""
        try:
            response = await self.session.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            return {}
        except json.JSONDecodeError:
            return {}

    def extract_brand_name(self, soup: BeautifulSoup, url: str) -> str:
        """Extract brand name from the website"""
        # Try multiple methods to get brand name
        brand_name = None
        
        # Method 1: Meta property
        meta_brand = soup.find('meta', property='og:site_name')
        if meta_brand:
            brand_name = meta_brand.get('content')
        
        # Method 2: Title tag
        if not brand_name:
            title = soup.find('title')
            if title:
                brand_name = title.get_text().split('|')[0].split('-')[0].strip()
        
        # Method 3: Header logo alt text
        if not brand_name:
            logo = soup.find('img', {'class': re.compile(r'logo', re.I)})
            if logo:
                brand_name = logo.get('alt', '')
        
        # Method 4: Domain name as fallback
        if not brand_name:
            domain = urlparse(url).netloc
            brand_name = domain.replace('www.', '').split('.')[0].capitalize()
        
        return brand_name or "Unknown Brand"

    async def fetch_product_catalog(self, base_url: str) -> List[ProductModel]:
        """Fetch complete product catalog"""
        products = []
        page = 1
        
        while True:
            products_url = f"{base_url.rstrip('/')}/products.json?limit=250&page={page}"
            data = await self.fetch_json(products_url)
            
            if not data.get('products'):
                break
                
            for product in data['products']:
                product_model = ProductModel(
                    id=str(product.get('id', '')),
                    title=product.get('title', ''),
                    description=BeautifulSoup(product.get('body_html', ''), 'html.parser').get_text()[:500],
                    price=str(product.get('variants', [{}])[0].get('price', '0')),
                    images=[img.get('src', '') for img in product.get('images', [])],
                    variants=product.get('variants', [])
                )
                products.append(product_model)
            
            if len(data['products']) < 250:
                break
            page += 1
        
        return products

    def extract_hero_products(self, soup: BeautifulSoup, all_products: List[ProductModel]) -> List[ProductModel]:
        """Extract hero/featured products from homepage"""
        hero_products = []
        
        # Look for product links on homepage
        product_links = soup.find_all('a', href=re.compile(r'/products/'))
        product_handles = set()
        
        for link in product_links[:10]:  # Limit to first 10 found
            href = link.get('href', '')
            if '/products/' in href:
                handle = href.split('/products/')[-1].split('?')[0]
                product_handles.add(handle)
        
        # Match with actual products
        for product in all_products:
            if product.title and any(handle.lower() in product.title.lower().replace(' ', '-') for handle in product_handles):
                hero_products.append(product)
                if len(hero_products) >= 6:
                    break
        
        return hero_products

    async def fetch_policy_content(self, base_url: str, policy_type: str) -> Optional[str]:
        """Fetch policy content (privacy, refund, etc.)"""
        common_paths = {
            'privacy': ['/pages/privacy-policy', '/privacy-policy', '/privacy', '/pages/privacy'],
            'refund': ['/pages/refund-policy', '/pages/return-policy', '/refund-policy', '/return-policy', 
                      '/pages/returns', '/returns', '/pages/refunds', '/refunds']
        }
        
        paths = common_paths.get(policy_type, [])
        
        for path in paths:
            try:
                url = urljoin(base_url, path)
                soup = await self.fetch_page(url)
                
                # Extract main content
                content_selectors = [
                    '.page-content', '.main-content', '.policy-content',
                    'article', 'main', '.content', '#content'
                ]
                
                for selector in content_selectors:
                    content_div = soup.select_one(selector)
                    if content_div:
                        text = content_div.get_text(separator=' ', strip=True)
                        if len(text) > 100:  # Ensure meaningful content
                            return text[:2000]  # Limit length
                
                # Fallback to body text
                body_text = soup.get_text(separator=' ', strip=True)
                if len(body_text) > 100:
                    return body_text[:2000]
                    
            except Exception as e:
                logger.warning(f"Could not fetch {policy_type} policy from {path}: {e}")
                continue
        
        return None

    def extract_faqs(self, soup: BeautifulSoup) -> List[FAQ]:
        """Extract FAQs from the website"""
        faqs = []
        
        # Common FAQ selectors
        faq_selectors = [
            '.faq-item', '.faq', '.accordion-item',
            '.question-answer', '.qa-item'
        ]
        
        for selector in faq_selectors:
            faq_elements = soup.select(selector)
            for element in faq_elements:
                question_elem = element.find(['h2', 'h3', 'h4', 'h5', '.question', '.faq-question'])
                answer_elem = element.find(['.answer', '.faq-answer', 'p'])
                
                if question_elem and answer_elem:
                    question = question_elem.get_text(strip=True)
                    answer = answer_elem.get_text(strip=True)
                    
                    if question and answer and len(question) > 10:
                        faqs.append(FAQ(question=question, answer=answer))
        
        # If no structured FAQs found, look for question patterns
        if not faqs:
            text = soup.get_text()
            q_pattern = re.compile(r'Q[:\.]?\s*([^?]*\?)\s*A[:\.]?\s*([^Q]*?)(?=Q[:\.]|$)', re.IGNORECASE | re.DOTALL)
            matches = q_pattern.findall(text)
            
            for question, answer in matches[:10]:  # Limit to 10
                question = question.strip()
                answer = answer.strip()[:300]  # Limit answer length
                if question and answer:
                    faqs.append(FAQ(question=question, answer=answer))
        
        return faqs[:15]  # Limit total FAQs

    def extract_social_handles(self, soup: BeautifulSoup) -> SocialHandles:
        """Extract social media handles"""
        social_handles = SocialHandles()
        
        # Find social media links
        social_links = soup.find_all('a', href=re.compile(r'(instagram|facebook|twitter|tiktok|youtube|linkedin)\.com'))
        
        for link in social_links:
            href = link.get('href', '').lower()
            if 'instagram.com' in href:
                social_handles.instagram = href
            elif 'facebook.com' in href:
                social_handles.facebook = href
            elif 'twitter.com' in href or 'x.com' in href:
                social_handles.twitter = href
            elif 'tiktok.com' in href:
                social_handles.tiktok = href
            elif 'youtube.com' in href:
                social_handles.youtube = href
            elif 'linkedin.com' in href:
                social_handles.linkedin = href
        
        return social_handles

    def extract_contact_details(self, soup: BeautifulSoup) -> ContactDetails:
        """Extract contact information"""
        contact_details = ContactDetails()
        
        text = soup.get_text()
        
        # Extract emails
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        emails = list(set(email_pattern.findall(text)))
        contact_details.emails = [email for email in emails if not email.endswith(('.png', '.jpg', '.gif'))][:5]
        
        # Extract phone numbers
        phone_pattern = re.compile(r'[\+]?[1-9]?[\s\-\(\)]?\d{3}[\s\-\(\)]?\d{3}[\s\-]?\d{4}')
        phones = list(set(phone_pattern.findall(text)))
        contact_details.phone_numbers = [phone.strip() for phone in phones][:3]
        
        return contact_details

    def extract_brand_context(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract brand context/about information"""
        # Look for about sections
        about_selectors = [
            '.about', '.brand-story', '.our-story',
            '.company-info', '[class*="about"]'
        ]
        
        for selector in about_selectors:
            about_section = soup.select_one(selector)
            if about_section:
                text = about_section.get_text(separator=' ', strip=True)
                if len(text) > 50:
                    return text[:1000]
        
        # Look for meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            content = meta_desc.get('content', '')
            if len(content) > 50:
                return content
        
        return None

    def extract_important_links(self, soup: BeautifulSoup, base_url: str) -> ImportantLinks:
        """Extract important links"""
        important_links = ImportantLinks()
        
        # Find links by text content
        links = soup.find_all('a', href=True)
        
        for link in links:
            text = link.get_text().lower().strip()
            href = link.get('href')
            
            if not href.startswith('http'):
                href = urljoin(base_url, href)
            
            if any(term in text for term in ['track', 'order', 'tracking']):
                important_links.order_tracking = href
            elif any(term in text for term in ['contact', 'contact us']):
                important_links.contact_us = href
            elif any(term in text for term in ['blog', 'news', 'articles']):
                important_links.blogs = href
            elif any(term in text for term in ['shipping', 'delivery']):
                important_links.shipping_info = href
            elif any(term in text for term in ['size', 'guide', 'sizing']):
                important_links.size_guide = href
        
        return important_links

    async def search_competitors(self, brand_name: str) -> List[str]:
        """Search for potential competitors"""
        # This is a simplified implementation
        # In a real scenario, you might use search APIs or more sophisticated methods
        competitors = []
        
        search_queries = [
            f"{brand_name} competitors",
            f"alternatives to {brand_name}",
            f"brands like {brand_name}"
        ]
        
        # For now, return empty list as we don't have search API access
        # In production, you would implement actual competitor discovery
        return competitors

    async def fetch_store_insights(self, website_url: str) -> BrandInsightsModel:
        """Main method to fetch all store insights"""
        try:
            # Ensure URL has scheme
            if not website_url.startswith(('http://', 'https://')):
                website_url = 'https://' + website_url
            
            # Fetch homepage
            soup = await self.fetch_page(website_url)
            
            # Extract brand name
            brand_name = self.extract_brand_name(soup, website_url)
            
            # Fetch product catalog
            product_catalog = await self.fetch_product_catalog(website_url)
            
            # Extract hero products
            hero_products = self.extract_hero_products(soup, product_catalog)
            
            # Fetch policies
            privacy_policy = await self.fetch_policy_content(website_url, 'privacy')
            return_refund_policy = await self.fetch_policy_content(website_url, 'refund')
            
            # Extract other information
            faqs = self.extract_faqs(soup)
            social_handles = self.extract_social_handles(soup)
            contact_details = self.extract_contact_details(soup)
            brand_context = self.extract_brand_context(soup)
            important_links = self.extract_important_links(soup, website_url)
            
            # Search for competitors (bonus feature)
            competitors = await self.search_competitors(brand_name)
            
            return BrandInsightsModel(
                website_url=website_url,
                brand_name=brand_name,
                product_catalog=product_catalog,
                hero_products=hero_products,
                privacy_policy=privacy_policy,
                return_refund_policy=return_refund_policy,
                faqs=faqs,
                social_handles=social_handles,
                contact_details=contact_details,
                brand_context=brand_context,
                important_links=important_links,
                competitors=[]  # Will be populated with actual competitor data
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching insights for {website_url}: {e}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database operations
class DatabaseOperations:
    @staticmethod
    def save_brand_insights(db: Session, insights: BrandInsightsModel) -> BrandInsights:
        """Save brand insights to database"""
        try:
            # Check if brand already exists
            existing_brand = db.query(BrandInsights).filter(
                BrandInsights.website_url == insights.website_url
            ).first()
            
            if existing_brand:
                # Update existing record
                existing_brand.brand_name = insights.brand_name
                existing_brand.hero_products = [product.dict() for product in insights.hero_products]
                existing_brand.privacy_policy = insights.privacy_policy
                existing_brand.return_refund_policy = insights.return_refund_policy
                existing_brand.faqs = [faq.dict() for faq in insights.faqs]
                existing_brand.social_handles = insights.social_handles.dict()
                existing_brand.contact_details = insights.contact_details.dict()
                existing_brand.brand_context = insights.brand_context
                existing_brand.important_links = insights.important_links.dict()
                existing_brand.updated_at = datetime.utcnow()
                
                # Delete existing products
                db.query(Product).filter(Product.brand_id == existing_brand.id).delete()
                
                brand = existing_brand
            else:
                # Create new record
                brand = BrandInsights(
                    website_url=insights.website_url,
                    brand_name=insights.brand_name,
                    hero_products=[product.dict() for product in insights.hero_products],
                    privacy_policy=insights.privacy_policy,
                    return_refund_policy=insights.return_refund_policy,
                    faqs=[faq.dict() for faq in insights.faqs],
                    social_handles=insights.social_handles.dict(),
                    contact_details=insights.contact_details.dict(),
                    brand_context=insights.brand_context,
                    important_links=insights.important_links.dict()
                )
                db.add(brand)
                db.flush()  # Get the ID
            
            # Save products
            for product in insights.product_catalog:
                db_product = Product(
                    brand_id=brand.id,
                    product_id=product.id,
                    title=product.title,
                    description=product.description,
                    price=product.price,
                    images=product.images,
                    variants=product.variants
                )
                db.add(db_product)
            
            db.commit()
            return brand
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error: {e}")
            raise HTTPException(status_code=500, detail="Database error occurred")

# FastAPI App
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Shopify Store Insights Fetcher",
    description="Fetch comprehensive insights from Shopify stores",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Shopify Store Insights Fetcher API", "version": "1.0.0"}

@app.post("/fetch-insights", response_model=BrandInsightsModel)
async def fetch_store_insights(
    request: StoreInsightsRequest,
    db: Session = Depends(get_db)
):
    """
    Fetch comprehensive insights from a Shopify store
    """
    async with ShopifyInsightsFetcher() as fetcher:
        insights = await fetcher.fetch_store_insights(str(request.website_url))
        
        # Save to database
        DatabaseOperations.save_brand_insights(db, insights)
        
        return insights

@app.get("/insights/{website_url:path}")
async def get_stored_insights(website_url: str, db: Session = Depends(get_db)):
    """
    Get previously stored insights for a website
    """
    brand = db.query(BrandInsights).filter(BrandInsights.website_url == website_url).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand insights not found")
    
    products = db.query(Product).filter(Product.brand_id == brand.id).all()
    
    return {
        "brand": brand,
        "products": products,
        "total_products": len(products)
    }

@app.get("/brands")
async def list_all_brands(db: Session = Depends(get_db)):
    """
    List all stored brands
    """
    brands = db.query(BrandInsights).all()
    return {"brands": brands, "total": len(brands)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)