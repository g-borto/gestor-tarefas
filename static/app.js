// Frontend do Gestor de Tarefas (JavaScript puro).

const $ = (sel) => document.querySelector(sel);
const views = ["login", "register", "tasks", "detail"];
let currentTask = null;

// ---------- Utilitários ----------
async function api(method, url, body) {
  const options = { method, headers: {}, credentials: "same-origin" };
  if (body !== undefined) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }
  const res = await fetch(url, options);
  const data = res.status === 204 ? null : await res.json().catch(() => null);
  if (res.status === 401 && !url.startsWith("/api/auth/")) {
    showLoggedOut();
    throw new Error("Sua sessão expirou. Faça login novamente.");
  }
  if (!res.ok) throw new Error((data && data.error) || "Erro inesperado.");
  return data;
}

function show(view) {
  views.forEach((v) => $(`#view-${v}`).classList.toggle("hidden", v !== view));
}

function message(text, type = "error") {
  const el = $("#message");
  el.textContent = text;
  el.className = `message ${type}`;
  if (!text) el.classList.add("hidden");
}

function formatDate(value) {
  // created_at vem do SQLite em UTC no formato "AAAA-MM-DD HH:MM:SS".
  const date = new Date(value.replace(" ", "T") + "Z");
  return isNaN(date) ? value : date.toLocaleString("pt-BR");
}

// ---------- Autenticação ----------
function showLoggedOut() {
  // Limpa os dados do usuário anterior da tela.
  $("#user-area").classList.add("hidden");
  $("#user-name").textContent = "";
  $("#task-list").innerHTML = "";
  currentTask = null;
  resetTaskForm();
  show("login");
}

function showLoggedIn(user) {
  $("#user-name").textContent = `Olá, ${user.name}`;
  $("#user-area").classList.remove("hidden");
  resetTaskForm();
  show("tasks");
  loadTasks();
}

$("#form-login").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = e.target;
  try {
    const user = await api("POST", "/api/auth/login", {
      email: f.email.value,
      password: f.password.value,
    });
    f.reset();
    message("");
    showLoggedIn(user);
  } catch (err) {
    message(err.message);
  }
});

$("#form-register").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = e.target;
  try {
    const user = await api("POST", "/api/auth/register", {
      name: f.name.value,
      email: f.email.value,
      password: f.password.value,
    });
    f.reset();
    message("Conta criada com sucesso!", "success");
    showLoggedIn(user);
  } catch (err) {
    message(err.message);
  }
});

$("#btn-logout").addEventListener("click", async () => {
  await api("POST", "/api/auth/logout").catch(() => {});
  message("");
  showLoggedOut();
});

document.querySelectorAll("[data-go]").forEach((link) =>
  link.addEventListener("click", (e) => {
    e.preventDefault();
    message("");
    show(link.dataset.go);
  })
);

// ---------- Tarefas ----------
async function loadTasks() {
  try {
    const tasks = await api("GET", "/api/tasks");
    const list = $("#task-list");
    list.innerHTML = "";
    $("#empty").classList.toggle("hidden", tasks.length > 0);
    tasks.forEach((task) => {
      const li = document.createElement("li");

      const title = document.createElement("span");
      title.className = "task-title";
      title.textContent = task.title; // textContent evita injeção de HTML

      const actions = document.createElement("div");
      actions.className = "actions";
      actions.append(
        button("Ver", "secondary", () => openDetail(task.id)),
        button("Editar", "", () => startEdit(task)),
        button("Excluir", "danger", () => removeTask(task))
      );

      li.append(title, actions);
      list.append(li);
    });
  } catch (err) {
    message(err.message);
  }
}

function button(label, cls, onClick) {
  const b = document.createElement("button");
  b.type = "button";
  b.textContent = label;
  if (cls) b.className = cls;
  b.addEventListener("click", onClick);
  return b;
}

function resetTaskForm() {
  const f = $("#form-task");
  f.reset();
  f.id.value = "";
  $("#form-title").textContent = "Nova tarefa";
  $("#btn-save").textContent = "Cadastrar";
  $("#btn-cancel").classList.add("hidden");
}

function startEdit(task) {
  const f = $("#form-task");
  f.id.value = task.id;
  f.title.value = task.title;
  f.description.value = task.description;
  $("#form-title").textContent = "Editar tarefa";
  $("#btn-save").textContent = "Salvar alterações";
  $("#btn-cancel").classList.remove("hidden");
  show("tasks");
  f.title.focus();
}

$("#btn-cancel").addEventListener("click", resetTaskForm);

$("#form-task").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = e.target;
  const payload = { title: f.title.value, description: f.description.value };
  if (!payload.title.trim()) {
    message("O título é obrigatório.");
    return;
  }
  try {
    if (f.id.value) {
      await api("PUT", `/api/tasks/${f.id.value}`, payload);
      message("Tarefa atualizada.", "success");
    } else {
      await api("POST", "/api/tasks", payload);
      message("Tarefa cadastrada.", "success");
    }
    resetTaskForm();
    loadTasks();
  } catch (err) {
    message(err.message);
  }
});

async function removeTask(task) {
  if (!confirm(`Excluir a tarefa "${task.title}"?`)) return;
  try {
    await api("DELETE", `/api/tasks/${task.id}`);
    message("Tarefa excluída.", "success");
    resetTaskForm();
    show("tasks");
    loadTasks();
  } catch (err) {
    message(err.message);
  }
}

async function openDetail(id) {
  try {
    const task = await api("GET", `/api/tasks/${id}`);
    currentTask = task;
    $("#detail-title").textContent = task.title;
    $("#detail-date").textContent = formatDate(task.created_at);
    $("#detail-description").textContent = task.description || "Sem descrição.";
    message("");
    show("detail");
  } catch (err) {
    message(err.message);
  }
}

$("#detail-back").addEventListener("click", () => show("tasks"));
$("#detail-edit").addEventListener("click", () => startEdit(currentTask));
$("#detail-delete").addEventListener("click", () => removeTask(currentTask));

// ---------- Inicialização ----------
api("GET", "/api/auth/me").then(showLoggedIn).catch(showLoggedOut);
