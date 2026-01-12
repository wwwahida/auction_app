<template>

<div class="d-flex align-items-center">
      <button class="btn btn-dark" @click="homePage">
        Home Page
      </button>
</div>
  <div class="container mt-3 pt-3">
    <div v-if="item" class="text-center">

      <img
        :src="item.picture"
        alt="Item image"
        class="img-fluid mb-5"
        style="max-height: 450px; object-fit: cover;"/>

      <h2 class="fw-bold mb-3">{{ item.title }}</h2>
      <h4 class="text-danger mb-3">Starting Price  :£{{ item.startingPrice.toFixed(2) }}</h4>
      <p class="text-primary mb-3">{{ item.description }}</p>
      <p class="text-muted">Bidding Ends at:  {{ formatDate(item.finishTime) }}</p>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';

interface Item {
  id: number;
  title: string;
  description: string;
  startingPrice: number;
  picture: string;
  finishTime: string;
}

const route = useRoute();
const item = ref<Item>({} as Item);

onMounted(async () => {
  const id = Number(route.params.id); 
  const fetchResponse = await fetch(`/api/item/${id}/`, { credentials: 'include' });
  const itemValue = await fetchResponse.json();

  item.value = {
    id: itemValue.id,
    title: itemValue.title,
    description: itemValue.description,
    startingPrice: Number(itemValue.startingPrice),
    picture: itemValue.picture,
    finishTime: itemValue.finishTime,
  };
});

function formatDate(date: string): string {
  return new Date(date).toLocaleString();
}

function homePage() : void {
  window.location.href = '/';
}
</script>
