import { Controller, Get, Query, UseGuards } from '@nestjs/common';
import { StatsService } from './stats.service';
import { AuthGuard } from '../auth/auth.guard';
import { CurrentUser } from '../auth/user.decorator';

@Controller('stats')
@UseGuards(AuthGuard)
export class StatsController {
  constructor(private readonly statsService: StatsService) {}

  @Get('overview')
  getOverview(@CurrentUser() user: any) {
    return this.statsService.getUserStats(user.id);
  }

  @Get('activity')
  getActivity(
    @CurrentUser() user: any,
    @Query('limit') limit?: number,
  ) {
    return this.statsService.getRecentActivity(user.id, limit);
  }

  @Get('tags')
  getTags(@CurrentUser() user: any) {
    return this.statsService.getTagDistribution(user.id);
  }

  @Get('trend')
  getTrend(
    @CurrentUser() user: any,
    @Query('days') days?: number,
  ) {
    return this.statsService.getCreationTrend(user.id, days);
  }
}
