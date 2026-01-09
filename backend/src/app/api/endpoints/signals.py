from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional, List
from datetime import datetime, timedelta
from app.core.database import db
from app.models.schemas import SignalCreate, SignalResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=SignalResponse, status_code=status.HTTP_201_CREATED)
async def create_signal(signal: SignalCreate):
    """Создать новый сигнал"""
    client = db.get_client()
    
    try:
        timestamp = signal.timestamp or datetime.utcnow()
        
        # Вставляем сигнал
        client.insert("signals", [[
            signal.bot_name,
            signal.symbol,
            signal.action.value,
            signal.price,
            timestamp,
            signal.comment
        ]], column_names=["bot_name", "symbol", "action", "price", "timestamp", "comment"])
        
        # Получаем созданный сигнал
        query = """
            SELECT id, bot_name, symbol, action, price, timestamp, comment
            FROM signals
            WHERE bot_name = %(bot_name)s AND symbol = %(symbol)s
            ORDER BY timestamp DESC
            LIMIT 1
        """
        
        result = client.query(query, {
            "bot_name": signal.bot_name,
            "symbol": signal.symbol
        })
        
        if not result.result_rows:
            raise HTTPException(status_code=500, detail="Failed to retrieve signal")
        
        row = result.result_rows[0]
        return SignalResponse(
            id=str(row[0]),
            bot_name=row[1],
            symbol=row[2],
            action=row[3],
            price=row[4],
            timestamp=row[5],
            comment=row[6]
        )
        
    except Exception as e:
        logger.error(f"Error creating signal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[SignalResponse])
async def get_signals(
    hours_limit: Optional[int] = Query(None, ge=1),
    symbol: Optional[str] = None,
    bot_name: Optional[str] = None
):
    """Получить список сигналов"""
    client = db.get_client()
    
    try:
        query = """
            SELECT id, bot_name, symbol, action, price, timestamp, comment
            FROM signals
            WHERE 1=1
        """
        
        params = {}
        
        # Фильтры
        if hours_limit:
            time_limit = datetime.utcnow() - timedelta(hours=hours_limit)
            query += " AND timestamp >= %(time_limit)s"
            params["time_limit"] = time_limit
        
        if symbol:
            query += " AND symbol = %(symbol)s"
            params["symbol"] = symbol
        
        if bot_name:
            query += " AND bot_name = %(bot_name)s"
            params["bot_name"] = bot_name
        
        query += " ORDER BY timestamp DESC LIMIT 1000"
        
        result = client.query(query, params)
        
        signals = []
        for row in result.result_rows:
            signals.append(SignalResponse(
                id=str(row[0]),
                bot_name=row[1],
                symbol=row[2],
                action=row[3],
                price=row[4],
                timestamp=row[5],
                comment=row[6]
            ))
        
        return signals
        
    except Exception as e:
        logger.error(f"Error fetching signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/latest", response_model=SignalResponse)
async def get_latest_signal():
    """Получить последний сигнал"""
    client = db.get_client()
    
    try:
        result = client.query("""
            SELECT id, bot_name, symbol, action, price, timestamp, comment
            FROM signals
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        
        if not result.result_rows:
            raise HTTPException(status_code=404, detail="No signals found")
        
        row = result.result_rows[0]
        return SignalResponse(
            id=str(row[0]),
            bot_name=row[1],
            symbol=row[2],
            action=row[3],
            price=row[4],
            timestamp=row[5],
            comment=row[6]
        )
        
    except Exception as e:
        logger.error(f"Error fetching latest signal: {e}")
        raise HTTPException(status_code=500, detail=str(e))
