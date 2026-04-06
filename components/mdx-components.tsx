import type {
  AnchorHTMLAttributes,
  HTMLAttributes,
  TableHTMLAttributes,
  TdHTMLAttributes,
  ThHTMLAttributes,
} from "react";

function cx(...parts: (string | undefined)[]) {
  return parts.filter(Boolean).join(" ");
}

export const mdxComponents = {
  a: (props: AnchorHTMLAttributes<HTMLAnchorElement>) => (
    <a
      {...props}
      className="font-medium text-accent underline-offset-2 hover:text-accent/90 hover:underline"
    />
  ),

  table: ({ className, children, ...props }: TableHTMLAttributes<HTMLTableElement>) => (
    <div className="mdx-table-scroll my-8 w-full overflow-x-auto rounded-lg border border-[rgba(255,255,255,0.1)] bg-[#12121A]">
      <table
        {...props}
        className={cx(
          "mdx-table w-full min-w-[min(100%,520px)] border-collapse text-left text-sm",
          className,
        )}
      >
        {children}
      </table>
    </div>
  ),

  thead: ({ className, ...props }: HTMLAttributes<HTMLTableSectionElement>) => (
    <thead {...props} className={cx("bg-[rgba(255,255,255,0.08)]", className)} />
  ),

  tbody: ({ className, ...props }: HTMLAttributes<HTMLTableSectionElement>) => (
    <tbody {...props} className={cx(className)} />
  ),

  tr: ({ className, ...props }: HTMLAttributes<HTMLTableRowElement>) => (
    <tr {...props} className={cx(className)} />
  ),

  th: ({ className, ...props }: ThHTMLAttributes<HTMLTableCellElement>) => (
    <th
      {...props}
      className={cx(
        "border border-[rgba(255,255,255,0.1)] px-4 py-3 align-top text-sm font-semibold text-white",
        className,
      )}
    />
  ),

  td: ({ className, ...props }: TdHTMLAttributes<HTMLTableCellElement>) => (
    <td
      {...props}
      className={cx(
        "border border-[rgba(255,255,255,0.1)] px-4 py-3 align-top text-muted",
        className,
      )}
    />
  ),
};
