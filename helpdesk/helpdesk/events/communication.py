import frappe


def after_insert(doc, method=None):
    print("Firing")
    if doc.reference_doctype != "HD Ticket":
        return

    ticket = doc.reference_name
    subject = frappe.db.get_value("HD Ticket", ticket, "subject") or ticket
    sender = doc.sender_full_name or doc.sender or doc.owner

    agents = frappe.get_all(
        "ToDo",
        filters={
            "reference_type": "HD Ticket",
            "reference_name": ticket,
            "status": ("!=", "Cancelled")
        },
        pluck="owner"
    )

    for user in agents:
        if doc.sender and doc.sender == user:
            continue

        frappe.publish_realtime(
            "helpdesk:new_message",
            {
                "type": "alert",
                "title": f"Ticket #{ticket}: {subject}",
                "message": f"From: {sender}",
                "link": f"/helpdesk/tickets/{ticket}"
            },
            user=user
        )
