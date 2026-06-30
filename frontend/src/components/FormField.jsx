/**
 * Labelled form input with inline validation messaging.
 */
import styles from "./FormField.module.css";

/**
 * Render a labelled input and optional field-level error.
 * @param {{
 *   id: string,
 *   label: string,
 *   type?: string,
 *   value: string,
 *   onChange: (event: import("react").ChangeEvent<HTMLInputElement>) => void,
 *   error?: string|null,
 *   placeholder?: string,
 *   autoComplete?: string,
 *   required?: boolean,
 *   step?: string,
 *   min?: string,
 * }} props
 */
function FormField({
  id,
  label,
  type = "text",
  value,
  onChange,
  error = null,
  placeholder = "",
  autoComplete,
  required = false,
  step,
  min,
}) {
  return (
    <div className={styles.field}>
      <label className={styles.label} htmlFor={id}>
        {label}
      </label>
      <input
        id={id}
        name={id}
        type={type}
        className={error ? `${styles.input} ${styles.inputError}` : styles.input}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        autoComplete={autoComplete}
        required={required}
        step={step}
        min={min}
        aria-invalid={Boolean(error)}
      />
      {error ? <span className={styles.error}>{error}</span> : null}
    </div>
  );
}

export default FormField;
