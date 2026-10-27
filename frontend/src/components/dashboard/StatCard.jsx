import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import { motion } from "framer-motion";

export function StatCard({ label, value, note, icon: Icon, tone = "blue", delta }) {
  return (
    <motion.div className="stat-card card" whileHover={{ y: -3 }} transition={{ duration: 0.18 }}>
      <div className="stat-top">
        <span className="stat-label">{label}</span>
        <span className={`stat-icon stat-icon-${tone}`}>
          <Icon size={17} />
        </span>
      </div>
      <div className="stat-value">{value}</div>
      <div className="stat-foot">
        <span>{note}</span>
        {delta && (
          <span className={delta.startsWith("-") ? "delta-down" : "delta-up"}>
            {delta.startsWith("-") ? <ArrowDownRight size={13} /> : <ArrowUpRight size={13} />}
            {delta}
          </span>
        )}
      </div>
    </motion.div>
  );
}
