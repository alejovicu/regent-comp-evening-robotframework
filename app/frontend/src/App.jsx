import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth.jsx";
import Header from "./components/Header.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import ShopPage from "./pages/ShopPage.jsx";
import CartPage from "./pages/CartPage.jsx";
import CatalogAdminPage from "./pages/CatalogAdminPage.jsx";
import IngestionPage from "./pages/IngestionPage.jsx";
import { CartProvider } from "./cart.jsx";

const homeFor = (user) => (user?.role === "admin" ? "/admin/products" : "/shop");

function RequireRole({ role, children }) {
  const { user, loading } = useAuth();
  if (loading) return <p id="loading">Loading…</p>;
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== role) return <Navigate to={homeFor(user)} replace />;
  return children;
}

export default function App() {
  const { user, loading } = useAuth();
  return (
    <CartProvider>
      <Header />
      <main className="container">
        <Routes>
          <Route path="/login" element={user ? <Navigate to={homeFor(user)} replace /> : <LoginPage />} />
          <Route path="/shop" element={<RequireRole role="user"><ShopPage /></RequireRole>} />
          <Route path="/cart" element={<RequireRole role="user"><CartPage /></RequireRole>} />
          <Route path="/admin/products" element={<RequireRole role="admin"><CatalogAdminPage /></RequireRole>} />
          <Route path="/admin/ingestion" element={<RequireRole role="admin"><IngestionPage /></RequireRole>} />
          <Route path="*" element={loading ? null : <Navigate to={user ? homeFor(user) : "/login"} replace />} />
        </Routes>
      </main>
    </CartProvider>
  );
}
