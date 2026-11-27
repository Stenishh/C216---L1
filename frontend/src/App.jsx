import { Navigate, NavLink, Route, Routes } from "react-router-dom";
import {
  CustomerDetail,
  CustomerEdit,
  CustomerForm,
  CustomerList,
} from "./pages/Customers";
import { OrderDetail } from "./pages/OrderDetail";
import { OrderEdit, OrderForm, OrderList } from "./pages/Orders";

export default function App() {
  return (
    <>
      <a className="skip-link" href="#content">
        Ir para o conteúdo
      </a>
      <header className="app-header">
        <div className="header-inner">
          <NavLink className="brand" to="/orders">
            repara<span>Assistência técnica</span>
          </NavLink>
          <nav aria-label="Navegação principal">
            <NavLink to="/orders">Ordens de serviço</NavLink>
            <NavLink to="/customers">Clientes</NavLink>
          </nav>
        </div>
      </header>
      <main
        id="content"
        tabIndex={-1}
        className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-8"
      >
        <Routes>
          <Route path="/" element={<Navigate to="/orders" replace />} />
          <Route path="/customers" element={<CustomerList />} />
          <Route path="/customers/new" element={<CustomerForm />} />
          <Route path="/customers/:id" element={<CustomerDetail />} />
          <Route path="/customers/:id/edit" element={<CustomerEdit />} />
          <Route path="/orders" element={<OrderList />} />
          <Route path="/orders/new" element={<OrderForm />} />
          <Route path="/orders/:id" element={<OrderDetail />} />
          <Route path="/orders/:id/edit" element={<OrderEdit />} />
          <Route
            path="*"
            element={
              <>
                <h1>Página não encontrada</h1>
                <NavLink to="/orders">Voltar às ordens</NavLink>
              </>
            }
          />
        </Routes>
      </main>
    </>
  );
}
