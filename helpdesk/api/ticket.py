import frappe
from frappe import _
from frappe.utils import now

from helpdesk.utils import agent_only


def assign_ticket_to_agent(ticket_id, agent_id=None):
    if not ticket_id:
        return

    ticket_doc = frappe.get_doc("HD Ticket", ticket_id)

    if not agent_id:
        # assign to self
        agent_id = frappe.session.user

    if not frappe.db.exists("HD Agent", agent_id):
        frappe.throw(_("Tickets can only be assigned to agents"))

    ticket_doc.assign_agent(agent_id)
    return ticket_doc


@frappe.whitelist()
@agent_only
def bulk_assign_ticket_to_agent(ticket_ids, agent_id=None):
    if ticket_ids:
        ticket_docs = []
        for ticket_id in ticket_ids:
            ticket_doc = assign_ticket_to_agent(ticket_id, agent_id)
            ticket_docs.append(ticket_doc)
        return ticket_docs

@frappe.whitelist()
def mark_ticket_seen(ticket):
    user = frappe.session.user

    # check if already marked seen
    exists = frappe.db.exists(
        "HD Ticket Seen",
        {
            "parent": ticket,
            "parenttype": "HD Ticket",
            "user": user,
        },
    )

    if exists:
        return {"status": "already_seen"}

    frappe.get_doc({
        "doctype": "HD Ticket Seen",
        "parent": ticket,
        "parenttype": "HD Ticket",
        "parentfield": "seen_by",
        "user": user,
        "seen_on": now(),
    }).insert(ignore_permissions=True)

    frappe.db.commit()

    return {"status": "marked_seen"}

def mark_ticket_unread(ticket):
    doc = frappe.get_doc("HD Ticket", ticket)

    doc.set("seen_by", [])
    frappe.db.commit()

    doc.save(ignore_permissions=True)
