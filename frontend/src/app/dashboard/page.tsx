"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getProducts, Product, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

export default function Dashboard() {
  const [products, setProducts] = useState<Product[]>([]);
  const [error, setError] = useState("");
  const { token, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (token === null) return;
    getProducts()
      .then(setProducts)
      .catch((err) => {
        if (err instanceof ApiError && err.status === 401) {
          logout();
          router.push("/");
        } else {
          setError("Failed to load inventory");
        }
      });
  }, [token, logout, router]);

  if (token === null) {
    router.push("/");
    return null;
  }

  return (
    <main className="mx-auto max-w-3xl p-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-xl font-semibold">Inventory</h1>
        <button onClick={() => { logout(); router.push("/"); }} className="text-sm text-gray-500">
          Log out
        </button>
      </div>
      {error && <p className="text-red-600">{error}</p>}
      <table className="w-full text-left">
        <thead>
          <tr className="border-b text-sm text-gray-500">
            <th className="py-2">Product</th>
            <th>Price</th>
            <th>Stock</th>
          </tr>
        </thead>
        <tbody>
          {products.map((p) => (
            <tr key={p.id} className="border-b">
              <td className="py-2">{p.name}</td>
              <td>${p.price}</td>
              <td className={p.stock_qty <= p.low_stock_at ? "font-semibold text-red-600" : ""}>
                {p.stock_qty}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}