/**
 * Registration page.
 *
 * Enforces the same password policy as the backend for fast feedback, creates
 * the account, then signs the user in automatically and routes to the
 * dashboard.
 */
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import FormField from "../components/FormField.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { register } from "../services/authService.js";
import {
  extractErrorMessage,
  validateEmail,
  validatePassword,
} from "../utils/validators.js";
import styles from "./Auth.module.css";

/** Render the registration form. */
function RegisterPage() {
  const { signIn } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ full_name: "", email: "", password: "" });
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const updateField = (key) => (event) =>
    setForm((current) => ({ ...current, [key]: event.target.value }));

  const validate = () => {
    const nextErrors = {
      full_name: form.full_name.trim() ? null : "Full name is required.",
      email: validateEmail(form.email),
      password: validatePassword(form.password),
    };
    setErrors(nextErrors);
    return Object.values(nextErrors).every((value) => value === null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setFormError(null);
    if (!validate()) {
      return;
    }

    setIsSubmitting(true);
    try {
      await register(form);
      await signIn({ email: form.email, password: form.password });
      navigate("/", { replace: true });
    } catch (error) {
      setFormError(extractErrorMessage(error, "Could not create the account."));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.brand}>🔒 SecureBank</div>
        <p className={styles.subtitle}>Create your account</p>
        {formError ? <div className={styles.formError}>{formError}</div> : null}
        <form onSubmit={handleSubmit} noValidate>
          <FormField
            id="full_name"
            label="Full name"
            value={form.full_name}
            onChange={updateField("full_name")}
            error={errors.full_name}
            autoComplete="name"
            placeholder="Ada Lovelace"
          />
          <FormField
            id="email"
            label="Email"
            type="email"
            value={form.email}
            onChange={updateField("email")}
            error={errors.email}
            autoComplete="email"
            placeholder="you@example.com"
          />
          <FormField
            id="password"
            label="Password"
            type="password"
            value={form.password}
            onChange={updateField("password")}
            error={errors.password}
            autoComplete="new-password"
            placeholder="At least 10 characters"
          />
          <button className={styles.submit} type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Creating account…" : "Create account"}
          </button>
        </form>
        <p className={styles.footer}>
          Already registered? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}

export default RegisterPage;
