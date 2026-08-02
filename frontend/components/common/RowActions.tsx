"use client";
import { Pencil, Trash2 } from "lucide-react";
import { useState } from "react";

import CreateForm, { type Field } from "@/components/common/CreateForm";
import Modal from "@/components/ui/Modal";
import { useRemoveById } from "@/hooks/useContent";

interface Props {
  resource: string;
  id: string;
  fields?: Field[];
  initial?: Record<string, unknown>;
  transform?: (v: Record<string, unknown>) => Record<string, unknown>;
}

/** Compact edit (modal, pre-filled) + delete (confirm) actions for card/list rows. */
export default function RowActions({ resource, id, fields, initial, transform }: Props) {
  const [editing, setEditing] = useState(false);
  const remove = useRemoveById(resource);
  const onDelete = () => {
    if (window.confirm("آیا از حذف این مورد مطمئن هستید؟")) remove.mutate(id);
  };
  return (
    <span className="flex items-center gap-1" onClick={(e) => e.preventDefault()}>
      {fields && (
        <button onClick={() => setEditing(true)} className="rounded p-1 text-ink-400 hover:bg-brand-50 hover:text-brand-600" aria-label="ویرایش">
          <Pencil size={15} />
        </button>
      )}
      <button onClick={onDelete} className="rounded p-1 text-ink-400 hover:bg-red-50 hover:text-red-600" aria-label="حذف">
        <Trash2 size={15} />
      </button>
      {fields && (
        <Modal open={editing} onClose={() => setEditing(false)} title="ویرایش">
          <CreateForm resource={resource} fields={fields} transform={transform}
            editId={id} initialValues={initial} onDone={() => setEditing(false)} />
        </Modal>
      )}
    </span>
  );
}
