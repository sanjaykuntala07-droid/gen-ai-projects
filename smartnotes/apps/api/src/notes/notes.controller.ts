import {
  Controller,
  Get,
  Post,
  Patch,
  Delete,
  Body,
  Param,
  Query,
  UseGuards,
  Res,
  UseInterceptors,
  UploadedFiles,
} from '@nestjs/common';
import { FilesInterceptor } from '@nestjs/platform-express';
import { Response } from 'express';
import { NotesService } from './notes.service';
import { CreateNoteDto, UpdateNoteDto } from './dto';
import { AuthGuard } from '../auth/auth.guard';
import { CurrentUser } from '../auth/user.decorator';
import { SearchService } from '../search/search.service';
import { ExportService } from './export.service';
import { ImportService } from './import.service';

@Controller('notes')
@UseGuards(AuthGuard)
export class NotesController {
  constructor(
    private readonly notesService: NotesService,
    private readonly searchService: SearchService,
    private readonly exportService: ExportService,
    private readonly importService: ImportService,
  ) {}

  @Get('search')
  search(
    @CurrentUser() user: any,
    @Query('q') query: string,
    @Query('limit') limit?: number,
  ) {
    return this.searchService.search(user.id, query, limit);
  }

  @Get('export/all')
  async exportAll(
    @CurrentUser() user: any,
    @Res() res: Response,
  ) {
    const buffer = await this.exportService.exportAllNotesToZip(user.id);
    res.setHeader('Content-Type', 'application/zip');
    res.setHeader('Content-Disposition', 'attachment; filename="smartnotes_export.zip"');
    res.send(buffer);
  }

  @Get(':id/export')
  async exportOne(
    @CurrentUser() user: any,
    @Param('id') id: string,
    @Res() res: Response,
  ) {
    const { title, markdown } = await this.exportService.exportNoteToMarkdown(user.id, id);
    const safeTitle = title.replace(/[^a-zA-Z0-9]/g, '_');
    res.setHeader('Content-Type', 'text/markdown');
    res.setHeader('Content-Disposition', `attachment; filename="${safeTitle}.md"`);
    res.send(markdown);
  }

  @Post('import')
  @UseInterceptors(FilesInterceptor('files'))
  async importNotes(
    @CurrentUser() user: any,
    @UploadedFiles() files: any[],
  ) {
    const importedNotes = [];
    if (files && files.length > 0) {
      for (const file of files) {
        const content = file.buffer.toString('utf-8');
        const note = await this.importService.importMarkdown(user.id, file.originalname, content);
        importedNotes.push(note);
      }
    }
    return importedNotes;
  }

  @Post()
  create(@CurrentUser() user: any, @Body() dto: CreateNoteDto) {
    return this.notesService.create(user.id, dto);
  }

  @Get()
  findAll(
    @CurrentUser() user: any,
    @Query('page') page?: number,
    @Query('limit') limit?: number,
    @Query('tagId') tagId?: string,
    @Query('archived') archived?: boolean,
  ) {
    return this.notesService.findAll(user.id, { page, limit, tagId, archived });
  }

  @Get(':id')
  findOne(@CurrentUser() user: any, @Param('id') id: string) {
    return this.notesService.findOne(user.id, id);
  }

  @Patch(':id')
  update(
    @CurrentUser() user: any,
    @Param('id') id: string,
    @Body() dto: UpdateNoteDto,
  ) {
    return this.notesService.update(user.id, id, dto);
  }

  @Delete(':id')
  remove(@CurrentUser() user: any, @Param('id') id: string) {
    return this.notesService.remove(user.id, id);
  }
}
