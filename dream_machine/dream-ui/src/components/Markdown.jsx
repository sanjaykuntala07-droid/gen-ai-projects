/** Simple markdown-to-html renderer (no external lib needed) */
export default function Markdown({ content }) {
  if (!content) return null;
  const html = content
    // headings
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm,  '<h2>$1</h2>')
    .replace(/^# (.+)$/gm,   '<h1>$1</h1>')
    // bold
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // italic
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // inline code
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // horizontal rule
    .replace(/^---$/gm, '<hr style="border-color:var(--b-subtle);margin:16px 0">')
    // unordered lists
    .replace(/^\s*[-•]\s+(.+)$/gm, '<li>$1</li>')
    .replace(/(<li>[\s\S]*?<\/li>)(?=\s*<li>|\s*$)/g, (m) => `<ul>${m}</ul>`)
    // line breaks
    .replace(/\n{2,}/g, '<br><br>')
    .replace(/\n/g, '<br>');

  return (
    <div
      className="markdown-body"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
