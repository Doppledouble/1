<script setup>
import { ref, reactive, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getItemHistory } from "../../services/transactionService.js";
import { getItemById } from "../../services/itemService.js";
import { formatDate, toQueryDateString } from "../../utils/formatDate.js";
import DateRangeFilter from "../../components/DateRangeFilter.vue";

const route = useRoute();
const router = useRouter();
const itemId = computed(() => route.params.itemId);

const item = ref(null);
const transactions = ref([]);
const loading = ref(true);

const txPage = ref(1);
const txTotal = ref(0);
const txTotalPages = ref(1);
const txPageSize = 10;
const txLoading = ref(false);

const sortBy = ref("created_at");
const sortOrder = ref("desc");

const filters = reactive({
  type: "",
  quantity: "",
  employee: "",
  location: "",
  notes: "",
});

const dateRange = ref({ start: null, end: null });

const typeLabel = {
  add: "Penambahan",
  remove: "Pengurangan",
  adjustment: "Penyesuaian",
  return: "Pengembalian",
  assignment: "Pemakaian (Tool)",
  withdraw: "Pemakaian (Material)",
};

const quantityClass = (transaction) => {
  if (transaction.quantity > 0) return "qty-positive";
  if (transaction.quantity < 0) return "qty-negative";
  return "";
};

const toggleSort = (key) => {
  if (sortBy.value === key) {
    sortOrder.value = sortOrder.value === "asc" ? "desc" : "asc";
  } else {
    sortBy.value = key;
    sortOrder.value = "asc";
  }
  txPage.value = 1;
  loadTransactions();
};

const getSortIcon = (key) => {
  if (sortBy.value !== key) return "ti-selector";
  return sortOrder.value === "asc" ? "ti-chevron-up" : "ti-chevron-down";
};

const loadTransactions = async () => {
  txLoading.value = true;
  try {
    const res = await getItemHistory(itemId.value, {
      page: txPage.value,
      page_size: txPageSize,
      sort_by: sortBy.value,
      sort_order: sortOrder.value,
      type: filters.type || undefined,
      quantity: filters.quantity === "" ? undefined : filters.quantity,
      employee: filters.employee || undefined,
      location: filters.location || undefined,
      notes: filters.notes || undefined,
      date_from: toQueryDateString(dateRange.value.start),
      date_to: toQueryDateString(dateRange.value.end),
    });
    transactions.value = res.data.items;
    txTotal.value = res.data.total;
    txPage.value = res.data.page;
    txTotalPages.value = res.data.total_pages;
  } catch (error) {
    console.error("Failed to load transactions", error);
  } finally {
    txLoading.value = false;
  }
};

const loadItem = async () => {
  try {
    const res = await getItemById(itemId.value);
    item.value = res.data;
  } catch (error) {
    console.error("Failed to load item", error);
    item.value = null;
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
  txPage.value = page;
  loadTransactions();
};

let filterDebounce = null;
watch(
  [filters, dateRange],
  () => {
    clearTimeout(filterDebounce);
    filterDebounce = setTimeout(() => {
      txPage.value = 1;
      loadTransactions();
    }, 400);
  },
  { deep: true },
);

watch(
  () => route.params.itemId,
  async () => {
    Object.keys(filters).forEach((key) => (filters[key] = ""));
    txPage.value = 1;
    loading.value = true;
    await Promise.all([loadItem(), loadTransactions()]);
    loading.value = false;
  },
  { immediate: true },
);

const goBack = () => router.back();
</script>

<template>
  <section class="transaction-page">
    <button class="btn-ghost back-btn" @click="goBack">
      <i class="ti ti-arrow-left"></i>
      Kembali ke Daftar Item
    </button>

    <div class="section-header">
      <div class="section-tag">Inventory Management</div>
      <h1 class="section-title">
        Riwayat Transaksi{{ item ? ` — ${item.name}` : "" }}
      </h1>
      <p v-if="item" class="item-subtitle">
        {{ item.type === "material" ? "Material" : "Alat" }} &middot;
        {{ item.category || "-" }} &middot; Stok saat ini: {{ item.count }}
        {{ item.unit }}
      </p>
    </div>

    <div class="card dashboard-table-area">
      <div class="dash-table-header">
        <span>Total Transaksi: {{ txTotal }}</span>
      </div>

      <div class="dash-table">
        <div class="dash-table-row head">
          <div class="dash-cell sortable" @click="toggleSort('type')">
            Aksi <i :class="['ti', getSortIcon('type')]" aria-hidden="true" />
          </div>
          <div class="dash-cell sortable" @click="toggleSort('quantity')">
            Jumlah
            <i :class="['ti', getSortIcon('quantity')]" aria-hidden="true" />
          </div>
          <div class="dash-cell sortable" @click="toggleSort('employee')">
            Dilakukan Oleh
            <i :class="['ti', getSortIcon('employee')]" aria-hidden="true" />
          </div>
          <div class="dash-cell sortable" @click="toggleSort('location')">
            Lokasi
            <i :class="['ti', getSortIcon('location')]" aria-hidden="true" />
          </div>
          <div class="dash-cell sortable" @click="toggleSort('notes')">
            Catatan
            <i :class="['ti', getSortIcon('notes')]" aria-hidden="true" />
          </div>
          <div class="dash-cell sortable" @click="toggleSort('created_at')">
            Tanggal
            <i :class="['ti', getSortIcon('created_at')]" aria-hidden="true" />
          </div>
        </div>

        <div class="dash-table-row filter-row">
          <div class="dash-cell">
            <select v-model="filters.type">
              <option value="">Semua</option>
              <option value="add">Penambahan</option>
              <option value="remove">Pengurangan</option>
              <option value="adjustment">Penyesuaian</option>
              <option value="return">Pengembalian</option>
              <option value="assignment">Pemakaian (Tool)</option>
              <option value="withdraw">Pemakaian (Material)</option>
            </select>
          </div>
          <div class="dash-cell">
            <input
              v-model="filters.quantity"
              placeholder="Cari..."
              type="number"
            />
          </div>
          <div class="dash-cell">
            <input v-model="filters.employee" placeholder="Cari karyawan..." />
          </div>
          <div class="dash-cell">
            <input v-model="filters.location" placeholder="Cari lokasi..." />
          </div>
          <div class="dash-cell">
            <input v-model="filters.notes" placeholder="Cari catatan..." />
          </div>
          <div class="dash-cell">
            <DateRangeFilter
              v-model="dateRange"
              placeholder="Filter tanggal..."
            />
          </div>
        </div>

        <div v-if="loading" class="empty-state">Memuat riwayat...</div>
        <div v-else-if="!item" class="empty-state">Item tidak ditemukan.</div>

        <template v-else>
          <div
            v-for="transaction in transactions"
            :key="transaction.id"
            class="dash-table-row"
          >
            <div class="dash-cell">
              <span :class="['type-badge', transaction.transaction_type]">
                {{ typeLabel[transaction.transaction_type] }}
              </span>
            </div>

            <div class="dash-cell" :class="quantityClass(transaction)">
              {{ transaction.quantity > 0 ? "+" : ""
              }}{{ transaction.quantity }} {{ item.unit }}
            </div>

            <div class="dash-cell">
              {{
                transaction.employee
                  ? `${transaction.employee.first_name} ${transaction.employee.last_name}`
                  : "—"
              }}
            </div>
            <div class="dash-cell">{{ transaction.location || "—" }}</div>

            <div class="dash-cell">{{ transaction.notes || "—" }}</div>

            <div class="dash-cell">
              {{ formatDate(transaction.created_at) }}
            </div>
          </div>

          <div v-if="transactions.length === 0" class="empty-state">
            Belum ada riwayat transaksi untuk item ini.
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
        </template>
      </div>
    </div>
  </section>
</template>

<style scoped>
.transaction-page {
  padding-top: 20px;
}

.back-btn {
  padding: 8px 16px;
  font-size: 13px;
  margin-bottom: 20px;
}

.item-subtitle {
  color: var(--text-muted);
  font-size: 14px;
  margin-top: 6px;
}

.dash-table-row {
  display: grid;
  grid-template-columns: 0.8fr 0.5fr 1fr 1fr 1fr 0.8fr auto;
  gap: 16px;
  padding: 12px 20px;
  align-items: center;
  border-bottom: 1px solid var(--border-light);
  font-size: 13px;
}

.empty-state {
  padding: 40px;
  text-align: center;
  color: var(--text-muted);
}

.type-badge {
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}

.qty-positive {
  color: #0f6e56;
  font-weight: 600;
}

.qty-negative {
  color: #991b1b;
  font-weight: 600;
}
</style>
