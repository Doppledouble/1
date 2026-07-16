<script setup>
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import WithdrawForm from "../../components/WithdrawForm.vue";
import { withdrawMaterial } from "../../services/transactionService.js";

const route = useRoute();
const router = useRouter();

const loading = ref(false);

const initialData = {
  item_id: route.query.item_id ? parseInt(route.query.item_id) : null,
  employee_id: null,
  location: "",
  quantity: 1,
  notes: "",
};

const handleSubmit = async (formData) => {
  try {
    loading.value = true;
    await withdrawMaterial(formData.item_id, {
      quantity: formData.quantity,
      employee_id: formData.employee_id,
      location: formData.location,
      notes: formData.notes,
    });
    router.push("/items/material");
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <section class="container create-page">
    <div class="section-header">
      <div class="section-tag">Inventory Management</div>
      <h1 class="section-title">Ambil Material</h1>
    </div>

    <WithdrawForm
      :initial-data="initialData"
      :loading="loading"
      submit-label="Ambil Material"
      @submit="handleSubmit"
      @cancel="router.back()"
    />
  </section>
</template>
