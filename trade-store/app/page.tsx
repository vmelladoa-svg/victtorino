import { PRODUCTS } from "@/lib/products";
import { countByCategory } from "@/lib/categories";
import { TopBar } from "@/components/TopBar";
import { Header } from "@/components/Header";
import { Hero } from "@/components/Hero";
import { TrustStrip } from "@/components/TrustStrip";
import { CategoryGrid } from "@/components/CategoryGrid";
import { PromoBanners } from "@/components/PromoBanners";
import { BestSellers } from "@/components/BestSellers";
import { OffersSection } from "@/components/OffersSection";
import { Catalog } from "@/components/Catalog";
import { ProSection } from "@/components/ProSection";
import { DespachoSection } from "@/components/DespachoSection";
import { InstallSection } from "@/components/InstallSection";
import { AmbientGallery } from "@/components/AmbientGallery";
import { HowToBuy } from "@/components/HowToBuy";
import { About } from "@/components/About";
import { Testimonials } from "@/components/Testimonials";
import { Faq } from "@/components/Faq";
import { Newsletter } from "@/components/Newsletter";
import { CtaBand } from "@/components/CtaBand";
import { Footer } from "@/components/Footer";

export default function HomePage() {
  const counts = countByCategory(PRODUCTS);
  return (
    <>
      <TopBar />
      <Header />
      <main>
        <Hero productCount={PRODUCTS.length} />
        <TrustStrip />
        <CategoryGrid counts={counts} />
        <PromoBanners />
        <BestSellers products={PRODUCTS} />
        <OffersSection products={PRODUCTS} />
        <Catalog products={PRODUCTS} />
        <ProSection />
        <DespachoSection />
        <InstallSection />
        <AmbientGallery />
        <HowToBuy />
        <About />
        <Testimonials />
        <Faq />
        <Newsletter />
        <CtaBand />
      </main>
      <Footer />
    </>
  );
}
