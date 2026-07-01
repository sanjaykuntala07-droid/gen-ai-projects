import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { CreateReminderDto } from './dto';

@Injectable()
export class RemindersService {
  constructor(private readonly prisma: PrismaService) {}

  async create(userId: string, noteId: string, dto: CreateReminderDto) {
    // Verify note belongs to user
    const note = await this.prisma.note.findFirst({
      where: { id: noteId, userId },
    });

    if (!note) {
      throw new NotFoundException('Note not found');
    }

    return this.prisma.reminder.create({
      data: {
        noteId,
        remindAt: new Date(dto.remindAt),
        deliveryChannel: dto.deliveryChannel || 'EMAIL',
      },
      include: { note: true },
    });
  }

  async findUpcoming(userId: string, limit = 5) {
    return this.prisma.reminder.findMany({
      where: {
        status: 'PENDING',
        note: { userId },
        remindAt: { gte: new Date() },
      },
      include: {
        note: { select: { id: true, title: true } },
      },
      orderBy: { remindAt: 'asc' },
      take: limit,
    });
  }

  async remove(userId: string, id: string) {
    const reminder = await this.prisma.reminder.findFirst({
      where: { id, note: { userId } },
    });

    if (!reminder) {
      throw new NotFoundException('Reminder not found');
    }

    return this.prisma.reminder.delete({ where: { id } });
  }

  async findDueReminders() {
    return this.prisma.reminder.findMany({
      where: {
        status: 'PENDING',
        remindAt: { lte: new Date() },
      },
      include: {
        note: {
          include: { user: true },
        },
      },
    });
  }

  async markAsSent(id: string) {
    return this.prisma.reminder.update({
      where: { id },
      data: { status: 'SENT' },
    });
  }
}
