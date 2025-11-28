"""
Database models and configuration for TSETMC data management.
Professional and clean database structure for Tehran Stock Exchange data.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Index as SQLIndex, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'tsetmc_data.db')}")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ==================== MARKET STRUCTURE TABLES ====================

class Market(Base):
    """Representation of different markets in Tehran Stock Exchange"""
    __tablename__ = "markets"

    market_id = Column(Float, primary_key=True, index=True)
    market_name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    symbols = relationship("Symbol", back_populates="market")


class Sector(Base):
    """Representation of different sectors and industries"""
    __tablename__ = "sectors"

    sector_id = Column(Float, primary_key=True, index=True)
    sector_name = Column(String(100), nullable=False, unique=True, index=True)
    sector_name_en = Column(String(100), nullable=True)
    english_name = Column(String(100), nullable=True)
    us_equivalent = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    symbols = relationship("Symbol", back_populates="sector")
    indices = relationship("Index", back_populates="sector")


class Panel(Base):
    """Representation of different panels"""
    __tablename__ = "panels"

    panel_id = Column(Float, primary_key=True, index=True)
    panel_name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    symbols = relationship("Symbol", back_populates="panel")


# ==================== SYMBOL TABLES ====================

class Symbol(Base):
    """List of symbols (stocks) in Tehran Stock Exchange"""
    __tablename__ = "symbols"

    symbol_en = Column(String(20), primary_key=True, index=True)
    symbol_fa = Column(String(50), index=True, nullable=True)
    name = Column(String(200), nullable=False, index=True)
    name_en = Column(String(200), nullable=True)
    web_id = Column(String(50), unique=True, nullable=True, index=True)
    industry = Column(String(100), nullable=True)

    # Foreign keys
    market_id = Column(Float, ForeignKey("markets.market_id"), nullable=False, index=True)
    sector_id = Column(Float, ForeignKey("sectors.sector_id"), nullable=False, index=True)
    panel_id = Column(Float, ForeignKey("panels.panel_id"), nullable=True, index=True)

    # Metadata
    is_active = Column(Integer, default=1, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_price_update = Column(DateTime, nullable=True)

    # Relationships
    market = relationship("Market", back_populates="symbols")
    sector = relationship("Sector", back_populates="symbols")
    panel = relationship("Panel", back_populates="symbols")
    prices = relationship("SymbolPrice", back_populates="symbol", cascade="all, delete-orphan")
    ri_data = relationship("RIData", back_populates="symbol", cascade="all, delete-orphan")
    shareholders = relationship("ShareholdersInfo", back_populates="symbol", cascade="all, delete-orphan")

    # Indices for better performance
    __table_args__ = (
        SQLIndex('idx_symbol_market_sector', 'market_id', 'sector_id'),
        SQLIndex('idx_symbol_active', 'is_active'),
    )


# ==================== PRICE TABLES ====================

class SymbolPrice(Base):
    """Daily prices for symbols"""
    __tablename__ = "symbol_prices"

    symbol = Column(String(20), ForeignKey("symbols.symbol_en"), primary_key=True, index=True)
    date = Column(String(10), primary_key=True, index=True)
    gregorian_date = Column(String(10), index=True, nullable=True)

    # Prices
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    final = Column(Float, nullable=True)

    # Volume and value
    volume = Column(Float, nullable=True)
    value = Column(Float, nullable=True)
    count = Column(Integer, nullable=True)

    # Adjusted prices
    adj_open = Column(Float, nullable=True)
    adj_high = Column(Float, nullable=True)
    adj_low = Column(Float, nullable=True)
    adj_close = Column(Float, nullable=True)
    adj_final = Column(Float, nullable=True)
    adj_volume = Column(Float, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    symbol = relationship("Symbol", back_populates="prices")

    # Indices
    __table_args__ = (
        SQLIndex('idx_price_date', 'date'),
        SQLIndex('idx_price_symbol_date', 'symbol', 'date'),
    )


class IndexPrice(Base):
    """Daily prices for indices"""
    __tablename__ = "index_prices"

    index_id = Column(Integer, ForeignKey("indices.id"), primary_key=True)
    date = Column(String(10), primary_key=True, index=True)
    gregorian_date = Column(String(10), index=True, nullable=True)

    # Prices
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    final = Column(Float, nullable=True)

    # Volume and value
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
    """Different indices (Total Index, Sector Index, etc.)"""
    __tablename__ = "indices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    name_en = Column(String(100), nullable=True)
    type = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Additional definitions
    web_id = Column(String(50), unique=True, nullable=True, index=True)
    sector_id = Column(Float, ForeignKey("sectors.sector_id"), nullable=True, index=True)

    # Metadata
    is_active = Column(Integer, default=1, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sector = relationship("Sector", back_populates="indices")
    prices = relationship("IndexPrice", back_populates="index", cascade="all, delete-orphan")


# ==================== INVESTOR RELATIONS DATA ====================

class RIData(Base):
    """Retail vs Institutional investor data"""
    __tablename__ = "ri_data"

    symbol = Column(String(20), ForeignKey("symbols.symbol_en"), primary_key=True, index=True)
    date = Column(String(10), primary_key=True, index=True)
    gregorian_date = Column(String(10), index=True, nullable=True)

    # Retail investor data
    no_buy_real = Column(Integer, nullable=True)
    no_sell_real = Column(Integer, nullable=True)
    vol_buy_real = Column(Float, nullable=True)
    vol_sell_real = Column(Float, nullable=True)
    val_buy_real = Column(Float, nullable=True)
    val_sell_real = Column(Float, nullable=True)

    # Institutional investor data
    no_buy_inst = Column(Integer, nullable=True)
    no_sell_inst = Column(Integer, nullable=True)
    vol_buy_inst = Column(Float, nullable=True)
    vol_sell_inst = Column(Float, nullable=True)
    val_buy_inst = Column(Float, nullable=True)
    val_sell_inst = Column(Float, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    symbol = relationship("Symbol", back_populates="ri_data")

    # Indices
    __table_args__ = (
        SQLIndex('idx_ri_data_date', 'date'),
        SQLIndex('idx_ri_data_symbol_date', 'symbol', 'date'),
    )


# ==================== CURRENCY DATA ====================

class UsdIrrPrice(Base):
    """USD to IRR exchange rates"""
    __tablename__ = "usd_irr_prices"

    date = Column(String(10), primary_key=True, index=True)
    gregorian_date = Column(String(10), index=True, nullable=True)

    # Prices
    buy_price = Column(Float, nullable=True)
    sell_price = Column(Float, nullable=True)
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)

    # Metadata
    source = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ==================== SHAREHOLDERS DATA ====================

class ShareholdersInfo(Base):
    """Shareholder information and major stakeholders"""
    __tablename__ = "shareholders_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), ForeignKey("symbols.symbol_en"), index=True, nullable=False)
    date = Column(String(10), index=True, nullable=False)
    gregorian_date = Column(String(10), index=True, nullable=True)

    # Shareholder information
    holder_name = Column(String(200), nullable=False, index=True)
    holder_type = Column(String(50), nullable=True)
    shares = Column(Float, nullable=True)
    shares_percent = Column(Float, nullable=True)

    # Additional information
    national_id = Column(String(20), nullable=True, index=True)
    change_percent = Column(Float, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    symbol = relationship("Symbol", back_populates="shareholders")

    # Indices
    __table_args__ = (
        SQLIndex('idx_shareholders_symbol_date', 'symbol', 'date'),
        SQLIndex('idx_shareholders_date', 'date'),
    )


# ==================== UTILITY FUNCTIONS ====================

def init_db():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)


def reset_table(model_class):
    """Drop and recreate a specific table"""
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    table_name = model_class.__tablename__

    with engine.connect() as conn:
        if inspector.has_table(table_name):
            conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
            conn.commit()

    model_class.__table__.create(bind=engine, checkfirst=True)


def reset_all_tables():
    """Drop and recreate all tables"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session (for dependency injection)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_session():
    """Get a session for database operations"""
    return SessionLocal()


# For backward compatibility
SymbolList = Symbol