export function MarkdownView({ text = "" }) {
  const lines = String(text).split(/\r?\n/);
  const blocks = [];
  let list = [];

  const flushList = () => {
    if (list.length) {
      blocks.push(
        <ul key={`list-${blocks.length}`}>
          {list.map((item, index) => <li key={index}>{item}</li>)}
        </ul>,
      );
      list = [];
    }
  };

  lines.forEach((line, index) => {
    const trimmed = line.trim();
    if (!trimmed) {
      flushList();
      return;
    }
    if (/^[-*]\s+/.test(trimmed)) {
      list.push(trimmed.replace(/^[-*]\s+/, ""));
      return;
    }
    flushList();
    const heading = trimmed.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      const level = Math.min(heading[1].length + 1, 4);
      const Heading = `h${level}`;
      blocks.push(<Heading key={`heading-${index}`}>{heading[2]}</Heading>);
    } else {
      blocks.push(<p key={`paragraph-${index}`}>{trimmed.replaceAll("**", "")}</p>);
    }
  });
  flushList();
  return <div className="markdown-view">{blocks}</div>;
}
