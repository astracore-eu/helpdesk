import { HDTicketPriority } from "@/types/doctypes";
import { parseColor } from "@/utils";
import { createListResource } from "frappe-ui";
import { defineStore } from "pinia";
import { colorMap } from "@/utils";

export const useTicketPriorityStore = defineStore("ticketPriority", () => {
  const priorities = createListResource({
    doctype: "HD Ticket Priority",
    cache: ["HD Ticket Priority", "list"],
    fields: [
      "color",
      "integer_value",
      "description"
    ],
    pageLength: 1000,
    auto: true,
    transform: (data: HDTicketPriority[]) => {
      return data.map((d) => {
        d["parsed_color"] = parseColor(d.color);
        return d;
      });
    },
  });

  const priorityMap = {
    Критичен: 1,
    Висок: 2,
    Среден: 3,
    Нисък: 4
  }

  function getPriority(label: string): HDTicketPriority | undefined {
    return priorities.data?.find(
      (s: HDTicketPriority) =>
        s.integer_value === priorityMap[label]
    );
  }

  return {
    priorities,
    colorMap,
    getPriority,
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
