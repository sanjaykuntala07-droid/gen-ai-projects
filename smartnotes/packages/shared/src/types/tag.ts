export interface Tag {
  id: string;
  userId: string;
  name: string;
  color: string;
}

export interface CreateTagDto {
  name: string;
  color: string;
}
