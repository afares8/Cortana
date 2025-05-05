from app.db.base import InMemoryDB
from app.services.traffic.models.traffic import TrafficSubmission, InvoiceRecord, InvoiceItem

traffic_submissions_db = InMemoryDB[TrafficSubmission](TrafficSubmission)
invoice_records_db = InMemoryDB[InvoiceRecord](InvoiceRecord)
invoice_items_db = InMemoryDB[InvoiceItem](InvoiceItem)
