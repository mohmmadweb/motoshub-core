// Persian display helpers.
export const faNum = (n: number | string) => Number(n).toLocaleString("fa-IR");

export const faDate = (iso: string) =>
  new Date(iso).toLocaleDateString("fa-IR", { year: "numeric", month: "long", day: "numeric" });

export const faDateTime = (iso: string) =>
  new Date(iso).toLocaleString("fa-IR", {
    year: "numeric", month: "long", day: "numeric", hour: "2-digit", minute: "2-digit",
  });
