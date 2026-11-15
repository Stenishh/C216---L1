import { useEffect, useState } from "react";
import { ItemForm } from "./components/ItemForm";
import { ItemList } from "./components/ItemList";

import { createItem, listItems } from "./services/items";

export default function App() {
  const [items, setItems] = useState([]);

  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");

  useEffect(() => {
    let active = true;
    listItems()
      .then((data) => {
        if (active) setItems(data);
      })
      .catch((error) => {
        if (active) setLoadError(error.message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  async function addItem(values) {
    const created = await createItem(values);
    setItems((current) => [...current, created]);
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8 text-slate-900 selection:bg-blue-100 sm:px-6 sm:py-14">
      <div className="mx-auto max-w-xl space-y-8">
        <header className="space-y-3">
          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Gerenciador de Itens
          </h1>
          <p className="text-slate-600">
            Cadastre um nome e os detalhes do seu item.
          </p>
          <p className="text-sm text-slate-600">
            Os itens são salvos no banco e permanecem após atualizar a página.
          </p>
        </header>
        <ItemForm onAdd={addItem} disabled={loading || !!loadError} />
        <section aria-labelledby="items-heading" className="space-y-4">
          <h2 id="items-heading" className="text-xl font-semibold">
            Itens cadastrados
          </h2>
          <p role="status" className="text-sm text-slate-600">
            {items.length}{" "}
            {items.length === 1 ? "item cadastrado" : "itens cadastrados"}
          </p>
          {loading ? (
            <p role="status">Carregando itens...</p>
          ) : loadError ? (
            <p role="alert">{loadError}</p>
          ) : (
            <ItemList items={items} />
          )}
        </section>
      </div>
    </main>
  );
}
