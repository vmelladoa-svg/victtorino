"use client";

import { BackToTop } from "./BackToTop";
import { MobileBar } from "./MobileBar";
import { CartDrawer } from "./CartDrawer";
import { CheckoutModal } from "./CheckoutModal";
import { ProductModal } from "./ProductModal";
import { ProModal } from "./ProModal";
import { AccountModal } from "./AccountModal";
import { TrackingModal } from "./TrackingModal";
import { InstallTermsModal } from "./InstallTermsModal";
import { Toast } from "./Toast";
import { WhatsAppFloat } from "./WhatsAppFloat";
import { WishlistDrawer } from "./WishlistDrawer";

/** Overlays y elementos flotantes globales que viven sobre toda la página. */
export function StoreChrome() {
  return (
    <>
      <WhatsAppFloat />
      <BackToTop />
      <MobileBar />
      <ProductModal />
      <CartDrawer />
      <WishlistDrawer />
      <CheckoutModal />
      <ProModal />
      <AccountModal />
      <TrackingModal />
      <InstallTermsModal />
      <Toast />
    </>
  );
}
