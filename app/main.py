"""
FastAPI application for TSETMC Data Management System

Provides comprehensive REST API endpoints for managing Tehran Stock Exchange data
including symbols, indices, prices, and market information.
"""

import logging
import sys
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Body, Query, Depends
from fastapi.background import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from app.db import SessionLocal, get_db, Symbol, Index, Market, Sector, Panel
from app.fetcher import (
    fetch_and_store_symbol_prices,
    fetch_and_store_index_prices,
    fetch_and_store_ri_data,
    fetch_and_store_shareholders_info,
    fetch_and_store_usd_irr_prices,
    initialize_all_lists,
    fetch_all_data,
    update_selected_symbols
)

# Configure encoding for Unicode support
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('tsetmc_api.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# Global task tracker
background_tasks = set()

# Pydantic Models for Request/Response
class UpdateSymbolsRequest(BaseModel):
    symbols: Optional[List[str]] = Field(None, description="List of symbol codes to update")
    adjust: bool = Field(True, description="Whether to use adjusted prices")
    background: bool = Field(False, description="Run in background")

class UpdateIndicesRequest(BaseModel):
    indices: Optional[List[str]] = Field(None, description="List of index names to update")
    background: bool = Field(False, description="Run in background")

class StatusResponse(BaseModel):
    status: str
    message: str
    timestamp: datetime
    task_id: Optional[str] = None

class DatabaseStats(BaseModel):
    symbols_count: int
    indices_count: int
    markets_count: int
    sectors_count: int
    panels_count: int
    symbol_prices_count: int
    index_prices_count: int

class SymbolInfo(BaseModel):
    symbol_en: str
    symbol_fa: str
    name: str
    market: str
    sector: str
    is_active: bool

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for startup and shutdown events"""
    # Startup
    logger.info("TSETMC API Server starting up...")
    yield
    # Shutdown
    logger.info("TSETMC API Server shutting down...")
    # Cancel all background tasks
    for task in background_tasks:
        task.cancel()
    background_tasks.clear()

# Create FastAPI application
app = FastAPI(
    title="TSETMC Data Management API",
    description="Comprehensive REST API for Tehran Stock Exchange data management",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency for database session
def get_database():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility Functions
def create_status_response(status: str, message: str, task_id: Optional[str] = None) -> StatusResponse:
    return StatusResponse(
        status=status,
        message=message,
        timestamp=datetime.now(),
        task_id=task_id
    )

async def run_in_background(task_func, *args, **kwargs):
    """Run a task in background and track it"""
    task = asyncio.create_task(task_func(*args, **kwargs))
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)
    return task

# Background Tasks
async def background_update_symbols(symbols: Optional[List[str]] = None, adjust: bool = True):
    """Background task for updating symbols"""
    try:
        if symbols:
            update_selected_symbols(symbols)
        else:
            fetch_and_store_symbol_prices(adjust=adjust)
        logger.info("Background symbol update completed")
    except Exception as e:
        logger.error(f"Background symbol update failed: {e}")

async def background_update_indices(indices: Optional[List[str]] = None):
    """Background task for updating indices"""
    try:
        fetch_and_store_index_prices(indices=indices)
        logger.info("Background index update completed")
    except Exception as e:
        logger.error(f"Background index update failed: {e}")

async def background_update_all():
    """Background task for updating all data"""
    try:
        fetch_all_data()
        logger.info("Background full update completed")
    except Exception as e:
        logger.error(f"Background full update failed: {e}")

# API Endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "TSETMC Data Management API",
        "version": "2.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/stats", response_model=DatabaseStats)
async def get_database_stats(db: SessionLocal = Depends(get_database)):
    """Get database statistics"""
    try:
        symbols_count = db.query(Symbol).count()
        indices_count = db.query(Index).count()
        markets_count = db.query(Market).count()
        sectors_count = db.query(Sector).count()
        panels_count = db.query(Panel).count()
        
        # Note: These would need proper counting from price tables
        symbol_prices_count = 0  # db.query(SymbolPrice).count()
        index_prices_count = 0   # db.query(IndexPrice).count()
        
        return DatabaseStats(
            symbols_count=symbols_count,
            indices_count=indices_count,
            markets_count=markets_count,
            sectors_count=sectors_count,
            panels_count=panels_count,
            symbol_prices_count=symbol_prices_count,
            index_prices_count=index_prices_count
        )
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/symbols", response_model=List[SymbolInfo])
async def get_symbols(
    active_only: bool = Query(True, description="Return only active symbols"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: SessionLocal = Depends(get_database)
):
    """Get list of symbols with pagination"""
    try:
        query = db.query(Symbol)
        if active_only:
            query = query.filter(Symbol.is_active == True)
        
        symbols = query.offset(skip).limit(limit).all()
        
        result = []
        for symbol in symbols:
            # Get market and sector names
            market_name = "Unknown"
            sector_name = "Unknown"
            
            if symbol.market_id:
                market = db.query(Market).filter(Market.market_id == symbol.market_id).first()
                if market:
                    market_name = market.market_name
            
            if symbol.sector_id:
                sector = db.query(Sector).filter(Sector.sector_id == symbol.sector_id).first()
                if sector:
                    sector_name = sector.sector_name
            
            result.append(SymbolInfo(
                symbol_en=symbol.symbol_en,
                symbol_fa=symbol.symbol_fa,
                name=symbol.name,
                market=market_name,
                sector=sector_name,
                is_active=bool(symbol.is_active)
            ))
        
        return result
    except Exception as e:
        logger.error(f"Error getting symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update/symbols", response_model=StatusResponse)
async def update_symbols(
    request: UpdateSymbolsRequest,
    background_tasks: BackgroundTasks
):
    """Update symbol prices"""
    try:
        if request.background:
            task = await run_in_background(
                background_update_symbols, 
                request.symbols, 
                request.adjust
            )
            return create_status_response(
                "started",
                "Symbol update started in background",
                str(id(task))
            )
        else:
            if request.symbols:
                update_selected_symbols(request.symbols)
            else:
                fetch_and_store_symbol_prices(adjust=request.adjust)
            
            return create_status_response(
                "completed",
                "Symbol prices updated successfully"
            )
    except Exception as e:
        logger.error(f"Error updating symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update/indices", response_model=StatusResponse)
async def update_indices(
    request: UpdateIndicesRequest,
    background_tasks: BackgroundTasks
):
    """Update index prices"""
    try:
        if request.background:
            task = await run_in_background(
                background_update_indices, 
                request.indices
            )
            return create_status_response(
                "started",
                "Index update started in background",
                str(id(task))
            )
        else:
            fetch_and_store_index_prices(indices=request.indices)
            return create_status_response(
                "completed",
                "Index prices updated successfully"
            )
    except Exception as e:
        logger.error(f"Error updating indices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update/investor-data", response_model=StatusResponse)
async def update_investor_data(background_tasks: BackgroundTasks):
    """Update retail/institutional data"""
    try:
        fetch_and_store_ri_data()
        return create_status_response(
            "completed",
            "Investor data updated successfully"
        )
    except Exception as e:
        logger.error(f"Error updating investor data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update/shareholders", response_model=StatusResponse)
async def update_shareholders(background_tasks: BackgroundTasks):
    """Update shareholder information"""
    try:
        fetch_and_store_shareholders_info()
        return create_status_response(
            "completed",
            "Shareholder information updated successfully"
        )
    except Exception as e:
        logger.error(f"Error updating shareholders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update/currency", response_model=StatusResponse)
async def update_currency():
    """Update USD/IRR exchange rates"""
    try:
        fetch_and_store_usd_irr_prices()
        return create_status_response(
            "completed",
            "Currency rates updated successfully"
        )
    except Exception as e:
        logger.error(f"Error updating currency: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update/all", response_model=StatusResponse)
async def update_all_data(background_tasks: BackgroundTasks):
    """Update all data (comprehensive update)"""
    try:
        task = await run_in_background(background_update_all)
        return create_status_response(
            "started",
            "Full data update started in background",
            str(id(task))
        )
    except Exception as e:
        logger.error(f"Error starting full update: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/initialize/database", response_model=StatusResponse)
async def initialize_database():
    """Initialize database with basic data"""
    try:
        initialize_all_lists()
        return create_status_response(
            "completed",
            "Database initialized successfully"
        )
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/background")
async def get_background_tasks():
    """Get information about running background tasks"""
    tasks_info = []
    for task in background_tasks:
        tasks_info.append({
            "task_id": str(id(task)),
            "done": task.done(),
            "cancelled": task.cancelled(),
            "exception": str(task.exception()) if task.exception() else None
        })
    
    return {
        "active_tasks": len(background_tasks),
        "tasks": tasks_info
    }

@app.get("/symbol/{symbol_code}")
async def get_symbol_info(symbol_code: str, db: SessionLocal = Depends(get_database)):
    """Get detailed information for a specific symbol"""
    try:
        symbol = db.query(Symbol).filter(Symbol.symbol_en == symbol_code).first()
        if not symbol:
            raise HTTPException(status_code=404, detail="Symbol not found")
        
        # Get related information
        market = db.query(Market).filter(Market.market_id == symbol.market_id).first()
        sector = db.query(Sector).filter(Sector.sector_id == symbol.sector_id).first()
        panel = db.query(Panel).filter(Panel.panel_id == symbol.panel_id).first() if symbol.panel_id else None
        
        return {
            "symbol_en": symbol.symbol_en,
            "symbol_fa": symbol.symbol_fa,
            "name": symbol.name,
            "name_en": symbol.name_en,
            "web_id": symbol.web_id,
            "industry": symbol.industry,
            "market": market.market_name if market else None,
            "sector": sector.sector_name if sector else None,
            "panel": panel.panel_name if panel else None,
            "is_active": bool(symbol.is_active),
            "last_price_update": symbol.last_price_update,
            "created_at": symbol.created_at,
            "updated_at": symbol.updated_at
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting symbol info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Additional utility endpoints
@app.get("/markets")
async def get_markets(db: SessionLocal = Depends(get_database)):
    """Get list of all markets"""
    try:
        markets = db.query(Market).all()
        return [
            {
                "market_id": market.market_id,
                "market_name": market.market_name,
                "description": market.description
            }
            for market in markets
        ]
    except Exception as e:
        logger.error(f"Error getting markets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sectors")
async def get_sectors(db: SessionLocal = Depends(get_database)):
    """Get list of all sectors"""
    try:
        sectors = db.query(Sector).all()
        return [
            {
                "sector_id": sector.sector_id,
                "sector_name": sector.sector_name,
                "sector_name_en": sector.sector_name_en,
                "english_name": sector.english_name
            }
            for sector in sectors
        ]
    except Exception as e:
        logger.error(f"Error getting sectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/tasks/background/{task_id}")
async def cancel_background_task(task_id: str):
    """Cancel a specific background task"""
    try:
        task_id_int = int(task_id)
        for task in background_tasks:
            if id(task) == task_id_int:
                task.cancel()
                background_tasks.discard(task)
                return create_status_response(
                    "cancelled",
                    f"Task {task_id} cancelled successfully"
                )
        
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID")
    except Exception as e:
        logger.error(f"Error cancelling task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )

def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Start the FastAPI server"""
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    start_server()