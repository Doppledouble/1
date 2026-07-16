<script setup>
import { ref } from "vue";
import { createEmployee } from "../../services/employeeService.js";
import { useRouter } from "vue-router";
import EmployeeForm from "../../components/EmployeeForm.vue";

const router = useRouter();

const loading = ref(false);

const handleSubmit = async (employeeData) => {
  try {
    loading.value = true;

    await createEmployee(employeeData);

    router.push("/employees");
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

      <h1 class="section-title">Tambah Karyawan</h1>
    </div>

    <EmployeeForm
      :loading="loading"
      submit-label="Tambah Karyawan"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />
  </section>
</template>
