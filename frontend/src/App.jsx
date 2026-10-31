import { useState } from "react";
import { ItemForm } from "./components/ItemForm";
import { ItemList } from "./components/ItemList";

export default function App() {
  const [items, setItems] = useState([]);

  // Na Prática 7, esta função passará a chamar POST /items.
  function addItem({ name, description }) {
    setItems((current) => [
      ...current,
      { id: crypto.randomUUID(), name, description },
    ]);
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
            Os itens ficam nesta sessão e desaparecem ao atualizar a página.
          </p>
        </header>
        <ItemForm onAdd={addItem} />
        <section aria-labelledby="items-heading" className="space-y-4">
          <h2 id="items-heading" className="text-xl font-semibold">
            Itens cadastrados
          </h2>
          <p role="status" className="text-sm text-slate-600">
            {items.length}{" "}
            {items.length === 1 ? "item cadastrado" : "itens cadastrados"}
          </p>
          <ItemList items={items} />
        </section>
      </div>
    </main>
  );
}
