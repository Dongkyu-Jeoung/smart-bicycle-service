import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { cartItemsCheck, updateCartItemsQty } from "../utils/cart.js";

export const useAuthStore = create(
  persist(
    (set, get) => ({
      userId: null,
      role: null,
      accessToken: null,
      isLogin: false,
      authChecked: true, // 로그인 상태를 로컬(localStorage)에서 바로 복구하므로 서버 확인 대기 불필요
      cartItems: [], // 로컬 장바구니: [{cid, pid, size, qty}]
      cartList: [], // 장바구니 리스트 공유 - Cart, Checkout 컴포넌트
      isUpdateFlag: false, // 장바구니 리스트 수량 변경

      login: ({ userId, role, accessToken, isLogin }) =>
        set({ userId, role, accessToken, isLogin, authChecked: true }),
      logout: () =>
        set({
          userId: null,
          role: null,
          accessToken: null,
          isLogin: false,
          authChecked: true,
        }),

      // 장바구니(로컬 데이터 기반)
      addCartItem: (cartItem) =>
        set((state) => ({ cartItems: cartItemsCheck(state.cartItems, cartItem) })),
      updateCartItemQty: (cid, type) =>
        set((state) => ({ cartItems: updateCartItemsQty(state.cartItems, cid, type) })),
      removeCartItem: (cid) =>
        set((state) => ({ cartItems: state.cartItems.filter((item) => item.cid !== cid) })),
      clearCartItems: () => set({ cartItems: [] }),

      setIsUpdateFlag: () =>
        set((state) => ({ isUpdateFlag: !state.isUpdateFlag })),
      setCartList: (cartList) => set(() => ({ cartList: cartList })),
    }),
    {
      name: "auth-storage",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        userId: state.userId,
        role: state.role,
        accessToken: state.accessToken,
        isLogin: state.isLogin,
        cartItems: state.cartItems,
      }),
    }
  )
);
