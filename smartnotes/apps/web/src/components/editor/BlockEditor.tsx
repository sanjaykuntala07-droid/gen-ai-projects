import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import TaskList from '@tiptap/extension-task-list';
import TaskItem from '@tiptap/extension-task-item';
import Highlight from '@tiptap/extension-highlight';
import Typography from '@tiptap/extension-typography';
import { useEffect } from 'react';

interface BlockEditorProps {
  content: string;
  onUpdate: (content: string) => void;
  editable?: boolean;
}

export function BlockEditor({ content, onUpdate, editable = true }: BlockEditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: { levels: [1, 2, 3] },
        codeBlock: {
          HTMLAttributes: {
            class: 'code-block',
          },
        },
      }),
      Placeholder.configure({
        placeholder: 'Start writing, or type "/" for commands...',
      }),
      TaskList,
      TaskItem.configure({
        nested: true,
      }),
      Highlight.configure({
        multicolor: true,
      }),
      Typography,
    ],
    content: content || '',
    editable,
    onUpdate: ({ editor }) => {
      onUpdate(editor.getHTML());
    },
    editorProps: {
      attributes: {
        class: 'ProseMirror',
        id: 'block-editor',
      },
      handleKeyDown: (view, event) => {
        // Slash command trigger
        if (event.key === '/' && !event.ctrlKey && !event.metaKey) {
          // Let the editor handle the '/' character first
          return false;
        }
        return false;
      },
    },
  });

  // Update editor content when note changes
  useEffect(() => {
    if (editor && content !== editor.getHTML()) {
      editor.commands.setContent(content || '');
    }
  }, [content]);

  if (!editor) return null;

  return (
    <div>
      {/* Floating Toolbar */}
      {editable && (
        <div
          style={{
            display: 'flex',
            gap: '2px',
            padding: '4px 8px',
            marginBottom: '12px',
            borderRadius: 'var(--radius-md)',
            background: 'var(--color-bg-tertiary)',
            border: '1px solid var(--color-border-light)',
            flexWrap: 'wrap',
          }}
        >
          <ToolbarButton
            active={editor.isActive('bold')}
            onClick={() => editor.chain().focus().toggleBold().run()}
            title="Bold (Ctrl+B)"
          >
            <strong>B</strong>
          </ToolbarButton>
          <ToolbarButton
            active={editor.isActive('italic')}
            onClick={() => editor.chain().focus().toggleItalic().run()}
            title="Italic (Ctrl+I)"
          >
            <em>I</em>
          </ToolbarButton>
          <ToolbarButton
            active={editor.isActive('strike')}
            onClick={() => editor.chain().focus().toggleStrike().run()}
            title="Strikethrough"
          >
            <s>S</s>
          </ToolbarButton>
          <ToolbarButton
            active={editor.isActive('code')}
            onClick={() => editor.chain().focus().toggleCode().run()}
            title="Inline Code"
          >
            {'</>'}
          </ToolbarButton>

          <div style={{
            width: 1,
            height: 20,
            background: 'var(--color-border)',
            margin: '0 4px',
            alignSelf: 'center',
          }} />

          <ToolbarButton
            active={editor.isActive('heading', { level: 1 })}
            onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
            title="Heading 1"
          >
            H1
          </ToolbarButton>
          <ToolbarButton
            active={editor.isActive('heading', { level: 2 })}
            onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
            title="Heading 2"
          >
            H2
          </ToolbarButton>
          <ToolbarButton
            active={editor.isActive('heading', { level: 3 })}
            onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
            title="Heading 3"
          >
            H3
          </ToolbarButton>

          <div style={{
            width: 1,
            height: 20,
            background: 'var(--color-border)',
            margin: '0 4px',
            alignSelf: 'center',
          }} />

          <ToolbarButton
            active={editor.isActive('bulletList')}
            onClick={() => editor.chain().focus().toggleBulletList().run()}
            title="Bullet List"
          >
            •
          </ToolbarButton>
          <ToolbarButton
            active={editor.isActive('orderedList')}
            onClick={() => editor.chain().focus().toggleOrderedList().run()}
            title="Numbered List"
          >
            1.
          </ToolbarButton>
          <ToolbarButton
            active={editor.isActive('taskList')}
            onClick={() => editor.chain().focus().toggleTaskList().run()}
            title="Task List"
          >
            ☑
          </ToolbarButton>

          <div style={{
            width: 1,
            height: 20,
            background: 'var(--color-border)',
            margin: '0 4px',
            alignSelf: 'center',
          }} />

          <ToolbarButton
            active={editor.isActive('blockquote')}
            onClick={() => editor.chain().focus().toggleBlockquote().run()}
            title="Quote"
          >
            "
          </ToolbarButton>
          <ToolbarButton
            active={editor.isActive('codeBlock')}
            onClick={() => editor.chain().focus().toggleCodeBlock().run()}
            title="Code Block"
          >
            {'{ }'}
          </ToolbarButton>
          <ToolbarButton
            active={false}
            onClick={() => editor.chain().focus().setHorizontalRule().run()}
            title="Horizontal Rule"
          >
            —
          </ToolbarButton>
          <ToolbarButton
            active={editor.isActive('highlight')}
            onClick={() => editor.chain().focus().toggleHighlight().run()}
            title="Highlight"
          >
            🖊
          </ToolbarButton>
        </div>
      )}

      <EditorContent editor={editor} />
    </div>
  );
}

function ToolbarButton({
  children,
  active,
  onClick,
  title,
}: {
  children: React.ReactNode;
  active: boolean;
  onClick: () => void;
  title: string;
}) {
  return (
    <button
      onClick={onClick}
      title={title}
      style={{
        padding: '4px 8px',
        borderRadius: 'var(--radius-sm)',
        fontSize: 'var(--font-size-sm)',
        fontWeight: active ? 600 : 400,
        color: active ? 'var(--color-accent)' : 'var(--color-text-secondary)',
        background: active ? 'var(--color-accent-soft)' : 'transparent',
        transition: 'all var(--transition-fast)',
        cursor: 'pointer',
        border: 'none',
        lineHeight: 1,
        minWidth: 28,
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      {children}
    </button>
  );
}
