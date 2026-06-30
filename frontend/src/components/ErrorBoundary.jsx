/**
 * Top-level error boundary.
 *
 * Catches rendering errors anywhere in the tree and shows a recoverable
 * fallback instead of a blank screen — a baseline reliability requirement.
 */
import { Component } from "react";
import styles from "./ErrorBoundary.module.css";

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, message: "" };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, message: error?.message ?? "Unexpected error" };
  }

  componentDidCatch(error, info) {
    // In production this is where errors would be forwarded to a monitoring
    // service. We log to the console to aid local debugging.
    console.error("Uncaught UI error:", error, info);
  }

  handleReset = () => {
    this.setState({ hasError: false, message: "" });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className={styles.wrapper}>
          <div className={styles.card}>
            <h1>Something went wrong</h1>
            <p className={styles.detail}>{this.state.message}</p>
            <button className={styles.button} onClick={this.handleReset}>
              Try again
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
