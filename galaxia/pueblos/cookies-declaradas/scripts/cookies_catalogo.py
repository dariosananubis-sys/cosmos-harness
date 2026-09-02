#!/usr/bin/env python3
"""Catalogo unico de cookies: que es cada una, quien la pone y cuanto dura.

Lo comparten `legales-cookies-complianz.py` (rellena la ficha dentro del plugin)
y `legales-bloque-cookies.py` (escribe la tabla en las webs sin plugin que la
genere). Un solo sitio donde corregir un texto legal.
"""
import re

FUNCIONAL = "Funcional"
ESTADISTICAS = "Estadísticas (anónimas)"
MARKETING = "Marketing/seguimiento"

# patron de nombre -> (propia, purpose, cookieFunction, retention)
# El orden importa: se aplica el primer patron que encaje.
CATALOGO = [
    (r"^cmplz_", True, FUNCIONAL,
     "guardar el consentimiento de cookies elegido por el usuario y no volver a preguntarlo",
     "365 días"),
    (r"^wp-settings-time-", True, FUNCIONAL,
     "guardar la fecha de las preferencias de interfaz del usuario registrado", "1 año"),
    (r"^wp-settings-", True, FUNCIONAL,
     "guardar las preferencias de interfaz del usuario registrado", "1 año"),
    (r"^wordpress_logged_in", True, FUNCIONAL,
     "mantener la sesión iniciada del usuario registrado", "sesión"),
    (r"^wordpress_sec", True, FUNCIONAL,
     "autenticar de forma segura al usuario registrado en el área de administración", "sesión"),
    (r"^(wordpress_test_cookie|test)$", True, FUNCIONAL,
     "comprobar si el navegador acepta cookies", "sesión"),
    (r"^wp_lang", True, FUNCIONAL, "recordar el idioma elegido en la web", "sesión"),
    (r"^wpEmojiSettingsSupports", True, FUNCIONAL,
     "guardar si el navegador puede mostrar emojis", "sesión"),
    (r"^WP_DATA_USER", True, FUNCIONAL,
     "guardar datos de trabajo del usuario en el panel de administración", "sesión"),
    (r"^WP_PREFERENCES_USER", True, FUNCIONAL,
     "guardar las preferencias del usuario en el panel de administración", "1 año"),
    (r"^e_kit-elements-defaults", True, FUNCIONAL,
     "guardar los valores por defecto de los elementos del editor", "sesión"),
    (r"^e_document", True, FUNCIONAL,
     "guardar los ajustes globales de la plantilla del editor", "sesión"),
    (r"^e_globals", True, FUNCIONAL,
     "proporcionar funcionalidad entre páginas del editor", "sesión"),
    (r"^elementor$", True, FUNCIONAL,
     "guardar acciones hechas por el usuario en el editor de páginas", "persistente"),
    (r"^loglevel", True, FUNCIONAL,
     "fijar el nivel de registro de errores que guarda el navegador", "persistente"),
    (r"^pll_language", True, FUNCIONAL, "recordar el idioma elegido en la web", "1 año"),
    (r"^wp-wpml_current_language", True, FUNCIONAL,
     "recordar el idioma elegido en la web", "1 día"),
    (r"^_lscache_vary", True, FUNCIONAL,
     "servir al visitante la version en cache que le corresponde", "2 dias"),
    (r"^googtrans", False, FUNCIONAL,
     "recordar el idioma al que se traduce la web", "sesión"),
    (r"^SLO_", False, FUNCIONAL,
     "recordar el estado del widget de traducción del sitio", "sesión"),
    (r"^bis_data", False, FUNCIONAL,
     "guardar el estado de los servicios de Google usados en la web", "sesión"),
    (r"^_gat", False, ESTADISTICAS,
     "limitar el porcentaje de solicitudes enviadas a Google Analytics", "1 minuto"),
    (r"^_gid", False, ESTADISTICAS,
     "distinguir a los usuarios en las estadísticas de visitas", "24 horas"),
    (r"^_ga", False, ESTADISTICAS,
     "distinguir a los usuarios y mantener el estado de la sesión de medición de visitas",
     "2 años"),
    (r"^_gcl_", False, MARKETING,
     "medir las conversiones de los anuncios de Google", "90 días"),
    (r"^_fbp", False, MARKETING,
     "identificar el navegador para medir y segmentar anuncios de Meta", "90 días"),
    (r"^(NID|CONSENT|SOCS|AEC|1P_JAR)$", False, MARKETING,
     "guardar las preferencias del usuario en los servicios de Google incrustados en la web",
     "6 meses"),
    (r"^(VISITOR_INFO1_LIVE|YSC|yt-remote)", False, MARKETING,
     "recordar la reproducción y las preferencias de los vídeos incrustados de YouTube",
     "6 meses"),
    (r"API$", False, MARKETING,
     "cargar el servicio externo incrustado en la web y comunicar la dirección IP del visitante "
     "a su proveedor", "sesión"),
    # Cookies que solo existen dentro del panel: Complianz las caza al escanear con la
    # sesion de admin abierta y, sin ficha, imprime "Proposito pendiente de investigacion".
    # retention None = respetar el plazo que ya tenga; solo se rellena si esta vacio.
    (r"^(__mp|mp_)", False, ESTADISTICAS,
     "medir de forma agregada cómo se usa el editor de páginas; solo se instala a usuarios "
     "registrados que acceden al panel de administración", None),
    (r"^(elementor[-_]|e_wp)", True, FUNCIONAL,
     "recordar el estado y las preferencias del editor de páginas; solo se instala a "
     "usuarios registrados que acceden al panel de administración", None),
    (r"^(uf_|usetiful)", False, FUNCIONAL,
     "mostrar las guías de ayuda del panel de administración; solo se instala a usuarios "
     "registrados que acceden al panel", None),
    (r"^(wcpdf_|wc-blocks_|storeApi|WOOCOMMERCE_CHECKOUT|dgwt_|checklists|tours|featurebase)",
     True, FUNCIONAL,
     "recordar el estado de las pantallas de la tienda en el panel de administración; solo "
     "se instala a usuarios registrados que acceden al panel", None),
    (r"^wc_fragments", True, FUNCIONAL,
     "guardar el contenido del carrito para mostrarlo sin recargar la página", "persistente"),
    (r"^woocommerce_items_in_cart", True, FUNCIONAL,
     "saber si hay productos en el carrito para mostrarlo actualizado", "sesión"),
    (r"^woocommerce_cart_hash", True, FUNCIONAL,
     "detectar cambios en el carrito de la tienda", "sesión"),
    (r"^wp_woocommerce_session", True, FUNCIONAL,
     "identificar la sesión de compra y recordar el carrito entre páginas", "2 días"),
    (r"^woocommerce_recently_viewed", True, FUNCIONAL,
     "recordar los productos vistos para volver a mostrarlos", "sesión"),
    # Pasarela de pago: medidas en un cliente con Stripe el 2026-08-28. Solo se instalan al llegar al
    # carrito o al pago, asi que no aparecen midiendo la portada.
    (r"^__stripe_mid$", False, FUNCIONAL,
     "prevenir el fraude en el pago identificando el dispositivo", "1 año"),
    (r"^__stripe_sid$", False, FUNCIONAL,
     "prevenir el fraude durante la sesión de pago", "30 minutos"),
    # Redes sociales incrustadas: Complianz las registra al escanear los embeds.
    # Nombres EXACTOS, con `$`: sin el ancla, los tokens de dos y tres letras se comen
    # cualquier cookie que empiece igual. Medido el 2026-08-28 en un sitio con WooCommerce (las 7
    # `sbjs_*` de WooCommerce las cazaba `sb`) y en otro sitio (`activechatyWidgets` la
    # cazaba `act`): la politica del cliente acababa declarando cookies de Meta que esa web
    # no instala, con la descripcion de Facebook e Instagram encima.
    (r"^(datr|c_user|xs|fr|sb|wd|act|presence|csm|_js_datr|_fbc|actppresence)$"
     r"|^(fbm|\*_fbm_)",
     False, MARKETING,
     "reconocer la sesión de Facebook e Instagram para mostrar sus contenidos incrustados y "
     "medir los anuncios de Meta", None),
    (r"^(tt_csrf_token|tt_webid|ttwid|webapp[-_]|s_v_web_id|MONITOR_WEB_ID|csrf_session_id|_abck)",
     False, MARKETING,
     "identificar el navegador para los contenidos incrustados de TikTok y medir sus anuncios",
     None),
    (r"^(wa_lang_pref|wa_ul)$", False, FUNCIONAL,
     "recordar el idioma y la sesión de WhatsApp al abrir el chat desde la web", None),
    (r"^vuid$", False, ESTADISTICAS,
     "medir de forma agregada la reproducción de los vídeos incrustados de Vimeo", None),
    (r"^(GPS|PREF|__utmt_player)$", False, MARKETING,
     "recordar las preferencias de reproducción de los vídeos incrustados de YouTube", None),
    (r"^(li_|li-|lidc|linkedin|X-LI-|lms_|bcookie|bscookie|UserMatchHistory|"
     r"AnalyticsSyncHistory|BizographicsOptOut|"
     r"_guid|sdsc)", False, MARKETING,
     "reconocer al visitante en LinkedIn para mostrar sus contenidos incrustados y medir sus "
     "anuncios", None),
    (r"^(__tea_cache|guide-login-config|autoplay-config|^f$)", False, MARKETING,
     "recordar la sesión y las preferencias de reproducción de los contenidos incrustados de "
     "TikTok", None),
    (r"^(chatyWidget|activechatyWidgets|cht_country_code|hide-)", True, FUNCIONAL,
     "recordar si ya se ha mostrado o cerrado el botón de contacto y desde qué país se "
     "visita, para ofrecer el canal adecuado", None),
    (r"^_grecaptcha$", False, FUNCIONAL,
     "distinguir a las personas de los robots en los formularios de la web", "persistente"),
    (r"^PHPSESSID$", True, FUNCIONAL,
     "mantener la sesión del visitante mientras navega por la web", "sesión"),
    (r"^wc_cart_created", True, FUNCIONAL,
     "guardar cuándo se creó el carrito de la tienda", None),
    (r"^wc_cart_hash", True, FUNCIONAL,
     "detectar cambios en el carrito de la tienda", "sesión"),
    (r"^fpd-storage", True, FUNCIONAL,
     "guardar la configuración del personalizador de productos mientras se diseña", "sesión"),
    (r"^sbjs_(udata|first_add)", True, MARKETING,
     "guardar el origen desde el que llegó el visitante para atribuir los pedidos", "6 meses"),
    (r"^sbjs_session", True, MARKETING,
     "contar las páginas vistas de la visita para atribuir los pedidos", "30 minutos"),
    (r"^sbjs_", True, MARKETING,
     "guardar el origen desde el que llegó el visitante para atribuir los pedidos de la "
     "tienda", "sesión"),
    (r"^googlesitekit", True, FUNCIONAL,
     "guardar los datos que muestra el panel de Site Kit al administrador de la web; solo "
     "se instala a usuarios registrados que acceden al panel", None),
    (r"^rank-math", True, FUNCIONAL,
     "recordar la pestaña abierta en los ajustes de SEO del panel; solo se instala a "
     "usuarios registrados que acceden al panel", None),
    (r"^(igd_|jetDasboardData|customer-effort-score|tk_ai|tk_qs|litespeed_|"
     r"adobeCleanFontAdded|jetpack|woocommerce_admin)", True, FUNCIONAL,
     "recordar ajustes y avisos de las pantallas del panel de administración; solo se "
     "instala a usuarios registrados que acceden al panel", None),
    (r"^__paypal_storage__", False, FUNCIONAL,
     "permitir el pago con PayPal y prevenir el fraude en la pasarela", None),
    (r"^intercom", False, FUNCIONAL,
     "mantener la conversación del chat de soporte incrustado en la web", None),
    # Redes sociales incrustadas: Complianz las registra al escanear los embeds.
    # Nombres EXACTOS, con `$`: sin el ancla, los tokens de dos y tres letras se comen
    # cualquier cookie que empiece igual. Medido el 2026-08-28 en un sitio con WooCommerce (las 7
    # `sbjs_*` de WooCommerce las cazaba `sb`) y en otro sitio (`activechatyWidgets` la
    # cazaba `act`): la politica del cliente acababa declarando cookies de Meta que esa web
    # no instala, con la descripcion de Facebook e Instagram encima.
    (r"^(datr|c_user|xs|fr|sb|wd|act|presence|csm|_js_datr|_fbc|actppresence)$"
     r"|^(fbm|\*_fbm_)",
     False, MARKETING,
     "reconocer la sesión de Facebook e Instagram para mostrar sus contenidos incrustados y "
     "medir los anuncios de Meta", None),
    (r"^(tt_csrf_token|tt_webid|ttwid|webapp[-_]|s_v_web_id|MONITOR_WEB_ID|csrf_session_id|_abck)",
     False, MARKETING,
     "identificar el navegador para los contenidos incrustados de TikTok y medir sus anuncios",
     None),
    (r"^(wa_lang_pref|wa_ul)$", False, FUNCIONAL,
     "recordar el idioma y la sesión de WhatsApp al abrir el chat desde la web", None),
    (r"^vuid$", False, ESTADISTICAS,
     "medir de forma agregada la reproducción de los vídeos incrustados de Vimeo", None),
    (r"^(GPS|PREF|__utmt_player)$", False, MARKETING,
     "recordar las preferencias de reproducción de los vídeos incrustados de YouTube", None),
    (r"^(li_|li-|lidc|linkedin|X-LI-|lms_|bcookie|bscookie|UserMatchHistory|"
     r"AnalyticsSyncHistory|BizographicsOptOut|"
     r"_guid|sdsc)", False, MARKETING,
     "reconocer al visitante en LinkedIn para mostrar sus contenidos incrustados y medir sus "
     "anuncios", None),
    (r"^(__tea_cache|guide-login-config|autoplay-config|^f$)", False, MARKETING,
     "recordar la sesión y las preferencias de reproducción de los contenidos incrustados de "
     "TikTok", None),
    (r"^(chatyWidget|activechatyWidgets|cht_country_code|hide-)", True, FUNCIONAL,
     "recordar si ya se ha mostrado o cerrado el botón de contacto y desde qué país se "
     "visita, para ofrecer el canal adecuado", None),
    (r"^_grecaptcha$", False, FUNCIONAL,
     "distinguir a las personas de los robots en los formularios de la web", "persistente"),
    (r"^PHPSESSID$", True, FUNCIONAL,
     "mantener la sesión del visitante mientras navega por la web", "sesión"),
    (r"^(pys_|pysTrafficSource|last_pys|lastExternalReferrer)", True, MARKETING,
     "guardar de dónde llegó el visitante y qué páginas ve, para medir el rendimiento de "
     "las campañas publicitarias", None),
    (r"^topicsLastReferenceTime", False, MARKETING,
     "guardar cuándo se consultaron por última vez los temas de interés que el navegador "
     "comparte con los anunciantes", None),
    (r"^ratingData", True, FUNCIONAL,
     "recordar las valoraciones que el visitante ya ha enviado", None),
    (r"^e_site-editor", True, FUNCIONAL,
     "guardar los ajustes del editor de plantillas; solo se instala a usuarios registrados "
     "que acceden al panel de administración", None),
    (r"^(ht_ctc_admin|mtnc_upsell)", True, FUNCIONAL,
     "recordar avisos ya vistos en el panel de administración; solo se instala a usuarios "
     "registrados que acceden al panel", None),
    (r"^popup-\d+-impressions-count", True, FUNCIONAL,
     "contar cuántas veces se ha mostrado un aviso emergente para no repetirlo", None),
    (r"^country_code$", True, FUNCIONAL,
     "recordar el país detectado del visitante para adaptar los contenidos", None),
    (r"^joinchat", True, FUNCIONAL,
     "recordar el país detectado para mostrar el botón de contacto por WhatsApp", None),
    (r"^woocommerce_cart_hash|^woocommerce_items_in_cart|^wp_woocommerce_session",
     True, FUNCIONAL, "recordar los productos añadidos al carrito de la tienda", "2 días"),
]


# patron de nombre -> servicio al que pertenece la cookie. Sin esto Complianz las
# agrupa bajo "Varios" y escribe "El intercambio de datos esta pendiente de
# investigacion", que es literalmente lo que el Kit Digital marca como incumplimiento.
SERVICIOS = [
    (r"^cmplz_", "Complianz"),
    (r"^(e_|elementor|loglevel)", "Elementor"),
    (r"^(__mp|mp_)", "Mixpanel"),
    (r"^(uf_|usetiful)", "Usetiful"),
    (r"^googlesitekit", "Google Site Kit"),
    (r"^_grecaptcha$", "reCAPTCHA"),
    (r"^rank-math", "Rank Math"),
    (r"^__paypal_storage__", "PayPal"),
    (r"^__stripe_", "Stripe"),
    (r"^intercom", "Intercom"),
    (r"^(wcpdf_|wc-blocks_|storeApi|WOOCOMMERCE_CHECKOUT|dgwt_|checklists|tours|featurebase|sbjs_|"
     r"woocommerce_|wp_woocommerce_)", "WooCommerce"),
    (r"^(wp_lang|wp-settings|wordpress_|WP_DATA_USER|WP_PREFERENCES_USER|wpEmoji)", "WordPress"),
    (r"^(pys_|pysTrafficSource|last_pys)", "PixelYourSite"),
    (r"^(_ga|_gid|_gat)", "Google Analytics"),
    (r"^(SLO_|googtrans|bis_data)", "Google Translate"),
    (r"^(_gcl_)", "Google Ads"),
    (r"^topicsLastReferenceTime", "Google Ads"),
    (r"^(pys_|pysTrafficSource|last_pys|lastExternalReferrer)", "PixelYourSite"),
    (r"^(_fbp|datr|c_user|xs|fr|sb|wd|act|presence|csm|_js_datr|_fbc|actppresence)$"
     r"|^(fbm|\*_fbm_)", "Meta"),
    (r"^(tt_csrf_token|tt_webid|ttwid|webapp[-_]|s_v_web_id|MONITOR_WEB_ID|csrf_session_id|_abck|__tea_cache|guide-login-config|autoplay-config)", "TikTok"),
    (r"^(li_|li-|lidc|linkedin|X-LI-|lms_|bcookie|bscookie|UserMatchHistory|AnalyticsSyncHistory|BizographicsOptOut|_guid|sdsc)", "LinkedIn"),
    (r"^(wa_lang_pref|wa_ul)$", "WhatsApp"),
    (r"^vuid$", "Vimeo"),
    (r"^(GPS|PREF|__utmt_player|VISITOR_INFO1_LIVE|YSC|yt-remote)", "YouTube"),
]
# nombre -> (tipo en castellano, tipo en ingles, de terceros, comparte datos, url privacidad)
FICHA_SERVICIO = {
    "Complianz": ("gestión del consentimiento", "consent management", 0, 0, ""),
    "Elementor": ("creación de contenido", "content creation", 0, 0, ""),
    "WordPress": ("desarrollo de sitios web", "website development", 0, 0, ""),
    "Google Analytics": ("estadísticas de visitas", "statistics", 1, 1,
                         "https://policies.google.com/privacy"),
    "Google Translate": ("traducción del sitio", "site translation", 1, 1,
                         "https://policies.google.com/privacy"),
    "Google Ads": ("publicidad", "advertising", 1, 1, "https://policies.google.com/privacy"),
    "PixelYourSite": ("medir campañas publicitarias", "advertising measurement", 0, 0, ""),
    "Meta": ("publicidad", "advertising", 1, 1, "https://www.facebook.com/privacy/policy/"),
    "Mixpanel": ("medir el uso del editor de páginas", "product analytics", 1, 1,
                 "https://mixpanel.com/legal/privacy-policy/"),
    "Usetiful": ("guías de ayuda del panel", "user onboarding", 1, 1,
                 "https://www.usetiful.com/privacy-policy"),
    "WooCommerce": ("tienda online", "e-commerce", 0, 0, ""),
    "Sourcebuster JS": ("atribuir el origen de los pedidos", "traffic attribution", 0, 0, ""),
    "Fancy Product Designer": ("personalizar productos", "product customizer", 0, 0, ""),
    "Custom Field Bulk Editor": ("editar campos desde el panel", "admin bulk editing", 0, 0, ""),
    "Google Fonts": ("mostrar fuentes web", "display of webfonts", 1, 1,
                     "https://policies.google.com/privacy"),
    "Google Maps": ("mostrar mapas", "maps display", 1, 1,
                    "https://business.safety.google/privacy/"),
    "AddToAny": ("botones para compartir", "social sharing", 1, 1,
                 "https://www.addtoany.com/privacy"),
    "YouTube": ("vídeos incrustados", "embedded videos", 1, 1,
                "https://policies.google.com/privacy"),
    "LinkedIn": ("contenido incrustado y anuncios", "embedded content and ads", 1, 1,
                 "https://www.linkedin.com/legal/privacy-policy"),
    "TikTok": ("contenido incrustado", "embedded content", 1, 1,
               "https://www.tiktok.com/legal/privacy-policy"),
    "WhatsApp": ("chat de contacto", "contact chat", 1, 1,
                 "https://www.whatsapp.com/legal/privacy-policy"),
    "Vimeo": ("vídeos incrustados", "embedded videos", 1, 1,
              "https://vimeo.com/privacy"),
    "Instagram": ("contenido incrustado", "embedded content", 1, 1,
                  "https://privacycenter.instagram.com/policy"),
    "reCAPTCHA": ("protección de formularios", "form protection", 1, 1,
                  "https://policies.google.com/privacy"),
    "Google Site Kit": ("panel de estadísticas del sitio", "site statistics dashboard", 0, 0,
                        "https://policies.google.com/privacy"),
    "Rank Math": ("optimización para buscadores", "search engine optimization", 0, 0, ""),
    "PayPal": ("pasarela de pago", "payment gateway", 1, 1,
               "https://www.paypal.com/es/legalhub/privacy-full"),
    "Intercom": ("chat de soporte", "customer support chat", 1, 1,
                 "https://www.intercom.com/legal/privacy"),
}

def clasifica(nombre):
    """Devuelve (propia, tipo, finalidad, plazo) o None si no esta catalogada."""
    for patron, propia, purpose, funcion, retencion in CATALOGO:
        if re.search(patron, nombre, re.I):
            return propia, purpose, funcion, retencion
    return None


def servicio_de(nombre):
    for patron, servicio in SERVICIOS:
        if re.search(patron, nombre, re.I):
            return servicio
    return None


# Cookies que SOLO existen dentro de /wp-admin, para el administrador de la web: nunca
# llegan a un visitante. Listarlas en la politica publica no informa de nada y ademas
# revienta la lectura en movil (nombres como
# `wcpdf_general_settings_accordion_state_checkout_fields` se salen del viewport).
SOLO_PANEL = (
    r"^wcpdf_", r"^wc-blocks_dismissed", r"^(uf_|usetiful)", r"^elementor_sidebar_",
    r"^elementor-global-", r"^e_kit-elements-defaults", r"^(__mp|mp_)", r"^googlesitekit",
    r"^rank-math-option", r"^WP_DATA_USER", r"^WP_PREFERENCES_USER", r"^jetDasboardData",
    r"^igd_", r"^customer-effort-score", r"^tk_ai$", r"^tk_qs$", r"^checklists",
    r"^tours$", r"^featurebase", r"^dgwt_wcas_settings", r"^adobeCleanFontAdded",
    r"^litespeed_docref", r"^elementor_wpdash_session", r"^__mp_opt_in_out",
    r"^e_site-editor", r"^ht_ctc_admin", r"^mtnc_upsell", r"^wc_iam_settings",
    r"^wp-autosave", r"^wp-settings-time-\d+$", r"^attributes-notice-dismissed",
    r"^wc_remote_logging", r"^savefrom-helper", r"^mcp(Functions|Settings)",
    r"^environmentCategories", r"^mwai_", r"^e_my_templates_source", r"^debug$",
)


def solo_panel(nombre):
    return any(re.search(patron, nombre, re.I) for patron in SOLO_PANEL)
