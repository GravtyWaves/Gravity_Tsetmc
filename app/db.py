
"""
Database models and configuration for TSETMC data management.
Professional and clean database structure for Tehran Stock Exchange data.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Index as SQLIndex
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'tsetmc_data.db')}")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ==================== MARKET STRUCTURE TABLES ====================

class Market(Base):
    """نمایندگی بازارهای مختلف در بورس تهران (بورس، فرابورس، پایه‌های مختلف)"""
    __tablename__ = "markets"
    
    market_id = Column(Float, primary_key=True, index=True)
    market_name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    symbols = relationship("SymbolList", back_populates="market")


class Sector(Base):
    """نمایندگی بخش‌ها و صنایع مختلف"""
    __tablename__ = "sectors"
    
    sector_id = Column(Float, primary_key=True, index=True)
    sector_name = Column(String(100), nullable=False, unique=True, index=True)
    sector_name_en = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    symbols = relationship("SymbolList", back_populates="sector")
    indices = relationship("Index", back_populates="sector")


class Panel(Base):
    """نمایندگی پنل‌های مختلف (پایه‌های مختلف)"""
    __tablename__ = "panels"
    
    panel_id = Column(Float, primary_key=True, index=True)
    panel_name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    symbols = relationship("SymbolList", back_populates="panel")


# ==================== SYMBOL TABLES ====================

class SymbolList(Base):
    """لیست نمادها (سهام) در بورس تهران"""
    __tablename__ = "symbol_list"
    
    symbol_en = Column(String(20), primary_key=True, index=True)  # نماد انگلیسی
    symbol_fa = Column(String(50), index=True, nullable=True)  # نماد فارسی
    name = Column(String(200), nullable=False, index=True)  # نام شرکت
    name_en = Column(String(200), nullable=True)  # نام انگلیسی
    web_id = Column(String(50), unique=True, nullable=True, index=True)  # شناسه وب TSETMC
    
    # Foreign keys
    market_id = Column(Float, nullable=False, index=True)
    sector_id = Column(Float, nullable=False, index=True)
    panel_id = Column(Float, nullable=True, index=True)
    
    # Metadata
    is_active = Column(Integer, default=1, index=True)  # آیا فعال است
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_price_update = Column(DateTime, nullable=True)  # آخرین به‌روزرسانی قیمت
    
    # Relationships
    market = relationship("Market", back_populates="symbols")
    sector = relationship("Sector", back_populates="symbols")
    panel = relationship("Panel", back_populates="symbols")
    prices = relationship("SymbolPrice", back_populates="symbol_obj", cascade="all, delete-orphan")
    ri_data = relationship("RIData", back_populates="symbol_obj", cascade="all, delete-orphan")
    shareholders = relationship("ShareholdersInfo", back_populates="symbol_obj", cascade="all, delete-orphan")
    
    # Indices for better performance
    __table_args__ = (
        SQLIndex('idx_symbol_market_sector', 'market_id', 'sector_id'),
        SQLIndex('idx_symbol_active', 'is_active'),
    )


# ==================== PRICE TABLES ====================

class SymbolPrice(Base):
    """قیمت‌های روزانه نمادها"""
    __tablename__ = "symbol_prices"
    
    symbol = Column(String(20), primary_key=True, index=True)
    date = Column(String(10), primary_key=True, index=True)  # تاریخ جلالی (YYYY-MM-DD)
    gregorian_date = Column(String(10), index=True, nullable=True)  # تاریخ میلادی
    
    # قیمت‌ها
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    final = Column(Float, nullable=True)  # قیمت پایانی
    last = Column(Float, nullable=True)  # آخرین قیمت
    
    # حجم و ارزش
    volume = Column(Float, nullable=True)  # تعداد سهام
    value = Column(Float, nullable=True)  # ارزش معاملات
    count = Column(Integer, nullable=True)  # تعداد معاملات
    
    # قیمت‌های تعدیل‌شده
    adjusted_close = Column(Float, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    symbol_obj = relationship("SymbolList", back_populates="prices")
    
    # Indices
    __table_args__ = (
        SQLIndex('idx_price_date', 'date'),
        SQLIndex('idx_price_symbol_date', 'symbol', 'date'),
    )


class IndexPrice(Base):
    """قیمت‌های روزانه شاخص‌ها"""
    __tablename__ = "index_prices"
    
    index_id = Column(Integer, primary_key=True)
    date = Column(String(10), primary_key=True, index=True)  # تاریخ جلالی
    gregorian_date = Column(String(10), index=True, nullable=True)  # تاریخ میلادی
    
    # قیمت‌ها
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    final = Column(Float, nullable=True)
    
    # حجم و ارزش
    volume = Column(Float, nullable=True)
    value = Column(Float, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    index = relationship("Index", back_populates="prices")
    
    # Indices
    __table_args__ = (
        SQLIndex('idx_index_price_date', 'date'),
        SQLIndex('idx_index_price_index_date', 'index_id', 'date'),
    )


# ==================== INDEX TABLES ====================

class Index(Base):
    """شاخص‌های مختلف (شاخص کل، شاخص بخشی، ...)"""
    __tablename__ = "indices"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)  # نام شاخص
    name_en = Column(String(100), nullable=True)  # نام انگلیسی
    type = Column(String(50), nullable=False, index=True)  # نوع: market, sector, custom
    description = Column(Text, nullable=True)
    
    # معریف‌های اضافی
    web_id = Column(String(50), unique=True, nullable=True, index=True)  # شناسه وب TSETMC
    sector_id = Column(Float, nullable=True, index=True)  # اگر شاخص بخشی است
    
    # Metadata
    is_active = Column(Integer, default=1, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sector = relationship("Sector", back_populates="indices")
    prices = relationship("IndexPrice", back_populates="index", cascade="all, delete-orphan")


# ==================== INVESTOR RELATIONS DATA ====================

class RIData(Base):
    """داده‌های حقوقی و حقیقی (Retail vs Institutional)"""
    __tablename__ = "ri_data"
    
    symbol = Column(String(20), primary_key=True, index=True)
    date = Column(String(10), primary_key=True, index=True)  # تاریخ جلالی
    gregorian_date = Column(String(10), index=True, nullable=True)
    
    # داده‌های حقیقی
    no_buy_real = Column(Integer, nullable=True)  # تعداد خریدار حقیقی
    no_sell_real = Column(Integer, nullable=True)  # تعداد فروشنده حقیقی
    vol_buy_real = Column(Float, nullable=True)  # حجم خریدار حقیقی
    vol_sell_real = Column(Float, nullable=True)  # حجم فروشنده حقیقی
    val_buy_real = Column(Float, nullable=True)  # ارزش خریدار حقیقی
    val_sell_real = Column(Float, nullable=True)  # ارزش فروشنده حقیقی
    
    # داده‌های حقوقی
    no_buy_inst = Column(Integer, nullable=True)  # تعداد خریدار حقوقی
    no_sell_inst = Column(Integer, nullable=True)  # تعداد فروشنده حقوقی
    vol_buy_inst = Column(Float, nullable=True)  # حجم خریدار حقوقی
    vol_sell_inst = Column(Float, nullable=True)  # حجم فروشنده حقوقی
    val_buy_inst = Column(Float, nullable=True)  # ارزش خریدار حقوقی
    val_sell_inst = Column(Float, nullable=True)  # ارزش فروشنده حقوقی
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    symbol_obj = relationship("SymbolList", back_populates="ri_data")
    
    # Indices
    __table_args__ = (
        SQLIndex('idx_ri_data_date', 'date'),
        SQLIndex('idx_ri_data_symbol_date', 'symbol', 'date'),
    )


# ==================== CURRENCY DATA ====================

class UsdIrrPrice(Base):
    """قیمت دلار آمریکا در مقابل ریال ایران"""
    __tablename__ = "usd_irr_prices"
    
    date = Column(String(10), primary_key=True, index=True)  # تاریخ جلالی
    gregorian_date = Column(String(10), index=True, nullable=True)  # تاریخ میلادی
    
    # قیمت‌ها
    buy_price = Column(Float, nullable=True)  # قیمت خرید
    sell_price = Column(Float, nullable=True)  # قیمت فروش
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    
    # Metadata
    source = Column(String(100), nullable=True)  # منبع داده
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ==================== SHAREHOLDERS DATA ====================

class ShareholdersInfo(Base):
    """اطلاعات سهامداران و سهام‌داران عمده"""
    __tablename__ = "shareholders_info"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), index=True, nullable=False)
    date = Column(String(10), index=True, nullable=False)  # تاریخ جلالی
    gregorian_date = Column(String(10), index=True, nullable=True)
    
    # اطلاعات سهامدار
    holder_name = Column(String(200), nullable=False, index=True)  # نام سهامدار
    holder_type = Column(String(50), nullable=True)  # نوع: فرد، شرکت، بانک، ...
    shares = Column(Float, nullable=True)  # تعداد سهام
    shares_percent = Column(Float, nullable=True)  # درصد مالکیت
    
    # اطلاعات تکمیلی
    national_id = Column(String(20), nullable=True, index=True)  # شناسه ملی
    change_percent = Column(Float, nullable=True)  # تغییر درصدی نسبت به قبل
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    symbol_obj = relationship("SymbolList", back_populates="shareholders")
    
    # Indices
    __table_args__ = (
        SQLIndex('idx_shareholders_symbol_date', 'symbol', 'date'),
        SQLIndex('idx_shareholders_date', 'date'),
    )


# ==================== UTILITY FUNCTIONS ====================

def init_db():
    """ایجاد تمام جداول در دیتابیس"""
    Base.metadata.create_all(bind=engine)


def reset_table(model_class):
    """حذف و دوباره ایجاد یک جدول خاص"""
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    table_name = model_class.__tablename__
    
    with engine.connect() as conn:
        if inspector.has_table(table_name):
            conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
            conn.commit()
    
    model_class.__table__.create(bind=engine, checkfirst=True)


def reset_all_tables():
    """حذف و دوباره ایجاد تمام جداول"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def get_session():
    """دریافت یک session برای کار با دیتابیس"""
    return SessionLocal()