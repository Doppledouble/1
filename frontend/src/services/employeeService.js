import api from "./api";

export const getEmployees = () => {
  return api.get("/employees");
};

export const getEmployeeById = (id) => {
  return api.get(`/employees/${id}`);
}

export const createEmployee = (employeeData) => {
  return api.post("/employees", employeeData);
}

export const updateEmployee = (id, employeeData) => {
  return api.patch(`/employees/${id}`, employeeData);
};

export const deleteEmployee = (id) => {
  return api.delete(`/employees/${id}`);
};

export const getEmployeeSummary = (id) => {
  return api.get(`/employees/${id}/summary`);
};

export const getEmployeeCurrentTools = (id) => {
  return api.get(`/employees/${id}/current-tools`);
};

export const getEmployeeTransactions = (id, page = 1, pageSize = 10) =>{
  return api.get(`/employees/${id}/transactions`, { params: { page, page_size: pageSize } })
};