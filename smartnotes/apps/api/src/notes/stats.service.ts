import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';

@Injectable()
export class StatsService {
  constructor(private readonly prisma: PrismaService) {}

  async getUserStats(userId: string) {
    const [totalNotes, archivedNotes, totalTags, totalReminders] = await Promise.all([
      this.prisma.note.count({ where: { userId, archived: false } }),
      this.prisma.note.count({ where: { userId, archived: true } }),
      this.prisma.tag.count({ where: { userId } }),
      this.prisma.reminder.count({
        where: {
          note: { userId },
          status: 'PENDING',
        },
      }),
    ]);

    return {
      totalNotes,
      archivedNotes,
      totalTags,
      totalReminders,
    };
  }

  async getRecentActivity(userId: string, limit = 5) {
    return this.prisma.note.findMany({
      where: { userId },
      orderBy: { updatedAt: 'desc' },
      take: limit,
      include: {
        tags: {
          include: {
            tag: true,
          },
        },
      },
    });
  }

  async getTagDistribution(userId: string) {
    const tags = await this.prisma.tag.findMany({
      where: { userId },
      select: {
        id: true,
        name: true,
        color: true,
        _count: {
          select: { notes: true },
        },
      },
    });

    return tags.map((t) => ({
      id: t.id,
      name: t.name,
      color: t.color,
      count: t._count.notes,
    }));
  }

  async getCreationTrend(userId: string, days = 7) {
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days + 1);
    startDate.setHours(0, 0, 0, 0);

    const notes = await this.prisma.note.findMany({
      where: {
        userId,
        createdAt: { gte: startDate },
      },
      select: { createdAt: true },
    });

    // Initialize trend map for the last N days
    const trendMap: { [date: string]: number } = {};
    for (let i = 0; i < days; i++) {
      const d = new Date(startDate);
      d.setDate(startDate.getDate() + i);
      const dateStr = d.toISOString().split('T')[0];
      trendMap[dateStr] = 0;
    }

    // Populate counts
    notes.forEach((note) => {
      const dateStr = note.createdAt.toISOString().split('T')[0];
      if (trendMap[dateStr] !== undefined) {
        trendMap[dateStr]++;
      }
    });

    // Convert to sorted array
    return Object.keys(trendMap).sort().map((date) => ({
      date,
      count: trendMap[date],
    }));
  }
}
