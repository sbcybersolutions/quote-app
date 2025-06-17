// src/global.d.ts
declare global {
  /**
   * The Firebase configuration object provided by the Canvas environment.
   * It's a JSON string that needs to be parsed.
   */
  const __firebase_config: string;

  /**
   * The unique application ID provided by the Canvas environment.
   */
  const __app_id: string;

  /**
   * The initial Firebase custom authentication token provided by the Canvas environment.
   */
  const __initial_auth_token: string | undefined; // Use undefined as it might not always be present
}

// This ensures the file is treated as a module and not just a global script.
export {};