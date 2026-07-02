import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  const configService = app.get(ConfigService);
  const port = configService.get<number>('PORT', 3000);

  // Global validation pipe
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
      transformOptions: {
        enableImplicitConversion: true,
      },
    }),
  );

  // CORS configuration
  const origin = configService.get<string>('CORS_ORIGIN', 'http://localhost:5173');
  app.enableCors({
    origin: [origin, /\.onrender\.com$/], // Allow your specific origin OR any render domain
    methods: ['GET', 'POST', 'PATCH', 'DELETE', 'OPTIONS'],
    credentials: true,
  });

  // Global prefix
  app.setGlobalPrefix('api', {
    exclude: ['health'],
  });

  // Root route for simple verification
  app.getHttpAdapter().get('/', (req, res) => {
    res.send('SmartNotes API is running');
  });

  await app.listen(port, '0.0.0.0');
  console.log(`🚀 SmartNotes API running on http://localhost:${port}`);
}

bootstrap();
