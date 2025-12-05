from django.db import connection

cursor = connection.cursor()
cursor.execute(
    """
    SELECT name FROM sqlite_master 
    WHERE type='index' 
    AND (name LIKE '%vehicle_category%' 
         OR name LIKE '%immat_aerienne%' 
         OR name LIKE '%francisation%' 
         OR name LIKE '%grid_type%' 
         OR name LIKE '%maritime_category%' 
         OR name LIKE '%aerial_type%')
"""
)

print("Indexes created:")
for row in cursor.fetchall():
    print(" -", row[0])
