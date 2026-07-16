<script setup>
import { ref } from "vue";
import { createItem } from "../../services/itemService.js";
import { useRouter } from "vue-router";
import ItemForm from "../../components/ItemForm.vue";

const router = useRouter();

const loading = ref(false);

const handleSubmit = async (itemData) => {
  try {
    loading.value = true;

    await createItem(itemData);

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

      <h1 class="section-title">Tambah Barang</h1>
    </div>

    <ItemForm
      :loading="loading"
      submit-label="Tambah Barang"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />
  </section>
</template>
