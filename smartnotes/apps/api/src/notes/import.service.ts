import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { marked } from 'marked';

@Injectable()
export class ImportService {
  constructor(private readonly prisma: PrismaService) {}

  async importMarkdown(userId: string, filename: string, markdown: string) {
    let title = filename.replace(/\.md$/i, '');
    let markdownContent = markdown;

    // Parse frontmatter
    const frontmatterRegex = /^---\r?\n([\s\S]*?)\r?\n---\r?\n/;
    const fmMatch = markdown.match(frontmatterRegex);
    if (fmMatch) {
      const frontmatter = fmMatch[1];
      markdownContent = markdown.replace(frontmatterRegex, '');
      const lines = frontmatter.split('\n');
      for (const line of lines) {
        const parts = line.split(':');
        if (parts.length >= 2) {
          const key = parts[0].trim().toLowerCase();
          const val = parts.slice(1).join(':').trim();
          if (key === 'title') {
            title = val.replace(/^["']|["']$/g, '');
          }
        }
      }
    }

    // Extract first H1 as title if not set by frontmatter
    const headingMatch = markdownContent.match(/^#\s+(.+)$/m);
    if (headingMatch) {
      title = headingMatch[1].trim();
      markdownContent = markdownContent.replace(/^#\s+.+\n*/, '');
    }

    // Convert markdown to HTML
    const htmlContent = await marked.parse(markdownContent);

    // Save to database
    return this.prisma.note.create({
      data: {
        userId,
        title,
        content: htmlContent,
      },
      include: {
        tags: { include: { tag: true } },
        reminders: true,
      },
    });
  }
}
