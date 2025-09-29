import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";
import MixpanelInitializer from "./MixpanelInitializer";
import { LayoutProvider } from "./(presentation-generator)/context/LayoutContext";
import { Toaster } from "@/components/ui/sonner";


export const metadata: Metadata = {
  metadataBase: new URL("https://my.com"),
  title: "td-smart-ppt",
  description:
    "td-smart-ppt",
  keywords: [
    "AI presentation generator",
    "专业幻灯片",
  ],
  alternates: {
    canonical: "https://my.com",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {

  return (
    <html lang="en">
      <body className="antialiased">
        <Providers>
          <MixpanelInitializer>
            <LayoutProvider>
              {children}
            </LayoutProvider>
          </MixpanelInitializer>
        </Providers>
        <Toaster position="top-center" />
      </body>
    </html>
  );
}

