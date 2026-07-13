<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getItems, getTools, getMaterials } from "../../services/itemService.js";

const router = useRouter();
const route = useRoute();
const items = ref([]);

const loadItems = async () => {
  try {
    let response;

    if (route.path === "/items/tools") {
      response = await getTools();
    } else if (route.path === "/items/materials") {
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
  loadItems
);

const pageTitle = computed(() => {
  if (route.path === "/items/tools") return "Daftar Tools";
  if (route.path === "/items/materials") return "Daftar Materials";
  return "Daftar Barang";
});

const goToTransactionPage = (itemId) => {
  router.push(`/transactions/items/${itemId}`);
};
</script>

<template>
  <section class="item-page">
    <div class="section-header">
      <div class="section-tag">Transaction History</div>
      <h1 class="section-title">{{ pageTitle }}</h1>
    </div>

    <div class="item-grid">
      <div
        v-for="item in items"
        :key="item.id"
        class="item-card"
        @click="goToTransactionPage(item.id)"
      >
        <div class="item-icon">
          {{ item.name?.charAt(0).toUpperCase() }}
        </div>

        <div class="item-info">
          <h3>{{ item.name }}</h3>
          <p>{{ item.category }}</p>
          <span>{{ item.count }} {{ item.unit }}</span>
        </div>
      </div>
    </div>

    <div v-if="items.length === 0" class="empty-state">
      Belum ada data barang.
    </div>
  </section>
</template>

<style scoped>
.item-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 24px;
}

.item-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.item-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}

.item-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: var(--accent);

  display: flex;
  align-items: center;
  justify-content: center;

  font-weight: 700;
  margin-bottom: 16px;
}

.item-info h3 {
  margin: 0 0 8px;
}

.item-info p {
  margin: 0;
  color: var(--text-muted);
}

.item-info span {
  display: inline-block;
  margin-top: 10px;
  font-weight: 600;
}

.empty-state {
  margin-top: 40px;
  text-align: center;
  color: var(--text-muted);
}
</style>
```
