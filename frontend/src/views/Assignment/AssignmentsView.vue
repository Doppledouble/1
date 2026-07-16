<script setup>
import { ref, onMounted } from "vue";
import {
  getActiveAssignments,
  returnAssignment,
} from "../../services/assignmentService.js";
import { useTableControls } from "../../composables/useTableControls.js";
import { useRouter } from "vue-router";
import ActionDropdown from "../../components/ActionDropdown.vue";
import { useInfiniteScroll } from "../../composables/useInfiniteScroll.js";

const router = useRouter();
const assignments = ref([]);

const addAssignment = () => {
  router.push("/assignments/create");
};

const editAssignment = (id) => {
  router.push(`/assignments/${id}/edit`);
};

const { filters, result, toggleSort, getSortIcon } = useTableControls(
  // this is the whole transaction data
  assignments,
  [
    // Keys for sorting that are received from each table column header
    { key: "item", type: "text", resolve: (t) => t.item?.name },
    {
      key: "employee",
      type: "text",
      resolve: (t) =>
        `${t.employee?.first_name ?? ""} ${t.employee?.last_name ?? ""}`,
    },
    { key: "quantity", type: "number", resolve: (t) => t.quantity },
    { key: "location", type: "text", resolve: (t) => t.location },
    {
      key: "assigned_at",
      type: "date",
      resolve: (t) => new Date(t.assigned_at),
    },
  ],
  "assigned_at", // default sort key
);

const { visibleData, hasMore, setSentinel } = useInfiniteScroll(result, 10);

const loadAssignments = async () => {
  try {
    const response = await getActiveAssignments();
    assignments.value = response.data;
  } catch (error) {
    console.error(error);
  }
};

onMounted(loadAssignments);

const returnAssignmentHandler = async (id) => {
  const confirmed = confirm("Yakin ingin mengembalikan barang ini?");

  if (!confirmed) return;

  try {
    await returnAssignment(id);

    // Refresh data
    await loadAssignments();
  } catch (error) {
    console.error(error);
  }
};

const getAssignmentActions = (assignment) => [
  {
    label: "Kembalikan",
    icon: "ti-trash",
    handler: () => returnAssignmentHandler(assignment.id),
    variant: "danger",
  },
];
</script>

<template>
  <section class="assignment-page">
    <!-- HEADER -->
    <div class="section-header">
      <div class="section-tag">Employee Management</div>

      <h1 class="section-title">Daftar Pemakaian</h1>
    </div>

    <!-- SECTION  DASHBOARD -->
    <div class="card dashboard-table-area">
      <div class="dash-table-header">
        <span>Total Pemakaian: {{ assignments.length }}</span>

        <button class="btn-acid" @click="addAssignment">
          + Tambah Pemakaian
        </button>
      </div>

      <div class="dash-table">
        <div class="dash-table-sticky-header">
          <div class="dash-table-row head">
            <div class="dash-cell sortable" @click="toggleSort('item')">
              Nama Barang
              <i :class="['ti', getSortIcon('item')]" aria-hidden="true" />
            </div>
            <div class="dash-cell sortable" @click="toggleSort('employee')">
              PIC
              <i :class="['ti', getSortIcon('employee')]" aria-hidden="true" />
            </div>
            <div class="dash-cell sortable" @click="toggleSort('quantity')">
              Jumlah
              <i :class="['ti', getSortIcon('quantity')]" aria-hidden="true" />
            </div>
            <div class="dash-cell sortable" @click="toggleSort('location')">
              Lokasi
              <i :class="['ti', getSortIcon('location')]" aria-hidden="true" />
            </div>
            <div class="dash-cell sortable" @click="toggleSort('assigned_at')">
              Tanggal Dipakai
              <i
                :class="['ti', getSortIcon('assigned_at')]"
                aria-hidden="true"
              />
            </div>
            <div class="dash-cell">Aksi</div>
          </div>

          <!-- FILTER ROW -->
          <div class="dash-table-row filter-row">
            <div class="dash-cell">
              <input v-model="filters.item" placeholder="Cari barang..." />
            </div>
            <div class="dash-cell">
              <input v-model="filters.employee" placeholder="Cari PIC..." />
            </div>
            <div class="dash-cell">
              <input
                v-model="filters.count"
                placeholder="Cari jumlah..."
                type="number"
              />
            </div>
            <div class="dash-cell">
              <input v-model="filters.location" placeholder="Cari lokasi..." />
            </div>
            <div class="dash-cell">
              <input
                v-model="filters.assigned_at"
                placeholder="Cari tanggal..."
              />
            </div>
          </div>
        </div>

        <div
          v-for="assignment in visibleData"
          :key="assignment.id"
          class="dash-table-row"
        >
          <div class="dash-cell dash-cell-name">
            {{ assignment.item?.name }}
          </div>

          <div class="dash-cell">
            {{ assignment.employee?.first_name }}
            {{ assignment.employee?.last_name }}
          </div>

          <div class="dash-cell">
            {{ assignment.quantity }}
          </div>

          <div class="dash-cell">
            {{ assignment.location }}
          </div>

          <div class="dash-cell">
            {{ new Date(assignment.assigned_at).toLocaleDateString() }}
          </div>

          <div class="dash-cell action-buttons">
            <ActionDropdown :actions="getAssignmentActions(assignment)" />
          </div>
        </div>

        <div v-if="assignments.length === 0" class="empty-state">
          Belum ada data pemakaian.
        </div>
        <div v-if="hasMore" :ref="setSentinel" class="scroll-sentinel">
          Memuat lebih banyak...
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.assignment-page {
  padding-top: 20px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-danger {
  padding: 8px 14px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  background: #ef4444;
  color: white;
  transition: transform 0.2s ease;
}

.btn-danger:hover {
  transform: translateY(-2px);
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

.dash-table-row {
  display: grid;
  grid-template-columns: 1fr 0.5fr 0.5fr 0.5fr 1fr 0.5fr;
  gap: 16px;
  padding: 12px 20px;
  align-items: center;
  border-bottom: 1px solid var(--border-light);
  font-size: 13px;
}

.dash-table-row .dash-cell:not(:first-child) {
  text-align: center;
  justify-content: center;
  display: flex;
  align-items: center;
}
</style>
