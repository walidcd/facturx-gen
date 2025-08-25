from facturx import xml_check_xsd
from app.builder import build_facturx_basic

sample_invoice = {
    'invoice_id': 'INV-1',
    'issue_date': '20240317',
    'currency': 'EUR',
    'seller': {'name': 'Seller Corp'},
    'buyer': {'name': 'Buyer Inc'},
    'items': [
        {'name': 'Product', 'quantity': 1, 'price': 100.0, 'tax_rate': 0.0}
    ]
}

def test_build_facturx_basic():
    xml = build_facturx_basic(sample_invoice)
    assert '<rsm:CrossIndustryInvoice' in xml
    xml_check_xsd(xml, flavor='factur-x', level='basic')
