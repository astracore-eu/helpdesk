import { HDTicketStatus } from "@/types/doctypes";
import { parseColor } from "@/utils";
import { createListResource } from "frappe-ui";
import { defineStore } from "pinia";
import { colorMap } from "@/utils";

export const useTicketStatusStore = defineStore("ticketStatus", () => {
  const statuses = createListResource({
    doctype: "HD Ticket Status",
    cache: ["HD Ticket Status", "list"],
    fields: [
      "label_agent",
      "label_customer",
      "order",
      "different_view",
      "category",
      "color",
      "enabled",
    ],
    orderBy: "`tabHD Ticket Status`.order",
    pageLength: 1000,
    auto: true,
    transform: (data: HDTicketStatus[]) => {
      return data.map((d) => {
        if (!d.different_view) {
          d.label_customer = d.label_agent;
        }
        d["parsed_color"] = parseColor(d.color);
        return d;
      });
    },
  });

  function getStatus(label: string): HDTicketStatus | undefined {
    return statuses.data?.find(
      (s: HDTicketStatus) =>
        s.label_agent === label || s.label_customer === label
    );
  }

  return {
    statuses,
    colorMap,
    getStatus,
  };
});
function parseColor(color: string): string {
  color = color.toLowerCase();
  let textColor = `!text-${color}-600`;
  if (color == "black") {
    textColor = "!text-ink-gray-9";
  } else if (["gray", "green"].includes(color)) {
    textColor = `!text-${color}-700`;
  }

  return textColor;
}
