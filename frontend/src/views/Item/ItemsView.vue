<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  getItems,
  getTools,
  getMaterials,
  deleteItem,
} from "../../services/itemService.js";
import { useTableControls } from "../../composables/useTableControls.js";
import { useInfiniteScroll } from "../../composables/useInfiniteScroll.js";
import ActionDropdown from "../../components/ActionDropdown.vue";

const router = useRouter();
const route = useRoute();
const items = ref([]);

const addItem = () => {
  router.push("/items/create");
};

const editItem = (id) => {
  router.push(`/items/${id}/edit`);
};

const historyItem = (id) => {
  router.push(`/transactions/items/${id}`);
};

const assignItem = (itemId) => {
  router.push({
    name: "assignment-create",
    query: { item_id: itemId },
  });
};

const prefetchItemCreate = () => {
  import("./ItemCreateView.vue");
};

const { filters, result, toggleSort, getSortIcon } = useTableControls(
  items,
  [
    { key: "name", type: "text", resolve: (t) => t.name },
    { key: "category", type: "text", resolve: (t) => t.category },
    { key: "count", type: "number", resolve: (t) => t.count },
    { key: "unit", type: "text", resolve: (t) => t.unit },
  ],
  "created_at",
);

const { visibleData, hasMore, setSentinel } = useInfiniteScroll(result, 10);

const loadItems = async () => {
  try {
    let response;

    if (route.path === "/items/tool") {
      response = await getTools();
    } else if (route.path === "/items/material") {
      response = await getMaterials();
    } else {
      response = await getItems();
    }

    items.value = response.data;
  } catch (error) {
    console.error(error);
  }
};

onMounted(loadItems);

watch(
  () => route.path,
  () => {
    loadItems();
  },
);

const pageTitle = computed(() => {
  if (route.path === "/items/tool") return "Daftar Tool";
  if (route.path === "/items/material") return "Daftar Material";
  return "Daftar Barang";
});

const deleteItemHandler = async (id) => {
  const confirmed = confirm("Yakin ingin menghapus barang ini?");

  if (!confirmed) return;

  try {
    await deleteItem(id);
    await loadItems();
  } catch (error) {
    console.error(error);
  }
};

const getItemActions = (item) => {
  const actions = [];

  if (item.type === "material") {
    actions.push({ label: "Ambil", handler: () => withdrawItem(item.id) });
  } else {
    actions.push({ label: "Assign", handler: () => assignItem(item.id) });
  }

  actions.push({ label: "Edit", handler: () => editItem(item.id) });
  actions.push({
    label: "Hapus",
    handler: () => deleteItemHandler(item.id),
    variant: "danger",
  });

  return actions;
};

const withdrawItem = (itemId) => {
  router.push({
    name: "withdraw-create",
    query: { item_id: itemId },
  });
};
</script>

<template>
  <section class="item-page">
    <!-- HEADER -->
    <div class="section-header">
      <div class="section-tag">Employee Management</div>

      <h1 class="section-title">
        {{ pageTitle }}
      </h1>
    </div>

    <!-- SECTION 1 : DASHBOARD -->
    <div class="card dashboard-table-area">
      <div class="dash-table-header">
        <span>Total Barang: {{ result.length }} / {{ items.length }}</span>

        <button
          class="btn-acid"
          @pointerenter="prefetchItemCreate"
          @click="addItem"
        >
          + Tambah Barang
        </button>
      </div>

      <div class="dash-table">
        <div class="dash-table-sticky-header">
          <div class="dash-table-row head">
            <div class="dash-cell sortable" @click="toggleSort('name')">
              Nama <i :class="['ti', getSortIcon('name')]" aria-hidden="true" />
            </div>
            <div class="dash-cell sortable row-center" @click="toggleSort('category')">
              Kategori
              <i :class="['ti', getSortIcon('category')]" aria-hidden="true" />
            </div>
            <div class="dash-cell sortable row-center" @click="toggleSort('count')">
              Jumlah
              <i :class="['ti', getSortIcon('count')]" aria-hidden="true" />
            </div>
            <div class="dash-cell sortable row-center" @click="toggleSort('unit')">
              Unit <i :class="['ti', getSortIcon('unit')]" aria-hidden="true" />
            </div>
            <div class="dash-cell row-center">Aksi</div>
            <div class="dash-cell row-center">History</div>
          </div>

          <!-- FILTER ROW -->
          <div class="dash-table-row filter-row">
            <div class="dash-cell">
              <input v-model="filters.name" placeholder="Cari barang..." />
            </div>
            <div class="dash-cell">
              <input
                v-model="filters.category"
                placeholder="Cari kategori..."
              />
            </div>
            <div class="dash-cell">
              <input
                v-model="filters.count"
                placeholder="Cari jumlah..."
                type="number"
              />
            </div>
            <div class="dash-cell">
              <input v-model="filters.unit" placeholder="Cari satuan..." />
            </div>
          </div>
        </div>

        <div v-for="item in visibleData" :key="item.id" class="dash-table-row">
          <div class="dash-cell dash-cell-name">
            {{ item.name }}
          </div>

          <div class="dash-cell row-center">
            {{ item.category }}
          </div>

          <div class="dash-cell row-center">
            {{ item.count }}
          </div>

          <div class="dash-cell row-center">
            {{ item.unit }}
          </div>
          <div class="dash-cell action-buttons row-center">
            <ActionDropdown :actions="getItemActions(item)" />
          </div>
          <div class="dash-cell action-buttons row-center">
            <button class="btn-small btn-acid row-center" @click="historyItem(item.id)">
              <span>detail</span>
            </button>
          </div>
        </div>

        <div v-if="items.length === 0" class="empty-state">
          Belum ada data barang.
        </div>
        <div v-if="hasMore" :ref="setSentinel" class="scroll-sentinel">
          Memuat lebih banyak...
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.item-page {
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
  grid-template-columns:
    1fr
    1fr
    1fr
    1fr
    1fr
    0.5fr;
  gap: 16px;
  padding: 12px 20px;
  align-items: center;
  border-bottom: 1px solid var(--border-light);
  font-size: 13px;
}
</style>
