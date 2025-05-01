"""Symbol schemas."""
from pydantic import BaseModel


class Symbol(BaseModel):
    """Symbol schema."""
    
    symbol: str
    base_asset: str
    quote_asset: str
