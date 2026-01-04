<template>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet"/>

<div class="d-flex align-items-center mb-3">
  <h1 class="me-3 mb-0">Home Page</h1>

  <router-link
    :to="{ name: 'postItem' }"
    class="btn btn-success text-white btn-md"
  >
    Post New Item
  </router-link>
</div>
 
<div class="container my-3">
    <form class="d-flex" @submit.prevent="searchforItems" >
      <input
        type="text"
        class="form-control me-3"
        placeholder="Search for items"
         v-model="searchValue"
        
      />
      <button type="submit" class="btn btn-danger">
        Search
      </button>
    </form>

     <ul class="list-group mt-3" v-if="items.length > 0">
      <li v-for="item in items" :key="item.id" class="list-group-item d-flex align-items-center bg-warning">
        <a href="#" class = "text-dark fw-bold">{{ item.title }}</a>
        <span class = "text-secondary fw-bold ms-5">{{ item.description }}</span>
      </li>
    </ul>
     <p v-else-if="searchValue && items.length === 0">No items found.</p>
  </div>


</template>

<script lang="ts" setup>
import { ref } from "vue";
import { itemStores } from '../stores/allItems';


interface Item {
  id: number;
  title: string;
  description: string;
}

const searchValue = ref<string>("");
const items = ref<Item[]>([]);
const itemStore = itemStores();

loadItem();

function loadItem(){
  itemStore.loadAllItems();
}

async function searchforItems() {
  const searchWord = searchValue.value.toLowerCase();

  if (!searchWord) {
    return;
  }

  items.value = itemStore.allItems.filter(
    item =>
      item.title.toLowerCase().includes(searchWord) || item.description.toLowerCase().includes(searchWord)
  );
}
</script>
