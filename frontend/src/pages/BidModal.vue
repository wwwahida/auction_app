<template>
  <teleport to="body">
    <div v-if="open" class="bid-backdrop" @click.self="emitClose">
      <div class="bid-modal card shadow">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-start mb-2">
            <h5 class="mb-0">Place a bid</h5>
            <button class="btn btn-sm btn-outline-secondary" @click="emitClose">✕</button>
          </div>

          <p class="mb-2">
            <strong>{{ itemTitle }}</strong>
          </p>
          <p class="text-muted mb-3">
            Current price: <strong>£{{formatMoney(props.currentPrice) }}</strong>
          </p>

          <label class="form-label">Your bid (£)</label>
          <input
            class="form-control"
            type="number"
            step="0.01"
            min="0"
            v-model="bidAmount"
            @keydown.enter.prevent="submit"
            :placeholder="placeholderText"
            autofocus
          />

          <div v-if="error" class="alert alert-danger mt-3 mb-0">
            {{ error }}
          </div>

          <div class="d-flex justify-content-end gap-2 mt-3">
            <button class="btn btn-outline-secondary" @click="emitClose" :disabled="submitting">
              Cancel
            </button>
            <button class="btn btn-primary" @click="submit" :disabled="submitting">
              {{ submitting ? "Submitting..." : "Place bid" }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";

const props = defineProps<{
  open: boolean;
  itemTitle: string;
  currentPrice: string | number;
  submitting: boolean;
  error: string;
  initialAmount?: string;
}>();

const minSuggested = computed(() => {
  const cp = Number(props.currentPrice ?? 0);
  const next = (Number.isFinite(cp) ? cp : 0) + 0.50;
  return next.toFixed(2);
});

const placeholderText = computed(() => `e.g. ${minSuggested.value}`);

function formatMoney(v: number | string | undefined | null): string {
  const n = Number(v ?? 0);
  return Number.isNaN(n) ? "0.00" : n.toFixed(2);
}

const emit = defineEmits<{
  (e: "close"): void;
  (e: "submit", amount: string): void;
}>();

const bidAmount = ref(props.initialAmount ?? "");

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) bidAmount.value = props.initialAmount ?? "";
  }
);

function emitClose() {
  emit("close");
}

function submit() {
  emit("submit", bidAmount.value);
}
</script>

<style scoped>
.bid-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.35);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px;
  z-index: 9999;
}

.bid-modal {
  width: 100%;
  max-width: 420px;
  border-radius: 12px;
}
</style>
