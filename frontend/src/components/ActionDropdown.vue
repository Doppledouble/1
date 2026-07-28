<script setup>
import { ref, onUnmounted, nextTick } from "vue";

const props = defineProps({
  actions: {
    type: Array,
    required: false,
    // [{ label: 'Assign', handler: fn, variant: 'default' | 'danger' }]
  },
});

const isOpen = ref(false);
const triggerRef = ref(null);
const menuRef = ref(null);

const menuStyle = ref({});

const ITEM_HEIGHT = 40;
const MENU_WIDTH = 160;
const VIEWPORT_MARGIN = 8;

const computePosition = () => {
  if (!triggerRef.value) return;

  const rect = triggerRef.value.getBoundingClientRect();
  const estimatedHeight = (props.actions?.length ?? 0) * ITEM_HEIGHT + 8;

  const spaceBelow = window.innerHeight - rect.bottom;
  const spaceAbove = rect.top;
  const openUpward = spaceBelow < estimatedHeight + VIEWPORT_MARGIN && spaceAbove > spaceBelow;

  let left = rect.right - MENU_WIDTH;
  left = Math.max(VIEWPORT_MARGIN, Math.min(left, window.innerWidth - MENU_WIDTH - VIEWPORT_MARGIN));

  const top = openUpward ? rect.top - estimatedHeight - 4 : rect.bottom + 4;

  menuStyle.value = {
    position: "fixed",
    top: `${top}px`,
    left: `${left}px`,
    width: `${MENU_WIDTH}px`,
  };
};

const closeOnScrollOrResize = () => close();

const open = async () => {
  isOpen.value = true;
  await nextTick();
  computePosition();
  window.addEventListener("scroll", closeOnScrollOrResize, true);
  window.addEventListener("resize", closeOnScrollOrResize);
  document.addEventListener("click", handleClickOutside, true);
};

const close = () => {
  isOpen.value = false;
  window.removeEventListener("scroll", closeOnScrollOrResize, true);
  window.removeEventListener("resize", closeOnScrollOrResize);
  document.removeEventListener("click", handleClickOutside, true);
};

const toggle = () => {
  if (isOpen.value) {
    close();
  } else {
    open();
  }
};

const handleClickOutside = (event) => {
  const clickedTrigger = triggerRef.value?.contains(event.target);
  const clickedMenu = menuRef.value?.contains(event.target);
  if (!clickedTrigger && !clickedMenu) {
    close();
  }
};

const handleAction = (handler) => {
  handler();
  close();
};

onUnmounted(() => {
  window.removeEventListener("scroll", closeOnScrollOrResize, true);
  window.removeEventListener("resize", closeOnScrollOrResize);
});
</script>

<template>
  <div class="action-dropdown">
    <button ref="triggerRef" class="btn-ghost dropdown-trigger" @click="toggle">
      Aksi
      <i :class="['ti', isOpen ? 'ti-chevron-up' : 'ti-chevron-down']" />
    </button>

    <Teleport to="body">
      <div
        v-if="isOpen"
        ref="menuRef"
        class="dropdown-menu"
        :style="menuStyle"
      >
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
    </Teleport>
  </div>
</template>

<style scoped>
.action-dropdown {
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

</style>

<style>
.dropdown-menu {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: 10px;
  z-index: 9999;
  overflow: hidden;
  box-shadow: inset 0 1px 0 var(--white), 0 4px 12px rgba(0, 0, 0, 0.08);
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
  color: #991b1b;
}
</style>