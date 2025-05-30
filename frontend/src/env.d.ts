
interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_BYPASS_AUTH: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
