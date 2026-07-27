"use client";
import { Plus } from "lucide-react";
import { useState } from "react";

import CreateForm, { type Field } from "@/components/common/CreateForm";
import Button from "@/components/ui/Button";
import Modal from "@/components/ui/Modal";

interface Props {
  resource: string;
  fields: Field[];
  label: string;
  transform?: (v: Record<string, unknown>) => Record<string, unknown>;
}

/** Standalone "+ new" button + create modal for custom (non-ContentList) pages. */
export default function AddButton({ resource, fields, label, transform }: Props) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <Button size="sm" icon={<Plus size={15} />} onClick={() => setOpen(true)}>{label}</Button>
      <Modal open={open} onClose={() => setOpen(false)} title={label}>
        <CreateForm resource={resource} fields={fields} transform={transform} onDone={() => setOpen(false)} />
      </Modal>
    </>
  );
}
