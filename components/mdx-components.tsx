import type { AnchorHTMLAttributes } from "react";

export const mdxComponents = {
  a: (props: AnchorHTMLAttributes<HTMLAnchorElement>) => (
    <a
      {...props}
      className="font-medium text-accent underline-offset-2 hover:text-accent/90 hover:underline"
    />
  ),
};
