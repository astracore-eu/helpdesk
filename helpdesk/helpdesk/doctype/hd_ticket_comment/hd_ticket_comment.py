# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from helpdesk.mixins.mentions import HasMentions
from helpdesk.utils import capture_event, get_doc_room, publish_event


class HDTicketComment(HasMentions, Document):
    mentions_field = "content"

    def on_update(self):
        self.notify_mentions()

    def after_insert(self):
        event = "helpdesk:ticket-comment"
        data = {"ticket_id": self.reference_ticket}
        telemetry_event = "ticket_comment_added"

        room = get_doc_room("HD Ticket", self.reference_ticket)
        publish_event(
            event,
            room=room,
            data=data,
        )
        capture_event(telemetry_event)
        self._notify_assigned_agents()

    def _notify_assigned_agents(self):
        ticket = self.reference_ticket
        subject = frappe.db.get_value("HD Ticket", ticket, "subject") or ticket
        sender = frappe.db.get_value("User", self.commented_by, "full_name") or self.commented_by

        agents = frappe.get_all(
            "ToDo",
            filters={
                "reference_type": "HD Ticket",
                "reference_name": ticket,
                "status": ("!=", "Cancelled"),
            },
            pluck="owner",
        )

        for user in agents:
            if self.commented_by == user:
                continue

            frappe.publish_realtime(
                "helpdesk:new_message",
                {
                    "type": "alert",
                    "title": f"Ticket #{ticket}: {subject}",
                    "message": f"From: {sender}",
                    "link": f"/helpdesk/tickets/{ticket}",
                },
                user=user,
            )

    def after_delete(self):
        event = "helpdesk:ticket-comment"
        data = {"ticket_id": self.reference_ticket}
        telemetry_event = "ticket_comment_deleted"

        room = get_doc_room("HD Ticket", self.reference_ticket)
        publish_event(event, room=room, data=data)
        capture_event(telemetry_event)
