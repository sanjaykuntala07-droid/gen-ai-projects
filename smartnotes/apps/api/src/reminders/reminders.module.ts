import { Module } from '@nestjs/common';
import { ScheduleModule } from '@nestjs/schedule';
import { RemindersController } from './reminders.controller';
import { RemindersService } from './reminders.service';
import { RemindersProcessor } from './reminders.processor';
import { AuthModule } from '../auth/auth.module';

@Module({
  imports: [AuthModule, ScheduleModule.forRoot()],
  controllers: [RemindersController],
  providers: [RemindersService, RemindersProcessor],
  exports: [RemindersService],
})
export class RemindersModule {}
