import { IsString, IsOptional, MaxLength, MinLength, Matches } from 'class-validator';

export class CreateTagDto {
  @IsString()
  @MinLength(1)
  @MaxLength(50)
  name: string;

  @IsString()
  @Matches(/^#[0-9a-fA-F]{6}$/, { message: 'Color must be a valid hex color (e.g., #ff0000)' })
  color: string;
}
