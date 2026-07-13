<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

import EmployeeForm from "../../components/EmployeeForm.vue";
import { getEmployeeById,updateEmployee } from "../../services/employeeService.js";

const route = useRoute();
const router = useRouter();

const employeeId = route.params.id;

console.log("employeeId:", employeeId);

const loading = ref(false);

const employee = ref({
  first_name: "",
  last_name : "",
  contact     : null
});

onMounted(async () => {
  try {
    const response = await getEmployeeById(employeeId);

    employee.value = response.data;
  } catch (error) {
    console.error(error);
  }
});

const handleSubmit = async (employeeData) => {
  try {
    loading.value = true;

    await updateEmployee(employeeId, employeeData);

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
      <div class="section-tag">
        Employee Management
      </div>

      <h1 class="section-title">
        Update Karyawan
      </h1>
    </div>

    <EmployeeForm
      :initial-data="employee"
      :loading="loading"
      submit-label="Update Karyawan"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />
  </section>
</template>