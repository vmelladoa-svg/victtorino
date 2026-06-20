"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import type { CartItem, Product } from "./types";
import { type ProAccount, tierForSpend } from "./pro";
import { DEFAULT_ZONE } from "./shipping";

const CART_KEY = "trade_cart_v1";
const WISH_KEY = "trade_wishlist_v1";
const PRO_KEY = "trade_pro_v1";
const USER_KEY = "trade_user_v1";
const ZONE_KEY = "trade_zone_v1";

export interface User {
  name: string;
  email: string;
}

interface StoreContextValue {
  // carrito
  cart: CartItem[];
  cartCount: number;
  addToCart: (p: Product) => void;
  setQty: (id: string, qty: number) => void;
  removeItem: (id: string) => void;
  clearCart: () => void;
  justAdded: string | null;
  // favoritos (wishlist)
  wishlist: string[];
  wishlistCount: number;
  toggleWishlist: (id: string) => void;
  isWished: (id: string) => boolean;
  wishlistOpen: boolean;
  openWishlist: () => void;
  closeWishlist: () => void;
  // Trade Pro
  pro: ProAccount | null;
  proDiscountPct: number;
  registerPro: (data: Omit<ProAccount, "spend">) => void;
  addProSpend: (amount: number) => void;
  proModalOpen: boolean;
  openProModal: () => void;
  closeProModal: () => void;
  // cuenta de usuario
  user: User | null;
  login: (email: string) => void;
  register: (name: string, email: string) => void;
  logout: () => void;
  accountOpen: boolean;
  openAccount: () => void;
  closeAccount: () => void;
  // seguimiento de pedido
  trackOpen: boolean;
  openTracking: () => void;
  closeTracking: () => void;
  // zona de despacho
  shipZone: string;
  setShipZone: (id: string) => void;
  // condiciones de instalación
  installTermsOpen: boolean;
  openInstallTerms: () => void;
  closeInstallTerms: () => void;
  // UI
  cartOpen: boolean;
  openCart: () => void;
  closeCart: () => void;
  checkoutOpen: boolean;
  openCheckout: () => void;
  closeCheckout: () => void;
  viewProduct: Product | null;
  setViewProduct: (p: Product | null) => void;
  toast: string | null;
  // catálogo
  activeCat: string;
  setActiveCat: (c: string) => void;
  pickCategory: (c: string) => void;
}

const StoreContext = createContext<StoreContextValue | null>(null);

export function useStore(): StoreContextValue {
  const ctx = useContext(StoreContext);
  if (!ctx) throw new Error("useStore debe usarse dentro de <StoreProvider>");
  return ctx;
}

export function StoreProvider({ children }: { children: React.ReactNode }) {
  const [cart, setCart] = useState<CartItem[]>([]);
  const [wishlist, setWishlist] = useState<string[]>([]);
  const [wishlistOpen, setWishlistOpen] = useState(false);
  const [pro, setPro] = useState<ProAccount | null>(null);
  const [proModalOpen, setProModalOpen] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [accountOpen, setAccountOpen] = useState(false);
  const [trackOpen, setTrackOpen] = useState(false);
  const [shipZone, setShipZone] = useState(DEFAULT_ZONE);
  const [installTermsOpen, setInstallTermsOpen] = useState(false);
  const [hydrated, setHydrated] = useState(false);
  const [cartOpen, setCartOpen] = useState(false);
  const [checkoutOpen, setCheckoutOpen] = useState(false);
  const [viewProduct, setViewProduct] = useState<Product | null>(null);
  const [activeCat, setActiveCat] = useState("Todos");
  const [justAdded, setJustAdded] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  const addedTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const toastTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // cargar carrito + favoritos desde localStorage al montar
  useEffect(() => {
    try {
      const raw = localStorage.getItem(CART_KEY);
      if (raw) setCart(JSON.parse(raw));
      const w = localStorage.getItem(WISH_KEY);
      if (w) setWishlist(JSON.parse(w));
      const pr = localStorage.getItem(PRO_KEY);
      if (pr) setPro(JSON.parse(pr));
      const u = localStorage.getItem(USER_KEY);
      if (u) setUser(JSON.parse(u));
      const z = localStorage.getItem(ZONE_KEY);
      if (z) setShipZone(z);
    } catch {
      /* ignore */
    }
    setHydrated(true);
  }, []);

  // persistir (solo después de hidratar para no pisar con [] inicial)
  useEffect(() => {
    if (!hydrated) return;
    localStorage.setItem(CART_KEY, JSON.stringify(cart));
  }, [cart, hydrated]);

  useEffect(() => {
    if (!hydrated) return;
    localStorage.setItem(WISH_KEY, JSON.stringify(wishlist));
  }, [wishlist, hydrated]);

  useEffect(() => {
    if (!hydrated) return;
    if (pro) localStorage.setItem(PRO_KEY, JSON.stringify(pro));
    else localStorage.removeItem(PRO_KEY);
  }, [pro, hydrated]);

  useEffect(() => {
    if (!hydrated) return;
    if (user) localStorage.setItem(USER_KEY, JSON.stringify(user));
    else localStorage.removeItem(USER_KEY);
  }, [user, hydrated]);

  useEffect(() => {
    if (!hydrated) return;
    localStorage.setItem(ZONE_KEY, shipZone);
  }, [shipZone, hydrated]);

  // con un overlay abierto: bloquear scroll del fondo (sin salto) + cerrar con Escape
  useEffect(() => {
    const anyOpen =
      cartOpen ||
      checkoutOpen ||
      wishlistOpen ||
      proModalOpen ||
      accountOpen ||
      trackOpen ||
      installTermsOpen ||
      !!viewProduct;
    if (!anyOpen) return;
    const sw = window.innerWidth - document.documentElement.clientWidth;
    const prevOverflow = document.body.style.overflow;
    const prevPad = document.body.style.paddingRight;
    document.body.style.overflow = "hidden";
    if (sw > 0) document.body.style.paddingRight = sw + "px";
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      if (installTermsOpen) setInstallTermsOpen(false);
      else if (proModalOpen) setProModalOpen(false);
      else if (accountOpen) setAccountOpen(false);
      else if (trackOpen) setTrackOpen(false);
      else if (checkoutOpen) setCheckoutOpen(false);
      else if (viewProduct) setViewProduct(null);
      else if (wishlistOpen) setWishlistOpen(false);
      else if (cartOpen) setCartOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => {
      document.body.style.overflow = prevOverflow;
      document.body.style.paddingRight = prevPad;
      window.removeEventListener("keydown", onKey);
    };
  }, [cartOpen, checkoutOpen, wishlistOpen, proModalOpen, accountOpen, trackOpen, installTermsOpen, viewProduct]);

  const cartCount = useMemo(() => cart.reduce((s, it) => s + it.qty, 0), [cart]);

  const toggleWishlist = useCallback((id: string) => {
    setWishlist((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  }, []);
  const isWished = useCallback((id: string) => wishlist.includes(id), [wishlist]);

  const registerPro = useCallback((data: Omit<ProAccount, "spend">) => {
    setPro({ ...data, spend: 0 });
  }, []);
  const addProSpend = useCallback((amount: number) => {
    setPro((prev) => (prev ? { ...prev, spend: prev.spend + amount } : prev));
  }, []);
  const proDiscountPct = pro ? tierForSpend(pro.spend).pct : 0;

  const login = useCallback((email: string) => {
    setUser({ name: email.split("@")[0], email });
  }, []);
  const register = useCallback((name: string, email: string) => {
    setUser({ name, email });
  }, []);
  const logout = useCallback(() => setUser(null), []);

  const addToCart = useCallback((p: Product) => {
    setCart((prev) => {
      const ex = prev.find((it) => it.id === p.id);
      if (ex) return prev.map((it) => (it.id === p.id ? { ...it, qty: it.qty + 1 } : it));
      return [...prev, { id: p.id, qty: 1 }];
    });
    setJustAdded(p.id);
    setToast(p.name + " agregado al carrito");
    if (addedTimer.current) clearTimeout(addedTimer.current);
    if (toastTimer.current) clearTimeout(toastTimer.current);
    addedTimer.current = setTimeout(() => setJustAdded(null), 1600);
    toastTimer.current = setTimeout(() => setToast(null), 2400);
  }, []);

  const removeItem = useCallback((id: string) => {
    setCart((prev) => prev.filter((it) => it.id !== id));
  }, []);

  const setQty = useCallback(
    (id: string, qty: number) => {
      if (qty <= 0) return removeItem(id);
      setCart((prev) => prev.map((it) => (it.id === id ? { ...it, qty } : it)));
    },
    [removeItem]
  );

  const clearCart = useCallback(() => setCart([]), []);

  const pickCategory = useCallback((cat: string) => {
    setActiveCat(cat);
    const el = document.getElementById("catalogo");
    if (el) {
      const y = el.getBoundingClientRect().top + window.scrollY - 80;
      window.scrollTo({ top: y, behavior: "smooth" });
    }
  }, []);

  const value: StoreContextValue = {
    cart,
    cartCount,
    addToCart,
    setQty,
    removeItem,
    clearCart,
    justAdded,
    wishlist,
    wishlistCount: wishlist.length,
    toggleWishlist,
    isWished,
    wishlistOpen,
    openWishlist: useCallback(() => setWishlistOpen(true), []),
    closeWishlist: useCallback(() => setWishlistOpen(false), []),
    pro,
    proDiscountPct,
    registerPro,
    addProSpend,
    proModalOpen,
    openProModal: useCallback(() => setProModalOpen(true), []),
    closeProModal: useCallback(() => setProModalOpen(false), []),
    user,
    login,
    register,
    logout,
    accountOpen,
    openAccount: useCallback(() => setAccountOpen(true), []),
    closeAccount: useCallback(() => setAccountOpen(false), []),
    trackOpen,
    openTracking: useCallback(() => setTrackOpen(true), []),
    closeTracking: useCallback(() => setTrackOpen(false), []),
    shipZone,
    setShipZone,
    installTermsOpen,
    openInstallTerms: useCallback(() => setInstallTermsOpen(true), []),
    closeInstallTerms: useCallback(() => setInstallTermsOpen(false), []),
    cartOpen,
    openCart: useCallback(() => setCartOpen(true), []),
    closeCart: useCallback(() => setCartOpen(false), []),
    checkoutOpen,
    openCheckout: useCallback(() => {
      setCartOpen(false);
      setCheckoutOpen(true);
    }, []),
    closeCheckout: useCallback(() => setCheckoutOpen(false), []),
    viewProduct,
    setViewProduct,
    toast,
    activeCat,
    setActiveCat,
    pickCategory,
  };

  return <StoreContext.Provider value={value}>{children}</StoreContext.Provider>;
}
