export function ItemList({ items }) {
  if (items.length === 0) {
    return (
      <p className="rounded-xl border border-dashed border-slate-300 p-6 text-slate-600">
        Nenhum item cadastrado.
      </p>
    );
  }
  return (
    <ul className="space-y-3">
      {items.map((item) => (
        <li
          key={item.id}
          className="rounded-xl border border-slate-200 bg-white p-5 [overflow-wrap:anywhere]"
        >
          <p className="font-semibold">{item.name}</p>
          {item.description && (
            <p className="mt-1 whitespace-pre-wrap text-sm text-slate-600">
              {item.description}
            </p>
          )}
        </li>
      ))}
    </ul>
  );
}
