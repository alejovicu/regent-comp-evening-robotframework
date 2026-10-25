import { useEffect, useState } from "react";
import { api, money } from "../api.js";
import { useCart } from "../cart.jsx";
import { Flash, useFlash } from "../flash.jsx";

export default function ShopPage() {
  const { add } = useCart();
  const [products, setProducts] = useState([]);
  const [quantities, setQuantities] = useState({});
  const [search, setSearch] = useState("");
  const [flash, showFlash, clearFlash] = useFlash();

  useEffect(() => {
    const q = search ? `?q=${encodeURIComponent(search)}` : "";
    api(`/products${q}`).then(setProducts).catch((e) => showFlash("error", e.message));
  }, [search, showFlash]);

  async function addToCart(product) {
    const quantity = Number(quantities[product.sku] || 1);
    try {
      await add(product.id, quantity);
      showFlash("success", `Added ${quantity} × ${product.name} to cart`);
    } catch (e) {
      showFlash("error", e.message);
    }
  }

  return (
    <section>
      <h1 id="page-title">Product catalog</h1>
      <Flash flash={flash} onClose={clearFlash} />
      <input id="search-input" className="search" placeholder="Search by name or SKU"
             value={search} onChange={(e) => setSearch(e.target.value)} />
      {products.length === 0 ? (
        <p id="no-products" className="empty">No products found.</p>
      ) : (
        <table id="product-table">
          <thead>
            <tr><th>SKU</th><th>Product</th><th>Description</th><th className="num">Price</th><th>Qty</th><th></th></tr>
          </thead>
          <tbody>
            {products.map((p) => (
              <tr key={p.id} id={`product-row-${p.sku}`} data-sku={p.sku}>
                <td className="product-sku">{p.sku}</td>
                <td className="product-name" id={`product-name-${p.sku}`}>{p.name}</td>
                <td className="product-description muted">{p.description}</td>
                <td className="product-price num" id={`product-price-${p.sku}`}>{money(p.price)}</td>
                <td>
                  <input id={`qty-${p.sku}`} className="qty" type="number" min="1" max="99"
                         aria-label={`Quantity for ${p.name}`}
                         value={quantities[p.sku] ?? 1}
                         onChange={(e) => setQuantities({ ...quantities, [p.sku]: e.target.value })} />
                </td>
                <td>
                  <button id={`add-to-cart-${p.sku}`} onClick={() => addToCart(p)}>Add to cart</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
