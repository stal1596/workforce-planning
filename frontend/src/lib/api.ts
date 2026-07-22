const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, body.detail ?? "Request failed");
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export interface Product {
  id: number;
  name: string;
  price: string;
  stock_qty: number;
  low_stock_at: number;
}

export async function login(email: string, password: string): Promise<{ access_token: string }> {
  const body = new URLSearchParams({ username: email, password });
  return request("/api/auth/login", { method: "POST", body });
}

export async function getProducts(): Promise<Product[]> {
  return request("/api/products");
}

export async function recordSale(productId: number, qty: number): Promise<unknown> {
  return request("/api/sales", {
    method: "POST",
    body: JSON.stringify({ product_id: productId, qty }),
  });
}