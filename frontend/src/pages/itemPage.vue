<template>
  <BidModal
    v-if="bidOpen && bidItem"
    :open="bidOpen"
    :item-title="bidItem.title"
    :current-price="String(bidItem.currentPrice ?? bidItem.startingPrice)"
    :error="bidError"
    :submitting="bidSubmitting"
    @close="closeBid"
    @submit="submitBid"
  />
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet"/>

  <nav class="navbar navbar-expand bg-light w-100 fixed-top px-3">
    <div class="d-flex align-items-center">
      <button v-if="!isAuthenticated" class="btn btn-primary" @click="goLogin">
        Sign in
      </button>
    </div>

      <button class="btn btn-outline-dark btn-sm" @click="goHome">
        ← Back to listings
      </button>

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

  <div class="container py-4">
    <!-- Loading / error -->
    <div v-if="loading" class="alert alert-info">Loading item...</div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

    <div v-else-if="item" class="row g-4 align-items-start">
      <!-- LEFT: Image -->
      <div class="col-12 col-lg-6">
        <div class="card shadow-sm">
          <img
            :src="item.picture"
            class="card-img-top"
            alt="Item image"
            style="max-height: 520px; object-fit: cover;"
          />
        </div>

        <!-- Description card -->
        <div class="card shadow-sm mt-3">
          <div class="card-body">
            <h5 class="card-title mb-2">Description</h5>
            <p class="card-text text-muted mb-0">
              {{ item.description }}
            </p>
          </div>
        </div>
      </div>

      <!-- RIGHT: Details -->
      <div class="col-12 col-lg-6">
        <!-- Title + meta -->
        <div class="card shadow-sm">
          <div class="card-body">
            <h2 class="fw-bold mb-2">{{ item.title }}</h2>

            <div class="d-flex flex-wrap gap-2 mb-3">
              <span class="badge bg-secondary">
                Ends: {{ formatDate(item.finishTime) }}
              </span>

              <span class="badge" :class="isEnded ? 'bg-danger' : 'bg-success'">
                {{ isEnded ? "Auction ended" : `Time left: ${timeLeftText}` }}
              </span>

              <span v-if="typeof item.bidCount === 'number'" class="badge bg-dark">
                {{ item.bidCount }} bids
              </span>
            </div>

            <!-- Prices -->
            <div class="p-3 rounded border bg-light">
              <div class="d-flex align-items-end justify-content-between">
                <div>
                  <div class="text-muted small">Current price</div>
                  <p class="display-6 fw-bold mb-0">
                    Price: £{{formatMoney((item.currentPrice ?? item.startingPrice)) }}
                  </p>
                </div>

                <div class="text-end">
                  <div class="text-muted small">Starting price</div>
                  <div class="h5 mb-0">
                    £{{ formatMoney(item.startingPrice) }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Alerts -->
            <div v-if="successMsg" class="alert alert-success mt-3 mb-0">
              {{ successMsg }}
            </div>

            <!-- Bid section -->
            <div class="mt-3">
              <div class="card border-0">
                <div class="card-body p-0">
                  <button class="btn btn-success w-100" @click="openBidModal">
                    Place a bid
                  </button>

                  <div class="text-muted small mt-2">
                    Your bid must be higher than £{{ formatMoney(currentPrice) }}.
                  </div>

                  <div v-if="isEnded" class="text-danger small mt-2">
                    This auction has ended. You can no longer bid.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Bid history (optional) -->
        <div v-if="bids.length" class="card shadow-sm mt-3">
          <div class="card-body">
            <h5 class="card-title mb-3">Recent bids</h5>

            <ul class="list-group list-group-flush">
              <li
                v-for="b in bids"
                :key="b.id"
                class="list-group-item d-flex justify-content-between align-items-center px-0"
              >
                <div>
                  <div class="fw-semibold">£{{ formatMoney(b.amount) }}</div>
                  <div class="text-muted small">
                    {{ b.username || "User" }} · {{ formatDate(b.createdAt) }}
                  </div>
                </div>
              </li>
            </ul>
          </div>
        </div>

        <!-- If no bids -->
        <div v-else class="card shadow-sm mt-3">
          <div class="card-body">
            <h5 class="card-title mb-1">Bid history</h5>
            <p class="text-muted mb-0">No bids yet.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import BidModal from "./BidModal.vue";

const bidOpen = ref(false);
const bidItem = ref<Item | null>(null);
const bidError = ref("");
const bidSubmitting = ref(false);

function openBidModal() {
  if (!isAuthenticated.value) return goLogin();
  if (!item.value) return;

  bidItem.value = item.value;
  bidError.value = "";
  bidOpen.value = true;
}

function closeBid() {
  bidOpen.value = false;
  bidItem.value = null;
  bidError.value = "";
}

async function submitBid(amountStr: string) {
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

    // update the displayed item price
    if (item.value && bidItem.value && item.value.id === bidItem.value.id) {
      item.value.currentPrice = newPrice;
    }

    // optional: show a success message
    successMsg.value = "Bid placed successfully!";

    closeBid();
  } catch (e) {
    bidError.value = e instanceof Error ? e.message : "Unknown error";
  } finally {
    bidSubmitting.value = false;
  }
}


interface Item {
  id: number;
  title: string;
  description: string;
  startingPrice: number | string;
  currentPrice?: number | string;   // optional (backend may not send yet)
  picture: string;
  finishTime: string;
  bidCount?: number;
}

interface BidRow {
  id: number;
  amount: number | string;
  username?: string;
  createdAt: string;
}

const route = useRoute();
const router = useRouter();

const loading = ref(true);
const error = ref("");
const item = ref<Item | null>(null);
const bids = ref<BidRow[]>([]);

const isAuthenticated = ref(false);
const successMsg = ref("");

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

function formatMoney(v: number | string | undefined | null): string {
  const n = Number(v ?? 0);
  if (Number.isNaN(n)) return "0.00";
  return n.toFixed(2);
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString();
}

function goHome() {
  router.push("/");
}

function goLogin(): void {
  // redirect back to this item page after login
  window.location.href = `/accounts/login/?next=${encodeURIComponent(window.location.pathname)}`;
}

async function refreshAuth(): Promise<void> {
  const res = await fetch("/api/session/", { credentials: "include" });
  const data = (await res.json()) as { isAuthenticated: boolean };
  isAuthenticated.value = data.isAuthenticated;
}

const currentPrice = computed(() => {
  if (!item.value) return 0;
  return item.value.currentPrice ?? item.value.startingPrice;
});

const isEnded = computed(() => {
  if (!item.value) return false;
  return new Date(item.value.finishTime).getTime() <= Date.now();
});

/** Countdown */
const timeLeftText = ref("—");
let timer: number | null = null;

function updateCountdown() {
  if (!item.value) return;
  const end = new Date(item.value.finishTime).getTime();
  const now = Date.now();
  const diff = end - now;

  if (diff <= 0) {
    timeLeftText.value = "0s";
    return;
  }

  const totalSeconds = Math.floor(diff / 1000);
  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const mins = Math.floor((totalSeconds % 3600) / 60);
  const secs = totalSeconds % 60;

  const parts: string[] = [];
  if (days) parts.push(`${days}d`);
  if (days || hours) parts.push(`${hours}h`);
  if (days || hours || mins) parts.push(`${mins}m`);
  parts.push(`${secs}s`);

  timeLeftText.value = parts.join(" ");
}

async function loadItem(): Promise<void> {
  loading.value = true;
  error.value = "";
  successMsg.value = "";

  try {
    const id = Number(route.params.id);

    const res = await fetch(`/api/item/${id}/`, { credentials: "include" });
    if (!res.ok) throw new Error("Failed to load item.");

    const data = await res.json();

    // Allow backend to send currentPrice/bids if available
    item.value = {
      id: data.id,
      title: data.title,
      description: data.description,
      startingPrice: Number(data.startingPrice),
      currentPrice: data.currentPrice !== undefined ? Number(data.currentPrice) : undefined,
      picture: data.picture,
      finishTime: data.finishTime,
    };


    // Optional: if your backend returns bids
    if (Array.isArray(data.bids)) {
      bids.value = data.bids.map((b: any, idx: number) => ({
        id: b.id ?? idx,
        amount: b.amount,
        username: b.username,
        createdAt: b.createdAt ?? b.created_at ?? new Date().toISOString(),
      }));
    } else {
      bids.value = [];
    }

    updateCountdown();
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Unknown error";
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  await refreshAuth();
  await loadItem();

  timer = window.setInterval(updateCountdown, 1000);
});

onUnmounted(() => {
  if (timer) window.clearInterval(timer);
});
</script>

<style scoped>
/* Simple modal without bootstrap JS */
.modal-backdrop-custom {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  z-index: 1050;
}

.modal-custom {
  width: 100%;
  max-width: 520px;
}
</style>
