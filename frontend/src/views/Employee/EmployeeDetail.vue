<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  getEmployeeSummary,
  getEmployeeCurrentTools,
  getEmployeeTransactions,
} from "../../services/employeeService.js";

const route = useRoute();
const router = useRouter();
const employeeId = parseInt(route.params.id);

const summary = ref(null);
const currentTools = ref([]);
const transactions = ref([]);
const loading = ref(true);
const notFound = ref(false);

const txLoading = ref(false);
const txPage = ref(1);
const txTotalPages = ref(1);
const txPageSize = 10;

const loadTransactions = async (page = 1) => {
  txLoading.value = true;
  try {
    const res = await getEmployeeTransactions(employeeId, page, txPageSize);
    transactions.value = res.data.items;
    txPage.value = res.data.page;
    txTotalPages.value = res.data.total_pages;
  } catch (error) {
    console.error("Failed to load transactions", error);
  } finally {
    txLoading.value = false;
  }
};

const goToPage = (page) => {
  if (txLoading.value || page < 1 || page > txTotalPages.value || page === txPage.value) return;
  loadTransactions(page);
};

onMounted(async () => {
  try {
    const [summaryRes, toolsRes, txRes] = await Promise.all([
      getEmployeeSummary(employeeId),
      getEmployeeCurrentTools(employeeId),
      getEmployeeTransactions(employeeId, 1, txPageSize),
    ]);

    summary.value = summaryRes.data;
    currentTools.value = toolsRes.data;
    transactions.value = txRes.data.items;
    txPage.value = txRes.data.page;
    txTotalPages.value = txRes.data.total_pages;
  } catch (error) {
    console.error("Failed to load employee detail", error);
    if (error?.response?.status === 404) {
      notFound.value = true;
    }
  } finally {
    loading.value = false;
  }
});

const formatDate = (value) => {
  if (!value) return "-";
  return new Date(value).toLocaleString("id-ID", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const statusClass = (type) => {
  const map = {
    ASSIGNMENT: "pending",
    RETURN: "active",
    WITHDRAW: "draft",
    ADJUSTMENT: "draft",
    ADD: "active",
    REMOVE: "draft",
  };
  return map[type] || "draft";
};

const goBack = () => router.back();
</script>

<template>
  <section class="container create-page">
    <div class="section-header emp-header">
      <div>
        <div class="section-tag">Employee Management</div>
        <h1 class="section-title">
          {{ summary ? `${summary.first_name} ${summary.last_name}` : "Detail Karyawan" }}
        </h1>
      </div>
      <button class="btn-ghost" @click="goBack">Kembali</button>
    </div>

    <div v-if="loading" class="emp-empty-state">Memuat data karyawan...</div>

    <div v-else-if="notFound" class="emp-empty-state">Karyawan tidak ditemukan.</div>

    <template v-else-if="summary">
      <!-- Personal detail -->
      <div class="card emp-info-card">
        <div class="emp-info-row">
          <div>
            <div class="dash-stat-label">Nama Lengkap</div>
            <div class="emp-info-value">{{ summary.first_name }} {{ summary.last_name }}</div>
          </div>
          <div>
            <div class="dash-stat-label">Kontak</div>
            <div class="emp-info-value">{{ summary.contact || "-" }}</div>
          </div>
        </div>
      </div>

      <!-- Stats -->
      <div class="emp-stats-grid">
        <div class="dash-stat-card">
          <div class="dash-stat-label">Alat Digunakan</div>
          <div class="dash-stat-value">{{ summary.active_tools_count }}</div>
        </div>
        <div class="dash-stat-card">
          <div class="dash-stat-label">Material Digunakan</div>
          <div class="dash-stat-value">{{ summary.materials_used_count }}</div>
        </div>
        <div class="dash-stat-card">
          <div class="dash-stat-label">Aktivitas Terakhir</div>
          <div class="dash-stat-value emp-stat-date">{{ formatDate(summary.last_activity) }}</div>
        </div>
      </div>

      <!-- Current tools -->
      <div class="dashboard-table-area emp-section">
        <div class="dash-table-header">
          <span>Alat yang Sedang Digunakan</span>
        </div>
        <div class="dash-table">
          <div class="emp-tools-row head">
            <div>Nama Barang</div>
            <div>Lokasi</div>
            <div>Jumlah</div>
            <div>Ditugaskan Pada</div>
          </div>
          <div v-if="currentTools.length === 0" class="emp-empty-row">
            Tidak ada alat yang sedang digunakan.
          </div>
          <div v-for="tool in currentTools" :key="tool.assignment_id" class="emp-tools-row">
            <div class="dash-cell-name">{{ tool.item_name }}</div>
            <div>{{ tool.location || "-" }}</div>
            <div>{{ tool.quantity }}</div>
            <div>{{ formatDate(tool.assigned_at) }}</div>
          </div>
        </div>
      </div>

      <!-- Transaction history -->
      <div class="dashboard-table-area emp-section">
        <div class="dash-table-header">
          <span>Riwayat Transaksi</span>
        </div>
        <div class="dash-table">
          <div class="emp-tx-row head">
            <div>Tanggal</div>
            <div>Barang</div>
            <div>Tipe</div>
            <div>Jumlah</div>
            <div>Lokasi / Catatan</div>
          </div>
          <div v-if="transactions.length === 0" class="emp-empty-row">
            Belum ada transaksi.
          </div>
          <div v-for="tx in transactions" :key="tx.id" class="emp-tx-row">
            <div>{{ formatDate(tx.created_at) }}</div>
            <div class="dash-cell-name">{{ tx.item_name }}</div>
            <div>
              <span class="dash-status" :class="statusClass(tx.transaction_type)">
                {{ tx.transaction_type }}
              </span>
            </div>
            <div>{{ tx.quantity }}</div>
            <div>{{ tx.location || tx.notes || "-" }}</div>
          </div>
        </div>

        <div class="emp-pagination" v-if="txTotalPages > 1">
          <button
            class="emp-page-btn"
            :disabled="txLoading || txPage === 1"
            @click="goToPage(txPage - 1)"
          >
            Sebelumnya
          </button>
          <span class="emp-page-info">Halaman {{ txPage }} dari {{ txTotalPages }}</span>
          <button
            class="emp-page-btn"
            :disabled="txLoading || txPage === txTotalPages"
            @click="goToPage(txPage + 1)"
          >
            Berikutnya
          </button>
        </div>
      </div>
    </template>
  </section>
</template>

<style scoped>
.emp-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  text-align: left;
  margin-bottom: 24px;
}

.emp-info-card {
  padding: 24px;
  margin-bottom: 20px;
}

.emp-info-row {
  display: flex;
  gap: 48px;
}

.emp-info-value {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin-top: 4px;
}

.emp-stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.emp-stat-date {
  font-size: 16px;
}

.emp-section {
  margin-bottom: 24px;
}

.emp-tools-row,
.emp-tx-row {
  display: grid;
  padding: 12px 20px;
  align-items: center;
  border-bottom: 1px solid var(--border-light);
  font-size: 13px;
}

.emp-tools-row {
  grid-template-columns: 2fr 1.5fr 1fr 1.5fr;
}

.emp-tx-row {
  grid-template-columns: 1.3fr 1.8fr 1fr 0.8fr 1.5fr;
}

.emp-tools-row.head,
.emp-tx-row.head {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: rgba(0, 0, 0, 0.015);
}

.emp-tools-row:last-child,
.emp-tx-row:last-child {
  border-bottom: none;
}

.emp-empty-row,
.emp-empty-state {
  padding: 24px 20px;
  color: var(--text-dim);
  font-size: 14px;
  text-align: center;
}

.emp-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-light);
}

.emp-page-btn {
  padding: 7px 16px;
  font-family: inherit;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
  transition: color 0.2s ease, border-color 0.2s ease;
}

.emp-page-btn:hover:not(:disabled) {
  color: var(--text);
  border-color: #ccc;
}

.emp-page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.emp-page-info {
  font-size: 13px;
  color: var(--text-dim);
}

@media (max-width: 768px) {
  .emp-header {
    flex-direction: column;
    gap: 16px;
  }

  .emp-info-row {
    flex-direction: column;
    gap: 16px;
  }

  .emp-stats-grid {
    grid-template-columns: 1fr;
  }

  .emp-tools-row,
  .emp-tx-row {
    font-size: 12px;
  }
}
</style>