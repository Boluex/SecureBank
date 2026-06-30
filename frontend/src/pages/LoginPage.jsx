/**
 * Login page.
 *
 * Validates input client-side, then delegates to the auth context which sets
 * httpOnly cookies via the backend. Shows a loading state while the request is
 * in flight and surfaces server errors inline.
 */
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import FormField from "../components/FormField.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { extractErrorMessage, validateEmail } from "../utils/validators.js";
import styles from "./Auth.module.css";

/** Render the login form. */
function LoginPage() {
  const { signIn } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fieldError, setFieldError] = useState(null);
  const [formError, setFormError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setFormError(null);
    const emailError = validateEmail(email);
    setFieldError(emailError);
    if (emailError || !password) {
      if (!password) setFormError("Password is required.");
      return;
    }

    setIsSubmitting(true);
    try {
      await signIn({ email, password });
      navigate("/", { replace: true });
    } catch (error) {
      setFormError(extractErrorMessage(error, "Invalid email or password."));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.brand}>🔒 SecureBank</div>
        <p className={styles.subtitle}>Sign in to your account</p>
        {formError ? <div className={styles.formError}>{formError}</div> : null}
        <form onSubmit={handleSubmit} noValidate>
          <FormField
            id="email"
            label="Email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            error={fieldError}
            autoComplete="email"
            placeholder="you@example.com"
          />
          <FormField
            id="password"
            label="Password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
            placeholder="Your password"
          />
          <button className={styles.submit} type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Signing in…" : "Sign in"}
          </button>
        </form>
        <p className={styles.footer}>
          No account? <Link to="/register">Create one</Link>
        </p>
      </div>
    </div>
  );
}

export default LoginPage;
