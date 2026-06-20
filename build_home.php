<?php
// Construye la home de Trade (bloques nativos) y la deja como portada.
$content = <<<'HTML'
<!-- wp:cover {"customGradient":"linear-gradient(135deg,#003078 0%,#0084B8 55%,#00B8E6 100%)","minHeight":480,"contentPosition":"center center","align":"full"} -->
<div class="wp-block-cover alignfull has-custom-content-position is-position-center-center" style="min-height:480px"><span aria-hidden="true" class="wp-block-cover__background has-background-gradient" style="background:linear-gradient(135deg,#003078 0%,#0084B8 55%,#00B8E6 100%)"></span><div class="wp-block-cover__inner-container">
<!-- wp:heading {"textAlign":"center","level":1,"style":{"typography":{"fontSize":"52px","fontWeight":"800","lineHeight":"1.1"},"color":{"text":"#ffffff"}}} -->
<h1 class="wp-block-heading has-text-align-center has-text-color" style="color:#ffffff;font-size:52px;font-weight:800;line-height:1.1">Soluciones para tu hogar</h1>
<!-- /wp:heading -->
<!-- wp:paragraph {"align":"center","style":{"typography":{"fontSize":"19px"},"color":{"text":"#e6f6fc"}}} -->
<p class="has-text-align-center has-text-color" style="color:#e6f6fc;font-size:19px">Grifería, baño y cocina de calidad — con despacho a todo Chile.</p>
<!-- /wp:paragraph -->
<!-- wp:buttons {"layout":{"type":"flex","justifyContent":"center"}} -->
<div class="wp-block-buttons"><!-- wp:button {"style":{"color":{"text":"#003078","background":"#ffffff"},"border":{"radius":"8px"},"typography":{"fontWeight":"700"}}} -->
<div class="wp-block-button"><a class="wp-block-button__link has-text-color has-background wp-element-button" href="/tienda/" style="border-radius:8px;color:#003078;background-color:#ffffff;font-weight:700">Ver catálogo</a></div>
<!-- /wp:button --></div>
<!-- /wp:buttons -->
</div></div>
<!-- /wp:cover -->

<!-- wp:heading {"textAlign":"center","style":{"spacing":{"margin":{"top":"56px"}}}} -->
<h2 class="wp-block-heading has-text-align-center" style="margin-top:56px">Lo más nuevo</h2>
<!-- /wp:heading -->

<!-- wp:woocommerce/product-new {"columns":4,"rows":2} /-->

<!-- wp:group {"style":{"spacing":{"padding":{"top":"48px","bottom":"48px"},"margin":{"top":"40px"}},"color":{"background":"#f5f7fa"}},"align":"full","layout":{"type":"constrained"}} -->
<div class="wp-block-group alignfull has-background" style="background-color:#f5f7fa;margin-top:40px;padding-top:48px;padding-bottom:48px">
<!-- wp:heading {"textAlign":"center"} -->
<h2 class="wp-block-heading has-text-align-center">Compra con confianza</h2>
<!-- /wp:heading -->
<!-- wp:columns {"style":{"spacing":{"margin":{"top":"24px"}}}} -->
<div class="wp-block-columns" style="margin-top:24px">
<!-- wp:column -->
<div class="wp-block-column"><!-- wp:paragraph {"align":"center","style":{"typography":{"fontSize":"34px"}}} --><p class="has-text-align-center" style="font-size:34px">🚚</p><!-- /wp:paragraph --><!-- wp:heading {"textAlign":"center","level":4} --><h4 class="wp-block-heading has-text-align-center">Despacho a todo Chile</h4><!-- /wp:heading --><!-- wp:paragraph {"align":"center"} --><p class="has-text-align-center">Envíos rápidos y seguros a tu hogar.</p><!-- /wp:paragraph --></div>
<!-- /wp:column -->
<!-- wp:column -->
<div class="wp-block-column"><!-- wp:paragraph {"align":"center","style":{"typography":{"fontSize":"34px"}}} --><p class="has-text-align-center" style="font-size:34px">🛡️</p><!-- /wp:paragraph --><!-- wp:heading {"textAlign":"center","level":4} --><h4 class="wp-block-heading has-text-align-center">Garantía oficial</h4><!-- /wp:heading --><!-- wp:paragraph {"align":"center"} --><p class="has-text-align-center">Productos con respaldo y garantía.</p><!-- /wp:paragraph --></div>
<!-- /wp:column -->
<!-- wp:column -->
<div class="wp-block-column"><!-- wp:paragraph {"align":"center","style":{"typography":{"fontSize":"34px"}}} --><p class="has-text-align-center" style="font-size:34px">🔒</p><!-- /wp:paragraph --><!-- wp:heading {"textAlign":"center","level":4} --><h4 class="wp-block-heading has-text-align-center">Pago 100% seguro</h4><!-- /wp:heading --><!-- wp:paragraph {"align":"center"} --><p class="has-text-align-center">Paga con Webpay con total tranquilidad.</p><!-- /wp:paragraph --></div>
<!-- /wp:column -->
</div>
<!-- /wp:columns -->
</div>
<!-- /wp:group -->
HTML;

$existing = get_page_by_path('home');
$args = array('post_title'=>'Home','post_name'=>'home','post_content'=>$content,'post_status'=>'publish','post_type'=>'page');
if ($existing) { $args['ID'] = $existing->ID; $id = wp_update_post($args); }
else { $id = wp_insert_post($args); }
update_option('show_on_front','page');
update_option('page_on_front', $id);
echo "home creada/actualizada ID=$id y fijada como portada\n";
