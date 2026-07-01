import {
  Controller,
  Post,
  Body,
  UseGuards,
  NotFoundException,
} from '@nestjs/common';
import { AiService } from './ai.service';
import { AuthGuard } from '../auth/auth.guard';
import { CurrentUser } from '../auth/user.decorator';
import { PrismaService } from '../prisma/prisma.service';

@Controller('ai')
@UseGuards(AuthGuard)
export class AiController {
  constructor(
    private readonly aiService: AiService,
    private readonly prisma: PrismaService,
  ) {}

  @Post('summarize')
  async summarize(
    @CurrentUser() user: any,
    @Body() body: { noteId: string },
  ) {
    const note = await this.getNote(user.id, body.noteId);
    const summary = await this.aiService.summarize(note.content);
    return { summary };
  }

  @Post('suggest-tags')
  async suggestTags(
    @CurrentUser() user: any,
    @Body() body: { noteId: string },
  ) {
    const note = await this.getNote(user.id, body.noteId);
    const existingTags = await this.prisma.tag.findMany({
      where: { userId: user.id },
      select: { name: true },
    });
    const tags = await this.aiService.suggestTags(
      note.content,
      existingTags.map((t) => t.name),
    );
    return { tags };
  }

  @Post('suggestions')
  async suggestions(
    @CurrentUser() user: any,
    @Body() body: { noteId: string },
  ) {
    const note = await this.getNote(user.id, body.noteId);
    const suggestions = await this.aiService.generateSuggestions(note.content);
    return { suggestions };
  }

  @Post('improve')
  async improve(
    @CurrentUser() user: any,
    @Body() body: { noteId: string },
  ) {
    const note = await this.getNote(user.id, body.noteId);
    const improved = await this.aiService.improveWriting(note.content);
    return { improved };
  }

  private async getNote(userId: string, noteId: string) {
    const note = await this.prisma.note.findFirst({
      where: { id: noteId, userId },
    });
    if (!note) {
      throw new NotFoundException('Note not found');
    }
    return note;
  }
}
