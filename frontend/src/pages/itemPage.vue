<template>
  <BidModal
    v-if="bidOpen && item"
    :open="bidOpen"
    :item-title="item.title"
    :current-price="String(currentPrice)"
    :error="bidError"
    :submitting="bidSubmitting"
    @close="closeBid"
    @submit="submitBid"
  />

  <nav class="navbar navbar-expand bg-light w-100 fixed-top px-3 border-bottom">
    <button class="btn btn-outline-dark btn-sm" @click="goHome">
      ← Back to listings
    </button>

    <div class="ms-auto d-flex align-items-center gap-2">
      <button v-if="!isAuthenticated" class="btn btn-primary btn-sm" @click="goLogin">
        Sign in
      </button>

      <div class="dropdown">
        <button
          class="btn btn-outline-primary dropdown-toggle btn-sm"
          type="button"
          data-bs-toggle="dropdown"
          aria-expanded="false"
        >
          My Profile
        </button>

        <ul class="dropdown-menu dropdown-menu-end">
          <li><button class="dropdown-item" @click="goProfile">View profile</button></li>
          <li><button class="dropdown-item" @click="goPostNewItem">Post new item</button></li>
          <li><hr class="dropdown-divider" /></li>

          <li v-if="isAuthenticated">
            <button class="dropdown-item text-danger" @click="signOut">Sign out</button>
          </li>
          <li v-else>
            <button class="dropdown-item" @click="goLogin">Sign in</button>
          </li>
        </ul>
      </div>
    </div>
  </nav>

  <div class="container py-4 pt-5 mt-4" style="padding-top: 72px;">
    <div v-if="loading" class="alert alert-info">Loading item...</div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

    <div v-else-if="item" class="row g-4 align-items-start">
      <div class="col-12 col-lg-6">
        <div class="card shadow-sm">
          <img
            :src="item.picture"
            class="card-img-top"
            alt="Item image"
            style="max-height: 520px; object-fit: cover;"
          />
        </div>

        <div class="card shadow-sm mt-3">
          <div class="card-body">
            <h5 class="card-title mb-2">Description</h5>
            <p class="card-text text-muted mb-0">{{ item.description }}</p>
          </div>
        </div>
      </div>

      <div class="col-12 col-lg-6">
        <div class="card shadow-sm">
          <div class="card-body">
            <h2 class="fw-bold mb-1">{{ item.title }}</h2>

            <div class="text-muted mb-3">
              <span v-if="item.sellerUsername">
                Listed by: <span class="fw-semibold">{{ item.sellerUsername }}</span>
              </span>
            </div>

            <div class="d-flex flex-wrap gap-2 mb-3">
              <span class="badge bg-secondary">Ends: {{ formatDate(item.finishTime) }}</span>
              <span class="badge" :class="isEnded ? 'bg-danger' : 'bg-success'">
                {{ isEnded ? "Auction ended" : `Time left: ${timeLeftText}` }}
              </span>
              <span v-if="typeof item.bidCount === 'number'" class="badge bg-dark">
                  {{ item.bidCount === 1 ? "1 bid" : item.bidCount + " bids" }}
              </span>
            </div>

            <div class="p-3 rounded border bg-light">
              <div class="d-flex align-items-end justify-content-between">
                <div>
                  <div class="text-muted small">Current price</div>
                  <div class="display-6 fw-bold mb-0">£{{ formatMoney(currentPrice) }}</div>
                </div>
                <div class="text-end">
                  <div class="text-muted small">Starting price</div>
                  <div class="h5 mb-0">£{{ formatMoney(item.startingPrice) }}</div>
                </div>
              </div>
            </div>

            <div v-if="successMsg" class="alert alert-success mt-3 mb-0">
              {{ successMsg }}
            </div>

            <div class="mt-3">
              <button class="btn btn-success w-100" :disabled="isEnded" @click="openBidModal">
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

        <div v-else class="card shadow-sm mt-3">
          <div class="card-body">
            <h5 class="card-title mb-1">Bid history</h5>
            <p class="text-muted mb-0">No bids yet.</p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <ItemForum
    v-if="item"
    :item-id="item.id"
    :is-authenticated="isAuthenticated"
  />
</template>

<script lang="ts" setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import BidModal from "./BidModal.vue";
import ItemForum from "./ItemForum.vue";

interface Item {
  id: number;
  title: string;
  description: string;
  startingPrice: number | string;
  currentPrice?: number | string;
  picture: string;
  finishTime: string;
  bidCount?: number;
  sellerUsername?: string;
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

const bidOpen = ref(false);
const bidError = ref("");
const bidSubmitting = ref(false);

/** Helpers */
function getCSRF(): string {
  return (
    document.cookie
      .split("; ")
      .find((row) => row.startsWith("csrftoken="))
      ?.split("=")[1] || ""
  );
}

function formatMoney(v: number | string | undefined | null): string {
  const n = Number(v ?? 0);
  return Number.isNaN(n) ? "0.00" : n.toFixed(2);
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString();
}

/** Nav actions */
function goHome() {
  router.push("/");
}

function goLogin(): void {
  window.location.href = `/accounts/login/?next=${encodeURIComponent(window.location.pathname)}`;
}

function goProfile(): void {
  if (!isAuthenticated.value) return goLogin();
  router.push({ name: "profile" });
}

function goPostNewItem(): void {
  if (!isAuthenticated.value) return goLogin();
  router.push({ name: "postItem" });
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

/** Auth */
async function refreshAuth(): Promise<void> {
  const res = await fetch("/api/session/", { credentials: "include" });
  const data = (await res.json()) as { isAuthenticated: boolean };
  isAuthenticated.value = data.isAuthenticated;
}

/** Prices */
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
  const diff = end - Date.now();
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

/** Load item */
async function loadItem(): Promise<void> {
  loading.value = true;
  error.value = "";
  successMsg.value = "";

  try {
    const id = Number(route.params.id);
    const res = await fetch(`/api/item/${id}/`, { credentials: "include" });
    if (!res.ok) throw new Error("Failed to load item.");

    const data = await res.json();

    item.value = {
      id: data.id,
      title: data.title,
      description: data.description,
      startingPrice: Number(data.startingPrice),
      currentPrice: data.currentPrice !== undefined ? Number(data.currentPrice) : undefined,
      picture: data.picture,
      finishTime: data.finishTime,
      sellerUsername: data.sellerUsername,
      bidCount: typeof data.bidCount === "number" ? data.bidCount : undefined,
    };

    bids.value = Array.isArray(data.bids)
      ? data.bids.map((b: any, idx: number) => ({
          id: b.id ?? idx,
          amount: b.amount,
          username: b.username,
          createdAt: b.createdAt ?? b.created_at ?? new Date().toISOString(),
        }))
      : [];

    updateCountdown();
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Unknown error";
  } finally {
    loading.value = false;
  }
}

/** Bid modal */
function openBidModal() {
  if (!isAuthenticated.value) return goLogin();
  if (!item.value) return;
  bidError.value = "";
  bidOpen.value = true;
}

function closeBid() {
  bidOpen.value = false;
  bidError.value = "";
}

async function submitBid(amountStr: string) {
  if (!item.value) return;

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
      body: JSON.stringify({ listingId: item.value.id, amount }),
    });

    const data = await res.json().catch(async () => {
      const text = await res.text();
      throw new Error(`Server error (${res.status}): ${text.slice(0, 200)}`);
    });

    if (!res.ok) {
      bidError.value = data?.error || "Bid failed.";
      return;
    }

    const newPrice = Number(data.currentPrice ?? amount);
    item.value.currentPrice = newPrice;
    successMsg.value = "Bid placed successfully!";
    await loadItem();
    closeBid();
  } catch (e) {
    bidError.value = e instanceof Error ? e.message : "Unknown error";
  } finally {
    bidSubmitting.value = false;
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