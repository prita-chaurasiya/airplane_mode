# import frappe
# from frappe.model.document import Document
# from frappe.utils import now_datetime, add_to_date, get_datetime

# class AirplaneTicket(Document):

#     def before_insert(self):
#         self.set_departure_time()

#     def validate(self):
#         # safety check (update case me bhi correct rahe)
#         if not self.departure_time:
#             self.set_departure_time()

#     def set_departure_time(self):
#         # system current time (UTC safe handling)
#         current_time = get_datetime(now_datetime())

#         # +2 hours increment
#         departure_time = add_to_date(current_time, hours=2)

#         # assign
#         self.departure_time = departure_time
import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, add_to_date, get_datetime


class AirplaneTicket(Document):

    # -----------------------------
    # AUTO NAME
    # -----------------------------
    def autoname(self):

        count = frappe.db.count("Airplane Ticket") + 1

        self.name = (
            f"{self.flight}-"
            f"{self.source_airport_code}-TO-"
            f"{self.destination_airport_code}-"
            f"{count:05d}"
        )

    # -----------------------------
    # VALIDATION
    # -----------------------------
    def validate(self):

        if not self.passenger:
            frappe.throw("Passenger is required")

        if not self.flight:
            frappe.throw("Flight is required")

        self.set_departure_time()
        self.calculate_amounts()

    # -----------------------------
    # DEPARTURE TIME (+2 HOURS)
    # -----------------------------
    def set_departure_time(self):

        current_time = get_datetime(now_datetime())
        self.departure_time = add_to_date(current_time, hours=2)

    # -----------------------------
    # TAX + TOTAL CALCULATION
    # -----------------------------
    def calculate_amounts(self):

        price = float(self.ticket_price or 0)

        tax_map = {
            "0%": 0,
            "5%": 5,
            "12%": 12,
            "18%": 18,
            "28%": 28
        }

        tax_percent = tax_map.get(self.tax_rate, 0)

        tax_amount = (price * tax_percent) / 100
        total_amount = price + tax_amount

        self.tax_amount = tax_amount
        self.total_amount = total_amount


# -----------------------------
# EMAIL FUNCTION
# -----------------------------
@frappe.whitelist()
def send_ticket_email_api(docname):

    doc = frappe.get_doc("Airplane Ticket", docname)

    # Admin Email
    if doc.admin_email:
        frappe.sendmail(
            recipients=[doc.admin_email],
            subject=doc.email_subject or "New Airplane Ticket Created",
            message=doc.email_body or f"""
                <h3>✈ New Ticket Created</h3>
                <p><b>Passenger:</b> {doc.passenger}</p>
                <p><b>Flight:</b> {doc.flight}</p>
                <p><b>Price:</b> {doc.ticket_price}</p>
                <p><b>Tax:</b> {doc.tax_rate}</p>
                <p><b>Total:</b> {doc.total_amount}</p>
            """,
            now=True
        )

    # Passenger Email
    if doc.passenger_email:
        frappe.sendmail(
            recipients=[doc.passenger_email],
            subject="✈ Ticket Confirmed Successfully",
            message=f"""
                <h2>✈ Ticket Confirmed ✔</h2>

                <p><b>Passenger:</b> {doc.passenger}</p>
                <p><b>Ticket:</b> {doc.name}</p>
                <p><b>Flight:</b> {doc.flight}</p>
                <p><b>Departure:</b> {doc.departure_time}</p>

                <hr>

                <p><b>Price:</b> {doc.ticket_price}</p>
                <p><b>Tax:</b> {doc.tax_rate}</p>
                <p><b>Tax Amount:</b> {doc.tax_amount}</p>
                <p><b>Total:</b> {doc.total_amount}</p>
            """,
            now=True
        )

    return "Success"