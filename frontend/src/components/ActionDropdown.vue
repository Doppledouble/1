<script setup>
import { ref, onMounted, onUnmounted } from "vue";

defineProps({
  actions: {
    type: Array,
    required: false,
    // [{ label: 'Assign', handler: fn, variant: 'default' | 'danger' }]
  },
});

const isOpen = ref(false);
const dropdownRef = ref(null);

const toggle = () => {
  isOpen.value = !isOpen.value;
};

const close = () => {
  isOpen.value = false;
};

const handleClickOutside = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    close();
  }
};

onMounted(() => {
  document.addEventListener("click", handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener("click", handleClickOutside);
});

const handleAction = (handler) => {
  handler();
  close();
};
</script>

<template>
  <div class="action-dropdown" ref="dropdownRef">
    <button class="dropdown-trigger" @click="toggle">
      Aksi
      <i :class="['ti', isOpen ? 'ti-chevron-up' : 'ti-chevron-down']" />
    </button>

    <div v-if="isOpen" class="dropdown-menu">
      <button
        v-for="action in actions"
        :key="action.label"
        class="dropdown-item"
        :class="action.variant"
        @click="handleAction(action.handler)"
      >
        {{ action.label }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.action-dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-trigger {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: 10px;
  cursor: pointer;
  padding: 6px 12px;
  font: inherit;
  font-size: 12px;
  font-weight: 600;
  color: var(--text);
}

.dropdown-trigger:hover {
  background: var(--surface);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 4px);
  right: 0;
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: 10px;
  min-width: 140px;
  z-index: 20;
  overflow: hidden;
  box-shadow: inset 0 1px 0 var(--white), 0 4px 12px rgba(0,0,0,0.08);
}

.dropdown-item {
  display: block;
  width: 100%;
  padding: 10px 14px;
  background: none;
  border: none;
  cursor: pointer;
  font: inherit;
  font-size: 13px;
  text-align: left;
  color: var(--text);
}

.dropdown-item:hover {
  background: var(--surface);
}

.dropdown-item.danger {
  color: #991B1B;
}
</style>