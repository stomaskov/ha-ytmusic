import { defineConfig } from "vite";

export default defineConfig({
  build: {
    outDir: "../custom_components/ytmusic/frontend",
    emptyOutDir: false,
    sourcemap: false,
    cssCodeSplit: false,
    lib: {
      entry: "src/ytmusic-card.ts",
      formats: ["es"],
      fileName: () => "ytmusic-card.js",
    },
    rollupOptions: { output: { inlineDynamicImports: true } },
  },
  test: { environment: "happy-dom", globals: true },
});
