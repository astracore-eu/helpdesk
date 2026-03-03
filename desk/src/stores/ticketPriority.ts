import { HDTicketPriority } from "@/types/doctypes";
import { parseColor } from "@/utils";
import { createListResource } from "frappe-ui";
import { defineStore } from "pinia";

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

    const colorMap = {
        Green: ["text-green-700", "bg-surface-green-2"],
        Black: ["text-black", "bg-surface-gray-2"],
        Gray: ["text-gray-700", "bg-surface-gray-2"],
        Blue: ["text-blue-700", "bg-surface-blue-2"],
        Red: ["text-red-500", "bg-surface-red-1"],
        Pink: ["text-pink-500", "bg-surface-pink-1"],
        Orange: ["text-orange-600", "bg-surface-orange-1"],
        Amber: ["text-amber-700", "bg-surface-amber-2"],
        Yellow: ["text-yellow-700", "bg-surface-amber-2"],
        Cyan: ["text-cyan-700", "bg-surface-cyan-1"],
        Teal: ["text-teal-700", "bg-teal-100"],
        Violet: ["text-violet-700", "bg-surface-violet-1"],
        Purple: ["text-purple-700", "bg-purple-100"],
        Default: ["text-ink-gray-9", "bg-surface-gray-2"],
    };

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
