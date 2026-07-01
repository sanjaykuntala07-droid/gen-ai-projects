import { Controller, Get, Query, UseGuards } from '@nestjs/common';
import { SearchService } from './search.service';
import { AuthGuard } from '../auth/auth.guard';
import { CurrentUser } from '../auth/user.decorator';

@Controller('notes/search')
@UseGuards(AuthGuard)
export class SearchController {
  constructor(private readonly searchService: SearchService) {}

  @Get()
  search(
    @CurrentUser() user: any,
    @Query('q') query: string,
    @Query('limit') limit?: number,
  ) {
    return this.searchService.search(user.id, query, limit);
  }
}
