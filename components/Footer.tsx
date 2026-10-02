import Link from "next/link";

export function Footer() {
  return (
    <footer className="mt-auto border-t border-white/10 bg-[#211625] py-12 text-white">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-5 px-5 text-center sm:flex-row sm:px-8 sm:text-left">
        <p className="text-[12px] text-[#aa9caf]">
          © 2026 Relova ·{" "}
          <Link href="/about" className="transition-colors hover:text-primary">
            About
          </Link>
          {" · "}
          <a
            href="https://relova.ai"
            className="transition-colors hover:text-primary"
          >
            relova.ai
          </a>
        </p>
      </div>
    </footer>
  );
}
