<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  initialData: {
    type: Object,
    default: () => ({
      first_name: "",
      last_name: "",
      contact: null,
    }),
  },

  submitLabel: {
    type: String,
    default: "Simpan",
  },

  loading: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits([
  "submit",
  "cancel"
]);

const form = ref({
  first_name: "",
  last_name: "",
  contact: null,
});

watch(
  () => props.initialData,
  (value) => {
    form.value = { ...value };
  },
  { immediate: true }
);

const submitForm = () => {
  emit("submit", 
  { ...form.value,
    contact:
      form.value.contact?.trim() || null,
   });
};
</script>

<template>
  <div class="card employee-form-card">
    <form @submit.prevent="submitForm">

      <div class="form-group">
        <label>Nama Depan</label>

        <input
          v-model="form.first_name"
          type="text"
          required
        />
      </div>

      <div class="form-group">
        <label>Nama Belakang</label>

        <input
          v-model="form.last_name"
          type="text"
          required
        />
      </div>

      <div class="form-group">
        <label>Contact</label>

        <input
          v-model="form.contact"
          type="tel"
          placeholder="08xxxxxxxxxx"
        />
      </div>

      <div class="form-actions">

        <button
          type="button"
          class="btn-ghost"
          @click="$emit('cancel')"
        >
          Batal
        </button>

        <button
          type="submit"
          class="btn-acid"
          :disabled="loading"
        >
          {{ loading ? "Menyimpan..." : submitLabel }}
        </button>

      </div>

    </form>
  </div>
</template>

<style scoped>
.employee-form-card {
  max-width: 700px;
  margin: 0 auto;
  padding: 32px;
}

.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
}

.form-group label {
  margin-bottom: 8px;
  font-weight: 600;
}

.form-group input {
  padding: 14px;
  border: 1px solid var(--border);
  border-radius: 10px;
}

.form-checkbox {
  display: flex;
  gap: 10px;
  align-items: center;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 30px;
}
</style>