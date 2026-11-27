import { useRef, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import { customers } from "../api/customers";
import { orderActions, orders } from "../api/orders";
import {
  dateTime,
  ErrorNotice,
  Field,
  Pagination,
  ResourceState,
} from "../components/Feedback";
import { StatusBadge } from "../components/StatusBadge";
import { actions, currency, decisions, statuses } from "../domain/orders";
import { useResource } from "../hooks/useResource";

export function OrderDetail() {
  const { id } = useParams();
  const resource = useResource(orders.get, { id });
  return (
    <ResourceState resource={resource}>
      {resource.data && (
        <OrderRecord
          key={id}
          initialOrder={resource.data}
          reload={resource.reload}
        />
      )}
    </ResourceState>
  );
}

function OrderRecord({ initialOrder, reload }) {
  const [order, setOrder] = useState(initialOrder);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [historyRevision, setHistoryRevision] = useState(0);
  const lock = useRef(false);
  const navigate = useNavigate();
  const location = useLocation();
  async function perform(action, body, method = "POST", success) {
    if (lock.current) return false;
    lock.current = true;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const updated =
        method === "DELETE"
          ? await orders.remove(order.id)
          : await orderActions[action](order.id, body);
      if (method === "DELETE") {
        navigate("/orders", {
          replace: true,
          state: { message: "Ordem excluída." },
        });
      } else {
        setOrder(updated);
        setMessage(success || "Atendimento atualizado.");
        if (method === "POST") setHistoryRevision((revision) => revision + 1);
      }
      return updated || true;
    } catch (error) {
      setError(error.message);
      return false;
    } finally {
      lock.current = false;
      setBusy(false);
    }
  }
  return (
    <section>
      <Link to="/orders">Voltar às ordens</Link>
      <div className="page-heading mt-6">
        <div>
          <h1>Ordem #{order.id}</h1>
          <p className="muted">
            {order.brand} {order.model}
          </p>
        </div>
        <StatusBadge status={order.status} />
      </div>
      {location.state?.message && !message && (
        <p className="notice" role="status">
          {location.state.message}
        </p>
      )}
      {message && (
        <p className="notice" role="status">
          {message}
        </p>
      )}
      <ErrorNotice message={error} />
      {error && (
        <button
          type="button"
          className="secondary mb-4"
          disabled={busy}
          onClick={reload}
        >
          Atualizar dados da ordem
        </button>
      )}
      <OrderProgress status={order.status} />
      <div className="panel order-data">
        <h2>Dados do atendimento</h2>
        <dl>
          <div>
            <dt>Cliente</dt>
            <dd>
              <CustomerContact id={order.customer_id} />
            </dd>
          </div>
          <div>
            <dt>Equipamento</dt>
            <dd>
              {order.equipment_type === "notebook" ? "Notebook" : "Computador"}{" "}
              · {order.brand} {order.model}
            </dd>
          </div>
          <div>
            <dt>Número de série</dt>
            <dd>{order.serial_number || "Não informado"}</dd>
          </div>
          <div>
            <dt>Abertura</dt>
            <dd>{dateTime(order.created_at)}</dd>
          </div>
          <div>
            <dt>Última atualização</dt>
            <dd>{dateTime(order.updated_at)}</dd>
          </div>
          <div className="wide">
            <dt>Problema relatado</dt>
            <dd>{order.reported_problem}</dd>
          </div>
          <div className="wide">
            <dt>Diagnóstico</dt>
            <dd>{order.diagnosis || "Não informado"}</dd>
          </div>
          <div>
            <dt>Orçamento</dt>
            <dd>{currency(order.budget_amount)}</dd>
          </div>
          <div>
            <dt>Decisão do orçamento</dt>
            <dd>{decisions[order.budget_decision]}</dd>
          </div>
          <div className="wide">
            <dt>Serviço realizado</dt>
            <dd>{order.service_performed || "Não informado"}</dd>
          </div>
          {order.cancellation_reason && (
            <div className="wide">
              <dt>Motivo do cancelamento</dt>
              <dd>{order.cancellation_reason}</dd>
            </div>
          )}
        </dl>
        {order.status === "received" && !busy && (
          <div className="actions">
            <Link className="button secondary" to={`/orders/${order.id}/edit`}>
              Editar dados de abertura
            </Link>
          </div>
        )}
      </div>
      <OrderWorkflow
        key={`${order.status}-${order.budget_decision}`}
        order={order}
        busy={busy}
        perform={perform}
      />
      <OrderHistory key={`${order.id}-${historyRevision}`} id={order.id} />
    </section>
  );
}

function CustomerContact({ id }) {
  const resource = useResource(customers.get, { id });
  return (
    <>
      <Link to={`/customers/${id}`}>
        {resource.data?.name || `Cliente #${id}`}
      </Link>
      {resource.data && (
        <span className="block text-sm muted">{resource.data.phone}</span>
      )}
      {resource.error && (
        <span className="block text-sm">
          Contato indisponível. Abra o cadastro para tentar novamente.
        </span>
      )}
    </>
  );
}

const workflowStages = [
  ["received", "Recebimento"],
  ["in_diagnosis", "Diagnóstico"],
  ["awaiting_approval", "Orçamento"],
  ["in_repair", "Reparo"],
  ["completed", "Retirada"],
  ["delivered", "Entrega"],
];

function OrderProgress({ status }) {
  const current = workflowStages.findIndex(([value]) => value === status);
  if (current < 0) return null;
  return (
    <ol className="order-progress" aria-label="Etapas do atendimento">
      {workflowStages.map(([value, label], index) => (
        <li
          key={value}
          data-state={
            index < current ? "done" : index === current ? "current" : "next"
          }
          aria-current={index === current ? "step" : undefined}
        >
          <span aria-hidden="true">{index < current ? "✓" : index + 1}</span>
          {label}
        </li>
      ))}
    </ol>
  );
}

const workflowCopy = {
  received: [
    "Conferência de entrada",
    "Confira o equipamento antes de iniciar a avaliação técnica.",
  ],
  in_diagnosis: [
    "Diagnóstico e orçamento",
    "Registre a avaliação e prepare o valor para aprovação do cliente.",
  ],
  awaiting_approval: [
    "Aprovação do orçamento",
    "Registre a decisão do cliente para dar continuidade ao atendimento.",
  ],
  in_repair: [
    "Execução do reparo",
    "Descreva o serviço realizado antes de concluir esta etapa.",
  ],
  completed: [
    "Equipamento pronto para retirada",
    "O reparo terminou. Registre a entrega quando o cliente retirar o equipamento.",
  ],
  delivered: ["Atendimento finalizado", "Equipamento entregue ao cliente."],
  cancelled: [
    "Atendimento cancelado",
    "Consulte abaixo os dados e o histórico desta ordem.",
  ],
};

function OrderWorkflow({ order, busy, perform }) {
  const [confirmation, setConfirmation] = useState("");
  const [reason, setReason] = useState("");
  const [diagnosis, setDiagnosis] = useState(order.diagnosis || "");
  const [budget, setBudget] = useState(order.budget_amount ?? "");
  const [service, setService] = useState(order.service_performed || "");
  const confirmationLabels = {
    "request-approval": "Solicitar aprovação",
    "approve-budget": "Confirmar aprovação",
    "reject-budget": "Confirmar rejeição",
    "complete-repair": "Concluir reparo",
    deliver: "Confirmar entrega",
    cancel: "Confirmar cancelamento",
    delete: "Confirmar exclusão",
  };
  const confirmationMessages = {
    "request-approval": `Solicitar aprovação do orçamento de ${currency(order.budget_amount)}? Diagnóstico e valor ficarão bloqueados.`,
    "approve-budget": `Registrar que o cliente aprovou o orçamento de ${currency(order.budget_amount)}?`,
    "reject-budget":
      "A rejeição cancela a ordem e preserva o histórico. Informe o motivo registrado pelo cliente.",
    "complete-repair":
      "Concluir o reparo? O serviço realizado ficará bloqueado para edição.",
    deliver:
      "Confirma que o equipamento foi entregue ao cliente? A ordem será encerrada.",
    cancel: "Cancelar o atendimento? Os dados e o histórico serão preservados.",
    delete:
      "Excluir esta ordem e seu evento de abertura? A exclusão só é permitida sem andamento e não pode ser desfeita.",
  };
  const hasReason =
    confirmation === "cancel" || confirmation === "reject-budget";
  async function confirm(event) {
    event.preventDefault();
    const ok = await perform(
      confirmation === "delete" ? "" : confirmation,
      hasReason
        ? { reason: reason.trim() }
        : confirmation === "deliver"
          ? { confirmed: true }
          : undefined,
      confirmation === "delete" ? "DELETE" : "POST",
      confirmation === "deliver" ? "Entrega registrada." : undefined,
    );
    if (ok) {
      setConfirmation("");
      setReason("");
    }
  }
  function ask(action) {
    setConfirmation(action);
    setReason("");
  }
  const final = order.status === "delivered" || order.status === "cancelled";
  return (
    <div className="panel order-workflow" data-stage={order.status}>
      <header className="workflow-heading">
        <span className="workflow-symbol" aria-hidden="true">
          {order.status === "awaiting_approval" ||
          order.status === "in_diagnosis"
            ? "R$"
            : final || order.status === "completed"
              ? "✓"
              : "↗"}
        </span>
        <div>
          <p className="workflow-caption">
            {final ? "Resumo do atendimento" : "Próximo passo"}
          </p>
          <h2>{workflowCopy[order.status][0]}</h2>
          <p className="muted">{workflowCopy[order.status][1]}</p>
        </div>
      </header>
      {final ? (
        <p>
          Atendimento encerrado. Os dados e o histórico permanecem disponíveis
          para consulta.
        </p>
      ) : (
        <fieldset disabled={busy} aria-busy={busy}>
          <legend className="sr-only">Ações do atendimento</legend>
          {order.status === "received" && (
            <>
              <p>
                Confira os dados de abertura e inicie a avaliação do
                equipamento.
              </p>
              <button
                type="button"
                className="mt-4"
                onClick={() =>
                  perform(
                    "begin-diagnosis",
                    undefined,
                    "POST",
                    "Diagnóstico iniciado.",
                  )
                }
              >
                Iniciar diagnóstico
              </button>
            </>
          )}
          {order.status === "in_diagnosis" && (
            <form
              onSubmit={async (event) => {
                event.preventDefault();
                const saved = await perform(
                  "diagnosis",
                  {
                    diagnosis: diagnosis.trim() || null,
                    budget_amount: budget === "" ? null : budget,
                  },
                  "PATCH",
                  "Diagnóstico e orçamento salvos.",
                );
                if (saved) {
                  setDiagnosis(saved.diagnosis || "");
                  setBudget(saved.budget_amount ?? "");
                }
              }}
            >
              <div className="form-grid">
                <Field label="Diagnóstico" className="wide">
                  <textarea
                    value={diagnosis}
                    maxLength={2000}
                    onChange={(event) => setDiagnosis(event.target.value)}
                  />
                </Field>
                <Field
                  label="Orçamento (R$)"
                  type="number"
                  inputMode="decimal"
                  min="0"
                  max="999999.99"
                  step="0.01"
                  value={budget}
                  onChange={(event) => setBudget(event.target.value)}
                />
              </div>
              <p className="muted mt-3">
                Salve o diagnóstico e o valor antes de solicitar aprovação.
                Valor zero é permitido.
              </p>
              <div className="actions">
                <button type="submit">Salvar diagnóstico e orçamento</button>
                <button
                  type="button"
                  className="secondary"
                  disabled={
                    !order.diagnosis ||
                    order.budget_amount === null ||
                    diagnosis.trim() !== order.diagnosis ||
                    String(budget) !== String(order.budget_amount)
                  }
                  onClick={() => ask("request-approval")}
                >
                  Solicitar aprovação
                </button>
              </div>
            </form>
          )}
          {order.status === "awaiting_approval" && (
            <>
              <div className="budget-summary">
                <div>
                  <p>Valor do orçamento</p>
                  <strong>{currency(order.budget_amount)}</strong>
                </div>
                <span
                  className="budget-decision"
                  data-decision={order.budget_decision}
                >
                  {decisions[order.budget_decision]}
                </span>
              </div>
              <div className="actions">
                {order.budget_decision === "pending" ? (
                  <>
                    <button type="button" onClick={() => ask("approve-budget")}>
                      Registrar aprovação
                    </button>
                    <button
                      type="button"
                      className="danger"
                      onClick={() => ask("reject-budget")}
                    >
                      Rejeitar orçamento
                    </button>
                  </>
                ) : (
                  order.budget_decision === "approved" && (
                    <button
                      type="button"
                      onClick={() =>
                        perform(
                          "start-repair",
                          undefined,
                          "POST",
                          "Reparo iniciado.",
                        )
                      }
                    >
                      Iniciar reparo
                    </button>
                  )
                )}
              </div>
            </>
          )}
          {order.status === "in_repair" && (
            <form
              onSubmit={(event) => {
                event.preventDefault();
                perform(
                  "repair",
                  { service_performed: service.trim() || null },
                  "PATCH",
                  "Serviço realizado salvo.",
                );
              }}
            >
              <Field label="Serviço realizado">
                <textarea
                  maxLength={2000}
                  value={service}
                  onChange={(event) => setService(event.target.value)}
                />
              </Field>
              <div className="actions">
                <button type="submit">Salvar serviço realizado</button>
                <button
                  type="button"
                  className="secondary"
                  disabled={
                    !order.service_performed ||
                    service.trim() !== order.service_performed
                  }
                  onClick={() => ask("complete-repair")}
                >
                  Concluir reparo
                </button>
              </div>
            </form>
          )}
          {order.status === "completed" && (
            <>
              <p>
                Reparo concluído. Aguarde a retirada e confirme a entrega ao
                cliente.
              </p>
              <button
                type="button"
                className="mt-4"
                onClick={() => ask("deliver")}
              >
                Registrar entrega
              </button>
            </>
          )}
          {["received", "in_diagnosis", "awaiting_approval"].includes(
            order.status,
          ) && (
            <div className="actions order-danger-actions">
              <p>Outras ações</p>
              <button
                type="button"
                className="secondary"
                onClick={() => ask("cancel")}
              >
                Cancelar ordem
              </button>
              {order.status === "received" && (
                <button
                  type="button"
                  className="secondary"
                  onClick={() => ask("delete")}
                >
                  Excluir ordem
                </button>
              )}
            </div>
          )}
          {confirmation && (
            <form
              className="workflow-confirmation"
              data-destructive={["cancel", "reject-budget", "delete"].includes(
                confirmation,
              )}
              onSubmit={confirm}
              aria-label="Confirmação da ação"
            >
              <h3>{confirmationLabels[confirmation]}</h3>
              <p>{confirmationMessages[confirmation]}</p>
              {hasReason && (
                <Field label="Motivo" className="mt-4">
                  <textarea
                    value={reason}
                    onChange={(event) => setReason(event.target.value)}
                    required
                    maxLength={500}
                  />
                </Field>
              )}
              <div className="actions">
                <button
                  type="submit"
                  className={
                    ["cancel", "reject-budget", "delete"].includes(confirmation)
                      ? "danger"
                      : ""
                  }
                >
                  {busy ? "Processando…" : confirmationLabels[confirmation]}
                </button>
                <button
                  type="button"
                  className="secondary"
                  onClick={() => setConfirmation("")}
                >
                  Voltar sem confirmar
                </button>
              </div>
            </form>
          )}
          {busy && (
            <p className="muted mt-4" role="status">
              Salvando atendimento…
            </p>
          )}
        </fieldset>
      )}
    </div>
  );
}

function OrderHistory({ id }) {
  const [offset, setOffset] = useState(0);
  const resource = useResource(orders.history, { id, offset, limit: 20 });
  return (
    <section className="panel" aria-label="Histórico de atendimento">
      <h2>Histórico de atendimento</h2>
      <ResourceState resource={resource}>
        {resource.data?.length === 0 ? (
          <p>Nenhum evento nesta página.</p>
        ) : (
          <ol className="history">
            {resource.data?.map((event) => (
              <li key={event.id}>
                <h3>{actions[event.action] || event.action}</h3>
                <p className="text-sm muted">{dateTime(event.created_at)}</p>
                <p>
                  {event.previous_status
                    ? `${statuses[event.previous_status]} → `
                    : ""}
                  {statuses[event.resulting_status]}
                </p>
                {event.observation && (
                  <p className="whitespace-pre-wrap">{event.observation}</p>
                )}
                {event.approved_amount !== null &&
                  event.approved_amount !== undefined && (
                    <p>Valor aprovado: {currency(event.approved_amount)}</p>
                  )}
              </li>
            ))}
          </ol>
        )}
        <Pagination
          offset={offset}
          count={resource.data?.length || 0}
          pageSize={20}
          onChange={setOffset}
        />
      </ResourceState>
    </section>
  );
}
