<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  getEmployeeSummary,
  getEmployeeCurrentTools,
  getEmployeeTransactions,
} from "../../services/employeeService.js";
import { formatDate } from "../../utils/formatDate.js";

const route = useRoute();
const router = useRouter();
const employeeId = computed(() => route.params.id);

const summary = ref(null);
const currentTools = ref([]);
const transactions = ref([]);
const loading = ref(true);
const notFound = ref(false);

const txLoading = ref(false);
const txPage = ref(1);
const txTotalPages = ref(1);
const txPageSize = 10;

const typeLabel = {
  add: "Penambahan",
  remove: "Pengurangan",
  adjustment: "Penyesuaian",
  return: "Pengembalian",
  assignment: "Pemakaian (Tool)",
  withdraw: "Pemakaian (Material)",
};

const loadTransactions = async (page = 1) => {
  txLoading.value = true;
  try {
    const res = await getEmployeeTransactions(
      employeeId.value,
      page,
      txPageSize,
    );
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
  if (
    txLoading.value ||
    page < 1 ||
    page > txTotalPages.value ||
    page === txPage.value
  )
    return;
  loadTransactions(page);
};

onMounted(async () => {
  try {
    const [summaryRes, toolsRes, txRes] = await Promise.all([
      getEmployeeSummary(employeeId.value),
      getEmployeeCurrentTools(employeeId.value),
      getEmployeeTransactions(employeeId.value, 1, txPageSize),
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
          {{
            summary
              ? `${summary.first_name} ${summary.last_name}`
              : "Detail Karyawan"
          }}
        </h1>
      </div>
      <button class="btn-ghost" @click="goBack">Kembali</button>
    </div>

    <div v-if="loading" class="emp-empty-state">Memuat data karyawan...</div>

    <div v-else-if="notFound" class="emp-empty-state">
      Karyawan tidak ditemukan.
    </div>

    <template v-else-if="summary">
      <!-- Personal detail -->
      <div class="card emp-info-card">
        <div class="emp-info-row">
          <div>
            <div class="dash-stat-label">Nama Lengkap</div>
            <div class="emp-info-value">
              {{ summary.first_name }} {{ summary.last_name }}
            </div>
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
          <div class="dash-stat-value">{{ summary.tools_used_count }}</div>
        </div>
        <div class="dash-stat-card">
          <div class="dash-stat-label">Material Digunakan</div>
          <div class="dash-stat-value">{{ summary.materials_used_count }}</div>
        </div>
        <div class="dash-stat-card">
          <div class="dash-stat-label">Aktivitas Terakhir</div>
          <div class="dash-stat-value emp-stat-date">
            {{ formatDate(summary.last_activity) }}
          </div>
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
            <div>Jumlah</div>
            <div>Lokasi</div>
            <div>Ditugaskan Pada</div>
          </div>
          <div v-if="currentTools.length === 0" class="emp-empty-row">
            Tidak ada alat yang sedang digunakan.
          </div>
          <div
            v-for="tool in currentTools"
            :key="tool.assignment_id"
            class="emp-tools-row"
          >
            <div class="dash-cell-name">{{ tool.item_name }}</div>
            <div>{{ tool.quantity }}</div>
            <div>{{ tool.location || "-" }}</div>
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
            <div>Barang</div>
            <div>Tipe</div>
            <div>Jumlah</div>
            <div>Lokasi</div>
            <div>Tanggal</div>
          </div>
          <div v-if="transactions.length === 0" class="emp-empty-row">
            Belum ada transaksi.
          </div>
          <div v-for="tx in transactions" :key="tx.id" class="emp-tx-row">
            <div class="dash-cell-name">{{ tx.item_name }}</div>
            <div>
              <span :class="['type-badge', tx.transaction_type]">
                {{ typeLabel[tx.transaction_type] }}
              </span>
            </div>
            <div>{{ tx.quantity }}</div>
            <div>{{ tx.location  || "-" }}</div>
            <div>{{ formatDate(tx.created_at) }}</div>
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
          <span class="emp-page-info"
            >Halaman {{ txPage }} dari {{ txTotalPages }}</span
          >
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

<style scoped></style>
