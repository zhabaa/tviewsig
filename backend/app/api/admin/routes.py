# Добавим эти импорты в начало файла
from datetime import datetime, timedelta

# Добавим эти эндпоинты в router

@router.get("/api/analytics")
async def admin_analytics_api(
    days: int = Query(30, ge=1, le=365),
    admin: dict = Depends(verify_admin_key)
):
    """API для получения аналитики"""
    try:
        client = get_client()
        
        # Основная статистика
        total_query = "SELECT COUNT(*) FROM signals"
        total = client.query(total_query).first_row[0]
        
        # Среднее в день
        avg_query = f"""
            SELECT COUNT(*) / {days} as avg_daily
            FROM signals
            WHERE timestamp >= now() - INTERVAL {days} DAY
        """
        avg_result = client.query(avg_query)
        avg_daily = avg_result.first_row[0] if avg_result.first_row else 0
        
        # Уникальные боты и символы
        unique_bots_query = f"""
            SELECT COUNT(DISTINCT bot_name) 
            FROM signals 
            WHERE timestamp >= now() - INTERVAL {days} DAY
        """
        unique_bots = client.query(unique_bots_query).first_row[0]
        
        unique_symbols_query = f"""
            SELECT COUNT(DISTINCT symbol) 
            FROM signals 
            WHERE timestamp >= now() - INTERVAL {days} DAY
        """
        unique_symbols = client.query(unique_symbols_query).first_row[0]
        
        # Данные по часам
        hourly_query = f"""
            SELECT 
                toHour(timestamp) as hour,
                COUNT(*) as count
            FROM signals
            WHERE timestamp >= now() - INTERVAL {days} DAY
            GROUP BY hour
            ORDER BY hour
        """
        hourly_result = client.query(hourly_query).result_rows
        hourly_data = [0] * 24
        for hour, count in hourly_result:
            if 0 <= hour < 24:
                hourly_data[hour] = count
        
        # Топ ботов
        top_bots_query = f"""
            SELECT 
                bot_name, 
                COUNT(*) as signal_count
            FROM signals
            WHERE timestamp >= now() - INTERVAL {days} DAY
            GROUP BY bot_name
            ORDER BY signal_count DESC
            LIMIT 10
        """
        top_bots_result = client.query(top_bots_query).result_rows
        top_bots_labels = [row[0] for row in top_bots_result]
        top_bots_data = [row[1] for row in top_bots_result]
        
        # Данные по дням
        daily_query = f"""
            SELECT 
                toDate(timestamp) as date,
                COUNT(*) as count
            FROM signals
            WHERE timestamp >= now() - INTERVAL {days} DAY
            GROUP BY date
            ORDER BY date
        """
        daily_result = client.query(daily_query).result_rows
        daily_labels = [row[0].strftime('%Y-%m-%d') for row in daily_result]
        daily_data = [row[1] for row in daily_result]
        
        # Топ символов
        top_symbols_query = f"""
            SELECT 
                symbol,
                COUNT(*) as signal_count,
                SUM(CASE WHEN action = 'BUY' THEN 1 ELSE 0 END) as buy_count,
                SUM(CASE WHEN action = 'SELL' THEN 1 ELSE 0 END) as sell_count,
                AVG(price) as avg_price
            FROM signals
            WHERE timestamp >= now() - INTERVAL {days} DAY
            GROUP BY symbol
            ORDER BY signal_count DESC
            LIMIT 10
        """
        top_symbols = []
        for row in client.query(top_symbols_query).result_rows:
            top_symbols.append({
                "symbol": row[0],
                "signal_count": row[1],
                "buy_count": row[2],
                "sell_count": row[3],
                "avg_price": float(row[4]) if row[4] else None
            })
        
        return JSONResponse({
            "total": total,
            "avg_daily": float(avg_daily),
            "unique_bots": unique_bots,
            "unique_symbols": unique_symbols,
            "hourly_data": hourly_data,
            "top_bots_labels": top_bots_labels,
            "top_bots_data": top_bots_data,
            "daily_labels": daily_labels,
            "daily_data": daily_data,
            "top_symbols": top_symbols
        })
        
    except Exception as e:
        logger.error(f"Ошибка получения аналитики: {e}")
        return JSONResponse({"error": str(e)})


@router.get("/api/export")
async def admin_export_data(
    admin: dict = Depends(verify_admin_key)
):
    """Экспорт данных в JSON"""
    try:
        client = get_client()
        
        # Получаем все сигналы
        signals_query = """
            SELECT 
                id, bot_name, symbol, action, price, timestamp, comment
            FROM signals
            ORDER BY timestamp DESC
            LIMIT 10000
        """
        signals = client.query(signals_query).result_rows
        
        # Формируем данные для экспорта
        export_data = {
            "export_date": datetime.utcnow().isoformat(),
            "total_signals": len(signals),
            "signals": [
                {
                    "id": str(s[0]),
                    "bot_name": s[1],
                    "symbol": s[2],
                    "action": s[3],
                    "price": float(s[4]),
                    "timestamp": s[5].isoformat() if s[5] else None,
                    "comment": s[6]
                }
                for s in signals
            ]
        }
        
        # Возвращаем как JSON файл
        import json
        from fastapi.responses import Response
        
        json_data = json.dumps(export_data, ensure_ascii=False, indent=2)
        return Response(
            content=json_data,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=signals_export_{datetime.utcnow().date()}.json"
            }
        )
        
    except Exception as e:
        logger.error(f"Ошибка экспорта данных: {e}")
        return JSONResponse({"error": str(e)})


@router.post("/api/clear-old")
async def admin_clear_old_data(
    days: int = Form(90),
    admin: dict = Depends(verify_admin_key)
):
    """Удаление старых данных"""
    try:
        client = get_client()
        
        # Получаем количество записей для удаления
        count_query = f"""
            SELECT COUNT(*) 
            FROM signals 
            WHERE timestamp < now() - INTERVAL {days} DAY
        """
        count_result = client.query(count_query)
        to_delete = count_result.first_row[0] if count_result.first_row else 0
        
        if to_delete > 0:
            # Удаляем старые записи
            delete_query = f"""
                ALTER TABLE signals 
                DELETE WHERE timestamp < now() - INTERVAL {days} DAY
            """
            client.command(delete_query)
        
        return JSONResponse({
            "success": True,
            "deleted": to_delete,
            "message": f"Удалено {to_delete} записей старше {days} дней"
        })
        
    except Exception as e:
        logger.error(f"Ошибка очистки данных: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e)
        })
