import { defineStore } from 'pinia';

interface Item {
  id: number;
  title: string;
  description: string;
  startingPrice: number;
  picture: string;
  finishTime: string;
}

export const itemStores = defineStore('itemStore', {
  state: () => ({
    allItems: [] as Item[],
  }),

  actions: {
    async loadAllItems() {
      const validItems = await fetch('/api/get-items/', {
        credentials: 'include',
      });

      if (validItems.ok) {
        const data = await validItems.json();
        this.allItems = data.items;
      }
    },
  },
});
