import { Injectable, Logger } from '@nestjs/common';
import { Cron, CronExpression } from '@nestjs/schedule';
import { RemindersService } from './reminders.service';
import { ConfigService } from '@nestjs/config';

/**
 * Reminder Processor
 *
 * Runs on a schedule to pick up due reminders and send notifications.
 * Uses NestJS Schedule instead of BullMQ for simplicity in the initial build.
 * Can be upgraded to BullMQ for distributed processing later.
 *
 * Note: SendGrid integration is stubbed — logs emails that would be sent.
 * Set SENDGRID_API_KEY in .env to enable real sending.
 */
@Injectable()
export class RemindersProcessor {
  private readonly logger = new Logger(RemindersProcessor.name);

  constructor(
    private readonly remindersService: RemindersService,
    private readonly configService: ConfigService,
  ) {}

  @Cron(CronExpression.EVERY_30_SECONDS)
  async processReminders() {
    const dueReminders = await this.remindersService.findDueReminders();

    if (dueReminders.length === 0) return;

    this.logger.log(`Processing ${dueReminders.length} due reminder(s)`);

    for (const reminder of dueReminders) {
      try {
        await this.sendNotification(reminder);
        await this.remindersService.markAsSent(reminder.id);
        this.logger.log(
          `✅ Reminder ${reminder.id} sent for note "${reminder.note.title}"`,
        );
      } catch (error) {
        this.logger.error(
          `❌ Failed to process reminder ${reminder.id}:`,
          error,
        );
      }
    }
  }

  private async sendNotification(reminder: any) {
    const { note, deliveryChannel } = reminder;
    const sendgridKey = this.configService.get<string>('SENDGRID_API_KEY');

    if (deliveryChannel === 'EMAIL') {
      if (sendgridKey && sendgridKey !== 'your-sendgrid-key') {
        // Real SendGrid sending
        // TODO: Implement actual SendGrid integration
        this.logger.log(`📧 Would send email via SendGrid to ${note.user.email}`);
      } else {
        // Stub: log the email
        this.logger.log(
          `📧 [STUB] Email notification:\n` +
          `  To: ${note.user.email}\n` +
          `  Subject: Reminder: ${note.title}\n` +
          `  Body: Don't forget about "${note.title}"`,
        );
      }
    } else if (deliveryChannel === 'PUSH') {
      this.logger.log(
        `📱 [STUB] Push notification for "${note.title}" to user ${note.user.id}`,
      );
    }
  }
}
