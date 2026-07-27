"use client";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight } from "lucide-react";
import Link from "next/link";
import { type ReactNode } from "react";

import Card from "@/components/ui/Card";
import { api, type Envelope } from "@/lib/api";
import { faDateTime } from "@/lib/format";

interface Props<T> {
  resource: string;
  id: string;
  backHref: string;
  backLabel: string;
  render: (item: T) => ReactNode;
}

/** Generic detail view: fetches /{resource}/{id}, shows a back link + rendered body. */
export default function DetailView<T extends { created_at?: string }>({
  resource, id, backHref, backLabel, render,
}: Props<T>) {
  const { data, isLoading, isError } = useQuery({
    queryKey: [resource, id],
    queryFn: async () => (await api.get<Envelope<T>>(`/${resource}/${id}`)).data.data,
  });

  return (
    <div>
      <Link href={backHref} className="mb-4 inline-flex items-center gap-1 text-sm text-ink-500 hover:text-brand-600">
        <ArrowRight size={16} /> {backLabel}
      </Link>
      {isLoading && <Card className="p-8 text-center text-sm text-ink-400">در حال بارگذاری…</Card>}
      {isError && <Card className="p-8 text-center text-sm text-red-600">مورد یافت نشد یا دسترسی مجاز نیست.</Card>}
      {data && (
        <Card className="p-6">
          {render(data)}
          {data.created_at && (
            <p className="mt-6 border-t border-ink-200 pt-3 text-xs text-ink-400">ثبت: {faDateTime(data.created_at)}</p>
          )}
        </Card>
      )}
    </div>
  );
}
