import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import TurndownService from 'turndown';
import JSZip from 'jszip';

@Injectable()
export class ExportService {
  private readonly turndownService: TurndownService;

  constructor(private readonly prisma: PrismaService) {
    this.turndownService = new TurndownService();
  }

  async exportNoteToMarkdown(userId: string, noteId: string): Promise<{ title: string; markdown: string }> {
    const note = await this.prisma.note.findFirst({
      where: { id: noteId, userId },
    });

    if (!note) {
      throw new NotFoundException('Note not found');
    }

    const markdown = this.turndownService.turndown(note.content || '');
    const title = note.title || 'Untitled';
    const fileContent = `# ${title}\n\n${markdown}`;

    return { title, markdown: fileContent };
  }

  async exportAllNotesToZip(userId: string): Promise<Buffer> {
    const notes = await this.prisma.note.findMany({
      where: { userId },
    });

    const zip = new JSZip();

    for (const note of notes) {
      const markdown = this.turndownService.turndown(note.content || '');
      const title = note.title || 'Untitled';
      const fileContent = `# ${title}\n\n${markdown}`;
      // Clean title for filename
      const safeTitle = title.replace(/[^a-zA-Z0-9]/g, '_');
      zip.file(`${safeTitle}.md`, fileContent);
    }

    return zip.generateAsync({ type: 'nodebuffer' });
  }
}
