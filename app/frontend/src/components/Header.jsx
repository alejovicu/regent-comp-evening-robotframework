import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../auth.jsx";
import { useCart } from "../cart.jsx";

export default function Header() {
  const { user, logout } = useAuth();
  const { cart } = useCart();
  const navigate = useNavigate();

  return (
    <header className="topbar">
      <span className="brand" id="brand">🛒 Demo Shop</span>
      {user && (
        <nav>
          {user.role === "user" && (
            <>
              <NavLink id="nav-shop" to="/shop">Shop</NavLink>
              <NavLink id="nav-cart" to="/cart">
                Cart <span id="cart-count" className="badge">{cart.item_count}</span>
              </NavLink>
            </>
          )}
          {user.role === "admin" && (
            <>
              <NavLink id="nav-products" to="/admin/products">Catalog</NavLink>
              <NavLink id="nav-ingestion" to="/admin/ingestion">SFTP ingestion</NavLink>
            </>
          )}
        </nav>
      )}
      {user && (
        <div className="who">
          <span id="current-user">{user.username}</span>
          <span id="current-role" className={`role role-${user.role}`}>{user.role}</span>
          <button id="logout-button" className="secondary"
                  onClick={() => { logout(); navigate("/login"); }}>
            Log out
          </button>
        </div>
      )}
    </header>
  );
}
