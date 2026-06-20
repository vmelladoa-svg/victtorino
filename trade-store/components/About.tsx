import { Icon, ICONS } from "./Icon";

export function About() {
  return (
    <section className="block soft" id="nosotros">
      <div className="wrap about-grid">
        <div>
          <span className="sec-kicker">Nosotros</span>
          <h2>Una tienda pensada para que equipar tu hogar sea simple</h2>
          <p>
            En <strong>Trade</strong> creemos que renovar el baño o la cocina no debería ser
            complicado ni caro. Por eso reunimos en un solo lugar grifería, espejos, duchas,
            sanitarios y accesorios de instalación, seleccionados por su calidad y respaldados
            con garantía.
          </p>
          <p>
            Trabajamos con materiales durables — acero inoxidable, cerámica y acabados
            cromados — y mantenemos precios actualizados y transparentes, sin sorpresas.
          </p>
        </div>
        <div className="about-points">
          <div className="about-point">
            <Icon d={ICONS.check} size={22} />
            <div>
              <b>Selección con criterio</b>
              <span>
                Cada producto pasa por revisión de materiales y terminaciones antes de entrar
                al catálogo.
              </span>
            </div>
          </div>
          <div className="about-point">
            <Icon d={ICONS.shield} size={22} />
            <div>
              <b>Garantía real de 6 meses</b>
              <span>
                Si un producto falla por defecto de fábrica, lo cambiamos sin trámites eternos.
              </span>
            </div>
          </div>
          <div className="about-point">
            <Icon d={ICONS.chat} size={22} />
            <div>
              <b>Asesoría antes de comprar</b>
              <span>
                ¿Dudas de medidas o compatibilidad? Escríbenos por WhatsApp y te orientamos.
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
