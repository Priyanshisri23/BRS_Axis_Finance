export interface User {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  username: string;
  is_active: boolean;
  is_superuser: boolean;
  created_by?: {
    id: number | null;
    full_name: string | null;
  } | null;
  updated_by?: {
    id: number | null;
    full_name: string | null;
  } | null;
  created_on: string | null;
  updated_on: string | null;
}