<template>
  <img
    v-if="config.brandLogo"
    :src="config.brandLogo"
    alt="Brand Logo"
    class="h-8 w-8 shrink-0 object-cover"
  />
  <img
    v-else
    :src="firmLogo"
    alt="Brand Logo"
    class="h-8 w-8 shrink-0 object-contain"
  />
</template>

<script setup lang="ts">
import firmLogo from "@/assets/logos/firmLogo-noBackground.png";

import { useConfigStore } from "@/stores/config";
const config = useConfigStore();
</script>

<style scoped></style>
