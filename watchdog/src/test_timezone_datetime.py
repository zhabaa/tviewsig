from datetime import datetime, timezone
for _ in range(3): print()

# Тест 1 - старая версия (deprecated)
result1 = datetime.utcnow().isoformat()
print("old:", result1)
print("type:", type(result1))

for _ in range(3): print()

# Тест 2 - новая версия
result2 = datetime.now(timezone.utc).isoformat()
print("new:", result2)
print("type:", type(result2))

for _ in range(3): print()

# Сравнение
print("Строки одинаковые?", result1 == result2)

for _ in range(3): print()

# Дополнительная проверка - разница во времени
dt1 = datetime.utcnow()
dt2 = datetime.now(timezone.utc).replace(tzinfo=None)  # убираем таймзону для сравнения
print("Время совпадает?", dt1 == dt2)
