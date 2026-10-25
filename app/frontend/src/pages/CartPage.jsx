import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { money } from "../api.js";
import { useCart } from "../cart.jsx";
import { Flash, useFlash } from "../flash.jsx";

export default function CartPage() {
  const { cart, refresh, update, remove, clear } = useCart();
  const [flash, showFlash, clearFlash] = useFlash();
  const [edits, setEdits] = useState({});

  useEffect(() => {
    refresh().catch((e) => showFlash("error", e.message));
  }, [refresh, showFlash]);

  const attempt = (fn, message) => async () => {
    try {
      await fn();
      if (message) showFlash("success", message);
    } catch (e) {
      showFlash("error", e.message);
    }
  };

  return (
    <section>
      <h1 id="page-title">Your cart</h1>
      <Flash flash={flash} onClose={clearFlash} />
      {cart.items.length === 0 ? (
        <p id="cart-empty" className="empty">
          Your cart is empty. <Link id="continue-shopping" to="/shop">Browse products</Link>
        </p>
      ) : (
        <>
          <table id="cart-table">
            <thead>
              <tr><th>SKU</th><th>Product</th><th className="num">Price</th><th>Qty</th><th className="num">Subtotal</th><th></th></tr>
            </thead>
            <tbody>
              {cart.items.map((item) => (
                <tr key={item.product_id} id={`cart-row-${item.sku}`} data-sku={item.sku}>
                  <td>{item.sku}</td>
                  <td className="cart-name">{item.name}</td>
                  <td className="num">{money(item.price)}</td>
                  <td>
                    <input id={`cart-qty-${item.sku}`} className="qty" type="number" min="1" max="99"
                           aria-label={`Quantity for ${item.name}`}
                           value={edits[item.sku] ?? item.quantity}
                           onChange={(e) => setEdits({ ...edits, [item.sku]: e.target.value })} />
                    <button id={`update-qty-${item.sku}`} className="secondary small"
                            onClick={attempt(async () => {
                              await update(item.product_id, Number(edits[item.sku] ?? item.quantity));
                              setEdits({ ...edits, [item.sku]: undefined });
                            }, "Cart updated")}>
                      Update
                    </button>
                  </td>
                  <td className="num" id={`cart-subtotal-${item.sku}`}>{money(item.line_total)}</td>
                  <td>
                    <button id={`remove-${item.sku}`} className="danger"
                            onClick={attempt(() => remove(item.product_id), `Removed ${item.name}`)}>
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="cart-footer">
            <button id="clear-cart" className="secondary" onClick={attempt(clear, "Cart cleared")}>
              Empty cart
            </button>
            <p className="total">
              Items: <strong id="cart-item-count">{cart.item_count}</strong> · Total:{" "}
              <strong id="cart-total">{money(cart.total)}</strong>
            </p>
          </div>
        </>
      )}
    </section>
  );
}
