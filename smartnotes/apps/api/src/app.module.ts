import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { ThrottlerModule } from '@nestjs/throttler';
import { HealthModule } from './health/health.module';
import { PrismaModule } from './prisma/prisma.module';
import { AuthModule } from './auth/auth.module';
import { NotesModule } from './notes/notes.module';
import { TagsModule } from './tags/tags.module';
import { RemindersModule } from './reminders/reminders.module';
import { SearchModule } from './search/search.module';
import { AiModule } from './ai/ai.module';
import { SharingModule } from './sharing/sharing.module';

@Module({
  imports: [
    // Config
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: ['.env', '../../.env'],
    }),

    // Rate limiting
    ThrottlerModule.forRoot([
      {
        name: 'short',
        ttl: 1000,
        limit: 10,
      },
      {
        name: 'medium',
        ttl: 60000,
        limit: 100,
      },
    ]),

    // Core modules
    PrismaModule,
    HealthModule,
    AuthModule,

    // Feature modules
    NotesModule,
    TagsModule,
    RemindersModule,
    SearchModule,
    AiModule,
    SharingModule,
  ],
})
export class AppModule {}
