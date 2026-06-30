/**
 * Loading indicator used by every asynchronous view.
 */
import styles from "./Spinner.module.css";

/**
 * Render an animated spinner with an optional label.
 * @param {{label?: string}} props
 */
function Spinner({ label = "Loading…" }) {
  return (
    <div className={styles.wrapper} role="status" aria-live="polite">
      <span className={styles.spinner} aria-hidden="true" />
      <span className={styles.label}>{label}</span>
    </div>
  );
}

export default Spinner;
