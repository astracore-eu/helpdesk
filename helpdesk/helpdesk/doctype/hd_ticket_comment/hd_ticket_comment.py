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
        preview = frappe.utils.strip_html(self.content or "")[:80]

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
                    "title": f"New comment in {ticket}",
                    "message": f"{self.commented_by}: {preview}",
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
