<script setup>
import { ref, watch, onMounted, computed } from "vue";
import api from "../services/api.js";
import Multiselect from "vue-multiselect";
import "vue-multiselect/dist/vue-multiselect.css";

const props = defineProps({
  initialData: {
    type: Object,
    default: () => ({
      item_id: "",
      employee_id: "",
      location: "",
      quantity: 1,
      notes: "",
    }),
  },
  submitLabel: { type: String, default: "Simpan" },
  loading: { type: Boolean, default: false },
});

const emit = defineEmits(["submit"]);

const items = ref([]);
const employees = ref([]);

onMounted(async () => {
  try {
    const requests = [api.get("/employees")];

    if (!props.initialData?.item_id) {
      requests.unshift(api.get("/items/material")); // ← only materials
    } else {
      requests.unshift(api.get(`/items/${props.initialData.item_id}`));
    }

    const [itemsRes, employeesRes] = await Promise.all(requests);

    items.value = props.initialData?.item_id
      ? [itemsRes.data]
      : itemsRes.data;

    employees.value = employeesRes.data;
  } catch (error) {
    console.error("Failed to load withdraw data", error);
  }
});

const form = ref({
  item_id: null,
  employee_id: null,
  location: "",
  quantity: 1,
  notes: "",
});

const selectedItem = ref(null);
const selectedEmployee = ref(null);

watch(() => props.initialData, (value) => {
  form.value = { ...value };
}, { immediate: true });

watch([items, () => form.value.item_id], ([itemList, itemId]) => {
  selectedItem.value = itemList.find(i => i.id === itemId) || null;
});

watch([employees, () => form.value.employee_id], ([empList, empId]) => {
  selectedEmployee.value = empList.find(e => e.id === empId) || null;
});

const onItemSelect = (option) => {
  form.value.item_id = option ? option.id : null;
};

const onEmployeeSelect = (option) => {
  form.value.employee_id = option ? option.id : null;
};

const isItemLocked = computed(() => !!props.initialData?.item_id);
const employeeLabel = (e) => `${e.first_name} ${e.last_name}`;

const submitForm = () => {
  emit("submit", { ...form.value });
};
</script>

<template>
  <div class="card item-form-card">
    <form @submit.prevent="submitForm">
      <div class="form-group">
        <label>Material</label>
        <Multiselect
          v-model="selectedItem"
          :options="items"
          label="name"
          track-by="id"
          placeholder="Pilih material"
          :disabled="isItemLocked"
          @update:model-value="onItemSelect"
        />
        <small v-if="isItemLocked" style="color: var(--text-muted)">
          Item sudah dipilih otomatis
        </small>
      </div>

      <div class="form-group">
        <label>
          Diambil Oleh
        </label>
        <Multiselect
          v-model="selectedEmployee"
          :options="employees"
          :custom-label="employeeLabel"
          track-by="id"
          placeholder="Pilih karyawan..."
          @update:model-value="onEmployeeSelect"
        />
      </div>

      <div class="form-group">
        <label>Jumlah</label>
        <input
          v-model.number="form.quantity"
          type="number"
          min="1"
          required
        />
      </div>

      <div class="form-group">
        <label>Lokasi Penggunaan</label>
        <input
          v-model="form.location"
          type="text"
          placeholder="Contoh: Site A, Lantai 3..."
        />
      </div>

      <div class="form-group">
        <label>
          Catatan
        </label>
        <input v-model="form.notes" type="text" placeholder="Catatan tambahan..." />
      </div>

      <div class="form-actions">
        <button type="button" class="btn-ghost" @click="$emit('cancel')">
          Batal
        </button>
        <button type="submit" class="btn-acid" :disabled="loading">
          {{ loading ? "Menyimpan..." : submitLabel }}
        </button>
      </div>

    </form>
  </div>
</template>

<style scoped>
.item-form-card {
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

.form-group input,
.form-group select {
  padding: 14px;
  border: 1px solid var(--border);
  border-radius: 10px;
  font: inherit;
  font-size: 14px;
  background: var(--white);
  color: var(--text);
}

.form-group input:focus {
  outline: none;
  border-color: var(--text);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 30px;
}
</style>