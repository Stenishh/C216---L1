import { cloneElement, useId } from "react";

export function ErrorNotice({ message }) {
  return message ? (
    <p className="notice" role="alert">
      {message}
    </p>
  ) : null;
}

export function ResourceState({ resource, children }) {
  if (resource.loading) return <p role="status">Carregando dados…</p>;
  if (resource.error)
    return (
      <div>
        <ErrorNotice message={resource.error} />
        <button type="button" className="secondary" onClick={resource.reload}>
          Tentar novamente
        </button>
      </div>
    );
  return children;
}

export function Pagination({ offset, count, pageSize, onChange }) {
  return (
    <nav className="actions" aria-label="Paginação">
      <button
        type="button"
        className="secondary"
        disabled={offset === 0}
        onClick={() => onChange(Math.max(0, offset - pageSize))}
      >
        Página anterior
      </button>
      <span>Página {Math.floor(offset / pageSize) + 1}</span>
      <button
        type="button"
        className="secondary"
        disabled={count < pageSize}
        onClick={() => onChange(offset + pageSize)}
      >
        Próxima página
      </button>
    </nav>
  );
}

export function Field({ label, children, ...props }) {
  const id = useId();
  return (
    <label htmlFor={id} className={`field ${props.className || ""}`}>
      <span>{label}</span>
      {children ? (
        cloneElement(children, { id })
      ) : (
        <input {...props} id={id} className={undefined} />
      )}
    </label>
  );
}

export const dateTime = (value) =>
  new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
