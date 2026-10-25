import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api } from "./api.js";
import { useAuth } from "./auth.jsx";

// Keeps the shopper's cart in one place so the header badge and pages agree.
const CartContext = createContext(null);
const EMPTY = { items: [], item_count: 0, total: 0 };

export function CartProvider({ children }) {
  const { user } = useAuth();
  const [cart, setCart] = useState(EMPTY);

  const refresh = useCallback(async () => {
    if (user?.role !== "user") return setCart(EMPTY);
    setCart(await api("/cart"));
  }, [user]);

  useEffect(() => {
    refresh().catch(() => setCart(EMPTY));
  }, [refresh]);

  const run = async (path, options) => {
    const updated = await api(path, options);
    setCart(updated);
    return updated;
  };

  const value = {
    cart,
    refresh,
    add: (product_id, quantity) => run("/cart/items", { method: "POST", body: { product_id, quantity } }),
    update: (product_id, quantity) => run(`/cart/items/${product_id}`, { method: "PUT", body: { quantity } }),
    remove: (product_id) => run(`/cart/items/${product_id}`, { method: "DELETE" }),
    clear: () => run("/cart", { method: "DELETE" }),
  };
  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export const useCart = () => useContext(CartContext);
