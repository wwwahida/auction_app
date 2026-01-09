<template>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet"/>

  <div class="container" style="max-width: 720px;">
    <div class="d-flex align-items-center justify-content-between mb-3">
      <h1 class="mb-0">Profile</h1>
      <button class="btn btn-outline-danger" @click="signOut">
        Sign out
      </button>

      <router-link :to="{ name: 'Main Page' }" class="btn btn-outline-secondary">Back</router-link>
    </div>

    <div v-if="loading" class="alert alert-info">Loading...</div>
    <div v-else>
      <div v-if="error" class="alert alert-danger">{{ error }}</div>
      <div v-if="success" class="alert alert-success">{{ success }}</div>

      <div class="card p-3">
        <div class="d-flex gap-3 align-items-start">
          <div>
            <img
              v-if="previewUrl || profile.displayPic"
              :src="previewUrl || profile.displayPic || ''"
              style="width: 120px; height: 120px; object-fit: cover;"
              class="rounded border"
              alt="Profile picture"
            />
            <div v-else class="border rounded d-flex align-items-center justify-content-center"
                 style="width: 120px; height: 120px;">
              No image
            </div>
          </div>

          <div class="flex-grow-1">
            <div class="mb-3">
              <label class="form-label">Profile image</label>
              <input class="form-control" type="file" accept="image/*" @change="onFileChange" />
            </div>

            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">First name</label>
                <input class="form-control" v-model="profile.firstName" />
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Last name</label>
                <input class="form-control" v-model="profile.lastName" />
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label">Username</label>
              <input class="form-control" v-model="profile.username" />
            </div>

            <div class="mb-3">
              <label class="form-label">Email</label>
              <input class="form-control" type="email" v-model="profile.email" />
            </div>

            <div class="mb-3">
              <label class="form-label">Date of birth</label>
              <input class="form-control" type="date" v-model="profile.dob" />
            </div>

            <button class="btn btn-primary" @click="save" :disabled="saving">
              {{ saving ? 'Saving...' : 'Save changes' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref } from "vue";

interface UserProfile {
  username: string;
  firstName: string;
  lastName: string;
  email: string;
  dob: string; // yyyy-mm-dd
  displayPic: string | null;
}

const loading = ref(true);
const saving = ref(false);
const error = ref<string>("");
const success = ref<string>("");

const profile = ref<UserProfile>({
  username: "",
  firstName: "",
  lastName: "",
  email: "",
  dob: "",
  displayPic: null,
});

const file = ref<File | null>(null);
const previewUrl = ref<string>("");

function getCSRF(): string {
  return document.cookie
    .split("; ")
    .find(row => row.startsWith("csrftoken="))
    ?.split("=")[1] || "";
}

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement;
  const f = input.files?.[0] || null;
  file.value = f;

  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value);
  previewUrl.value = f ? URL.createObjectURL(f) : "";
}

async function loadProfile() {
  loading.value = true;
  error.value = "";
  try {
    const res = await fetch("/api/profile/", { credentials: "include" });
    if (!res.ok) throw new Error("Failed to load profile");
    const data = (await res.json()) as UserProfile;
    profile.value = data;
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Unknown error";
  } finally {
    loading.value = false;
  }
}

async function save() {
  saving.value = true;
  error.value = "";
  success.value = "";

  try {
    const fd = new FormData();
    fd.append("username", profile.value.username);
    fd.append("firstName", profile.value.firstName);
    fd.append("lastName", profile.value.lastName);
    fd.append("email", profile.value.email);
    fd.append("dob", profile.value.dob);
    if (file.value) fd.append("displayPic", file.value);

    const res = await fetch("/api/profile/", {
      method: "POST",
      credentials: "include",
      headers: { "X-CSRFToken": getCSRF() },
      body: fd,
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data?.error || "Failed to save profile");
    }

    profile.value = data as UserProfile;
    success.value = "Saved!";
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Unknown error";
  } finally {
    saving.value = false;
  }
}

onMounted(loadProfile);

async function signOut() {
  try {
    await fetch("/api/logout/", {
      method: "POST",
      credentials: "include",
      headers: {
        "X-CSRFToken": getCSRF(),
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: "",
    });
  } finally {
    // redirect to login page regardless of success/failure
    window.location.href = "/accounts/login/";
  }
}

</script>
