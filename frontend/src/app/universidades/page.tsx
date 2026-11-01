import type { Metadata } from "next";
import Link from "next/link";
import { ArrowUpRight, Compass, GraduationCap, MessagesSquare, Sprout } from "lucide-react";
import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "Para universidades",
  description: "Nexo Académico conecta ideas, talento y oportunidades para formar equipos universitarios. Conoce nuestra propuesta de piloto.",
};

export default function UniversitiesPage() {
  return (
    <div className={styles.page}>
      <section className={styles.hero} aria-labelledby="university-title">
        <div>
          <p className={styles.eyebrow}>NEXO ACADÉMICO / PARA UNIVERSIDADES</p>
          <h1 id="university-title">El próximo gran equipo empieza en tu campus.</h1>
          <p className={styles.intro}>Conectamos estudiantes, ideas y oportunidades para que los proyectos universitarios encuentren con quién avanzar.</p>
          <div className={styles.actions}>
            <Link href="/" className={styles.primary}>Explorar la plataforma <ArrowUpRight size={18} /></Link>
            <a href="#piloto" className={styles.secondary}>Conocer el piloto</a>
          </div>
          <p className={styles.caption}>MVP funcional · Propuesta de piloto universitario</p>
        </div>
        <div className={styles.path} aria-label="Recorrido de colaboración">
          <span className={styles.pathLabel}>DE LA IDEA AL EQUIPO</span>
          <div><Sprout size={24} /><span><strong>Una idea con propósito</strong><small>Publica el reto y los roles que buscas.</small></span></div>
          <div><Compass size={24} /><span><strong>Talento que se encuentra</strong><small>Descubre proyectos por intereses y universidad.</small></span></div>
          <div><MessagesSquare size={24} /><span><strong>Un primer paso juntos</strong><small>Postúlate, conversa y acuerda la colaboración.</small></span></div>
          <p>Investigación · Tecnología · Innovación</p>
        </div>
      </section>

      <section className={styles.section} aria-labelledby="purpose-title">
        <p className="eyebrow">EL PUNTO DE PARTIDA</p>
        <h2 id="purpose-title">Hay ideas que necesitan algo más que un grupo de clase.</h2>
        <p className={styles.lead}>Nexo propone un lugar común para descubrir qué se está construyendo, qué habilidades hacen falta y cómo dar el primer paso para colaborar.</p>
        <div className={styles.cards}>
          <article><span>01 / ESTUDIANTES</span><h3>Encuentra dónde aportar.</h3><p>Explora proyectos, presenta tus habilidades y envía una solicitud con contexto.</p></article>
          <article><span>02 / EQUIPOS</span><h3>Dale visibilidad a tu idea.</h3><p>Publica los roles que necesitas, revisa postulaciones y conversa en privado.</p></article>
          <article><span>03 / COMUNIDAD ACADÉMICA</span><h3>Acerca las oportunidades.</h3><p>Consulta eventos y convocatorias con sus fechas y enlaces oficiales.</p></article>
        </div>
      </section>

      <section className={styles.pilot} id="piloto" aria-labelledby="pilot-title">
        <div><GraduationCap size={32} /><p className="eyebrow">PROPUESTA DE COLABORACIÓN</p><h2 id="pilot-title">Empecemos con un piloto de 8 semanas.</h2><p>Una facultad o semillero, un responsable institucional y una comunidad inicial. Un alcance pequeño para aprender con evidencia.</p><a href="#acuerdo" className="button button-primary">Ver qué necesitamos acordar</a></div>
        <ol>
          <li><span>SEMANAS 1–2</span><h3>Preparar la comunidad</h3><p>Acordar objetivos, participantes, dominios institucionales y acompañamiento.</p></li>
          <li><span>SEMANAS 3–6</span><h3>Activar las conexiones</h3><p>Publicar proyectos, invitar estudiantes y acompañar las primeras solicitudes.</p></li>
          <li><span>SEMANAS 7–8</span><h3>Evaluar y decidir</h3><p>Revisar participación, solicitudes aceptadas y aprendizajes con los equipos.</p></li>
        </ol>
      </section>

      <section className={styles.section} aria-labelledby="evidence-title">
        <p className="eyebrow">UN PILOTO CON PREGUNTAS CONCRETAS</p>
        <h2 id="evidence-title">Medir conexiones, aprender de las personas.</h2>
        <div className={styles.cards}>
          <article><h3>¿Se activa la comunidad?</h3><p>Participantes que publican un proyecto o envían una solicitud sobre el total de participantes registrados.</p></article>
          <article><h3>¿Se forman conexiones?</h3><p>Proyectos que reciben al menos una solicitud aceptada y tiempo hasta la primera postulación.</p></article>
          <article><h3>¿Vale la pena continuar?</h3><p>Entrevistas de cierre con estudiantes y responsables para entender utilidad, fricción y continuidad.</p></article>
        </div>
        <p className="muted small">Son métricas propuestas para el piloto; todavía no representan resultados ni un panel de analítica disponible.</p>
      </section>

      <section className={styles.section} aria-labelledby="questions-title">
        <h2 id="questions-title">Antes de empezar</h2>
        <details><summary>¿Qué podemos probar hoy?</summary><p>Perfiles, publicación y búsqueda de proyectos, solicitudes con aceptación o rechazo, notificaciones, conversaciones privadas y directorio de eventos. La participación requiere una cuenta con correo verificado.</p></details>
        <details><summary>¿Qué falta para abrir un piloto real?</summary><p>Configurar y validar el envío real de correo institucional, preparar el entorno operativo y acordar soporte y tratamiento de datos con la universidad. El MVP actual permite una demostración local controlada.</p></details>
        <details><summary>¿Cómo se sostendría Nexo?</summary><p>La hipótesis es una suscripción institucional con acompañamiento de activación, manteniendo el acceso de estudiantes dentro del convenio. Precio, alcance y disposición de pago deben validarse; no hay una oferta comercial cerrada.</p></details>
        <details><summary>¿Ya hay universidades asociadas?</summary><p>Esta es una propuesta para iniciar conversaciones. No anunciamos alianzas, usuarios activos ni resultados que todavía no estén validados.</p></details>
      </section>

      <section className={styles.closing} id="acuerdo">
        <p className="eyebrow">EL SIGUIENTE PASO</p><h2>Una comunidad. Un reto compartido. Un primer piloto.</h2><p>Proponemos una reunión para definir la facultad participante, el responsable, los objetivos y las condiciones de puesta en marcha. Explora el producto antes de acordar el alcance.</p>
        <Link href="/" className="button button-primary">Ver proyectos</Link>{" "}<Link href="/eventos" className="button button-secondary">Explorar oportunidades</Link>
      </section>
    </div>
  );
}
