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
    async searchItems(query: string): Promise<Item[]> {
      const res = await fetch(`/api/search-items/?q=${encodeURIComponent(query)}`, {
        credentials: "include",
      });

      if (!res.ok) return [];

      const data = (await res.json()) as { items: Item[] };
      return data.items;
    }
  },
});
