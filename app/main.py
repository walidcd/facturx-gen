from fastapi import FastAPI, Response
from pydantic import BaseModel, Field
from typing import List
from facturx import xml_check_xsd
from .builder import build_facturx_basic

class Party(BaseModel):
    name: str

class Item(BaseModel):
    name: str
    quantity: float
    price: float
    tax_rate: float = 0.0
    unit_code: str = Field('C62', description="UNECE unit code")

class Invoice(BaseModel):
    invoice_id: str
    issue_date: str
    currency: str = 'EUR'
    seller: Party
    buyer: Party
    items: List[Item]

app = FastAPI()

@app.post('/generate_facturx')
def generate_facturx(invoice: Invoice):
    xml = build_facturx_basic(invoice.model_dump())
    xml_check_xsd(xml, flavor='factur-x', level='basic')
    return Response(content=xml, media_type='application/xml')
