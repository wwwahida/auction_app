<template>
    <BidModal
      :open="bidOpen"
      :itemTitle="bidItem?.title ?? ''"
      :currentPrice="bidItem?.currentPrice ?? bidItem?.startingPrice ?? 0"
      :submitting="bidSubmitting"
      :error="bidError"
      @close="closeBid"
      @submit="submitBid"
    />
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet"/>

    <nav class="navbar navbar-expand bg-light w-100 fixed-top px-3">

    <div class="d-flex align-items-center">
      <button v-if="!isAuthenticated" class="btn btn-primary" @click="goLogin">
        Log in
      </button>
    </div>

    <div class="dropdown ms-auto">
      <button
        class="btn btn-outline-primary dropdown-toggle"
        type="button"
        data-bs-toggle="dropdown"
        aria-expanded="false"
      >
        My Profile
      </button>

      <ul class="dropdown-menu dropdown-menu-end">
        <li>
          <button class="dropdown-item" @click="goProfile">
            View profile
          </button>
        </li>

        <li>
          <button class="dropdown-item" @click="goPostNewItem">
            Post new item
          </button>
        </li>

        <li><hr class="dropdown-divider" /></li>

        <li v-if="isAuthenticated">
          <button class="dropdown-item text-danger" @click="signOut">
            Sign out
          </button>
        </li>

        <li v-else>
          <button class="dropdown-item" @click="goLogin">
            Sign in
          </button>
        </li>
      </ul>
    </div>
  </nav>
  <div class="container pt-5 mt-3">
    <h1 class="me-3 mb-0">Home Page</h1>
 
    <div class="container my-3">
        <form class="d-flex" @submit.prevent="searchforItems">
          <input
            type="text"
            class="form-control me-3"
            placeholder="Search for items"
            v-model="searchValue"
            @keydown.enter.prevent="searchforItems"
          />

          <button type="button" class="btn btn-danger" @click="searchforItems">
            Search
          </button>
        </form>


        <ul class="list-group mt-3" v-if="items.length > 0">
            <li v-for="item in items" :key="item.id" class="list-group-item">
              <div class="d-flex">

              <img
                :src="item.picture"
                alt="Item image"
                style="width: 115px; height: 115px; object-fit: cover;"
                class="me-3 rounded"
              />

              <div>
                <h5 class="fw-bold text-dark mb-1">{{ item.title }}</h5>
                <p class="fw-bold text-dark mb-1">
                  Price: £{{formatPrice(item.currentPrice ?? item.startingPrice)}}
                </p>
                <p class="text-secondary mb-1"> {{ item.description }} </p>

                <button class="btn btn-sm btn-outline-success mt-2" @click="openBid(item)">
                  Bid
                </button>
              </div>

            </div>
            </li>
          </ul>

        <p v-else-if="searchValue && items.length === 0">No items found.</p>
      </div>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { itemStores } from "../stores/allItems";
import BidModal from "./BidModal.vue";

const router = useRouter();

const isAuthenticated = ref<boolean>(false);

async function refreshAuth(): Promise<void> {
  const res = await fetch("/api/session/", { credentials: "include" });
  const data = (await res.json()) as { isAuthenticated: boolean };
  isAuthenticated.value = data.isAuthenticated;
}

function goLogin(): void {
  window.location.href = `/accounts/login/?next=${encodeURIComponent(window.location.pathname)}`;
}

function goProfile(): void {
  if (!isAuthenticated.value) {
    window.location.href = `/accounts/login/?next=${encodeURIComponent("/profile/")}`;
    return;
  }
  router.push({ name: "profile" });
}

function goPostNewItem(): void {
  if (!isAuthenticated.value) {
    window.location.href = `/accounts/login/?next=${encodeURIComponent("/newitem/")}`;
    return;
  }
  router.push({ name: "postItem" });
}

function getCSRF(): string {
  return (
    document.cookie
      .split("; ")
      .find((row) => row.startsWith("csrftoken="))
      ?.split("=")[1] || ""
  );
}

async function signOut(): Promise<void> {
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
    window.location.href = "/";
  }
}

interface Item {
  id: number;
  title: string;
  description: string;
  startingPrice: number | string;
  currentPrice?: number | string;
  picture: string;
  finishTime: string;
}

const searchValue = ref<string>("");
const items = ref<Item[]>([]);
const itemStore = itemStores();

async function loadItems(): Promise<void> {
  await itemStore.loadAllItems();
  items.value = itemStore.allItems;
} 

async function searchforItems(): Promise<void> {
  const q = searchValue.value.trim();

  const url = q
    ? `/api/search-items/?q=${encodeURIComponent(q)}`
    : `/api/get-items/`;

  const res = await fetch(url, { credentials: "include" });
  const data = (await res.json()) as { items: Item[] };
  items.value = data.items;
}

const bidOpen = ref(false);
const bidItem = ref<Item | null>(null);
const bidError = ref<string>("");
const bidSubmitting = ref(false);

function openBid(item: Item): void {
  if (!isAuthenticated.value) {
    window.location.href = `/accounts/login/?next=${encodeURIComponent(window.location.pathname)}`;
    return;
  }
  bidItem.value = item;
  bidError.value = "";
  bidOpen.value = true;
}

function closeBid(): void {
  bidOpen.value = false;
  bidItem.value = null;
  bidError.value = "";
}

async function submitBid(amountStr: string): Promise<void> {
  if (!bidItem.value) return;

  const amount = Number(amountStr);
  if (!amountStr || Number.isNaN(amount) || amount <= 0) {
    bidError.value = "Enter a valid bid amount.";
    return;
  }

  bidSubmitting.value = true;
  bidError.value = "";

  try {
    const res = await fetch("/api/place-bid/", {
      method: "POST",
      credentials: "include",
      headers: {
        "X-CSRFToken": getCSRF(),
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ listingId: bidItem.value.id, amount }),
    });

    let data: any = null;
    try {
      data = await res.json();
    } catch {
      const text = await res.text();
      throw new Error(`Server error (${res.status}): ${text.slice(0, 200)}`);
    }

    if (!res.ok) {
      bidError.value = data?.error || "Bid failed.";
      return;
    }

    if (res.redirected) {
      window.location.href = res.url;
      return;
    }

    const newPrice = Number(data.currentPrice ?? amount);
    const idx = items.value.findIndex((x) => x.id === bidItem.value!.id);
    if (idx !== -1) items.value[idx].currentPrice = newPrice;

    closeBid();
  } catch (e) {
    bidError.value = e instanceof Error ? e.message : "Unknown error";
  } finally {
    bidSubmitting.value = false;
  }

}

function formatPrice(value: number | string | null | undefined): string {
  const n = typeof value === "string" ? Number(value) : value ?? 0;
  if (Number.isNaN(n)) return "0.00";
  return n.toFixed(2);
}

onMounted(async () => {
  await refreshAuth();
  await loadItems();
});
</script>

