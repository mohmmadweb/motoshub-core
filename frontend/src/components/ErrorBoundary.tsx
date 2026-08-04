import { Component, type ReactNode } from "react";
import { AlertTriangle, RotateCcw } from "lucide-react";

/**
 * Catches render-time errors so one broken screen shows a readable message
 * instead of blanking the whole app (a white page with no clue).
 */
export default class ErrorBoundary extends Component<
  { children: ReactNode },
  { error: Error | null }
> {
  state: { error: Error | null } = { error: null };

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  componentDidCatch(error: Error, info: unknown) {
    // Keep the details in the console for debugging.
    console.error("UI crash:", error, info);
  }

  render() {
    const { error } = this.state;
    if (!error) return this.props.children;
    return (
      <div dir="rtl" className="card p-6 m-4 text-center">
        <AlertTriangle className="mx-auto text-amber-500 mb-3" size={28} />
        <h2 className="text-sm font-bold text-ink-900 mb-1.5">این بخش با خطا مواجه شد</h2>
        <p className="text-xs text-ink-500 leading-6 mb-4">
          بقیهٔ سامانه سالم است. می‌توانید دوباره تلاش کنید یا به صفحهٔ دیگری بروید.
        </p>
        <pre className="text-[11px] text-ink-400 bg-ink-50 rounded-lg p-3 overflow-x-auto text-left mb-4" dir="ltr">
          {error.message}
        </pre>
        <button
          onClick={() => this.setState({ error: null })}
          className="inline-flex items-center gap-1.5 text-xs bg-brand-600 text-white rounded-lg px-3.5 py-2 hover:bg-brand-700"
        >
          <RotateCcw size={13} /> تلاش دوباره
        </button>
      </div>
    );
  }
}
