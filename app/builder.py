from lxml import etree
from typing import List

NSMAP = {
    'rsm': 'urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100',
    'ram': 'urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100',
    'qdt': 'urn:un:unece:uncefact:data:standard:QualifiedDataType:100',
    'udt': 'urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100',
}


def build_facturx_basic(invoice: dict) -> str:
    """Build a minimal Factur-X BASIC profile XML from invoice data."""
    root = etree.Element(f"{{{NSMAP['rsm']}}}CrossIndustryInvoice", nsmap=NSMAP)

    ctx = etree.SubElement(root, f"{{{NSMAP['rsm']}}}ExchangedDocumentContext")
    guideline = etree.SubElement(ctx, f"{{{NSMAP['ram']}}}GuidelineSpecifiedDocumentContextParameter")
    etree.SubElement(guideline, f"{{{NSMAP['ram']}}}ID").text = "urn:factur-x.eu:1p0:basic"

    doc = etree.SubElement(root, f"{{{NSMAP['rsm']}}}ExchangedDocument")
    etree.SubElement(doc, f"{{{NSMAP['ram']}}}ID").text = invoice['invoice_id']
    etree.SubElement(doc, f"{{{NSMAP['ram']}}}TypeCode").text = '380'
    issue_dt = etree.SubElement(doc, f"{{{NSMAP['ram']}}}IssueDateTime")
    etree.SubElement(issue_dt, f"{{{NSMAP['udt']}}}DateTimeString", format="102").text = invoice['issue_date']

    trn = etree.SubElement(root, f"{{{NSMAP['rsm']}}}SupplyChainTradeTransaction")
    line_total = 0.0
    tax_total = 0.0

    for idx, item in enumerate(invoice['items'], 1):
        line = etree.SubElement(trn, f"{{{NSMAP['ram']}}}IncludedSupplyChainTradeLineItem")
        doc_line = etree.SubElement(line, f"{{{NSMAP['ram']}}}AssociatedDocumentLineDocument")
        etree.SubElement(doc_line, f"{{{NSMAP['ram']}}}LineID").text = str(idx)

        prod = etree.SubElement(line, f"{{{NSMAP['ram']}}}SpecifiedTradeProduct")
        etree.SubElement(prod, f"{{{NSMAP['ram']}}}Name").text = item['name']

        agr = etree.SubElement(line, f"{{{NSMAP['ram']}}}SpecifiedLineTradeAgreement")
        gross = etree.SubElement(agr, f"{{{NSMAP['ram']}}}GrossPriceProductTradePrice")
        etree.SubElement(gross, f"{{{NSMAP['ram']}}}ChargeAmount").text = f"{item['price']:.2f}"
        net = etree.SubElement(agr, f"{{{NSMAP['ram']}}}NetPriceProductTradePrice")
        etree.SubElement(net, f"{{{NSMAP['ram']}}}ChargeAmount").text = f"{item['price']:.2f}"

        delivery = etree.SubElement(line, f"{{{NSMAP['ram']}}}SpecifiedLineTradeDelivery")
        etree.SubElement(
            delivery,
            f"{{{NSMAP['ram']}}}BilledQuantity",
            unitCode=item.get('unit_code', 'C62'),
        ).text = str(item['quantity'])

        settle = etree.SubElement(line, f"{{{NSMAP['ram']}}}SpecifiedLineTradeSettlement")
        tax = etree.SubElement(settle, f"{{{NSMAP['ram']}}}ApplicableTradeTax")
        etree.SubElement(tax, f"{{{NSMAP['ram']}}}TypeCode").text = 'VAT'
        etree.SubElement(tax, f"{{{NSMAP['ram']}}}CategoryCode").text = 'S'
        etree.SubElement(tax, f"{{{NSMAP['ram']}}}RateApplicablePercent").text = f"{item['tax_rate']:.2f}"

        line_amount = item['quantity'] * item['price']
        line_total += line_amount
        tax_total += line_amount * item['tax_rate'] / 100

        line_sum = etree.SubElement(settle, f"{{{NSMAP['ram']}}}SpecifiedTradeSettlementLineMonetarySummation")
        etree.SubElement(line_sum, f"{{{NSMAP['ram']}}}LineTotalAmount").text = f"{line_amount:.2f}"

    agreement = etree.SubElement(trn, f"{{{NSMAP['ram']}}}ApplicableHeaderTradeAgreement")
    seller = etree.SubElement(agreement, f"{{{NSMAP['ram']}}}SellerTradeParty")
    etree.SubElement(seller, f"{{{NSMAP['ram']}}}Name").text = invoice['seller']['name']
    buyer = etree.SubElement(agreement, f"{{{NSMAP['ram']}}}BuyerTradeParty")
    etree.SubElement(buyer, f"{{{NSMAP['ram']}}}Name").text = invoice['buyer']['name']

    etree.SubElement(trn, f"{{{NSMAP['ram']}}}ApplicableHeaderTradeDelivery")

    settlement = etree.SubElement(trn, f"{{{NSMAP['ram']}}}ApplicableHeaderTradeSettlement")
    etree.SubElement(settlement, f"{{{NSMAP['ram']}}}InvoiceCurrencyCode").text = invoice['currency']
    tax_e = etree.SubElement(settlement, f"{{{NSMAP['ram']}}}ApplicableTradeTax")
    etree.SubElement(tax_e, f"{{{NSMAP['ram']}}}TypeCode").text = 'VAT'
    etree.SubElement(tax_e, f"{{{NSMAP['ram']}}}CategoryCode").text = 'S'
    etree.SubElement(tax_e, f"{{{NSMAP['ram']}}}RateApplicablePercent").text = f"{invoice['items'][0]['tax_rate']:.2f}"

    summ = etree.SubElement(settlement, f"{{{NSMAP['ram']}}}SpecifiedTradeSettlementHeaderMonetarySummation")
    etree.SubElement(summ, f"{{{NSMAP['ram']}}}LineTotalAmount").text = f"{line_total:.2f}"
    etree.SubElement(summ, f"{{{NSMAP['ram']}}}TaxBasisTotalAmount").text = f"{line_total:.2f}"
    etree.SubElement(summ, f"{{{NSMAP['ram']}}}TaxTotalAmount", currencyID=invoice['currency']).text = f"{tax_total:.2f}"
    grand = line_total + tax_total
    etree.SubElement(summ, f"{{{NSMAP['ram']}}}GrandTotalAmount").text = f"{grand:.2f}"
    etree.SubElement(summ, f"{{{NSMAP['ram']}}}DuePayableAmount").text = f"{grand:.2f}"

    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8').decode()
