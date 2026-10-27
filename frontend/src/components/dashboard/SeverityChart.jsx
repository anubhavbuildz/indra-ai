import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card } from "../ui/Primitives";

const COLORS = {
  CRITICAL: "#ff5d70",
  HIGH: "#ffad66",
  MEDIUM: "#f4d36a",
  LOW: "#66d9b2",
};

export function SeverityChart({ counts }) {
  const data = Object.entries(counts).map(([name, value]) => ({
    name: name.charAt(0) + name.slice(1).toLowerCase(),
    value,
    color: COLORS[name],
  }));
  return (
    <Card className="chart-card">
      <div className="section-heading">
        <div>
          <div className="section-title">Finding severity</div>
          <div className="section-subtitle">From the latest completed audit</div>
        </div>
        <span className="chart-caption">LATEST RUN</span>
      </div>
      <div className="severity-chart">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 12, right: 6, left: -22, bottom: 0 }}>
            <CartesianGrid stroke="#202a39" vertical={false} />
            <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: "#8290a4", fontSize: 11 }} />
            <YAxis allowDecimals={false} axisLine={false} tickLine={false} tick={{ fill: "#718096", fontSize: 10 }} />
            <Tooltip
              cursor={{ fill: "rgba(255,255,255,.025)" }}
              contentStyle={{
                background: "#111722",
                border: "1px solid #293548",
                borderRadius: 10,
                color: "#eaf1f8",
                fontSize: 12,
              }}
            />
            <Bar dataKey="value" radius={[5, 5, 1, 1]} maxBarSize={34}>
              {data.map((entry) => (
                <Cell key={entry.name} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="chart-legend">
        {data.map(({ name, color, value }) => (
          <div key={name}>
            <span style={{ background: color }} />
            {name}
            <strong>{value}</strong>
          </div>
        ))}
      </div>
    </Card>
  );
}
