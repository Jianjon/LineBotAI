import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Print all database-related environment variables (without showing actual passwords)
db_url = os.environ.get("DATABASE_URL", "Not set")
masked_url = db_url
if "postgres://" in db_url or "postgresql://" in db_url:
    # Mask the password in the URL for logging
    parts = db_url.split("@")
    if len(parts) > 1:
        auth_parts = parts[0].split(":")
        if len(auth_parts) > 2:
            masked_url = f"{auth_parts[0]}:****@{parts[1]}"

logger.info(f"DATABASE_URL: {masked_url}")
logger.info(f"PGHOST: {os.environ.get('PGHOST', 'Not set')}")
logger.info(f"PGPORT: {os.environ.get('PGPORT', 'Not set')}")
logger.info(f"PGDATABASE: {os.environ.get('PGDATABASE', 'Not set')}")
logger.info(f"PGUSER: {os.environ.get('PGUSER', 'Not set')}")
logger.info(f"PGPASSWORD set: {'Yes' if os.environ.get('PGPASSWORD') else 'No'}")

# Try to connect to the database
try:
    import psycopg2
    
    # Try connecting directly with psycopg2 using environment variables
    logger.info("Attempting to connect using psycopg2 with environment variables...")
    conn = psycopg2.connect(
        host=os.environ.get("PGHOST"),
        port=os.environ.get("PGPORT"),
        database=os.environ.get("PGDATABASE"),
        user=os.environ.get("PGUSER"),
        password=os.environ.get("PGPASSWORD")
    )
    logger.info("✅ Successfully connected to the database using environment variables!")
    conn.close()
    
    # Try connecting with DATABASE_URL
    logger.info("Attempting to connect using psycopg2 with DATABASE_URL...")
    conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
    logger.info("✅ Successfully connected to the database using DATABASE_URL!")
    conn.close()
    
except Exception as e:
    logger.error(f"❌ Failed to connect to the database: {e}")