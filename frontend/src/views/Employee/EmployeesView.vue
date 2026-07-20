<script setup>
import { ref, onMounted } from "vue";
import {
  getEmployees,
  deleteEmployee,
} from "../../services/employeeService.js";
import { useTableControls } from "../../composables/useTableControls.js";
import { useRouter } from "vue-router";
import ActionDropdown from "../../components/ActionDropdown.vue";
import { useInfiniteScroll } from "../../composables/useInfiniteScroll.js";

const router = useRouter();
const employees = ref([]);

const addEmployee = () => {
  router.push("/employees/create");
};

const editEmployee = (id) => {
  router.push(`/employees/${id}/edit`);
};

const detailEmployee = (id) => {
  router.push(`/employees/${id}/detail`);
};

const prefetchEmployeeCreate = () => {
  import("./EmployeeCreateView.vue");
};

const { filters, result, toggleSort, getSortIcon } = useTableControls(
  employees,
  [
    { key: "first_name", type: "text", resolve: (t) => t.first_name },
    { key: "last_name", type: "text", resolve: (t) => t.last_name },
    { key: "contact", type: "text", resolve: (t) => t.contact },
  ],
  "created_at",
);

const { visibleData, hasMore, setSentinel } = useInfiniteScroll(result, 10);

const loadEmployees = async () => {
  try {
    const response = await getEmployees();
    employees.value = response.data;
  } catch (error) {
    console.error(error);
  }
};

onMounted(loadEmployees);

const deleteEmployeeHandler = async (id) => {
  const confirmed = confirm("Yakin ingin menghapus karyawan ini?");

  if (!confirmed) return;

  try {
    await deleteEmployee(id);

    // Refresh data
    await loadEmployees();
  } catch (error) {
    console.error(error);
  }
};

const getEmployeeActions = (employee) => [
  { label: "Edit", icon: "ti-edit", handler: () => editEmployee(employee.id) },
  {
    label: "Hapus",
    icon: "ti-trash",
    handler: () => deleteEmployeeHandler(employee.id),
    variant: "danger",
  },
];
</script>

<template>
  <section class="employee-page">
    <!-- HEADER -->
    <div class="section-header">
      <div class="section-tag">Employee Management</div>

      <h1 class="section-title">Daftar Karyawan</h1>
    </div>

    <!-- SECTION  DASHBOARD -->
    <div class="card dashboard-table-area">
      <div class="dash-table-header">
        <span
          >Total Karyawan: {{ result.length }} / {{ employees.length }}</span
        >

        <button
          class="btn-acid"
          @pointerenter="prefetchEmployeeCreate"
          @click="addEmployee"
        >
          + Tambah Karyawan
        </button>
      </div>

      <div class="dash-table">
        <div class="dash-table-sticky-header">
          <div class="dash-table-row head">
            <div class="dash-cell sortable" @click="toggleSort('first_name')">
              Nama Depan
              <i
                :class="['ti', getSortIcon('first_name')]"
                aria-hidden="true"
              />
            </div>
            <div class="dash-cell sortable row-center" @click="toggleSort('last_name')">
              Nama Belakang
              <i :class="['ti', getSortIcon('last_name')]" aria-hidden="true" />
            </div>
            <div class="dash-cell sortable row-center" @click="toggleSort('contact')">
              Kontak
              <i :class="['ti', getSortIcon('contact')]" aria-hidden="true" />
            </div>
            <div class="dash-cell row-center">Aksi</div>
            <div class="dash-cell row-center">Detail</div>
          </div>

          <!-- FILTER ROW -->
          <div class="dash-table-row filter-row">
            <div class="dash-cell">
              <input
                v-model="filters.first_name"
                placeholder="Cari nama depan..."
              />
            </div>
            <div class="dash-cell row-center">
              <input
                v-model="filters.last_name"
                placeholder="Cari nama belakang..."
              />
            </div>
            <div class="dash-cell row-center">
              <input v-model="filters.contact" placeholder="Cari kontak..." />
            </div>
            <div class="dash-cell row-center"></div>
          </div>
        </div>

        <div
          v-for="employee in visibleData"
          :key="employee.id"
          class="dash-table-row"
        >
          <div class="dash-cell dash-cell-name">
            {{ employee.first_name }}
          </div>

          <div class="dash-cell row-center">
            {{ employee.last_name }}
          </div>

          <div class="dash-cell row-center">
            {{ employee.contact }}
          </div>

          <div class="dash-cell row-center action-buttons">
            <ActionDropdown :actions="getEmployeeActions(employee)" />
          </div>
          <div class="dash-cell row-center action-buttons">
            <button
              class="btn-small btn-acid"
              @click="detailEmployee(employee.id)"
            >
              <span>Detail</span>
            </button>
          </div>
        </div>

        <div v-if="result.length === 0" class="empty-state">
          Belum ada data karyawan.
        </div>
        <div v-if="hasMore" :ref="setSentinel" class="scroll-sentinel">
          Memuat lebih banyak...
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.employee-page {
  padding-top: 20px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.dash-table-row {
  gap: 16px;
}

.empty-state {
  padding: 40px;
  text-align: center;
  color: var(--text-muted);
}

.dash-cell-icon {
  background: var(--accent);
  color: var(--text);
  font-weight: 700;
}
</style>
