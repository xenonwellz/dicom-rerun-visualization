import { defineConfig } from "vite"

export default defineConfig({
    optimizeDeps: {
        exclude: ["@rerun-io/web-viewer"]
    }
});