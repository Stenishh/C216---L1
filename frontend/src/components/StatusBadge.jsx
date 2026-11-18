import { statuses } from "../domain/orders";

export function StatusBadge({ status }) {
  return (
    <span className="badge" data-status={status}>
      {statuses[status] || status}
    </span>
  );
}
