import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

async def test_sql_data() -> None:
    """Test the SQL data fetching function.
    """
    # Database connection
    db_connection = psycopg2.connect(os.getenv("DATABASE_URL"))
    sql_query = f"SELECT product_name_de FROM public.deals where category_level_1 = 'Obst, Gemüse' order by discount_percentage desc limit 1;"
    with db_connection.cursor() as cursor:
        cursor.execute(sql_query)
        records = cursor.fetchall()
        print(records)
    db_connection.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_sql_data())