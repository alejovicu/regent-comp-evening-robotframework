import { useCallback, useEffect, useState } from "react";
import { api, money } from "../api.js";
import ConfirmDialog from "../components/ConfirmDialog.jsx";
import ProductForm from "../components/ProductForm.jsx";
import { Flash, useFlash } from "../flash.jsx";

export default function CatalogAdminPage() {
  const [products, setProducts] = useState([]);
  const [editing, setEditing] = useState(null); // null, "new" or a product
  const [deleting, setDeleting] = useState(null);
  const [flash, showFlash, clearFlash] = useFlash();

  const load = useCallback(
    () => api("/products").then(setProducts).catch((e) => showFlash("error", e.message)),
    [showFlash]
  );
  useEffect(() => { load(); }, [load]);

  async function save(form) {
    if (editing === "new") {
      await api("/products", { method: "POST", body: form });
      showFlash("success", `Product ${form.sku} created`);
    } else {
      const { name, price, description } = form;
      await api(`/products/${editing.id}`, { method: "PUT", body: { name, price, description } });
      showFlash("success", `Product ${editing.sku} updated`);
    }
    setEditing(null);
    load();
  }

  async function confirmDelete() {
    const product = deleting;
    setDeleting(null);
    try {
      await api(`/products/${product.id}`, { method: "DELETE" });
      showFlash("success", `Product ${product.sku} deleted`);
      load();
    } catch (e) {
      showFlash("error", e.message);
    }
  }

  return (
    <section>
      <div className="page-head">
        <h1 id="page-title">Catalog management</h1>
        <button id="add-product-button" onClick={() => setEditing("new")}>+ Add product</button>
      </div>
      <Flash flash={flash} onClose={clearFlash} />
      <p className="muted">Products: <span id="product-count">{products.length}</span></p>
      <table id="admin-product-table">
        <thead>
          <tr><th>SKU</th><th>Name</th><th>Description</th><th className="num">Price</th><th></th></tr>
        </thead>
        <tbody>
          {products.map((p) => (
            <tr key={p.id} id={`admin-row-${p.sku}`} data-sku={p.sku}>
              <td className="product-sku">{p.sku}</td>
              <td className="product-name">{p.name}</td>
              <td className="product-description muted">{p.description}</td>
              <td className="product-price num">{money(p.price)}</td>
              <td className="row-actions">
                <button id={`edit-${p.sku}`} className="secondary" onClick={() => setEditing(p)}>Edit</button>
                <button id={`delete-${p.sku}`} className="danger" onClick={() => setDeleting(p)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {editing && (
        <ProductForm product={editing === "new" ? null : editing} onSave={save} onCancel={() => setEditing(null)} />
      )}
      {deleting && (
        <ConfirmDialog message={`Delete ${deleting.name} (${deleting.sku})?`}
                       onConfirm={confirmDelete} onCancel={() => setDeleting(null)} />
      )}
    </section>
  );
}
