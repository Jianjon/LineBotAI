import logging
from app import app, db  # Import db also

# Set up logging for easier debugging
logging.basicConfig(level=logging.DEBUG)

# Create tables
with app.app_context():
    from models import User, Conversation  # Import models
    db.create_all()
    logging.debug("Database tables created or verified.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
