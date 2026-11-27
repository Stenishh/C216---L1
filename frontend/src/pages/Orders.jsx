import { useRef, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import { customers } from "../api/customers";
import { orders } from "../api/orders";
import {
  dateTime,
  ErrorNotice,
  Field,
  Pagination,
  ResourceState,
} from "../components/Feedback";
import { StatusBadge } from "../components/StatusBadge";
import { statuses } from "../domain/orders";
import { useResource } from "../hooks/useResource";

const pageSize = 20;

export function OrderList() {
  const [offset, setOffset] = useState(0);
  const [filters, setFilters] = useState({
    order_id: "",
    customer: "",
    status: "",
  });
  const [applied, setApplied] = useState({});
  const params = { offset, limit: pageSize, ...applied };
  const resource = useResource(orders.list, params);
  const summary = useResource(orders.summary);
  const location = useLocation();
  return (
    <section>
      <div className="page-heading">
        <div>
          <h1>Ordens de serviço</h1>
          <p className="muted">
            Do recebimento à entrega, cada atendimento em seu lugar.
          </p>
        </div>
        <Link className="button" to="/orders/new">
          Abrir ordem
        </Link>
      </div>
      {location.state?.message && (
        <p className="notice" role="status">
          {location.state.message}
        </p>
      )}
      <div className="panel mb-6">
        <h2>Painel operacional</h2>
        <ResourceState resource={summary}>
          <dl className="form-grid">
            <div>
              <dt>Ordens abertas</dt>
              <dd>{summary.data?.open}</dd>
            </div>
            <div>
              <dt>Aguardando decisão</dt>
              <dd>{summary.data?.awaiting_approval}</dd>
            </div>
            <div>
              <dt>Prontas para entrega</dt>
              <dd>{summary.data?.ready_for_delivery}</dd>
            </div>
          </dl>
        </ResourceState>
        <button
          type="button"
          className="mt-4"
          onClick={() => {
            resource.reload();
            summary.reload();
          }}
        >
          Atualizar dados
        </button>
      </div>
      <form
        className="panel mb-6"
        onSubmit={(event) => {
          event.preventDefault();
          setOffset(0);
          setApplied(
            Object.fromEntries(
              Object.entries(filters)
                .map(([key, value]) => [key, value.trim()])
                .filter(([, value]) => value),
            ),
          );
        }}
      >
        <div className="form-grid">
          <Field
            label="Número da ordem"
            type="number"
            min="1"
            step="1"
            value={filters.order_id}
            onChange={(event) =>
              setFilters({ ...filters, order_id: event.target.value })
            }
          />
          <Field
            label="Nome do cliente"
            maxLength={100}
            value={filters.customer}
            onChange={(event) =>
              setFilters({ ...filters, customer: event.target.value })
            }
          />
          <Field label="Status">
            <select
              value={filters.status}
              onChange={(event) =>
                setFilters({ ...filters, status: event.target.value })
              }
            >
              <option value="">Todos</option>
              {Object.entries(statuses).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </Field>
        </div>
        <div className="actions">
          <button type="submit">Filtrar ordens</button>
          <button
            type="button"
            onClick={() => {
              setFilters({ order_id: "", customer: "", status: "" });
              setApplied({});
              setOffset(0);
            }}
          >
            Limpar filtros
          </button>
        </div>
      </form>
      <div className="panel">
        <ResourceState resource={resource}>
          {resource.data?.length === 0 ? (
            <p>
              Nenhuma ordem nesta página. Abra uma ordem para iniciar um
              atendimento.
            </p>
          ) : (
            <div className="table-wrap">
              <table>
                <caption className="sr-only">
                  Ordens mais recentes primeiro
                </caption>
                <thead>
                  <tr>
                    <th>Ordem</th>
                    <th>Equipamento</th>
                    <th>Cliente</th>
                    <th>Situação</th>
                    <th>Abertura</th>
                  </tr>
                </thead>
                <tbody>
                  {resource.data?.map((order) => (
                    <tr key={order.id}>
                      <td>
                        <Link to={`/orders/${order.id}`}>#{order.id}</Link>
                      </td>
                      <td>
                        {order.brand} {order.model}
                        <span className="block text-sm muted">
                          {order.equipment_type === "notebook"
                            ? "Notebook"
                            : "Computador"}
                        </span>
                      </td>
                      <td>
                        <Link to={`/customers/${order.customer_id}`}>
                          Cliente #{order.customer_id}
                        </Link>
                      </td>
                      <td>
                        <StatusBadge status={order.status} />
                      </td>
                      <td>{dateTime(order.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <Pagination
            offset={offset}
            count={resource.data?.length || 0}
            pageSize={pageSize}
            onChange={setOffset}
          />
        </ResourceState>
      </div>
    </section>
  );
}

export function OrderEdit() {
  const { id } = useParams();
  const resource = useResource(orders.get, { id });
  return (
    <ResourceState resource={resource}>
      {resource.data &&
        (resource.data.status === "received" ? (
          <OrderForm key={id} order={resource.data} />
        ) : (
          <section>
            <h1>Edição indisponível</h1>
            <p>
              Os dados de abertura só podem ser editados enquanto a ordem
              estiver Recebida.
            </p>
            <Link to={`/orders/${id}`}>Voltar à ordem</Link>
          </section>
        ))}
    </ResourceState>
  );
}

function CustomerPicker({ value, onChange, disabled }) {
  const [search, setSearch] = useState("");
  const [offset, setOffset] = useState(0);
  const resource = useResource(customers.list, {
    q: search,
    offset,
    limit: pageSize,
  });
  const [selectedName, setSelectedName] = useState("");
  return (
    <div className="wide">
      <Field
        label="Buscar cliente por nome"
        type="search"
        maxLength={100}
        value={search}
        disabled={disabled}
        onChange={(event) => {
          setSearch(event.target.value);
          setOffset(0);
        }}
      />
      <div className="mt-4">
        <ResourceState resource={resource}>
          <Field label="Cliente">
            <select
              value={value}
              required
              disabled={disabled}
              onChange={(event) => {
                onChange(event.target.value);
                setSelectedName(
                  resource.data.find(
                    (customer) => String(customer.id) === event.target.value,
                  )?.name || "",
                );
              }}
            >
              <option value="">Selecione um cliente</option>
              {value &&
                !resource.data?.some(
                  (customer) => String(customer.id) === String(value),
                ) && (
                  <option value={value}>
                    {selectedName || "Cliente"} #{value} (selecionado)
                  </option>
                )}
              {resource.data?.map((customer) => (
                <option key={customer.id} value={customer.id}>
                  {customer.name} · #{customer.id} · {customer.phone}
                </option>
              ))}
            </select>
          </Field>
          {resource.data?.length === 0 && (
            <p className="muted mt-2">
              Nenhum cliente encontrado.{" "}
              <Link to="/customers/new">Cadastrar cliente</Link>
            </p>
          )}
          <Pagination
            offset={offset}
            count={resource.data?.length || 0}
            pageSize={pageSize}
            onChange={setOffset}
          />
        </ResourceState>
      </div>
    </div>
  );
}

export function OrderForm({ order }) {
  const [values, setValues] = useState({
    customer_id: order ? String(order.customer_id) : "",
    equipment_type: order?.equipment_type || "notebook",
    brand: order?.brand || "",
    model: order?.model || "",
    serial_number: order?.serial_number || "",
    reported_problem: order?.reported_problem || "",
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const lock = useRef(false);
  const navigate = useNavigate();
  const back = order ? `/orders/${order.id}` : "/orders";
  const change = (event) =>
    setValues((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  async function save(event) {
    event.preventDefault();
    if (lock.current) return;
    if (!values.customer_id) {
      setError("Selecione um cliente antes de salvar a ordem.");
      return;
    }
    lock.current = true;
    setBusy(true);
    setError("");
    try {
      const body = {
        ...values,
        customer_id: Number(values.customer_id),
        brand: values.brand.trim(),
        model: values.model.trim(),
        serial_number: values.serial_number.trim() || null,
        reported_problem: values.reported_problem.trim(),
      };
      const saved = order
        ? await orders.replace(order.id, body)
        : await orders.create(body);
      navigate(`/orders/${saved.id}`, {
        replace: true,
        state: { message: order ? "Ordem atualizada." : "Ordem aberta." },
      });
    } catch (error) {
      setError(error.message);
    } finally {
      lock.current = false;
      setBusy(false);
    }
  }
  return (
    <section>
      <Link to={back}>Voltar às ordens</Link>
      <div className="page-heading mt-6">
        <div>
          <h1>{order ? `Editar ordem #${order.id}` : "Abrir ordem"}</h1>
          <p className="muted">
            Identifique o cliente, o equipamento e o problema relatado.
          </p>
        </div>
      </div>
      <form className="panel" onSubmit={save} aria-busy={busy}>
        <ErrorNotice message={error} />
        <fieldset disabled={busy}>
          <legend className="sr-only">Dados de abertura</legend>
          <div className="form-grid">
            <CustomerPicker
              value={values.customer_id}
              disabled={busy}
              onChange={(value) =>
                setValues((current) => ({ ...current, customer_id: value }))
              }
            />
            <Field label="Tipo de equipamento">
              <select
                name="equipment_type"
                value={values.equipment_type}
                onChange={change}
              >
                <option value="notebook">Notebook</option>
                <option value="computer">Computador</option>
              </select>
            </Field>
            <Field
              label="Marca"
              name="brand"
              value={values.brand}
              onChange={change}
              required
              maxLength={100}
            />
            <Field
              label="Modelo"
              name="model"
              value={values.model}
              onChange={change}
              required
              maxLength={100}
            />
            <Field
              label="Número de série (opcional)"
              name="serial_number"
              value={values.serial_number}
              onChange={change}
              maxLength={100}
            />
            <Field label="Problema relatado" className="wide">
              <textarea
                name="reported_problem"
                value={values.reported_problem}
                onChange={change}
                required
                maxLength={2000}
              />
            </Field>
          </div>
          <div className="actions">
            <button type="submit">{busy ? "Salvando…" : "Salvar ordem"}</button>
            {!busy && <Link to={back}>Cancelar</Link>}
          </div>
        </fieldset>
      </form>
    </section>
  );
}
