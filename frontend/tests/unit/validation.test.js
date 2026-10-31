import { describe, expect, it } from "vitest";
import { NAME_MAX_LENGTH, validateItem } from "../../src/validation";

describe("validateItem", () => {
  it.each(["", "   ", "\n\t"])("rejeita nome vazio: %j", (name) => {
    expect(validateItem({ name, description: "" }).errors.name).toBe(
      "O nome é obrigatório.",
    );
  });
  it("rejeita nomes acima do limite", () => {
    expect(
      validateItem({ name: "a".repeat(NAME_MAX_LENGTH + 1), description: "" })
        .errors.name,
    ).toBe("O nome deve ter no máximo 100 caracteres.");
  });
  it("aceita o limite e remove espaços das extremidades", () => {
    const name = "a".repeat(NAME_MAX_LENGTH);
    expect(
      validateItem({ name: ` ${name} `, description: " detalhes " }),
    ).toEqual({ errors: {}, values: { name, description: "detalhes" } });
  });
  it("aceita descrição opcional vazia", () => {
    expect(validateItem({ name: " Item ", description: "   " })).toEqual({
      errors: {},
      values: { name: "Item", description: "" },
    });
  });
});
