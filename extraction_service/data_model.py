from pydantic import BaseModel

class Receipt(BaseModel):
    """
    Data model for a receipt
    """

    businessname: str
    date: str
    total: str
    category: str
