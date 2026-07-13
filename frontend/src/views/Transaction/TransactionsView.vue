<script setup>
import { ref, onMounted, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getItemHistory } from "../../services/transactionService.js";
import { getItemById } from "../../services/itemService.js"; 
import { useTableControls } from "../../composables/useTableControls.js";

const route = useRoute();
const router = useRouter();
const itemId = computed(() => route.params.itemId);

const item = ref(null);
const transactions = ref([]);
const loading = ref(false);

const typeLabel = {
  add: "Penambahan",
  remove: "Pengurangan",
  adjustment: "Penyesuaian",
  return: "Pengembalian",
  assignment: "Pemakaian (Tool)",
  withdraw: "Pemakaian (Material)"
};

const quantityClass = (transaction) => {
  if (transaction.quantity > 0) return "qty-positive";
  if (transaction.quantity < 0) return "qty-negative";
  return "";
};


const { filters, result, toggleSort, getSortIcon } = useTableControls(
  transactions,
  [
    { key: "type", type: "text", resolve: (t) => t.transaction_type },
    { key: "quantity", type: "number", resolve: (t) => t.quantity },
    { key: "employee", type: "text", resolve: (t) => `${t.employee?.first_name ?? ""} ${t.employee?.last_name ?? ""}` },
    { key: "location", type: "text", resolve: (t) => t.location ?? "" },
    { key: "notes", type: "text", resolve: (t) => t.notes ?? "" },
    { key: "created_at", type: "date", resolve: (t) => new Date(t.created_at) },
  ],
  "created_at"
);

const loadData = async () => {
  loading.value = true;
  try {
    const [transactionRes, itemRes] = await Promise.all([
      getItemHistory(itemId.value),
      getItemById(itemId.value)
    ]);
    transactions.value = transactionRes.data;
    item.value = itemRes.data;
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

watch(
  () => route.params.itemId,
  loadData,
  { immediate: true }
);

const goBack = () => {
  router.push({ name: "transactions-menu" });
};
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
        {{ item.category || "-" }} &middot;
        Stok saat ini: {{ item.count }} {{ item.unit }}
      </p>
    </div>

    <div class="card dashboard-table-area">
      <div class="dash-table-header">
        <span>Total Transaksi: {{ result.length }}</span>
      </div>

      <div class="dash-table">
        <div class="dash-table-row head">
          <div class="dash-cell sortable" @click="toggleSort('type')">
            Aksi <i :class="['ti', getSortIcon('type')]" aria-hidden="true" />
          </div>
          <div class="dash-cell sortable" @click="toggleSort('quantity')">
            Jumlah <i :class="['ti', getSortIcon('quantity')]" aria-hidden="true" />
          </div>
          <div class="dash-cell sortable" @click="toggleSort('employee')">
            Dilakukan Oleh <i :class="['ti', getSortIcon('employee')]" aria-hidden="true" />
          </div>
          <div class="dash-cell sortable" @click="toggleSort('location')">
            Lokasi <i :class="['ti', getSortIcon('location')]" aria-hidden="true" />
          </div>          
          <div class="dash-cell sortable" @click="toggleSort('notes')">
            Catatan <i :class="['ti', getSortIcon('notes')]" aria-hidden="true" />
          </div>
          <div class="dash-cell sortable" @click="toggleSort('created_at')">
            Tanggal <i :class="['ti', getSortIcon('created_at')]" aria-hidden="true" />
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
            <input v-model="filters.quantity" placeholder="Cari..." type="number" />
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
            <input v-model="filters.created_at" placeholder="dd/mm/yyyy" />
          </div>
        </div>

        <div v-if="loading" class="empty-state">Memuat riwayat...</div>

        <template v-else>
          <div
            v-for="transaction in result"
            :key="transaction.id"
            class="dash-table-row"
          >
            <div class="dash-cell">
              <span :class="['type-badge', transaction.transaction_type]">
                {{ typeLabel[transaction.transaction_type] }}
              </span>
            </div>

            <div class="dash-cell" :class="quantityClass(transaction)">
              {{ transaction.quantity > 0 ? "+" : "" }}{{ transaction.quantity }} {{ item.unit }}
            </div>

            <div class="dash-cell">
              {{
                transaction.employee
                  ? `${transaction.employee.first_name} ${transaction.employee.last_name}`
                  : "—"
              }}
            </div>
            <div class="dash-cell">{{ transaction.location|| "—" }}</div>

            <div class="dash-cell">{{ transaction.notes || "—" }}</div>

            <div class="dash-cell">
              {{ new Date(transaction.created_at).toLocaleDateString() }}
            </div>
          </div>

          <div v-if="result.length === 0" class="empty-state">
            Belum ada riwayat transaksi untuk item ini.
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

.type-badge.add   { background: #E1F5EE; color: #0F6E56; }
.type-badge.remove     { background: #FEE2E2; color: #991B1B; }
.type-badge.return     { background: #f2ffee; color: #0da904; }
.type-badge.assignment { background: #ffffee; color: #c35303; }
.type-badge.adjustment { background: #EEF2FF; color: #3730A3; }
.type-badge.withdraw   { background: #ffffee; color: #c35303;}

.qty-positive { color: #0F6E56; font-weight: 600; }
.qty-negative { color: #991B1B; font-weight: 600; }
</style>