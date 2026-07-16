<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

import ItemForm from "../../components/ItemForm.vue";
import { getItemById, updateItem } from "../../services/itemService.js";

const route = useRoute();
const router = useRouter();

const itemId = route.params.id;

console.log("itemId:", itemId);

const loading = ref(false);

const item = ref({
  name: "",
  category: "",
  type: "",
  count: 0,
  unit: "",
});

onMounted(async () => {
  try {
    const response = await getItemById(itemId);

    item.value = response.data;
  } catch (error) {
    console.error(error);
  }
});

const handleSubmit = async (itemData) => {
  try {
    loading.value = true;

    await updateItem(itemId, itemData);

    router.push("/items");
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const handleCancel = () => {
  router.back();
};
</script>

<template>
  <section class="container create-page">
    <div class="section-header">
      <div class="section-tag">Employee Management</div>

      <h1 class="section-title">Update Barang</h1>
    </div>

    <ItemForm
      :initial-data="item"
      :is-edit="true"
      :loading="loading"
      submit-label="Update Barang"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />
  </section>
</template>
