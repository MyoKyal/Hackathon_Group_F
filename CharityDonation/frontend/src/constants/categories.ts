export const ITEM_CATEGORIES = ["food", "clothes", "water", "medicine", "stationary"] as const;

export type ItemCategory = (typeof ITEM_CATEGORIES)[number];

export const ITEM_CATEGORY_LABELS: Record<ItemCategory, string> = {
  food: "Food",
  clothes: "Clothes",
  water: "Water",
  medicine: "Medicine",
  stationary: "Stationary",
};
