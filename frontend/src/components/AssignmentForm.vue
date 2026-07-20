<script setup>
import { ref, watch, onMounted, computed } from "vue";
import api from "../services/api.js";
import Multiselect from "vue-multiselect"
import "vue-multiselect/dist/vue-multiselect.css"
import DateTimePicker from "./DateTimePicker.vue";

const props = defineProps({
  initialData: {
    type: Object,
    default: () => ({
      item_id:"",
      employee_id: "",
      location: "",
      quantity: 0,
      assigned_at: null,
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

const emit = defineEmits(["submit", "cancel"]);

const items = ref([])
const employees = ref([])

onMounted(async () => {
  try {
    const requests = [
      api.get("/employees"),
    ]
    if (!props.initialData?.item_id) {
      requests.unshift(api.get("/items/tool"))
    } else {
      requests.unshift(api.get(`/items/${props.initialData.item_id}`))
    }

    const [itemsRes, employeesRes] = await Promise.all(requests)

    
    items.value = props.initialData?.item_id 
      ? [itemsRes.data]  
      : itemsRes.data     

    employees.value = employeesRes.data
  } catch (error) {
    console.error("Failed to load assignment data", error)
  }
})

const form = ref({
  item_id: null,
  employee_id: null,
  location: null,
  quantity: 1,
  notes: "",
  assigned_at:null,
});

const selectedItem = ref(null)
const selectedEmployee = ref(null)

watch(
  () => props.initialData,
  (value) => {
    form.value = { ...value };
  },
  { immediate: true }
);


watch([items, () => form.value.item_id], ([itemList, itemId]) => {
  selectedItem.value = itemList.find(i => i.id === itemId) || null
})

watch([employees, () => form.value.employee_id], ([empList, empId]) => {
  selectedEmployee.value = empList.find(e => e.id === empId) || null
})


const onItemSelect = (option) => {
  form.value.item_id = option ? option.id : null
}

const onEmployeeSelect = (option) => {
  form.value.employee_id = option ? option.id : null
}

const isItemLocked = computed(() => !!props.initialData?.item_id)


const employeeLabel = (employee) => `${employee.first_name} ${employee.last_name}`

const submitForm = () => {
  emit("submit", { ...form.value });
};
</script>

<template>
  <div class="card item-form-card">
    <form @submit.prevent="submitForm">

      <div class="form-group">
        <label>Barang</label>
        <Multiselect
          v-model="selectedItem"
          :options="items"
          label="name"
          track-by="id"
          placeholder="Pilih item"
          :disabled="isItemLocked"      
          @update:model-value="onItemSelect"
          required
        />
        <small v-if="isItemLocked" style="color: var(--text-muted)">
          Item sudah dipilih otomatis
        </small>
      </div>

      <div class="form-group">
        <label>Diambil Oleh</label>
        <Multiselect
          v-model="selectedEmployee"
          :options="employees"
          :custom-label="employeeLabel"
          track-by="id"
          placeholder="Pilih karyawan"
          @update:model-value="onEmployeeSelect"
          required
        />
      </div>

      <div class="form-group">
        <label>Quantity</label>
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
        <label>Catatan</label>

        <input
          v-model="form.notes"
          type="text"
        />
      </div>

      <div class="form-group">
        <label>Tanggal Assignment</label>
        <DateTimePicker
          v-model="form.assigned_at"
          placeholder="Pilih tanggal & waktu"
        />
        <small style="color: var(--text-muted)">
          Kosongkan jika sekarang
        </small>
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