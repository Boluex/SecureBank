/**
 * Application header with branding and session controls.
 */
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import styles from "./Navbar.module.css";

/** Render the top navigation bar for authenticated users. */
function Navbar() {
  const { email, signOut } = useAuth();
  const navigate = useNavigate();

  const handleSignOut = async () => {
    await signOut();
    navigate("/login", { replace: true });
  };

  return (
    <header className={styles.navbar}>
      <div className={styles.brand} onClick={() => navigate("/")}>
        <span className={styles.logo}>🔒</span>
        <span>SecureBank</span>
      </div>
      <div className={styles.session}>
        <span className={styles.email}>{email}</span>
        <button className={styles.signOut} onClick={handleSignOut}>
          Sign out
        </button>
      </div>
    </header>
  );
}

export default Navbar;
