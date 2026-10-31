import { useState } from "react";
import { validateItem } from "../validation";

export function ItemForm({ onAdd }) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [errors, setErrors] = useState({});

  function handleSubmit(event) {
    event.preventDefault();
    const result = validateItem({ name, description });
    setErrors(result.errors);
    if (Object.keys(result.errors).length > 0) return;
    onAdd(result.values);
    setName("");
    setDescription("");
  }

  const fieldClass =
    "w-full rounded-lg border border-slate-300 bg-white p-3 text-base outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-600/20";

  return (
    <form
      onSubmit={handleSubmit}
      noValidate
      className="space-y-5 rounded-xl border border-slate-200 bg-white p-5 sm:p-6"
    >
      <div className="space-y-2">
        <label htmlFor="item-name" className="block text-sm font-medium">
          Nome
        </label>
        <input
          id="item-name"
          value={name}
          onChange={(event) => setName(event.target.value)}
          required
          aria-invalid={errors.name ? "true" : "false"}
          aria-describedby={
            errors.name ? "item-name-help item-name-error" : "item-name-help"
          }
          className={fieldClass}
        />
        <p id="item-name-help" className="text-sm text-slate-600">
          Obrigatório. Até 100 caracteres.
        </p>
        {errors.name && (
          <p id="item-name-error" role="alert" className="text-sm text-red-700">
            {errors.name}
          </p>
        )}
      </div>
      <div className="space-y-2">
        <label htmlFor="item-description" className="block text-sm font-medium">
          Descrição
        </label>
        <textarea
          id="item-description"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          rows={3}
          aria-describedby="item-description-help"
          className={fieldClass}
        />
        <p id="item-description-help" className="text-sm text-slate-600">
          Opcional. Inclua os detalhes que precisar.
        </p>
      </div>
      <button
        type="submit"
        className="min-h-11 w-full cursor-pointer rounded-lg bg-blue-700 px-5 py-3 font-medium text-white hover:bg-blue-800 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-blue-700 sm:w-auto"
      >
        Adicionar
      </button>
    </form>
  );
}
