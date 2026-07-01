import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { CreateNoteDto, UpdateNoteDto } from './dto';

@Injectable()
export class NotesService {
  constructor(private readonly prisma: PrismaService) {}

  async create(userId: string, dto: CreateNoteDto) {
    return this.prisma.note.create({
      data: {
        userId,
        title: dto.title,
        content: dto.content || '',
      },
      include: {
        tags: { include: { tag: true } },
        reminders: true,
      },
    });
  }

  async findAll(
    userId: string,
    options: {
      page?: number;
      limit?: number;
      tagId?: string;
      archived?: boolean;
    } = {},
  ) {
    const { page = 1, limit = 20, tagId, archived = false } = options;
    const skip = (page - 1) * limit;

    const where: any = { userId, archived };

    if (tagId) {
      where.tags = { some: { tagId } };
    }

    const [data, total] = await Promise.all([
      this.prisma.note.findMany({
        where,
        include: {
          tags: { include: { tag: true } },
          reminders: {
            where: { status: 'PENDING' },
            orderBy: { remindAt: 'asc' },
            take: 1,
          },
        },
        orderBy: { updatedAt: 'desc' },
        skip,
        take: limit,
      }),
      this.prisma.note.count({ where }),
    ]);

    return {
      data,
      total,
      page,
      limit,
      totalPages: Math.ceil(total / limit),
    };
  }

  async findOne(userId: string, id: string) {
    const note = await this.prisma.note.findFirst({
      where: { id, userId },
      include: {
        tags: { include: { tag: true } },
        reminders: { orderBy: { remindAt: 'asc' } },
      },
    });

    if (!note) {
      throw new NotFoundException('Note not found');
    }

    return note;
  }

  async update(userId: string, id: string, dto: UpdateNoteDto) {
    // Verify ownership
    await this.findOne(userId, id);

    return this.prisma.note.update({
      where: { id },
      data: dto,
      include: {
        tags: { include: { tag: true } },
        reminders: true,
      },
    });
  }

  async remove(userId: string, id: string) {
    // Verify ownership
    await this.findOne(userId, id);

    return this.prisma.note.delete({ where: { id } });
  }
}
