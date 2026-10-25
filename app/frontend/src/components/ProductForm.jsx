import { useState } from "react";

// Used for both "add" (product is null) and "edit". SKU cannot change on edit.
export default function ProductForm({ product, onSave, onCancel }) {
  const [form, setForm] = useState({
    sku: product?.sku ?? "",
    name: product?.name ?? "",
    price: product?.price ?? "",
    description: product?.description ?? "",
  });
  const [error, setError] = useState("");
  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setError("");
    try {
      await onSave({ ...form, price: form.price === "" ? null : Number(form.price) });
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="modal-backdrop">
      <form id="product-form" className="card modal" onSubmit={submit}>
        <h2 id="product-form-title">{product ? `Edit ${product.sku}` : "Add product"}</h2>
        <label htmlFor="product-sku">SKU</label>
        <input id="product-sku" value={form.sku} onChange={set("sku")} disabled={Boolean(product)} />
        <label htmlFor="product-name">Name</label>
        <input id="product-name" value={form.name} onChange={set("name")} />
        <label htmlFor="product-price">Price</label>
        <input id="product-price" type="number" step="0.01" value={form.price} onChange={set("price")} />
        <label htmlFor="product-description">Description</label>
        <input id="product-description" value={form.description} onChange={set("description")} />
        {error && <p id="product-form-error" className="error" role="alert">{error}</p>}
        <div className="actions">
          <button id="cancel-product" type="button" className="secondary" onClick={onCancel}>Cancel</button>
          <button id="save-product" type="submit">Save</button>
        </div>
      </form>
    </div>
  );
}
