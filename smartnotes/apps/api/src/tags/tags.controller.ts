import {
  Controller,
  Get,
  Post,
  Delete,
  Body,
  Param,
  UseGuards,
} from '@nestjs/common';
import { TagsService } from './tags.service';
import { CreateTagDto } from './dto';
import { AuthGuard } from '../auth/auth.guard';
import { CurrentUser } from '../auth/user.decorator';

@Controller('tags')
@UseGuards(AuthGuard)
export class TagsController {
  constructor(private readonly tagsService: TagsService) {}

  @Post()
  create(@CurrentUser() user: any, @Body() dto: CreateTagDto) {
    return this.tagsService.create(user.id, dto);
  }

  @Get()
  findAll(@CurrentUser() user: any) {
    return this.tagsService.findAll(user.id);
  }

  @Delete(':id')
  remove(@CurrentUser() user: any, @Param('id') id: string) {
    return this.tagsService.remove(user.id, id);
  }

  @Post(':noteId/tags/:tagId')
  attachTag(
    @CurrentUser() user: any,
    @Param('noteId') noteId: string,
    @Param('tagId') tagId: string,
  ) {
    return this.tagsService.attachTag(user.id, noteId, tagId);
  }

  @Delete(':noteId/tags/:tagId')
  detachTag(
    @CurrentUser() user: any,
    @Param('noteId') noteId: string,
    @Param('tagId') tagId: string,
  ) {
    return this.tagsService.detachTag(user.id, noteId, tagId);
  }
}
