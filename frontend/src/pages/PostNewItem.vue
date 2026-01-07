<template>
  <link
    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"
    rel="stylesheet"/>

  <div class="container d-flex justify-content-center align-items-center min-vh-100">
    <div
      class="card shadow p-4 text-light"
      style="width: 600px; background-color: #001122; border-radius: 20px;"
    >
      <h4 class="text-center mb-4 text-light fw-bold">
        Post New Auction Item
      </h4>

      <form @submit.prevent="submitItem">
        <div class="mb-3">
          <label class="form-label">Item Image</label>
          <input
            id = "image"
            type="file"
            class="form-control"
            accept="image/*"
            required
          />
        </div>

        <div class="mb-3">
          <label class="form-label">Title</label>
          <input
            type="text"
            class="form-control"
            placeholder="Enter item title"
            v-model="form.title"
            required
          />
        </div>

        <div class="mb-3">
          <label class="form-label">Description</label>
          <textarea
            class="form-control"
            placeholder="Enter item description"
            v-model="form.description"
            required
          ></textarea>
        </div>

        <div class="mb-3">
          <label class="form-label">Starting Price (£)</label>
          <input
            type="number"
            class="form-control"
            min="0"
            step="0.01"
            v-model.number="form.startingPrice"
            required
          />
        </div>

        <div class="mb-3">
          <label class="form-label">Auction End Date and End Time</label>
          <input
            type="datetime-local"
            class="form-control"
            :min="minDate"
            v-model="form.endTime"
            required
          />
        </div>

        <button type="submit" class="btn btn-primary w-100 mt-3">
          Create Item
        </button>
        <router-link class="btn btn-danger w-100 mt-3" :to="{ name: 'Main Page' }"> Back to Main Page </router-link>
      </form>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

interface formTypes {
  title: string;
  description: string;
  startingPrice: number;
  endTime: string;
}

const router = useRouter();


const form = ref<formTypes>({
  title: "",
  description: "",
  startingPrice: 0,
  endTime: "",
});

const minDate = new Date(Date.now() + 24 * 60 * 60 * 1000) .toISOString() .slice(0, 16); 

function getCSRF(): string {
  return document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1] || '';
}



async function submitItem() {
   const image = document.querySelector<HTMLInputElement>("#image")!;
   const file = image.files![0];
  
  const itemDetails = new FormData();
  itemDetails.append("title", form.value.title);
  itemDetails.append("description", form.value.description);
  itemDetails.append("startingPrice", form.value.startingPrice.toString());
  itemDetails.append("endTime", form.value.endTime);
  itemDetails.append("image", file);

  const response = await fetch(`/api/add-item/`, {
      method: "POST",
      credentials: "include",
      headers: {
        "X-CSRFToken": getCSRF(),
      },
      body: itemDetails,
    });

  if (response.ok){
     router.push({ name: "Main Page" });
  }

 
  
}
</script>
