import { Injectable, NotFoundException, ConflictException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { CreateTagDto } from './dto';

@Injectable()
export class TagsService {
  constructor(private readonly prisma: PrismaService) {}

  async create(userId: string, dto: CreateTagDto) {
    // Check for duplicate tag name for this user
    const existing = await this.prisma.tag.findUnique({
      where: { userId_name: { userId, name: dto.name } },
    });

    if (existing) {
      throw new ConflictException('A tag with this name already exists');
    }

    return this.prisma.tag.create({
      data: { userId, ...dto },
    });
  }

  async findAll(userId: string) {
    return this.prisma.tag.findMany({
      where: { userId },
      orderBy: { name: 'asc' },
      include: {
        _count: { select: { notes: true } },
      },
    });
  }

  async remove(userId: string, id: string) {
    const tag = await this.prisma.tag.findFirst({
      where: { id, userId },
    });

    if (!tag) {
      throw new NotFoundException('Tag not found');
    }

    return this.prisma.tag.delete({ where: { id } });
  }

  async attachTag(userId: string, noteId: string, tagId: string) {
    // Verify note and tag belong to user
    const [note, tag] = await Promise.all([
      this.prisma.note.findFirst({ where: { id: noteId, userId } }),
      this.prisma.tag.findFirst({ where: { id: tagId, userId } }),
    ]);

    if (!note) throw new NotFoundException('Note not found');
    if (!tag) throw new NotFoundException('Tag not found');

    return this.prisma.noteTag.upsert({
      where: { noteId_tagId: { noteId, tagId } },
      create: { noteId, tagId },
      update: {},
      include: { tag: true },
    });
  }

  async detachTag(userId: string, noteId: string, tagId: string) {
    const note = await this.prisma.note.findFirst({
      where: { id: noteId, userId },
    });

    if (!note) throw new NotFoundException('Note not found');

    return this.prisma.noteTag.delete({
      where: { noteId_tagId: { noteId, tagId } },
    });
  }
}
