
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from .auth import get_current_user
from .database import (
    block_card_permanent, 
    get_account_by_id, 
    get_or_create_user,
    unblock_card, 
    get_card_status
)
from datetime import datetime, timezone

router = APIRouter()

class BlockCardRequest(BaseModel):
    reason: str

@router.post("/block-permanent/{account_id}")
def permanently_block_card_endpoint(
    account_id: str,
    request: BlockCardRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Permanently block/cancel a card (AGENTS & ADMINS ONLY).
    This is irreversible and requires agent verification.
    """
    role = current_user.get("role", "user")
    if role not in ["customer_support_agent", "admin"]:
        raise HTTPException(
            status_code=403, 
            detail="Forbidden: Only support agents can perform this action."
        )
    
    try:
        agent = get_or_create_user(
            current_user["email"],
            current_user.get("name"),
            role
        )
        
        if not agent or "user_id" not in agent:
            raise HTTPException(status_code=500, detail="Agent profile not found")
        
        account = get_account_by_id(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        success, message = block_card_permanent(
            account_id, 
            agent["user_id"], 
            request.reason
        )
        
        if success:
            return {
                "status": "success",
                "message": "Card permanently cancelled",
                "account_number": account.get("account_number"),
                "cancelled_by": agent.get("name"),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail=message)
    
    except Exception as e:
        print(f"Error in permanently blocking card endpoint: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred.")

# ... (other card-related endpoints like /status and /unblock)