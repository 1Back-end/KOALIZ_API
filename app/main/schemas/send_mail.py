from pydantic import BaseModel,ConfigDict

class EmailData(BaseModel):
    email_to: str
    invoice_number: str
    recipient_name: str
    company_name: str
    company_address: str
    contact_phone: str
    contact_email: str


model_config = ConfigDict(from_attributes=True)
