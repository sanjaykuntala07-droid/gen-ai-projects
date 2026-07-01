export interface User {
  id: string;
  email: string;
  name: string | null;
  authProviderId: string;
  createdAt: string;
}

export interface CreateUserDto {
  email: string;
  name?: string;
  authProviderId: string;
}
