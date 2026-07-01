import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';

/**
 * Search Service
 *
 * Database-agnostic full-text search.
 * Uses Prisma's native `contains` filter and highlights snippets in memory.
 * Compatible with SQLite, PostgreSQL, etc.
 */
@Injectable()
export class SearchService {
  constructor(private readonly prisma: PrismaService) {}

  async search(userId: string, query: string, limit = 20) {
    if (!query || query.trim().length === 0) {
      return [];
    }

    const lowercaseQuery = query.toLowerCase();

    // Query notes where title or content contains the query term
    const notes = await this.prisma.note.findMany({
      where: {
        userId,
        OR: [
          { title: { contains: query } },
          { content: { contains: query } },
        ],
      },
      orderBy: { updatedAt: 'desc' },
      take: limit,
    });

    // Format results to include rankings and highlights (snippets) in JS
    return notes.map((note) => {
      const titleMatch = note.title.toLowerCase().includes(lowercaseQuery);
      const contentText = this.stripHtml(note.content || '');
      const contentLower = contentText.toLowerCase();
      const index = contentLower.indexOf(lowercaseQuery);

      let snippet = '';
      if (index !== -1) {
        const start = Math.max(0, index - 40);
        const end = Math.min(contentText.length, index + query.length + 60);
        const before = contentText.slice(start, index);
        const matched = contentText.slice(index, index + query.length);
        const after = contentText.slice(index + query.length, end);
        
        snippet = `${start > 0 ? '...' : ''}${before}<mark>${matched}</mark>${after}${end < contentText.length ? '...' : ''}`;
      } else {
        snippet = contentText.slice(0, 100) + (contentText.length > 100 ? '...' : '');
      }

      return {
        id: note.id,
        title: note.title,
        content: note.content,
        archived: note.archived,
        createdAt: note.createdAt,
        updatedAt: note.updatedAt,
        snippet,
        rank: titleMatch ? 2 : 1, // Basic ranking: title matches rank higher
      };
    }).sort((a, b) => b.rank - a.rank);
  }

  private stripHtml(html: string): string {
    return html
      .replace(/<[^>]+>/g, '')
      .replace(/&nbsp;/g, ' ')
      .replace(/&amp;/g, '&')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .trim();
  }
}
