<template>
  <FrappeUIProvider>
    <PortalRoot />
  </FrappeUIProvider>
  <Dialogs />
  <Toaster rich-colors close-button position="bottom-right" />
</template>

<script setup lang="ts">
import { Dialogs } from "@/components/dialogs";
import { useConfigStore } from "@/stores/config";
import { stopSession } from "@/telemetry";
import { FrappeUIProvider, toast } from "frappe-ui";
import { computed, defineAsyncComponent, h, onMounted, onUnmounted } from "vue";
import Wifi from "~icons/lucide/wifi";
import WifiOff from "~icons/lucide/wifi-off";
import { Toaster, toast as sonner } from "vue-sonner";
import "vue-sonner/style.css";

import { useAuthStore } from "./stores/auth";
import { useFavicon } from "@vueuse/core";
import { storeToRefs } from "pinia";
import { __ } from "./translation";

import { globalStore } from "@/stores/globalStore";

const configStore = useConfigStore();
const { favicon } = storeToRefs(configStore);

const { $socket } = globalStore();

useFavicon(favicon);

onMounted(() => {
  window.addEventListener("online", () => {
    toast.create({
      message: __("You are now online"),
      icon: h(Wifi, { class: "text-white" }),
    });
  });

  window.addEventListener("offline", () => {
    toast.create({
      message: __("You are now offline"),
      icon: h(WifiOff, { class: "text-white" }),
    });
  });

  $socket.on("helpdesk:new_message", (data) => {
    if (data.type === "alert") {
      sonner(data.title, {
        description: data.message,
        duration: Infinity,
        action: data.link
          ? {
              label: "Open",
              onClick: () => {
                window.location.href = data.link;
              },
            }
          : undefined,
      });
    }
  });

});

const AgentPortalRoot = defineAsyncComponent(
  () => import("@/pages/desk/AgentRoot.vue")
);
const CustomerPortalRoot = defineAsyncComponent(
  () => import("@/pages/CustomerPortalRoot.vue")
);

const PortalRoot = computed(() => {
  const authStore = useAuthStore();
  if (authStore.hasDeskAccess && authStore.isAgent) {
    return AgentPortalRoot;
  } else {
    return CustomerPortalRoot;
  }
});

onUnmounted(() => {
  stopSession();
});
</script>
