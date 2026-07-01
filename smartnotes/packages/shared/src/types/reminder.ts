export enum ReminderStatus {
  PENDING = 'PENDING',
  SENT = 'SENT',
  DISMISSED = 'DISMISSED',
}

export enum DeliveryChannel {
  PUSH = 'PUSH',
  EMAIL = 'EMAIL',
}

export interface Reminder {
  id: string;
  noteId: string;
  remindAt: string;
  status: ReminderStatus;
  deliveryChannel: DeliveryChannel;
}

export interface CreateReminderDto {
  remindAt: string;
  deliveryChannel?: DeliveryChannel;
}
