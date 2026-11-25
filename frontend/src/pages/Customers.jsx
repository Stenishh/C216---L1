import { useRef, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import { request } from "../api/http";
import {
  dateTime,
  ErrorNotice,
  Field,
  Pagination,
  ResourceState,
} from "../components/Feedback";
import { useResource } from "../hooks/useResource";

const pageSize = 20;

export function CustomerList() {
  const [offset, setOffset] = useState(0);
  const resource = useResource(
    `/customers/?offset=${offset}&limit=${pageSize}`,
  );
  const location = useLocation();
  return (
    <section>
      <div className="page-heading">
        <div>
          <h1>Clientes</h1>
          <p className="muted">Contatos para acompanhar cada atendimento.</p>
        </div>
        <Link className="button" to="/customers/new">
          Cadastrar cliente
        </Link>
      </div>
      {location.state?.message && (
        <p className="notice" role="status">
          {location.state.message}
        </p>
      )}
      <div className="panel">
        <ResourceState resource={resource}>
          {resource.data?.length === 0 ? (
            <p>
              Nenhum cliente nesta página. Cadastre um cliente para abrir uma
              ordem.
            </p>
          ) : (
            <div className="table-wrap">
              <table>
                <caption className="sr-only">Clientes cadastrados</caption>
                <thead>
                  <tr>
                    <th>Cliente</th>
                    <th>Telefone</th>
                    <th>E-mail</th>
                  </tr>
                </thead>
                <tbody>
                  {resource.data?.map((customer) => (
                    <tr key={customer.id}>
                      <td>
                        <Link to={`/customers/${customer.id}`}>
                          {customer.name}
                        </Link>
                      </td>
                      <td>{customer.phone}</td>
                      <td>{customer.email || "Não informado"}</td>
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

export function CustomerDetail() {
  const { id } = useParams();
  const resource = useResource(`/customers/${id}`);
  return (
    <ResourceState resource={resource}>
      {resource.data && <CustomerRecord key={id} customer={resource.data} />}
    </ResourceState>
  );
}

function CustomerRecord({ customer }) {
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const lock = useRef(false);
  const navigate = useNavigate();
  const location = useLocation();
  async function remove() {
    if (lock.current) return;
    lock.current = true;
    setBusy(true);
    setError("");
    try {
      await request(`/customers/${customer.id}`, { method: "DELETE" });
      navigate("/customers", {
        replace: true,
        state: { message: "Cliente excluído." },
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
      <Link to="/customers">Voltar aos clientes</Link>
      <div className="page-heading mt-6">
        <div>
          <h1>{customer.name}</h1>
          <p className="muted">Cliente #{customer.id}</p>
        </div>
        <Link className="button" to={`/customers/${customer.id}/edit`}>
          Editar cliente
        </Link>
      </div>
      {location.state?.message && (
        <p className="notice" role="status">
          {location.state.message}
        </p>
      )}
      <div className="panel">
        <dl>
          <div>
            <dt>Telefone</dt>
            <dd>{customer.phone}</dd>
          </div>
          <div>
            <dt>E-mail</dt>
            <dd>{customer.email || "Não informado"}</dd>
          </div>
          <div>
            <dt>Cadastrado em</dt>
            <dd>{dateTime(customer.created_at)}</dd>
          </div>
        </dl>
      </div>
      <div className="panel">
        <h2>Excluir cliente</h2>
        <p>
          A exclusão é permitida para clientes sem ordens ou com todas as ordens
          entregues ou canceladas.
        </p>
        <ErrorNotice message={error} />
        {confirming ? (
          <fieldset aria-label="Confirmar exclusão">
            <p>
              Excluir o cadastro de {customer.name}? As ordens entregues ou
              canceladas e seus históricos também serão excluídos. Esta ação não
              pode ser desfeita.
            </p>
            <div className="actions">
              <button
                type="button"
                className="danger"
                disabled={busy}
                onClick={remove}
              >
                {busy ? "Excluindo…" : "Confirmar exclusão"}
              </button>
              <button
                type="button"
                className="secondary"
                disabled={busy}
                onClick={() => {
                  setConfirming(false);
                  setError("");
                }}
              >
                Manter cliente
              </button>
            </div>
          </fieldset>
        ) : (
          <button
            type="button"
            className="danger mt-4"
            onClick={() => setConfirming(true)}
          >
            Excluir cliente
          </button>
        )}
      </div>
    </section>
  );
}

export function CustomerEdit() {
  const { id } = useParams();
  const resource = useResource(`/customers/${id}`);
  return (
    <ResourceState resource={resource}>
      {resource.data && <CustomerForm key={id} customer={resource.data} />}
    </ResourceState>
  );
}

export function CustomerForm({ customer }) {
  const [values, setValues] = useState({
    name: customer?.name || "",
    phone: customer?.phone || "",
    email: customer?.email || "",
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const lock = useRef(false);
  const navigate = useNavigate();
  const back = customer ? `/customers/${customer.id}` : "/customers";
  const change = (event) =>
    setValues((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  async function save(event) {
    event.preventDefault();
    if (lock.current) return;
    lock.current = true;
    setBusy(true);
    setError("");
    try {
      const saved = await request(
        customer ? `/customers/${customer.id}` : "/customers/",
        {
          method: customer ? "PUT" : "POST",
          body: {
            name: values.name.trim(),
            phone: values.phone.trim(),
            email: values.email.trim() || null,
          },
        },
      );
      navigate(`/customers/${saved.id}`, {
        replace: true,
        state: {
          message: customer ? "Cliente atualizado." : "Cliente cadastrado.",
        },
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
      <Link to={back}>Voltar</Link>
      <div className="page-heading mt-6">
        <div>
          <h1>{customer ? "Editar cliente" : "Cadastrar cliente"}</h1>
          <p className="muted">Nome e telefone são obrigatórios.</p>
        </div>
      </div>
      <form className="panel" onSubmit={save} aria-busy={busy}>
        <ErrorNotice message={error} />
        <fieldset disabled={busy}>
          <legend className="sr-only">Dados do cliente</legend>
          <div className="form-grid">
            <Field
              label="Nome"
              name="name"
              value={values.name}
              onChange={change}
              required
              maxLength={100}
              autoComplete="name"
            />
            <Field
              label="Telefone"
              name="phone"
              value={values.phone}
              onChange={change}
              type="tel"
              required
              maxLength={20}
              pattern="[0-9\(\) \-]{10,20}"
              title="Informe DDD e telefone com 10 ou 11 dígitos; máscara é opcional."
              autoComplete="tel-national"
            />
            <Field
              label="E-mail (opcional)"
              name="email"
              value={values.email}
              onChange={change}
              type="email"
              maxLength={254}
              autoComplete="email"
            />
          </div>
          <div className="actions">
            <button type="submit">
              {busy ? "Salvando…" : "Salvar cliente"}
            </button>
            {!busy && <Link to={back}>Cancelar</Link>}
          </div>
        </fieldset>
      </form>
    </section>
  );
}
