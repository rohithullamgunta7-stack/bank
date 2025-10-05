
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Literal, List, Dict, Any
import re
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime

# Add these to your existing models.py

class FAQCreate(BaseModel):
    question: str
    answer: str
    category: str
    tags: List[str] = []
    source: str = "manual"  # manual, auto_generated, conversation
    
    @validator('question')
    def validate_question(cls, v):
        if not v.strip():
            raise ValueError('Question cannot be empty')
        if len(v) < 10:
            raise ValueError('Question too short (min 10 characters)')
        return v.strip()
    
    @validator('answer')
    def validate_answer(cls, v):
        if not v.strip():
            raise ValueError('Answer cannot be empty')
        if len(v) < 20:
            raise ValueError('Answer too short (min 20 characters)')
        return v.strip()

class FAQUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None

class FAQResponse(BaseModel):
    faq_id: str
    question: str
    answer: str
    category: str
    tags: List[str]
    source: str
    usage_count: int
    helpful_count: int
    not_helpful_count: int
    is_active: bool
    created_at: str
    updated_at: Optional[str] = None

class FAQSearchQuery(BaseModel):
    query: str
    limit: int = 10
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()

class FAQFeedback(BaseModel):
    faq_id: str
    helpful: bool
    comment: Optional[str] = None

class ConversationPattern(BaseModel):
    pattern_id: Optional[str] = None
    question_pattern: str
    answer_pattern: str
    occurrence_count: int = 1
    success_rate: float = 0.0
    category: str
    tags: List[str] = []
    sample_conversations: List[str] = []
# Define role types
UserRole = Literal["user", "customer_support_agent", "admin"]

# Add these to models.py

class FeedbackSubmission(BaseModel):
    rating: int
    comment: Optional[str] = None
    issue_resolved: bool
    conversation_id: Optional[str] = None
    escalation_id: Optional[str] = None
    feedback_type: Literal["bot_chat", "agent_support", "general"] = "bot_chat"
    
    @validator('rating')
    def validate_rating(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('Rating must be between 1 and 5')
        return v
    
    @validator('comment')
    def validate_comment(cls, v):
        if v and len(v) > 500:
            raise ValueError('Comment too long (max 500 characters)')
        return v.strip() if v else None

class FeedbackResponse(BaseModel):
    feedback_id: str
    message: str
    sentiment: Optional[str] = None

class FeedbackAnalytics(BaseModel):
    total_feedback: int
    average_rating: float
    sentiment_distribution: dict
    response_rate: float
    recent_feedback: list
    rating_distribution: dict
    trend: dict
    
class UserSignup(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: Optional[UserRole] = "user"

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        return v

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v.strip()

    @validator('email')
    def validate_email(cls, v):
        return v.lower().strip()

    @validator('role')
    def validate_role(cls, v):
        if v not in ["user", "customer_support_agent", "admin"]:
            raise ValueError('Role must be user, customer_support_agent, or admin')
        return v

class AdminSignup(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: UserRole
    admin_secret: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v.strip()

    @validator('email')
    def validate_email(cls, v):
        return v.lower().strip()

    @validator('role')
    def validate_role(cls, v):
        if v not in ["customer_support_agent", "admin"]:
            raise ValueError('Role must be customer_support_agent or admin')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @validator('email')
    def validate_email(cls, v):
        return v.lower().strip()

    @validator('password')
    def validate_password(cls, v):
        if not v:
            raise ValueError('Password is required')
        return v

class Token(BaseModel):
    access_token: str
    token_type: str

class MessageRequest(BaseModel):
    message: str

    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        if len(v.strip()) > 1000:
            raise ValueError('Message too long (max 1000 characters)')
        return v.strip()

# FIXED: Single MessageResponse with orders field
class MessageResponse(BaseModel):
    reply: str
    orders: Optional[List[Dict[str, Any]]] = None

class UserInfo(BaseModel):
    user_id: str
    email: str
    name: str
    role: UserRole
    created_at: Optional[str] = None

class RoleUpdateRequest(BaseModel):
    user_id: str
    new_role: UserRole

    @validator('new_role')
    def validate_role(cls, v):
        if v not in ["user", "customer_support_agent", "admin"]:
            raise ValueError('Role must be user, customer_support_agent, or admin')
        return v

class ConversationSummary(BaseModel):
    user_id: str
    user_name: str
    user_email: str
    message_count: int
    last_message: str
    last_timestamp: str

class DashboardStats(BaseModel):
    total_users: int
    total_conversations: int
    active_support_agents: int
    recent_activity: list

EscalationPriority = Literal["critical", "high", "medium", "low"]
EscalationStatus = Literal["pending", "assigned", "resolved", "closed"]

class EscalationRequest(BaseModel):
    reason: str
    issue_type: Optional[str] = None
    
    @validator('reason')
    def validate_reason(cls, v):
        if not v.strip():
            raise ValueError('Reason cannot be empty')
        if len(v.strip()) > 500:
            raise ValueError('Reason too long (max 500 characters)')
        return v.strip()

class AgentResponse(BaseModel):
    escalation_id: str
    message: str
    action_taken: Optional[str] = None
    
    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()

class EscalationResolution(BaseModel):
    escalation_id: str
    resolution_notes: str
    action_taken: str
    customer_satisfied: bool
    compensation_provided: Optional[str] = None
    
    @validator('resolution_notes')
    def validate_notes(cls, v):
        if not v.strip():
            raise ValueError('Resolution notes cannot be empty')
        return v.strip()

class EscalationNote(BaseModel):
    escalation_id: str
    note: str
    
    @validator('note')
    def validate_note(cls, v):
        if not v.strip():
            raise ValueError('Note cannot be empty')
        return v.strip()