import {
  Injectable,
  CanActivate,
  ExecutionContext,
  UnauthorizedException,
} from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { PrismaService } from '../prisma/prisma.service';

/**
 * Auth Guard - Stubbed for development
 *
 * In development mode (NODE_ENV !== 'production'), this guard
 * auto-authenticates as a dev user, allowing local development
 * without Auth0 credentials.
 *
 * In production, it validates Auth0 JWT tokens.
 * TODO: Implement real Auth0 JWT validation for production.
 */
@Injectable()
export class AuthGuard implements CanActivate {
  private readonly isDev: boolean;

  constructor(
    private readonly configService: ConfigService,
    private readonly prisma: PrismaService,
  ) {
    this.isDev =
      this.configService.get<string>('NODE_ENV', 'development') !== 'production';
  }

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest();

    if (this.isDev) {
      // Dev bypass: auto-create/use a test user
      const devUser = await this.getOrCreateDevUser();
      request.user = devUser;
      return true;
    }

    // Production: validate Auth0 token
    const authHeader = request.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      throw new UnauthorizedException('Missing or invalid authorization header');
    }

    // TODO: Validate JWT token with Auth0
    // For now, reject all requests in production without valid setup
    throw new UnauthorizedException('Auth0 is not configured yet');
  }

  private async getOrCreateDevUser() {
    const devEmail = 'dev@smartnotes.local';

    let user = await this.prisma.user.findUnique({
      where: { email: devEmail },
    });

    if (!user) {
      user = await this.prisma.user.create({
        data: {
          email: devEmail,
          name: 'Dev User',
          authProviderId: 'dev-local-001',
        },
      });
      console.log('🔧 Created dev user:', devEmail);
    }

    return user;
  }
}
