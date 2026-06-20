<?php
/**
 * Plugin Name: VTR Schema Merchant
 * Description: Agrega brand (Victtorino) y mpn (=SKU) al schema Product de RankMath para que Google Merchant Center acepte los productos (griferias sin GTIN real -> brand+mpn es identificador valido).
 * Author: Victtorino
 * Version: 1.0
 */

if ( ! defined( 'ABSPATH' ) ) { exit; }

add_filter( 'rank_math/snippet/rich_snippet_product_entity', function ( $entity ) {
    if ( ! is_array( $entity ) ) {
        return $entity;
    }

    // 1) Marca: si RankMath no la trae, fijar "Victtorino".
    if ( empty( $entity['brand'] ) ) {
        $entity['brand'] = array(
            '@type' => 'Brand',
            'name'  => 'Victtorino',
        );
    }

    // 2) MPN = SKU del producto (identificador del fabricante que Google acepta junto a la marca).
    if ( empty( $entity['mpn'] ) ) {
        $product = null;
        if ( function_exists( 'wc_get_product' ) ) {
            global $product;
            if ( ! ( $product instanceof WC_Product ) ) {
                $product = wc_get_product( get_the_ID() );
            }
        }
        if ( $product instanceof WC_Product ) {
            $sku = $product->get_sku();
            if ( ! empty( $sku ) ) {
                $entity['mpn'] = $sku;
            }
        }
    }

    return $entity;
}, 20 );
