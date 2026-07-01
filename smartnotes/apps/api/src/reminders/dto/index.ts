import { IsString, IsOptional, IsDateString, IsEnum } from 'class-validator';

export enum DeliveryChannelDto {
  PUSH = 'PUSH',
  EMAIL = 'EMAIL',
}

export class CreateReminderDto {
  @IsDateString()
  remindAt: string;

  @IsOptional()
  @IsEnum(DeliveryChannelDto)
  deliveryChannel?: DeliveryChannelDto;
}
