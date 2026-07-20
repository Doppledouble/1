<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from "vue";
import flatpickr from "flatpickr";
import "flatpickr/dist/flatpickr.min.css";

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({ start: null, end: null }),
  },
  placeholder: {
    type: String,
    default: "Pilih rentang tanggal",
  },
});

const emit = defineEmits(["update:modelValue"]);

const inputRef = ref(null);
let fp = null;

onMounted(() => {
  fp = flatpickr(inputRef.value, {
    mode: "range",
    dateFormat: "d/m/Y",
    onChange: (selectedDates) => {
      if (selectedDates.length === 2) {
        emit("update:modelValue", { start: selectedDates[0], end: selectedDates[1] });
      } else if (selectedDates.length === 0) {
        emit("update:modelValue", { start: null, end: null });
      }
    },
  });
});

onBeforeUnmount(() => fp?.destroy());

// lets a parent "reset filters" button clear the picker programmatically
watch(
  () => props.modelValue,
  (value) => {
    if (!value?.start && !value?.end) fp?.clear();
  }
);
</script>

<template>
  <input ref="inputRef" type="text" :placeholder="placeholder" readonly />
</template>