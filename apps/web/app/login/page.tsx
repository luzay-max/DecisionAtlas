import React, { Suspense } from "react";

import { LoginPanel } from "../../components/auth/login-panel";

export default function LoginPage() {
  return (
    <main className="home">
      <Suspense fallback={<div className="panel">Loading login...</div>}>
        <LoginPanel />
      </Suspense>
    </main>
  );
}
