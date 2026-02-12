import { call } from "frappe-ui";
import { ref, watch } from "vue";

type ViewForCount = {
  name: string;
  dt?: string;
  filters?: Record<string, any>;
};

export function useViewCounts(viewsRef) {
  const counts = ref<Record<string, number>>({});
  const loading = ref(false);

  async function fetchCounts(views: ViewForCount[]) {
    if (!views || views.length === 0) {
      counts.value = {};
      return;
    }

    loading.value = true;
    const entries = await Promise.all(
      views.map(async (view) => {
        try {
          const count = await call("frappe.client.get_count", {
            doctype: view.dt || "HD Ticket",
            filters: view.filters || {},
          });
          return [view.name, count] as const;
        } catch (error) {
          return [view.name, 0] as const;
        }
      })
    );

    const nextCounts: Record<string, number> = {};
    for (const [name, count] of entries) {
      nextCounts[name] = count;
    }
    counts.value = nextCounts;
    loading.value = false;
  }

  watch(
    viewsRef,
    (views) => {
      fetchCounts(views || []);
    },
    { immediate: true, deep: true }
  );

  return {
    counts,
    loading,
    reload: () => fetchCounts(viewsRef.value || []),
  };
}
