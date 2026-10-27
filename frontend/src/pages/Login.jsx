import { useState } from "react";
import { motion } from "framer-motion";
import { ArrowRight, Eye, EyeOff, Fingerprint, LockKeyhole } from "lucide-react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getErrorMessage } from "../lib/utils";
import { Button, Input } from "../components/ui/Primitives";
import agentIllustration from "../assets/three-specialist-agents.svg";
import indraaMark from "../assets/indraa-mark.svg";

export default function Login() {
  const { signIn, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) return <Navigate to="/" replace />;

  async function submit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await signIn(username, password);
      navigate(location.state?.from?.pathname || "/", { replace: true });
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-page">
      <div className="login-grid" />
      <div className="login-brand">
        <span className="brand-mark"><img src={indraaMark} alt="" /></span>
        <span>INDRAA</span>
        <small>AI CLOUD SECURITY POSTURE</small>
      </div>
      <div className="login-layout">
        <motion.section
          className="login-story"
          initial={{ opacity: 0, x: -18 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.45 }}
        >
          <div className="login-kicker"><span className="status-dot" /> PRIVATE CLOUD SECURITY WORKSPACE</div>
          <h1>Know what’s<br />hiding in your<br /><em>cloud.</em></h1>
          <p>Evidence-led AWS security review, with three specialist agents working in sequence.</p>
          <img
            className="login-agent-illustration"
            src={agentIllustration}
            alt="Cloud Agent audits infrastructure, Compliance Agent synthesizes guidance, and Senior Agent verifies evidence."
          />
        </motion.section>
        <motion.section
          className="login-card"
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <div className="login-card-icon"><Fingerprint size={22} /></div>
          <div className="eyebrow">WELCOME BACK</div>
          <h2>Sign in to Indraa</h2>
          <p className="login-card-description">Use the account configured for your backend.</p>
          <form onSubmit={submit} className="login-form">
            <label>
              <span>Username</span>
              <Input
                autoComplete="username"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                placeholder="Your workspace username"
                required
              />
            </label>
            <label>
              <span>Password</span>
              <div className="password-input">
                <Input
                  autoComplete="current-password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Enter your password"
                  required
                />
                <button type="button" onClick={() => setShowPassword(!showPassword)} aria-label="Toggle password visibility">
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </label>
            {error && <div className="form-error" role="alert">{error}</div>}
            <Button className="login-submit" type="submit" disabled={loading}>
              {loading ? "Authenticating…" : "Continue securely"}
              {!loading && <ArrowRight size={16} />}
            </Button>
          </form>
          <div className="login-card-foot"><LockKeyhole size={13} /> JWT-secured session · 30-minute token</div>
        </motion.section>
      </div>
      <div className="login-footnote">
        <span>INDRAA · AI CLOUD SECURITY POSTURE</span>
        <span>POWERED BY <b>NVIDIA</b></span>
      </div>
    </main>
  );
}
