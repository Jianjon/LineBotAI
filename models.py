import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Date
from app import db

class DailySummary(db.Model):
    """Model for daily conversation summaries"""
    __tablename__ = 'daily_summary'
    
    id = Column(Integer, primary_key=True)
    summary_date = Column(Date, unique=True, nullable=False)
    summary_content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<DailySummary {self.summary_date}>"

class User(db.Model):
    """Model for LINE users"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    line_user_id = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    role = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_interaction = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<User {self.line_user_id}>"

class Conversation(db.Model):
    """Model for conversation history"""
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<Conversation {self.id}>"