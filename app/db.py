
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'tsetmc_data.db')}")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SymbolList(Base):
    __tablename__ = "symbol_list"
    symbol_en = Column(String, primary_key=True, index=True)  # نماد انگلیسی (کلید اصلی)
    symbol_fa = Column(String, index=True)  # نماد فارسی
    name = Column(String)
    market_id = Column(Float, ForeignKey('markets.market_id'))
    sector_id = Column(Float, ForeignKey('sectors.sector_id'))
    panel_id = Column(Float, ForeignKey('panels.panel_id'))
    # Relationships
    market = relationship('Market', back_populates='symbols')
    sector = relationship('Sector', back_populates='symbols')
    panel = relationship('Panel', back_populates='symbols')
    prices = relationship('SymbolPrice', back_populates='symbol_obj')


# --- Unified Index Table ---
class Index(Base):
    __tablename__ = "indices"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True)  # e.g. شاخص کل، شاخص صنعت خودرو، ...
    type = Column(String, index=True)  # e.g. 'market', 'sector', 'custom'
    sector_id = Column(Float, ForeignKey('sectors.sector_id'), nullable=True)  # For sector indices
    web_id = Column(String, unique=True, nullable=True)
    description = Column(String, nullable=True)
    sector = relationship('Sector', back_populates='indices')
    prices = relationship('IndexPrice', back_populates='index')


class SymbolPrice(Base):
    __tablename__ = "symbol_prices"
    symbol = Column(String, ForeignKey('symbol_list.symbol_en'), primary_key=True)
    date = Column(String, primary_key=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    final = Column(Float)
    volume = Column(Float)
    value = Column(Float)
    no = Column(Integer)
    name = Column(String)
    market = Column(String)
    adj_open = Column(Float)
    adj_high = Column(Float)
    adj_low = Column(Float)
    adj_close = Column(Float)
    adj_final = Column(Float)
    # Relationship
    symbol_obj = relationship('SymbolList', back_populates='prices')

class IndexPrice(Base):
    __tablename__ = "index_prices"
    id = Column(Integer, primary_key=True, autoincrement=True)
    index_id = Column(Integer, ForeignKey('indices.id'))
    date = Column(String, index=True)
    value = Column(Float)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    # volume and weekday columns removed as requested
    # Relationship
    index = relationship('Index', back_populates='prices')


# Remove old industry index tables (all indices now unified)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)

# --- New Tables for Market, Panel, Sector ---
class Market(Base):
    __tablename__ = "markets"
    market_id = Column(Float, primary_key=True)
    market_name = Column(String)
    symbols = relationship('SymbolList', back_populates='market')

class Panel(Base):
    __tablename__ = "panels"
    panel_id = Column(Float, primary_key=True)
    panel_name = Column(String)
    symbols = relationship('SymbolList', back_populates='panel')

class Sector(Base):
    __tablename__ = "sectors"
    sector_id = Column(Float, primary_key=True)
    sector_name = Column(String)
    symbols = relationship('SymbolList', back_populates='sector')
    indices = relationship('Index', back_populates='sector')


# --- USD/IRR Price Table ---

# --- Shareholders Info Table ---
class ShareholdersInfo(Base):
    __tablename__ = "shareholders_info"
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, ForeignKey('symbol_list.symbol_en'), index=True)
    date = Column(String, index=True)  # تاریخ دریافت اطلاعات
    holder_name = Column(String, index=True)  # نام سهامدار
    holder_type = Column(String)  # نوع سهامدار (حقیقی/حقوقی)
    shares = Column(Float)  # تعداد سهام
    percent = Column(Float)  # درصد مالکیت
    change = Column(Float)  # تغییرات نسبت به روز قبل
    national_id = Column(String, nullable=True)  # شناسه ملی (در صورت وجود)
    # Relationship
    symbol_obj = relationship('SymbolList', backref='shareholders')

class UsdIrrPrice(Base):
    __tablename__ = "usd_irr_prices"
    date = Column(String, primary_key=True, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)



# --- Generic utility to drop and recreate any table by model class ---
def reset_table(model_class):
    """
    فقط جدول مربوط به model_class را حذف و دوباره ایجاد می‌کند (سایر جداول حذف نمی‌شوند)
    """
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    table_name = model_class.__tablename__
    with engine.connect() as conn:
        if inspector.has_table(table_name):
            conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
    model_class.__table__.create(bind=engine, checkfirst=True)

