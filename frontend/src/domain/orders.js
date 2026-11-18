export const statuses = {
  received: "Recebida",
  in_diagnosis: "Em diagnóstico",
  awaiting_approval: "Aguardando aprovação",
  in_repair: "Em reparo",
  completed: "Concluída",
  delivered: "Entregue",
  cancelled: "Cancelada",
};
export const decisions = {
  not_requested: "Não solicitado",
  pending: "Pendente",
  approved: "Aprovado",
  rejected: "Rejeitado",
};
export const actions = {
  open: "Ordem aberta",
  begin_diagnosis: "Diagnóstico iniciado",
  request_approval: "Aprovação solicitada",
  approve_budget: "Orçamento aprovado",
  reject_budget: "Orçamento rejeitado",
  start_repair: "Reparo iniciado",
  complete_repair: "Reparo concluído",
  deliver: "Equipamento entregue",
  cancel: "Ordem cancelada",
};
export const currency = (value) =>
  value === null || value === undefined
    ? "Não informado"
    : new Intl.NumberFormat("pt-BR", {
        style: "currency",
        currency: "BRL",
      }).format(Number(value));
