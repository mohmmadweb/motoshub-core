"use client";
import { zodResolver } from "@hookform/resolvers/zod";
import { Building2 } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import { useLogin } from "@/hooks/useAuth";

const schema = z.object({
  username: z.string().min(1, "نام کاربری الزامی است"),
  password: z.string().min(1, "گذرواژه الزامی است"),
});
type FormValues = z.infer<typeof schema>;

export default function LoginForm() {
  const login = useLogin();
  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { username: "admin", password: "demo1234" },
  });

  return (
    <div className="w-full max-w-sm rounded-2xl bg-white p-7 shadow-xl">
      <div className="mb-6 flex flex-col items-center text-center">
        <span className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-brand-600 text-white">
          <Building2 size={22} />
        </span>
        <h1 className="text-base font-bold text-ink-900">ورود به موتوشاب</h1>
        <p className="mt-1 text-xs text-ink-500">پلتفرم ارتباطات و فرآیندهای سازمانی</p>
      </div>

      <form
        className="space-y-3"
        onSubmit={handleSubmit((values) => login.mutate(values))}
      >
        <div>
          <Input placeholder="نام کاربری" {...register("username")} />
          {errors.username && <p className="mt-1 text-xs text-red-600">{errors.username.message}</p>}
        </div>
        <div>
          <Input type="password" placeholder="گذرواژه" {...register("password")} />
          {errors.password && <p className="mt-1 text-xs text-red-600">{errors.password.message}</p>}
        </div>
        {login.isError && (
          <p className="text-xs text-red-600">نام کاربری یا گذرواژه نادرست است.</p>
        )}
        <Button type="submit" className="w-full" loading={login.isPending}>
          ورود
        </Button>
      </form>

      <p className="mt-4 text-center text-[11px] text-ink-400">
        نمونه: admin / demo1234
      </p>
    </div>
  );
}
