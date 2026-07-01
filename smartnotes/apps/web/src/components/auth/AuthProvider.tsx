import { createContext, useContext, useState, useCallback, useEffect } from 'react';

interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  login: async () => {},
  signup: async () => {},
  logout: () => {},
});

export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // On mount, check for existing session
  useEffect(() => {
    const stored = localStorage.getItem('smartnotes_user');
    if (stored) {
      try {
        setUser(JSON.parse(stored));
      } catch {
        localStorage.removeItem('smartnotes_user');
      }
    }
    setIsLoading(false);
  }, []);

  const login = useCallback(async (email: string, _password: string) => {
    // In dev/stub mode: simulate auth with mock user
    // The backend auth guard auto-authenticates in dev mode anyway
    await new Promise((resolve) => setTimeout(resolve, 800)); // simulate network delay

    const mockUser: User = {
      id: 'dev-local-001',
      email,
      name: email.split('@')[0].replace(/[._-]/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
      avatar: undefined,
    };

    localStorage.setItem('smartnotes_user', JSON.stringify(mockUser));
    setUser(mockUser);
  }, []);

  const signup = useCallback(async (name: string, email: string, _password: string) => {
    await new Promise((resolve) => setTimeout(resolve, 800));

    const mockUser: User = {
      id: 'dev-local-001',
      email,
      name,
      avatar: undefined,
    };

    localStorage.setItem('smartnotes_user', JSON.stringify(mockUser));
    setUser(mockUser);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('smartnotes_user');
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        signup,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
