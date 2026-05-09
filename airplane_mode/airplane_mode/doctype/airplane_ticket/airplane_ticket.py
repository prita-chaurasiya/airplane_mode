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

        # Departure time auto set
        self.set_departure_time()

    # -----------------------------
    # DEPARTURE TIME (+2 HOURS)
    # -----------------------------
    def set_departure_time(self):

        current_time = get_datetime(now_datetime())
        self.departure_time = add_to_date(current_time, hours=2)


# -----------------------------
# EMAIL API FUNCTION
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
                <h3>New Ticket Created ✔</h3>
                <p><b>Passenger:</b> {doc.passenger}</p>
                <p><b>Flight:</b> {doc.flight}</p>
                <p><b>Ticket:</b> {doc.name}</p>
            """,
            now=True
        )

    # Passenger Email
    if doc.passenger_email:
        frappe.sendmail(
            recipients=[doc.passenger_email],
            subject="✈ Ticket Verification Successful",
            message=f"""
                <h2>Your Flight Ticket is Confirmed ✔</h2>

                <p><b>Passenger:</b> {doc.passenger}</p>
                <p><b>Ticket:</b> {doc.name}</p>
                <p><b>Flight:</b> {doc.flight}</p>
                <p><b>Departure Time:</b> {doc.departure_time}</p>

                <p>Status: Verified ✔</p>
            """,
            now=True
        )

    return "Success"