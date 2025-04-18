import os
import logging
import datetime
from flask import Flask, request, abort, render_template, jsonify, redirect, url_for
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from openai_service import generate_response
import traceback
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Configure database
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    # For SQLAlchemy 1.4+, we need to modify the database URL
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
else:
    logging.error("DATABASE_URL environment variable not set!")

# Initialize the database with the app
db.init_app(app)

# LINE Bot credentials
CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")

# Initialize LINE Bot API and WebhookHandler
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# Setup logging
logger = logging.getLogger(__name__)

@app.route("/")
def index():
    """Render the home page."""
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    """Display admin dashboard."""
    from models import User, Conversation
    import datetime
    
    users = User.query.all()
    total_conversations = Conversation.query.count()
    
    # Calculate active users today
    today_start = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    active_today = User.query.filter(User.last_interaction >= today_start).count()
    
    return render_template(
        "dashboard.html", 
        users=users, 
        total_conversations=total_conversations, 
        active_today=active_today
    )

@app.route("/user/<int:user_id>")
def view_user(user_id):
    """View user conversation history."""
    from models import User, Conversation
    
    user = User.query.get_or_404(user_id)
    conversations = Conversation.query.filter_by(user_id=user_id).order_by(Conversation.timestamp.desc()).all()
    
    return render_template("user_conversations.html", user=user, conversations=conversations)

@app.route("/user/<int:user_id>/edit")
def edit_user(user_id):
    """Edit user information."""
    from models import User
    
    user = User.query.get_or_404(user_id)
    return render_template("edit_user.html", user=user)

@app.route("/user/<int:user_id>/update", methods=["POST"])
def update_user(user_id):
    """Update user information."""
    from models import User
    
    user = User.query.get_or_404(user_id)
    
    # Update user information
    user.display_name = request.form.get("display_name", user.display_name)
    user.industry = request.form.get("industry")
    user.role = request.form.get("role")
    
    # Save changes
    db.session.commit()
    logger.debug(f"Updated user: {user}")
    
    return redirect(url_for("view_user", user_id=user.id))

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle webhook requests from LINE."""
    # Get X-Line-Signature header value
    signature = request.headers.get("X-Line-Signature")
    
    # Get request body as text
    body = request.get_data(as_text=True)
    logger.debug(f"Request body: {body}")
    
    try:
        # Handle webhook body
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature")
        abort(400)
    except Exception as e:
        logger.error(f"Error: {e}")
        traceback.print_exc()
        abort(500)
    
    return "OK"

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """Handle text message from LINE."""
    try:
        user_message = event.message.text
        line_user_id = event.source.user_id
        logger.debug(f"Received message from {line_user_id}: {user_message}")
        
        # Check if the user exists in the database, otherwise create
        from models import User, Conversation
        user = User.query.filter_by(line_user_id=line_user_id).first()
        
        if not user:
            # Try to get user profile from LINE
            try:
                profile = line_bot_api.get_profile(line_user_id)
                user = User(
                    line_user_id=line_user_id,
                    display_name=profile.display_name
                )
            except Exception as profile_error:
                logger.error(f"Error getting user profile: {profile_error}")
                user = User(line_user_id=line_user_id)
            
            db.session.add(user)
            db.session.commit()
            logger.debug(f"Created new user: {user}")
        else:
            # Update last interaction time
            user.last_interaction = datetime.datetime.utcnow()
            db.session.commit()
        
        # Generate response using OpenAI
        ai_response = generate_response(user_message)
        logger.debug(f"AI response: {ai_response}")
        
        # Save conversation
        conversation = Conversation(
            user_id=user.id,
            user_message=user_message,
            bot_response=ai_response
        )
        db.session.add(conversation)
        db.session.commit()
        logger.debug(f"Saved conversation: {conversation}")
        
        # Send response back to LINE
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=ai_response)
        )
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        traceback.print_exc()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="抱歉，我暫時無法處理您的訊息。請稍後再試。")
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
