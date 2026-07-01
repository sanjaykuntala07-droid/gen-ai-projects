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
} from '@nestjs/common';
import { SharingService } from './sharing.service';
import { AuthGuard } from '../auth/auth.guard';
import { CurrentUser } from '../auth/user.decorator';

@Controller()
export class SharingController {
  constructor(private readonly sharingService: SharingService) {}

  // Authenticated: Create a share link
  @Post('notes/:noteId/share')
  @UseGuards(AuthGuard)
  createShareLink(
    @CurrentUser() user: any,
    @Param('noteId') noteId: string,
    @Body() body: { permission: 'VIEW' | 'EDIT'; expiresAt?: string },
  ) {
    return this.sharingService.createShareLink(user.id, noteId, body.permission, body.expiresAt);
  }

  // Authenticated: List share links
  @Get('notes/:noteId/shares')
  @UseGuards(AuthGuard)
  listShares(
    @CurrentUser() user: any,
    @Param('noteId') noteId: string,
  ) {
    return this.sharingService.listShares(user.id, noteId);
  }

  // Authenticated: Revoke a share link
  @Delete('notes/:noteId/share/:shareId')
  @UseGuards(AuthGuard)
  revokeShare(
    @CurrentUser() user: any,
    @Param('noteId') noteId: string,
    @Param('shareId') shareId: string,
  ) {
    return this.sharingService.revokeShare(user.id, noteId, shareId);
  }

  // Public: Get shared note by token
  @Get('shared/:token')
  getSharedNote(@Param('token') token: string) {
    return this.sharingService.getSharedNote(token);
  }

  // Public: Update shared note by token (service validates permission)
  @Patch('shared/:token')
  updateSharedNote(
    @Param('token') token: string,
    @Body() body: { title?: string; content?: string },
  ) {
    return this.sharingService.updateSharedNote(token, body.title, body.content);
  }
}
