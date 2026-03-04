import frappe


def after_insert(doc, method=None):
    if doc.reference_doctype != "HD Ticket":
        return

    ticket = doc.reference_name

    preview = frappe.utils.strip_html(doc.content or "")[:80]

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
        if doc.owner == user:
            return

        # Possible to also insert the notification in the notification panel in future
        # frappe.get_doc({
        #     "doctype": "HD Notification",
        #     "user_from": doc.owner,
        #     "user_to": user,
        #     "notification_type": "Mention",
        #     "reference_ticket": ticket,
        #     "message": f"New message in {ticket}"
        # }).insert(ignore_permissions=True)

        frappe.publish_realtime(
            "helpdesk:new_message",
            {
                "type": "alert",
                "title": f"New message in {ticket}",
                "message": f"{doc.owner}: {preview}",
                "link": f"/helpdesk/tickets/{ticket}"
            },
            user=user
        )
