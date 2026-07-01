import { Module } from '@nestjs/common';
import { NotesController } from './notes.controller';
import { NotesService } from './notes.service';
import { StatsController } from './stats.controller';
import { StatsService } from './stats.service';
import { ExportService } from './export.service';
import { ImportService } from './import.service';
import { AuthModule } from '../auth/auth.module';
import { SearchModule } from '../search/search.module';

@Module({
  imports: [AuthModule, SearchModule],
  controllers: [NotesController, StatsController],
  providers: [NotesService, StatsService, ExportService, ImportService],
  exports: [NotesService, ExportService, ImportService],
})
export class NotesModule {}
