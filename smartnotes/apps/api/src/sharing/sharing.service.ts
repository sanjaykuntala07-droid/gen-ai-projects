import { Injectable, NotFoundException, ForbiddenException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { randomUUID } from 'crypto';

@Injectable()
export class SharingService {
  constructor(private readonly prisma: PrismaService) {}

  async createShareLink(userId: string, noteId: string, permission: 'VIEW' | 'EDIT', expiresAt?: string) {
    // Verify note belongs to user
    const note = await this.prisma.note.findFirst({
      where: { id: noteId, userId },
    });

    if (!note) {
      throw new NotFoundException('Note not found');
    }

    const shareToken = randomUUID();

    return this.prisma.sharedNote.create({
      data: {
        noteId,
        shareToken,
        permission,
        expiresAt: expiresAt ? new Date(expiresAt) : null,
      },
    });
  }

  async getSharedNote(shareToken: string) {
    const sharedNote = await this.prisma.sharedNote.findUnique({
      where: { shareToken },
      include: {
        note: {
          include: {
            tags: {
              include: {
                tag: true,
              },
            },
          },
        },
      },
    });

    if (!sharedNote) {
      throw new NotFoundException('Shared note link not found');
    }

    if (sharedNote.expiresAt && new Date() > sharedNote.expiresAt) {
      // Clean up expired share link
      await this.prisma.sharedNote.delete({ where: { id: sharedNote.id } });
      throw new NotFoundException('Shared note link has expired');
    }

    return {
      permission: sharedNote.permission,
      note: {
        id: sharedNote.note.id,
        title: sharedNote.note.title,
        content: sharedNote.note.content,
        updatedAt: sharedNote.note.updatedAt,
        tags: sharedNote.note.tags,
      },
    };
  }

  async updateSharedNote(shareToken: string, title?: string, content?: string) {
    const sharedNote = await this.prisma.sharedNote.findUnique({
      where: { shareToken },
    });

    if (!sharedNote) {
      throw new NotFoundException('Shared note link not found');
    }

    if (sharedNote.expiresAt && new Date() > sharedNote.expiresAt) {
      throw new NotFoundException('Shared note link has expired');
    }

    if (sharedNote.permission !== 'EDIT') {
      throw new ForbiddenException('You do not have permission to edit this note');
    }

    return this.prisma.note.update({
      where: { id: sharedNote.noteId },
      data: {
        title,
        content,
      },
    });
  }

  async listShares(userId: string, noteId: string) {
    // Verify note belongs to user
    const note = await this.prisma.note.findFirst({
      where: { id: noteId, userId },
    });

    if (!note) {
      throw new NotFoundException('Note not found');
    }

    return this.prisma.sharedNote.findMany({
      where: { noteId },
      orderBy: { createdAt: 'desc' },
    });
  }

  async revokeShare(userId: string, noteId: string, shareId: string) {
    // Verify note belongs to user
    const note = await this.prisma.note.findFirst({
      where: { id: noteId, userId },
    });

    if (!note) {
      throw new NotFoundException('Note not found');
    }

    const share = await this.prisma.sharedNote.findFirst({
      where: { id: shareId, noteId },
    });

    if (!share) {
      throw new NotFoundException('Share link not found');
    }

    return this.prisma.sharedNote.delete({
      where: { id: shareId },
    });
  }
}
