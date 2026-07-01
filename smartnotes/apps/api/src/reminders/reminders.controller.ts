import {
  Controller,
  Get,
  Post,
  Delete,
  Body,
  Param,
  Query,
  UseGuards,
} from '@nestjs/common';
import { RemindersService } from './reminders.service';
import { CreateReminderDto } from './dto';
import { AuthGuard } from '../auth/auth.guard';
import { CurrentUser } from '../auth/user.decorator';

@Controller()
@UseGuards(AuthGuard)
export class RemindersController {
  constructor(private readonly remindersService: RemindersService) {}

  @Post('notes/:noteId/reminders')
  create(
    @CurrentUser() user: any,
    @Param('noteId') noteId: string,
    @Body() dto: CreateReminderDto,
  ) {
    return this.remindersService.create(user.id, noteId, dto);
  }

  @Get('reminders/upcoming')
  findUpcoming(
    @CurrentUser() user: any,
    @Query('limit') limit?: number,
  ) {
    return this.remindersService.findUpcoming(user.id, limit);
  }

  @Delete('reminders/:id')
  remove(@CurrentUser() user: any, @Param('id') id: string) {
    return this.remindersService.remove(user.id, id);
  }
}
