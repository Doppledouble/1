<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from "vue";
import flatpickr from "flatpickr";
import "flatpickr/dist/flatpickr.min.css";

const props = defineProps({
  modelValue: {
    type: String, // same "yyyy-MM-ddTHH:mm" shape native datetime-local produces, or null
    default: null,
  },
  placeholder: {
    type: String,
    default: "Pilih tanggal & waktu",
  },
});

const emit = defineEmits(["update:modelValue"]);

const inputRef = ref(null);
let fp = null;

const toLocalInputString = (date) => {
  const pad = (n) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
};

onMounted(() => {
  fp = flatpickr(inputRef.value, {
    enableTime: true,
    dateFormat: "d/m/Y H:i",
    time_24hr: true,
    defaultDate: props.modelValue || null,
    onChange: (selectedDates) => {
      emit("update:modelValue", selectedDates.length === 1 ? toLocalInputString(selectedDates[0]) : null);
    },
  });
});

onBeforeUnmount(() => fp?.destroy());

watch(
  () => props.modelValue,
  (value) => {
    if (!value) fp?.clear();
  }
);
</script>

<template>
  <input ref="inputRef" type="text" :placeholder="placeholder" readonly />
</template>